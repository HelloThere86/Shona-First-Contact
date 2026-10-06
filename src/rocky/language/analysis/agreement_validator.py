"""Enhanced linguistic concord agreement validator with stem verification and evidence tracking."""

from __future__ import annotations

from typing import Sequence

from rocky.language.analysis.concord_analyzer import ShonaConcordAnalyzer
from rocky.language.analysis.concord_models import ConcordCategory
from rocky.language.analysis.knowledge_base import (
    LinguisticKnowledgeBase,
    build_default_knowledge_base,
)
from rocky.language.analysis.knowledge_models import (
    DetailedAgreementValidation,
    StemGrammaticalCategory,
    ValidationVerdict,
)
from rocky.language.analysis.models import CertaintyLevel
from rocky.language.exceptions import UnsupportedCategoryError
from rocky.language.text import Token


class ShonaAgreementValidator:
    """Validates concord agreement between nouns and dependent syntactic constituents."""

    def __init__(
        self,
        concord_analyzer: ShonaConcordAnalyzer | None = None,
        knowledge_base: LinguisticKnowledgeBase | None = None,
    ) -> None:
        self.concord_analyzer = concord_analyzer or ShonaConcordAnalyzer()
        self.knowledge_base = knowledge_base or build_default_knowledge_base()

    def validate(
        self,
        noun_word: str,
        target_word: str,
        category: ConcordCategory,
    ) -> list[DetailedAgreementValidation]:
        """Perform detailed concord agreement validation.

        Args:
            noun_word: Head noun or subject string.
            target_word: Dependent verb, adjective, or possessive string.
            category: Concord category to validate.

        Returns:
            List of DetailedAgreementValidation objects detailing matches, mismatches,
            ambiguity, or unverified stems.
        """
        if not isinstance(noun_word, str):
            raise TypeError(f"Noun word must be a string, received {type(noun_word).__name__}.")
        if not isinstance(target_word, str):
            raise TypeError(f"Target word must be a string, received {type(target_word).__name__}.")

        clean_noun = noun_word.strip().lower()
        clean_target = target_word.strip().lower()

        if not clean_noun:
            raise ValueError("Noun word cannot be empty or whitespace.")
        if not clean_target:
            raise ValueError("Target word cannot be empty or whitespace.")
        if not isinstance(category, ConcordCategory):
            raise UnsupportedCategoryError(
                f"Expected ConcordCategory enum, received {type(category).__name__}."
            )

        # 1. Obtain projected concord analyses from Rocky 0.5 analyzer
        concord_analyses = self.concord_analyzer.analyze_agreement(clean_noun, category)
        results: list[DetailedAgreementValidation] = []

        for c_analysis in concord_analyses:
            # Case A: Explicit handling for unsupported categories (Defect 2 fix)
            # Evaluated first so POSSESSIVE and OBJECT immediately return UNSUPPORTED_SYNTACTIC_FORM.
            if category not in (ConcordCategory.SUBJECT, ConcordCategory.ADJECTIVE):
                if category == ConcordCategory.POSSESSIVE:
                    explanation = (
                        f"Unsupported syntactic form: validation for category '{category.value}' "
                        f"is not yet implemented. Possessive morphology and stem validation "
                        f"will be supported in a future milestone."
                    )
                elif category == ConcordCategory.OBJECT:
                    explanation = (
                        f"Unsupported syntactic form: validation for category '{category.value}' "
                        f"is not yet implemented. Object concord validation is deferred to a future milestone."
                    )
                else:
                    explanation = (
                        f"Unsupported syntactic form: validation for category '{category.value}' "
                        f"is not supported by the current validator."
                    )

                results.append(
                    DetailedAgreementValidation(
                        noun_word=clean_noun,
                        target_word=clean_target,
                        category=category,
                        verdict=ValidationVerdict.UNSUPPORTED_SYNTACTIC_FORM,
                        certainty=c_analysis.certainty,
                        controlling_class_id=c_analysis.noun_class_id,
                        matched_prefix=None,
                        extracted_stem=None,
                        evidence=None,
                        explanation=explanation,
                    )
                )
                continue

            # Case B: Controller noun is unresolved
            if (
                c_analysis.certainty == CertaintyLevel.UNRESOLVED
                or not c_analysis.noun_class_id
                or not c_analysis.concord_prefix
            ):
                results.append(
                    DetailedAgreementValidation(
                        noun_word=clean_noun,
                        target_word=clean_target,
                        category=category,
                        verdict=ValidationVerdict.UNRESOLVED_CONTROLLER,
                        certainty=CertaintyLevel.UNRESOLVED,
                        controlling_class_id=c_analysis.noun_class_id,
                        matched_prefix=None,
                        extracted_stem=None,
                        evidence=None,
                        explanation=f"Validation inconclusive: noun class for '{clean_noun}' is unresolved.",
                    )
                )
                continue

            class_id = c_analysis.noun_class_id
            expected_prefix = c_analysis.concord_prefix

            # Case C: Adjectival Consonant Mutation for Class 9/10
            if category == ConcordCategory.ADJECTIVE and class_id in ("9", "10"):
                mutation = self.knowledge_base.get_mutation_by_surface(clean_target, class_id)
                if mutation:
                    verdict = (
                        ValidationVerdict.AMBIGUOUS_MATCH
                        if c_analysis.is_ambiguous
                        else (
                            ValidationVerdict.CONFIRMED_MATCH
                            if c_analysis.certainty == CertaintyLevel.CONFIRMED
                            else ValidationVerdict.TENTATIVE_MATCH
                        )
                    )
                    results.append(
                        DetailedAgreementValidation(
                            noun_word=clean_noun,
                            target_word=clean_target,
                            category=category,
                            verdict=verdict,
                            certainty=c_analysis.certainty,
                            controlling_class_id=class_id,
                            matched_prefix=None,
                            extracted_stem=mutation.base_stem,
                            evidence=mutation.evidence,
                            explanation=(
                                f"Valid Class {class_id} adjectival mutation: '{clean_target}' is the "
                                f"mutated form of base stem '-{mutation.base_stem}' (citation: {mutation.evidence.citation})."
                            ),
                        )
                    )
                    continue

            # Case D: Check prefix match
            if not clean_target.startswith(expected_prefix):
                results.append(
                    DetailedAgreementValidation(
                        noun_word=clean_noun,
                        target_word=clean_target,
                        category=category,
                        verdict=ValidationVerdict.CONCORD_MISMATCH,
                        certainty=c_analysis.certainty,
                        controlling_class_id=class_id,
                        matched_prefix=None,
                        extracted_stem=None,
                        evidence=None,
                        explanation=(
                            f"Concord mismatch: '{clean_target}' does not begin with expected "
                            f"{category.value} concord '{expected_prefix}' for Class {class_id}."
                        ),
                    )
                )
                continue

            # Case E: Prefix matched -> Decompose and evaluate the stem
            candidate_residue = clean_target[len(expected_prefix) :]

            # Minimum viable stem guard: target must not simply be the prefix itself
            if len(candidate_residue) < 1:
                results.append(
                    DetailedAgreementValidation(
                        noun_word=clean_noun,
                        target_word=clean_target,
                        category=category,
                        verdict=ValidationVerdict.UNSUPPORTED_SYNTACTIC_FORM,
                        certainty=c_analysis.certainty,
                        controlling_class_id=class_id,
                        matched_prefix=expected_prefix,
                        extracted_stem=None,
                        evidence=None,
                        explanation=(
                            f"Unsupported syntactic form: target word '{clean_target}' is too short "
                            f"to yield a viable stem after prefix '{expected_prefix}'."
                        ),
                    )
                )
                continue

            # Case F: Class 9/10 Adjective mutation fallthrough guard (Defect 1 fix)
            # If the adjective stem requires consonant mutation in Class 9/10 (e.g. -kuru -> huru),
            # ordinary prefixation (e.g. i- + kuru -> ikuru) must NOT bypass the mutation.
            if category == ConcordCategory.ADJECTIVE and class_id in ("9", "10"):
                base_mutation = self.knowledge_base.get_mutation_by_base(candidate_residue, class_id)
                if base_mutation and clean_target != base_mutation.mutated_stem:
                    results.append(
                        DetailedAgreementValidation(
                            noun_word=clean_noun,
                            target_word=clean_target,
                            category=category,
                            verdict=ValidationVerdict.CONCORD_MISMATCH,
                            certainty=c_analysis.certainty,
                            controlling_class_id=class_id,
                            matched_prefix=None,
                            extracted_stem=None,
                            evidence=base_mutation.evidence,
                            explanation=(
                                f"Concord mismatch: Class {class_id} requires consonant mutation for "
                                f"adjective stem '-{base_mutation.base_stem}' (expected mutated form "
                                f"'{base_mutation.mutated_stem}', not prefixation '{clean_target}')."
                            ),
                        )
                    )
                    continue

            stem_cat = (
                StemGrammaticalCategory.ADJECTIVE
                if category == ConcordCategory.ADJECTIVE
                else StemGrammaticalCategory.VERB
            )

            # In Shona finite verbs, the present habitual tense formative '-no-' connects
            # the subject concord to the verb stem (e.g., a-no-fara -> anofara).
            has_no_tense_marker = False
            candidate_stem = candidate_residue
            if (
                category == ConcordCategory.SUBJECT
                and candidate_residue.startswith("no")
                and len(candidate_residue) > 2
            ):
                # Direct-match safeguard: check if the unstripped residue is itself a stem (e.g. -noka)
                direct_match = self.knowledge_base.get_stem(candidate_residue, stem_cat)
                if direct_match is None:
                    candidate_stem = candidate_residue[2:]
                    has_no_tense_marker = True

            stem_record = self.knowledge_base.get_stem(candidate_stem, stem_cat)

            if stem_record:
                # Stem is recognized and documented in the knowledge base
                verdict = (
                    ValidationVerdict.AMBIGUOUS_MATCH
                    if c_analysis.is_ambiguous
                    else (
                        ValidationVerdict.CONFIRMED_MATCH
                        if c_analysis.certainty == CertaintyLevel.CONFIRMED
                        else ValidationVerdict.TENTATIVE_MATCH
                    )
                )
                tense_note = " and tense marker '-no-'" if has_no_tense_marker else ""
                explanation = (
                    f"Confirmed match: '{clean_target}' decomposes into Class {class_id} concord "
                    f"'{expected_prefix}'{tense_note} and verified {stem_cat.value} stem '-{stem_record.stem}' "
                    f"(citation: {stem_record.evidence.citation})."
                )
                results.append(
                    DetailedAgreementValidation(
                        noun_word=clean_noun,
                        target_word=clean_target,
                        category=category,
                        verdict=verdict,
                        certainty=c_analysis.certainty,
                        controlling_class_id=class_id,
                        matched_prefix=expected_prefix,
                        extracted_stem=stem_record.stem,
                        evidence=stem_record.evidence,
                        explanation=explanation,
                    )
                )
            else:
                # Stem is unrecognized (Diagnostic improvement)
                # Clarifies that the system does not assert that the residue is a valid verb stem.
                verdict = (
                    ValidationVerdict.AMBIGUOUS_MATCH
                    if c_analysis.is_ambiguous
                    else ValidationVerdict.UNVERIFIED_STEM_MATCH
                )
                tense_note = " and tense marker '-no-'" if has_no_tense_marker else ""
                explanation = (
                    f"Concord prefix '{expected_prefix}'{tense_note} matched for Class {class_id}, but "
                    f"the remaining material '-{candidate_stem}' is not recognized in the lexical knowledge base. "
                    f"Prefix matching alone does not establish grammatical validity, and the system is not "
                    f"asserting that the residue is a valid {stem_cat.value} stem."
                )
                results.append(
                    DetailedAgreementValidation(
                        noun_word=clean_noun,
                        target_word=clean_target,
                        category=category,
                        verdict=verdict,
                        certainty=CertaintyLevel.TENTATIVE,
                        controlling_class_id=class_id,
                        matched_prefix=expected_prefix,
                        extracted_stem=candidate_stem,
                        evidence=None,
                        explanation=explanation,
                    )
                )

        return results

    def validate_token(
        self,
        noun_token: Token,
        target_token: Token,
        category: ConcordCategory,
    ) -> list[DetailedAgreementValidation]:
        """Validate concord agreement between two Token instances from Rocky 0.3 text processing."""
        if noun_token.is_punctuation or target_token.is_punctuation:
            return []
        return self.validate(noun_token.normalized, target_token.normalized, category)