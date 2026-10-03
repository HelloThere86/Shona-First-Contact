"""Immutable data models for Shona linguistic representations and analysis results."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence

from rocky.language.exceptions import InvalidNounClassError, InvalidRuleError


class NumberCategory(str, Enum):
    """Grammatical number categories."""

    SINGULAR = "singular"
    PLURAL = "plural"
    INVARIABLE = "invariable"
    UNSPECIFIED = "unspecified"


class CertaintyLevel(str, Enum):
    """Certainty and verification status of a linguistic analysis."""

    CONFIRMED = "confirmed"      # Verified against documented lexical entries
    TENTATIVE = "tentative"      # Deduced via general rule matching; unverified
    UNRESOLVED = "unresolved"    # No rule or verified lexical match found


@dataclass(frozen=True)
class NounClass:
    """Represents a Bantu noun class definition.

    Attributes:
        identifier: Standard class designation (e.g., '1', '2', '1a', '2a', '7').
        prefix: Primary canonical prefix (e.g., 'mu-', 'va-', 'chi-').
        number: Grammatical number category (singular, plural, invariable, unspecified).
        vowel_prefix: Secondary prefix used before vowel-initial stems (e.g., 'mw-', 'v-').
        paired_class_id: Identifier of the corresponding plural or singular class.
        description: Documented semantic tendencies and notes.
        examples: Documented example nouns belonging to this class.
    """

    identifier: str
    prefix: str
    number: NumberCategory
    vowel_prefix: str | None = None
    paired_class_id: str | None = None
    description: str = ""
    examples: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        """Validate noun class parameters upon construction."""
        if not isinstance(self.identifier, str) or not self.identifier.strip():
            raise InvalidNounClassError("Noun class identifier must be a non-empty string.")
        if not isinstance(self.prefix, str) or not self.prefix.strip():
            raise InvalidNounClassError("Noun class prefix must be a non-empty string.")
        if not isinstance(self.number, NumberCategory):
            raise InvalidNounClassError(
                f"Noun class number must be a NumberCategory enum, received {type(self.number).__name__}."
            )

        object.__setattr__(self, "identifier", self.identifier.strip())
        object.__setattr__(self, "prefix", self.prefix.strip())
        if self.vowel_prefix is not None:
            object.__setattr__(self, "vowel_prefix", self.vowel_prefix.strip())
        if self.paired_class_id is not None:
            object.__setattr__(self, "paired_class_id", self.paired_class_id.strip())


@dataclass(frozen=True)
class WordFormRelationship:
    """Represents a documented relationship between two related word forms.

    Attributes:
        source_word: Base or singular word form.
        target_word: Derived, inflected, or plural word form.
        relationship_type: Linguistic relationship label (e.g., 'singular_plural').
        source_class_id: Noun class of the source word.
        target_class_id: Noun class of the target word.
        stem: Verified common stem, or None if decomposition is unconfirmed.
        is_confirmed: True if decomposition is linguistically verified.
        notes: Documentation of uncertainty or morphophonological changes.
    """

    source_word: str
    target_word: str
    relationship_type: str = "singular_plural"
    source_class_id: str | None = None
    target_class_id: str | None = None
    stem: str | None = None
    is_confirmed: bool = True
    notes: str = ""

    def __post_init__(self) -> None:
        """Validate and normalize word form relationships."""
        if not isinstance(self.source_word, str) or not self.source_word.strip():
            raise ValueError("Source word must be a non-empty string.")
        if not isinstance(self.target_word, str) or not self.target_word.strip():
            raise ValueError("Target word must be a non-empty string.")

        object.__setattr__(self, "source_word", self.source_word.strip().lower())
        object.__setattr__(self, "target_word", self.target_word.strip().lower())
        if self.stem is not None:
            object.__setattr__(self, "stem", self.stem.strip().lower())


@dataclass(frozen=True)
class MorphologicalRule:
    """Represents a documented morphological prefix transformation rule.

    Attributes:
        rule_id: Unique rule identifier.
        description: Linguistic documentation for the rule.
        source_prefix: Prefix matched on the input word.
        target_prefix: Replacement prefix for generating related forms.
        source_class_id: Noun class associated with source prefix.
        target_class_id: Noun class associated with target prefix.
        min_stem_length: Minimum length of the remaining stem required for match.
        notes: Morphophonological notes and usage limitations.
    """

    rule_id: str
    description: str
    source_prefix: str
    target_prefix: str
    source_class_id: str
    target_class_id: str
    min_stem_length: int = 2
    notes: str = ""

    def __post_init__(self) -> None:
        """Validate morphological rule definitions."""
        if not isinstance(self.rule_id, str) or not self.rule_id.strip():
            raise InvalidRuleError("Rule ID must be a non-empty string.")
        if not isinstance(self.source_prefix, str) or not self.source_prefix.strip():
            raise InvalidRuleError("Source prefix must be a non-empty string.")
        if not isinstance(self.target_prefix, str) or not self.target_prefix.strip():
            raise InvalidRuleError("Target prefix must be a non-empty string.")
        if not isinstance(self.source_class_id, str) or not self.source_class_id.strip():
            raise InvalidRuleError("Source class ID must be a non-empty string.")
        if not isinstance(self.target_class_id, str) or not self.target_class_id.strip():
            raise InvalidRuleError("Target class ID must be a non-empty string.")
        if self.min_stem_length < 1:
            raise InvalidRuleError("Minimum stem length must be at least 1.")

        object.__setattr__(self, "rule_id", self.rule_id.strip())
        object.__setattr__(self, "source_prefix", self.source_prefix.strip().lower())
        object.__setattr__(self, "target_prefix", self.target_prefix.strip().lower())
        object.__setattr__(self, "source_class_id", self.source_class_id.strip())
        object.__setattr__(self, "target_class_id", self.target_class_id.strip())

    def can_apply(self, word: str) -> bool:
        """Check whether this rule's source prefix matches the given word."""
        if not isinstance(word, str):
            return False
        clean_word = word.strip().lower()
        if not clean_word.startswith(self.source_prefix):
            return False
        stem_len = len(clean_word) - len(self.source_prefix)
        return stem_len >= self.min_stem_length

    def extract_candidate_stem(self, word: str) -> str | None:
        """Extract candidate stem by removing source prefix if rule matches."""
        if not self.can_apply(word):
            return None
        clean_word = word.strip().lower()
        return clean_word[len(self.source_prefix) :]

    def transform(self, word: str) -> str | None:
        """Derive paired word form by swapping source prefix for target prefix."""
        candidate_stem = self.extract_candidate_stem(word)
        if candidate_stem is None:
            return None
        return f"{self.target_prefix}{candidate_stem}"


@dataclass(frozen=True)
class WordAnalysis:
    """Detailed linguistic analysis result for a given word.

    Attributes:
        word: Normalized word analyzed.
        certainty: Level of certainty (CONFIRMED, TENTATIVE, UNRESOLVED).
        noun_class: Resolved NounClass object, or None if unknown.
        stem: Resolved or candidate root stem, or None.
        prefix: Resolved or candidate prefix, or None.
        number: Grammatical number category.
        paired_form: Expected singular or plural form, if resolved or derived.
        rule_id: Identifying rule or lexicon entry that produced this analysis.
        explanation: Explanation of how this analysis was derived or why unresolved.
        related_forms: Known or candidate related word forms.
    """

    word: str
    certainty: CertaintyLevel
    noun_class: NounClass | None = None
    stem: str | None = None
    prefix: str | None = None
    number: NumberCategory = NumberCategory.UNSPECIFIED
    paired_form: str | None = None
    rule_id: str | None = None
    explanation: str = ""
    related_forms: tuple[str, ...] = ()