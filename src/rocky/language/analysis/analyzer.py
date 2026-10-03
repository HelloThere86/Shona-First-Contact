"""Initial linguistic analyzer for Shona word structures and relationships."""

from __future__ import annotations

from typing import Sequence

from rocky.language.analysis.data import (
    build_default_noun_class_registry,
    build_default_rule_registry,
    get_default_word_relationships,
)
from rocky.language.analysis.models import (
    CertaintyLevel,
    NumberCategory,
    WordAnalysis,
    WordFormRelationship,
)
from rocky.language.analysis.registry import NounClassRegistry
from rocky.language.analysis.rules import RuleRegistry
from rocky.language.text import Token


class ShonaLinguisticAnalyzer:
    """Analyzes Shona words for noun classes, stems, and word-form relationships."""

    def __init__(
        self,
        class_registry: NounClassRegistry | None = None,
        rule_registry: RuleRegistry | None = None,
        relationships: Sequence[WordFormRelationship] | None = None,
    ) -> None:
        """Initialize the analyzer with linguistic data.

        Args:
            class_registry: NounClassRegistry instance (or default if None).
            rule_registry: RuleRegistry instance (or default if None).
            relationships: Sequence of verified WordFormRelationship entries (or default if None).
        """
        self.class_registry = class_registry or build_default_noun_class_registry()
        self.rule_registry = rule_registry or build_default_rule_registry()
        self.relationships = (
            list(relationships)
            if relationships is not None
            else get_default_word_relationships()
        )
        self._build_lexicon_index()

    def _build_lexicon_index(self) -> None:
        """Index verified relationships by source and target words."""
        self._lexicon: dict[str, list[tuple[WordFormRelationship, bool]]] = {}
        for rel in self.relationships:
            self._lexicon.setdefault(rel.source_word, []).append((rel, True))
            if rel.target_word != rel.source_word:
                self._lexicon.setdefault(rel.target_word, []).append((rel, False))

    def analyze_word(self, word: str) -> list[WordAnalysis]:
        """Analyze a normalized Shona word.

        Args:
            word: The normalized Shona word string.

        Returns:
            List of WordAnalysis objects (may contain multiple interpretations if ambiguous,
            or an unresolved analysis if no documented rule or entry matches).

        Raises:
            TypeError: If input is not a string.
            ValueError: If input is empty or whitespace-only.
        """
        if not isinstance(word, str):
            raise TypeError(f"Word must be a string, received {type(word).__name__}.")

        cleaned = word.strip().lower()
        if not cleaned:
            raise ValueError("Word cannot be empty or whitespace.")

        # Step 1: Check verified lexical relationships
        if cleaned in self._lexicon:
            return self._analyze_from_lexicon(cleaned)

        # Step 2: Check documented morphological rules
        matching_rules = self.rule_registry.find_matching_rules(cleaned)
        if matching_rules:
            return self._analyze_from_rules(cleaned, matching_rules)

        # Step 3: Explicit unresolved result when no rule applies
        return [
            WordAnalysis(
                word=cleaned,
                certainty=CertaintyLevel.UNRESOLVED,
                noun_class=None,
                stem=None,
                prefix=None,
                number=NumberCategory.UNSPECIFIED,
                paired_form=None,
                rule_id=None,
                explanation="No verified lexical entry or documented morphological rule matched this word form.",
                related_forms=(),
            )
        ]

    def _analyze_from_lexicon(self, word: str) -> list[WordAnalysis]:
        """Produce confirmed analyses from verified lexical entries."""
        results: list[WordAnalysis] = []
        for rel, is_source in self._lexicon[word]:
            class_id = rel.source_class_id if is_source else rel.target_class_id
            noun_class = self.class_registry.get(class_id) if class_id else None
            paired_word = rel.target_word if is_source else rel.source_word

            prefix: str | None = None
            if rel.stem and word.endswith(rel.stem):
                prefix = word[: -len(rel.stem)] or None

            # Handle invariable mass nouns (e.g. mvura, mukaka)
            if rel.relationship_type == "invariable":
                number = NumberCategory.INVARIABLE
            elif noun_class:
                number = noun_class.number
            else:
                number = NumberCategory.UNSPECIFIED

            certainty = CertaintyLevel.CONFIRMED if rel.is_confirmed else CertaintyLevel.TENTATIVE

            if rel.is_confirmed and rel.relationship_type == "invariable":
                explanation = (
                    f"Confirmed lexical entry: Class {class_id} invariable mass noun."
                )
            elif rel.is_confirmed and rel.stem:
                explanation = (
                    f"Confirmed lexical entry: Class {class_id} ({number.value}) paired with "
                    f"'{paired_word}' (stem: '{rel.stem}')."
                )
            elif rel.is_confirmed:
                explanation = (
                    f"Confirmed lexical entry: Class {class_id} ({number.value}) paired with "
                    f"'{paired_word}'."
                )
            else:
                explanation = (
                    f"Documented relationship for '{word}' without verified stem decomposition: {rel.notes}"
                )

            results.append(
                WordAnalysis(
                    word=word,
                    certainty=certainty,
                    noun_class=noun_class,
                    stem=rel.stem,
                    prefix=prefix,
                    number=number,
                    paired_form=paired_word if paired_word != word else None,
                    rule_id="lexicon_verified" if rel.is_confirmed else "lexicon_unconfirmed",
                    explanation=explanation,
                    related_forms=(paired_word,) if paired_word != word else (),
                )
            )
        return results

    def _analyze_from_rules(self, word: str, rules: Sequence) -> list[WordAnalysis]:
        """Produce tentative analyses from morphological transformation rules."""
        results: list[WordAnalysis] = []
        for rule in rules:
            candidate_stem = rule.extract_candidate_stem(word)
            candidate_paired = rule.transform(word)
            noun_class = self.class_registry.get(rule.source_class_id)
            number = noun_class.number if noun_class else NumberCategory.UNSPECIFIED

            explanation = (
                f"Tentative rule match via '{rule.rule_id}': candidate Class {rule.source_class_id} "
                f"with stem '{candidate_stem}' and hypothetical paired form '{candidate_paired}'. "
                f"Requires linguistic verification."
            )

            results.append(
                WordAnalysis(
                    word=word,
                    certainty=CertaintyLevel.TENTATIVE,
                    noun_class=noun_class,
                    stem=candidate_stem,
                    prefix=rule.source_prefix,
                    number=number,
                    paired_form=candidate_paired,
                    rule_id=rule.rule_id,
                    explanation=explanation,
                    related_forms=(candidate_paired,) if candidate_paired else (),
                )
            )
        return results

    def get_known_relationship(self, word: str) -> WordFormRelationship | None:
        """Retrieve the primary verified relationship for a word, if present."""
        if not isinstance(word, str):
            return None
        cleaned = word.strip().lower()
        if cleaned in self._lexicon:
            return self._lexicon[cleaned][0][0]
        return None

    def find_related_forms(self, word: str) -> list[str]:
        """Return all verified or candidate related forms for a given word."""
        analyses = self.analyze_word(word)
        related = set()
        for a in analyses:
            if a.paired_form:
                related.add(a.paired_form)
            related.update(a.related_forms)
        return sorted(related)

    def analyze_tokens(
        self, tokens: Sequence[Token]
    ) -> list[tuple[Token, list[WordAnalysis]]]:
        """Analyze a sequence of Token objects from Rocky 0.3 text processing."""
        results: list[tuple[Token, list[WordAnalysis]]] = []
        for token in tokens:
            if token.is_punctuation:
                continue
            analyses = self.analyze_word(token.normalized)
            results.append((token, analyses))
        return results