"""Data models for linguistic evidence, lexical knowledge, and detailed validation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from rocky.language.analysis.concord_models import ConcordCategory
from rocky.language.analysis.models import CertaintyLevel
from rocky.language.exceptions import InvalidConcordError


class EvidenceSourceType(str, Enum):
    """Classification of the authoritative basis for linguistic data."""

    GRAMMATICAL_LITERATURE = "grammatical_literature"  # Established descriptive grammars
    CORPUS_ATTESTED = "corpus_attested"                 # Attested in Shona textual corpora
    NATIVE_SPEAKER_REVIEW = "native_speaker_review"     # Verified by a native-speaker linguist
    PROVISIONAL_RULE = "provisional_rule"               # Hypothesized/derived rule; unverified


class AttestationStatus(str, Enum):
    """Lifecycle verification status of a linguistic fact or rule."""

    VERIFIED = "verified"          # Confirmed by authoritative literature or consensus
    PROVISIONAL = "provisional"    # Hypothesized; pending formal review
    CONTESTED = "contested"        # Disputed across dialects or authoritative sources


@dataclass(frozen=True)
class LinguisticEvidence:
    """Provenance and attestation record for linguistic facts.

    Requirement: attestation_status must be explicitly declared.
    """

    source_type: EvidenceSourceType
    citation: str
    attestation_status: AttestationStatus
    dialect_scope: str = "Standard Shona"
    notes: str = ""

    def __post_init__(self) -> None:
        """Validate evidence parameters."""
        if not isinstance(self.source_type, EvidenceSourceType):
            raise InvalidConcordError(
                f"Source type must be an EvidenceSourceType enum, received {type(self.source_type).__name__}."
            )
        if not isinstance(self.attestation_status, AttestationStatus):
            raise InvalidConcordError(
                f"Attestation status must be an AttestationStatus enum, received {type(self.attestation_status).__name__}."
            )
        if not isinstance(self.citation, str) or not self.citation.strip():
            raise InvalidConcordError("Citation must be a non-empty string.")

        object.__setattr__(self, "citation", self.citation.strip())


class StemGrammaticalCategory(str, Enum):
    """Grammatical word category of a lexical root stem."""

    VERB = "verb"
    ADJECTIVE = "adjective"
    NOUN = "noun"


@dataclass(frozen=True)
class StemRecord:
    """Documented lexical stem and its grammatical affiliation."""

    stem: str
    category: StemGrammaticalCategory
    evidence: LinguisticEvidence
    english_gloss: str = ""
    notes: str = ""

    def __post_init__(self) -> None:
        """Validate stem record parameters."""
        if not isinstance(self.stem, str) or not self.stem.strip():
            raise ValueError("Stem must be a non-empty string.")
        if not isinstance(self.category, StemGrammaticalCategory):
            raise TypeError("Category must be a StemGrammaticalCategory enum.")
        if not isinstance(self.evidence, LinguisticEvidence):
            raise TypeError("Evidence must be a LinguisticEvidence instance.")

        object.__setattr__(self, "stem", self.stem.strip().lower().lstrip("-"))


@dataclass(frozen=True)
class AdjectiveMutationRecord:
    """Documented Class 9/10 initial consonant mutation on an adjectival stem."""

    base_stem: str
    mutated_stem: str
    applicable_classes: tuple[str, ...]
    evidence: LinguisticEvidence
    notes: str = ""

    def __post_init__(self) -> None:
        """Validate mutation record parameters."""
        if not isinstance(self.base_stem, str) or not self.base_stem.strip():
            raise ValueError("Base stem must be a non-empty string.")
        if not isinstance(self.mutated_stem, str) or not self.mutated_stem.strip():
            raise ValueError("Mutated stem must be a non-empty string.")
        if not isinstance(self.evidence, LinguisticEvidence):
            raise TypeError("Evidence must be a LinguisticEvidence instance.")

        object.__setattr__(self, "base_stem", self.base_stem.strip().lower().lstrip("-"))
        object.__setattr__(self, "mutated_stem", self.mutated_stem.strip().lower().lstrip("-"))


class ValidationVerdict(str, Enum):
    """Granular verdict of a syntactic concord agreement validation check."""

    CONFIRMED_MATCH = "confirmed_match"
    # Concord matches and the target stem is documented/verified in the knowledge base.

    UNVERIFIED_STEM_MATCH = "unverified_stem_match"
    # Concord prefix matches, but the target stem is unknown/unverified (NOT classified as invalid).

    AMBIGUOUS_MATCH = "ambiguous_match"
    # Concord matches one candidate class of an ambiguous noun, but conflicts with another.

    CONCORD_MISMATCH = "concord_mismatch"
    # Concord prefix on target contradicts the expected concord for the controlling noun class.

    UNSUPPORTED_SYNTACTIC_FORM = "unsupported_syntactic_form"
    # Target cannot be decomposed into concord prefix + stem (e.g., word shorter than prefix, or homograph).

    UNRESOLVED_CONTROLLER = "unresolved_controller"
    # Controlling noun has an unknown or unresolved noun class.


@dataclass(frozen=True)
class DetailedAgreementValidation:
    """Detailed linguistic agreement validation result with explicit evidence tracking."""

    noun_word: str
    target_word: str
    category: ConcordCategory
    verdict: ValidationVerdict
    certainty: CertaintyLevel
    controlling_class_id: str | None
    matched_prefix: str | None
    extracted_stem: str | None
    evidence: LinguisticEvidence | None
    explanation: str