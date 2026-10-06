"""Repository of documented Shona stems, mutations, and linguistic evidence."""

from __future__ import annotations

from rocky.language.analysis.knowledge_models import (
    AdjectiveMutationRecord,
    AttestationStatus,
    EvidenceSourceType,
    LinguisticEvidence,
    StemGrammaticalCategory,
    StemRecord,
)

FORTUNE_GRAMMAR_EVIDENCE = LinguisticEvidence(
    source_type=EvidenceSourceType.GRAMMATICAL_LITERATURE,
    citation="Fortune (1984), Shona Grammatical Constructions, Vol. 1, pp. 109-111",
    attestation_status=AttestationStatus.VERIFIED,
    notes="Adjective agreement and consonant mutation rules for Classes 9 and 10.",
)

HANNAN_DICTIONARY_EVIDENCE = LinguisticEvidence(
    source_type=EvidenceSourceType.GRAMMATICAL_LITERATURE,
    citation="Hannan (1984), Standard Shona Dictionary, College Press",
    attestation_status=AttestationStatus.VERIFIED,
    notes="Verified standard dictionary headword and stem attestation.",
)


class LinguisticKnowledgeBase:
    """In-memory store of verified stems and phonological mutation rules."""

    def __init__(self) -> None:
        # Key: (stem, category) -> StemRecord
        self._stems: dict[tuple[str, StemGrammaticalCategory], StemRecord] = {}
        # Key: (base_stem, class_id) -> AdjectiveMutationRecord
        self._mutations_by_base: dict[tuple[str, str], AdjectiveMutationRecord] = {}
        # Key: (mutated_stem, class_id) -> AdjectiveMutationRecord
        self._mutations_by_surface: dict[tuple[str, str], AdjectiveMutationRecord] = {}

    def register_stem(self, record: StemRecord) -> None:
        """Register a verified lexical stem."""
        key = (record.stem, record.category)
        self._stems[key] = record

    def register_mutation(self, record: AdjectiveMutationRecord) -> None:
        """Register a documented initial consonant mutation rule."""
        for class_id in record.applicable_classes:
            self._mutations_by_base[(record.base_stem, class_id)] = record
            self._mutations_by_surface[(record.mutated_stem, class_id)] = record

    def get_stem(
        self, stem: str, category: StemGrammaticalCategory
    ) -> StemRecord | None:
        """Look up a stem by normalized string and grammatical category."""
        clean = stem.strip().lower().lstrip("-")
        return self._stems.get((clean, category))

    def has_stem(self, stem: str, category: StemGrammaticalCategory) -> bool:
        """Check if a stem is recognized under a grammatical category."""
        return self.get_stem(stem, category) is not None

    def get_mutation_by_surface(
        self, surface_word: str, class_id: str
    ) -> AdjectiveMutationRecord | None:
        """Look up whether a surface form is a documented adjectival mutation for a class."""
        clean = surface_word.strip().lower().lstrip("-")
        return self._mutations_by_surface.get((clean, class_id))

    def get_mutation_by_base(
        self, base_stem: str, class_id: str
    ) -> AdjectiveMutationRecord | None:
        """Look up the mutated form of a base adjective stem for a class."""
        clean = base_stem.strip().lower().lstrip("-")
        return self._mutations_by_base.get((clean, class_id))


def build_default_knowledge_base() -> LinguisticKnowledgeBase:
    """Build a knowledge base populated with documented Shona stems and mutation rules."""
    kb = LinguisticKnowledgeBase()

    # 1. Documented Adjective Stems (Fortune 1984, pp. 109-111; Hannan 1984)
    adjective_stems = [
        ("kuru", "big / adult / elder"),
        ("tete", "thin / slender"),
        ("refu", "tall / long"),
        ("diki", "small / young"),
        ("chena", "white / clean"),
        ("tsva", "new / fresh"),
        ("shoma", "few / little"),
        ("zhinji", "many / plentiful"),
        ("pamhi", "broad / wide"),
    ]

    for stem, gloss in adjective_stems:
        kb.register_stem(
            StemRecord(
                stem=stem,
                category=StemGrammaticalCategory.ADJECTIVE,
                evidence=HANNAN_DICTIONARY_EVIDENCE,
                english_gloss=gloss,
            )
        )

    # 2. Documented Verb Stems
    verb_stems = [
        ("fara", "be happy / rejoice"),
        ("naka", "be good / be sweet"),
        ("rara", "sleep"),
        ("tamba", "play / dance"),
        ("kura", "grow"),
        ("cheka", "cut"),
        ("noka", "fall / rain"),
        ("neta", "tire / be weary"),
        ("pera", "end / be finished"),
    ]

    for stem, gloss in verb_stems:
        kb.register_stem(
            StemRecord(
                stem=stem,
                category=StemGrammaticalCategory.VERB,
                evidence=HANNAN_DICTIONARY_EVIDENCE,
                english_gloss=gloss,
            )
        )

    # 3. Documented Adjectival Consonant Mutations for Classes 9 & 10 (Fortune 1984, p. 110)
    # Strictly limited to documented mutations (Refinement 5)
    mutations = [
        AdjectiveMutationRecord(
            base_stem="kuru",
            mutated_stem="huru",
            applicable_classes=("9", "10"),
            evidence=FORTUNE_GRAMMAR_EVIDENCE,
            notes="Velar stop k softens to glottal fricative h in Class 9/10.",
        ),
        AdjectiveMutationRecord(
            base_stem="tete",
            mutated_stem="nhete",
            applicable_classes=("9", "10"),
            evidence=FORTUNE_GRAMMAR_EVIDENCE,
            notes="Alveolar t undergoes nasal pre-plosion/aspiration to nh.",
        ),
        AdjectiveMutationRecord(
            base_stem="refu",
            mutated_stem="ndefu",
            applicable_classes=("9", "10"),
            evidence=FORTUNE_GRAMMAR_EVIDENCE,
            notes="Alveolar liquid r hardens to nd in Class 9/10.",
        ),
        AdjectiveMutationRecord(
            base_stem="pamhi",
            mutated_stem="mhamhi",
            applicable_classes=("9", "10"),
            evidence=FORTUNE_GRAMMAR_EVIDENCE,
            notes="Bilabial stop p nasalizes to mh in Class 9/10.",
        ),
        AdjectiveMutationRecord(
            base_stem="diki",
            mutated_stem="ndiki",
            applicable_classes=("9", "10"),
            evidence=FORTUNE_GRAMMAR_EVIDENCE,
            notes="Voiced alveolar stop d takes nasal pre-plosion nd in Class 9/10.",
        ),
        AdjectiveMutationRecord(
            base_stem="chena",
            mutated_stem="chena",
            applicable_classes=("9", "10"),
            evidence=FORTUNE_GRAMMAR_EVIDENCE,
            notes="Affricate ch remains unchanged in Class 9/10.",
        ),
    ]

    for mut in mutations:
        kb.register_mutation(mut)

    return kb