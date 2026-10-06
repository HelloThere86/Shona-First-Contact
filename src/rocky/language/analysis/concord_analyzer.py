"""Concord agreement analysis and validation engine."""

from __future__ import annotations

from typing import Sequence

from rocky.language.analysis.analyzer import ShonaLinguisticAnalyzer
from rocky.language.analysis.concord_data import build_default_concord_registry
from rocky.language.analysis.concord_models import (
    AgreementValidationResult,
    ConcordAnalysis,
    ConcordCategory,
    ConcordRecord,
)
from rocky.language.analysis.concord_registry import ConcordRegistry
from rocky.language.analysis.models import CertaintyLevel
from rocky.language.exceptions import UnsupportedCategoryError
from rocky.language.text import Token


class ShonaConcordAnalyzer:
    """Analyzes and validates concord agreement relationships for Shona sentences."""

    def __init__(
        self,
        concord_registry: ConcordRegistry | None = None,
        linguistic_analyzer: ShonaLinguisticAnalyzer | None = None,
    ) -> None:
        """Initialize concord analyzer with registries and linguistic analyzer.

        Args:
            concord_registry: ConcordRegistry instance (or default if None).
            linguistic_analyzer: ShonaLinguisticAnalyzer instance (or default if None).
        """
        self.concord_registry = concord_registry or build_default_concord_registry()
        self.linguistic_analyzer = linguistic_analyzer or ShonaLinguisticAnalyzer()

    def get_concord(
        self, noun_class_id: str, category: ConcordCategory
    ) -> ConcordRecord | None:
        """Retrieve the concord record for a noun class ID and category."""
        return self.concord_registry.get(noun_class_id, category)

    def analyze_agreement(
        self,
        noun_word: str,
        category: ConcordCategory,
        target_stem: str | None = None,
    ) -> list[ConcordAnalysis]:
        """Project candidate concord agreement markers for a given noun.

        Args:
            noun_word: Normalized head noun or subject.
            category: Grammatical concord category (SUBJECT, ADJECTIVE, POSSESSIVE, OBJECT).
            target_stem: Optional stem of the dependent verb/modifier (e.g. '-naka', '-kuru').

        Returns:
            List of ConcordAnalysis objects preserving ambiguity or returning unresolved status.

        Raises:
            TypeError: If noun_word is not a string.
            ValueError: If noun_word is empty or whitespace.
            UnsupportedCategoryError: If category is not an instance of ConcordCategory.
        """
        if not isinstance(noun_word, str):
            raise TypeError(f"Noun word must be a string, received {type(noun_word).__name__}.")

        cleaned_noun = noun_word.strip().lower()
        if not cleaned_noun:
            raise ValueError("Noun word cannot be empty or whitespace.")

        if not isinstance(category, ConcordCategory):
            raise UnsupportedCategoryError(
                f"Expected ConcordCategory enum, received {type(category).__name__}."
            )

        noun_analyses = self.linguistic_analyzer.analyze_word(cleaned_noun)
        clean_stem = target_stem.strip().lstrip("-").lower() if target_stem else None

        results: list[ConcordAnalysis] = []
        is_multi_class = len([a for a in noun_analyses if a.noun_class]) > 1

        for n_analysis in noun_analyses:
            # Case 1: Unresolved noun class
            if n_analysis.certainty == CertaintyLevel.UNRESOLVED or not n_analysis.noun_class:
                results.append(
                    ConcordAnalysis(
                        word=cleaned_noun,
                        category=category,
                        noun_class_id=None,
                        concord_prefix=None,
                        target_stem=clean_stem,
                        agreement_form=None,
                        certainty=CertaintyLevel.UNRESOLVED,
                        source="",
                        explanation=(
                            f"Cannot determine {category.value} concord: noun class for "
                            f"'{cleaned_noun}' is unresolved."
                        ),
                        is_ambiguous=False,
                    )
                )
                continue

            class_id = n_analysis.noun_class.identifier
            concord_record = self.concord_registry.get(class_id, category)

            # Case 2: No concord record found for this class and category
            if not concord_record:
                results.append(
                    ConcordAnalysis(
                        word=cleaned_noun,
                        category=category,
                        noun_class_id=class_id,
                        concord_prefix=None,
                        target_stem=clean_stem,
                        agreement_form=None,
                        certainty=CertaintyLevel.UNRESOLVED,
                        source="",
                        explanation=(
                            f"No documented {category.value} concord record for Class {class_id}."
                        ),
                        is_ambiguous=is_multi_class,
                    )
                )
                continue

            # Case 3: Confirmed vs. Tentative projection
            projection_certainty = (
                CertaintyLevel.CONFIRMED
                if n_analysis.certainty == CertaintyLevel.CONFIRMED and concord_record.certainty == CertaintyLevel.CONFIRMED
                else CertaintyLevel.TENTATIVE
            )

            agreement_form: str | None = None
            if clean_stem:
                agreement_form = f"{concord_record.concord_prefix}{clean_stem}"

            if projection_certainty == CertaintyLevel.CONFIRMED:
                explanation = (
                    f"Confirmed {category.value} concord '{concord_record.concord_prefix}' "
                    f"for Class {class_id} (source: {concord_record.source})."
                )
            else:
                explanation = (
                    f"Tentative {category.value} concord '{concord_record.concord_prefix}' "
                    f"derived from unverified candidate Class {class_id} for '{cleaned_noun}'. "
                    f"Requires linguistic verification."
                )

            results.append(
                ConcordAnalysis(
                    word=cleaned_noun,
                    category=category,
                    noun_class_id=class_id,
                    concord_prefix=concord_record.concord_prefix,
                    target_stem=clean_stem,
                    agreement_form=agreement_form,
                    certainty=projection_certainty,
                    source=concord_record.source,
                    explanation=explanation,
                    is_ambiguous=is_multi_class,
                )
            )

        return results

    def validate_agreement(
        self,
        noun_word: str,
        target_word: str,
        category: ConcordCategory,
    ) -> list[AgreementValidationResult]:
        """Validate whether a dependent word satisfies concord agreement with a head noun.

        Preserved for full backward compatibility with Rocky 0.5.
        """
        if not isinstance(target_word, str):
            raise TypeError(f"Target word must be a string, received {type(target_word).__name__}.")

        cleaned_target = target_word.strip().lower()
        if not cleaned_target:
            raise ValueError("Target word cannot be empty or whitespace.")

        candidate_analyses = self.analyze_agreement(noun_word, category)
        validation_results: list[AgreementValidationResult] = []

        for analysis in candidate_analyses:
            if analysis.certainty == CertaintyLevel.UNRESOLVED or not analysis.concord_prefix:
                validation_results.append(
                    AgreementValidationResult(
                        noun_word=analysis.word,
                        target_word=cleaned_target,
                        category=category,
                        is_valid=False,
                        certainty=CertaintyLevel.UNRESOLVED,
                        matched_concord=None,
                        expected_concords=(),
                        explanation=(
                            f"Validation inconclusive: noun class and concord for "
                            f"'{analysis.word}' could not be established."
                        ),
                    )
                )
                continue

            expected_prefix = analysis.concord_prefix
            expected_tuple = (expected_prefix,)

            if cleaned_target.startswith(expected_prefix):
                validation_results.append(
                    AgreementValidationResult(
                        noun_word=analysis.word,
                        target_word=cleaned_target,
                        category=category,
                        is_valid=True,
                        certainty=analysis.certainty,
                        matched_concord=expected_prefix,
                        expected_concords=expected_tuple,
                        explanation=(
                            f"Valid concord agreement: '{cleaned_target}' matches expected "
                            f"{category.value} concord '{expected_prefix}' for Class {analysis.noun_class_id}."
                        ),
                    )
                )
            else:
                validation_results.append(
                    AgreementValidationResult(
                        noun_word=analysis.word,
                        target_word=cleaned_target,
                        category=category,
                        is_valid=False,
                        certainty=analysis.certainty,
                        matched_concord=None,
                        expected_concords=expected_tuple,
                        explanation=(
                            f"Concord mismatch: '{cleaned_target}' does not begin with expected "
                            f"{category.value} concord '{expected_prefix}' for Class {analysis.noun_class_id}."
                        ),
                    )
                )

        return validation_results

    def validate_token_agreement(
        self,
        noun_token: Token,
        target_token: Token,
        category: ConcordCategory,
    ) -> list[AgreementValidationResult]:
        """Validate concord agreement between two Token instances from Rocky 0.3 text processing."""
        if noun_token.is_punctuation or target_token.is_punctuation:
            return []
        return self.validate_agreement(noun_token.normalized, target_token.normalized, category)