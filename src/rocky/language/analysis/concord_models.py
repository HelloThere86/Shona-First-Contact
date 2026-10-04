"""Data models for Shona concord agreement relationships and validation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from rocky.language.analysis.models import CertaintyLevel
from rocky.language.exceptions import InvalidConcordError


class ConcordCategory(str, Enum):
    """Grammatical agreement categories in Shona syntax."""

    SUBJECT = "subject"          # Subject prefix attached to verb stems (chivakashure chechirevo)
    ADJECTIVE = "adjective"      # Adjectival prefix attached to adjective stems (chipauro)
    POSSESSIVE = "possessive"    # Possessive prefix attached to possessive stem/noun (chirevamwene)
    OBJECT = "object"            # Object infix attached to verb stems


@dataclass(frozen=True)
class ConcordRecord:
    """Represents a documented concord marker for a specific noun class and category.

    Attributes:
        noun_class_id: Identifier of the controlling noun class (e.g. '1', '2', '7').
        category: Grammatical concord category (SUBJECT, ADJECTIVE, POSSESSIVE, OBJECT).
        concord_prefix: Primary canonical concord prefix marker (e.g. 'a-', 'va-', 'chi-').
        variant_prefix: Phonological or vowel-initial variant, if documented.
        certainty: Level of linguistic certainty (CONFIRMED, TENTATIVE, UNRESOLVED).
        source: Bibliographical citation or field verification note.
        notes: Morphophonological notes and usage limitations.
    """

    noun_class_id: str
    category: ConcordCategory
    concord_prefix: str
    variant_prefix: str | None = None
    certainty: CertaintyLevel = CertaintyLevel.CONFIRMED
    source: str = ""
    notes: str = ""

    def __post_init__(self) -> None:
        """Validate concord record parameters."""
        if not isinstance(self.noun_class_id, str) or not self.noun_class_id.strip():
            raise InvalidConcordError("Noun class ID must be a non-empty string.")
        if not isinstance(self.category, ConcordCategory):
            raise InvalidConcordError(
                f"Concord category must be a ConcordCategory enum, received {type(self.category).__name__}."
            )
        if not isinstance(self.concord_prefix, str) or not self.concord_prefix.strip():
            raise InvalidConcordError("Concord prefix must be a non-empty string.")
        if not isinstance(self.certainty, CertaintyLevel):
            raise InvalidConcordError(
                f"Certainty must be a CertaintyLevel enum, received {type(self.certainty).__name__}."
            )

        object.__setattr__(self, "noun_class_id", self.noun_class_id.strip())
        object.__setattr__(self, "concord_prefix", self.concord_prefix.strip().lower())
        if self.variant_prefix is not None:
            object.__setattr__(self, "variant_prefix", self.variant_prefix.strip().lower())


@dataclass(frozen=True)
class ConcordAnalysis:
    """Represents the projected concord agreement for a given noun and category.

    Attributes:
        word: Normalized head noun or subject analyzed.
        category: Target agreement category.
        noun_class_id: Resolved or candidate noun class ID, or None if unknown.
        concord_prefix: Resolved concord marker, or None if unresolved.
        target_stem: Target verb or modifier stem, if provided.
        agreement_form: Synthesized or predicted agreement form, or None.
        certainty: Level of certainty (CONFIRMED, TENTATIVE, UNRESOLVED).
        source: Documentation or rule source.
        explanation: Explanation of how concord was derived or why it is unresolved.
        is_ambiguous: True if derived from an ambiguous multi-class noun.
    """

    word: str
    category: ConcordCategory
    noun_class_id: str | None
    concord_prefix: str | None
    target_stem: str | None = None
    agreement_form: str | None = None
    certainty: CertaintyLevel = CertaintyLevel.CONFIRMED
    source: str = ""
    explanation: str = ""
    is_ambiguous: bool = False


@dataclass(frozen=True)
class AgreementValidationResult:
    """Represents the validation result of an agreement relationship between two words.

    Attributes:
        noun_word: Controlling noun/subject.
        target_word: Dependent word (verb, adjective, or possessive).
        category: Grammatical agreement category being validated.
        is_valid: True if target word satisfies documented concord for the noun.
        certainty: Level of certainty of the validation result.
        matched_concord: Concord prefix that matched, if valid.
        expected_concords: Tuple of candidate concord prefixes expected for this noun.
        explanation: Linguistic diagnostic detailing match or mismatch.
    """

    noun_word: str
    target_word: str
    category: ConcordCategory
    is_valid: bool
    certainty: CertaintyLevel
    matched_concord: str | None = None
    expected_concords: tuple[str, ...] = ()
    explanation: str = ""