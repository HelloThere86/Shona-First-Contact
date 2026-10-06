"""Automated tests for Rocky 0.6 Linguistic Knowledge and Validation."""

import pytest

from rocky.language import (
    AdjectiveMutationRecord,
    AttestationStatus,
    CertaintyLevel,
    ConcordCategory,
    DetailedAgreementValidation,
    EvidenceSourceType,
    InvalidConcordError,
    LinguisticEvidence,
    LinguisticKnowledgeBase,
    ShonaAgreementValidator,
    StemGrammaticalCategory,
    StemRecord,
    ValidationVerdict,
    build_default_knowledge_base,
    tokenize,
)


# ============================================================================
# 1. Linguistic Evidence Model Tests
# ============================================================================


def test_evidence_model_valid():
    evidence = LinguisticEvidence(
        source_type=EvidenceSourceType.GRAMMATICAL_LITERATURE,
        citation="Fortune (1984), p. 77",
        attestation_status=AttestationStatus.VERIFIED,
        notes="Standard subject concord",
    )
    assert evidence.source_type == EvidenceSourceType.GRAMMATICAL_LITERATURE
    assert evidence.attestation_status == AttestationStatus.VERIFIED
    assert evidence.citation == "Fortune (1984), p. 77"


def test_evidence_model_requires_explicit_attestation_status():
    # Refinement 4: Attestation status must be declared explicitly (no default)
    with pytest.raises(TypeError):
        LinguisticEvidence(
            source_type=EvidenceSourceType.GRAMMATICAL_LITERATURE,
            citation="Fortune (1984)",
        )


def test_evidence_model_invalid_inputs():
    with pytest.raises(InvalidConcordError, match="Source type must be an EvidenceSourceType enum"):
        LinguisticEvidence(
            source_type="not_an_enum",
            citation="Fortune (1984)",
            attestation_status=AttestationStatus.VERIFIED,
        )

    with pytest.raises(InvalidConcordError, match="Attestation status must be an AttestationStatus enum"):
        LinguisticEvidence(
            source_type=EvidenceSourceType.GRAMMATICAL_LITERATURE,
            citation="Fortune (1984)",
            attestation_status="not_an_enum",
        )

    with pytest.raises(InvalidConcordError, match="Citation must be a non-empty string"):
        LinguisticEvidence(
            source_type=EvidenceSourceType.GRAMMATICAL_LITERATURE,
            citation="   ",
            attestation_status=AttestationStatus.VERIFIED,
        )


# ============================================================================
# 2. Knowledge Base and Stems
# ============================================================================


def test_knowledge_base_stem_lookups():
    kb = build_default_knowledge_base()

    verb = kb.get_stem("fara", StemGrammaticalCategory.VERB)
    assert verb is not None
    assert verb.stem == "fara"
    assert verb.evidence.attestation_status == AttestationStatus.VERIFIED

    adj = kb.get_stem("kuru", StemGrammaticalCategory.ADJECTIVE)
    assert adj is not None
    assert adj.stem == "kuru"

    assert kb.has_stem("nonexistent_stem", StemGrammaticalCategory.VERB) is False


# ============================================================================
# 3. Adjective Consonant Mutation Tests (Refinement 5)
# ============================================================================


def test_adjective_mutation_lookups():
    kb = build_default_knowledge_base()

    # Class 9/10 mutation: -kuru -> huru
    mut_cl9 = kb.get_mutation_by_surface("huru", "9")
    assert mut_cl9 is not None
    assert mut_cl9.base_stem == "kuru"
    assert mut_cl9.evidence.source_type == EvidenceSourceType.GRAMMATICAL_LITERATURE

    # Check that unmutated base does not register as surface mutation
    assert kb.get_mutation_by_surface("kuru", "9") is None


# ============================================================================
# 4. Enhanced Agreement Validation Tests
# ============================================================================


@pytest.fixture
def validator() -> ShonaAgreementValidator:
    return ShonaAgreementValidator()


def test_confirmed_match_with_recognized_stem(validator: ShonaAgreementValidator):
    # munhu (Class 1) + anofara (a- + -no- + -fara)
    res = validator.validate("munhu", "anofara", ConcordCategory.SUBJECT)
    assert len(res) == 1
    v = res[0]
    assert v.verdict == ValidationVerdict.CONFIRMED_MATCH
    assert v.matched_prefix == "a"
    assert v.extracted_stem == "fara"
    assert v.evidence is not None
    assert "Hannan (1984)" in v.evidence.citation


def test_unverified_stem_match_distinguished_from_invalid(validator: ShonaAgreementValidator):
    # Refinement 1: An unrecognized stem must not be classified as invalid.
    # munhu (Class 1) + anobhururuka (a- + -no- + -bhururuka; stem is not in knowledge base)
    res = validator.validate("munhu", "anobhururuka", ConcordCategory.SUBJECT)
    assert len(res) == 1
    v = res[0]
    assert v.verdict == ValidationVerdict.UNVERIFIED_STEM_MATCH
    assert v.certainty == CertaintyLevel.TENTATIVE
    assert v.matched_prefix == "a"
    assert v.extracted_stem == "bhururuka"
    assert "not recognized in the lexical knowledge base" in v.explanation


def test_concord_mismatch_detected(validator: ShonaAgreementValidator):
    # munhu (Class 1) + vanofara (Class 2 prefix va-)
    res = validator.validate("munhu", "vanofara", ConcordCategory.SUBJECT)
    assert len(res) == 1
    v = res[0]
    assert v.verdict == ValidationVerdict.CONCORD_MISMATCH
    assert v.matched_prefix is None


def test_false_positive_eliminated_for_non_decomposable_target(validator: ShonaAgreementValidator):
    # Target word 'a' cannot be decomposed into a valid stem
    res = validator.validate("munhu", "a", ConcordCategory.SUBJECT)
    assert len(res) == 1
    v = res[0]
    assert v.verdict == ValidationVerdict.UNSUPPORTED_SYNTACTIC_FORM
    assert "too short to yield a viable stem" in v.explanation


def test_class_9_adjectival_mutation_validation(validator: ShonaAgreementValidator):
    # imba (Class 9) + huru (mutated from -kuru)
    res = validator.validate("imba", "huru", ConcordCategory.ADJECTIVE)
    assert len(res) == 1
    v = res[0]
    assert v.verdict == ValidationVerdict.CONFIRMED_MATCH
    assert v.extracted_stem == "kuru"
    assert v.evidence is not None
    assert "Fortune (1984)" in v.evidence.citation


def test_ambiguous_noun_agreement_handling(validator: ShonaAgreementValidator):
    # mufaro is ambiguous between Class 1 and Class 3
    res_verb = validator.validate("mufaro", "unopera", ConcordCategory.SUBJECT)
    assert len(res_verb) == 2
    # One branch matches Class 3 (unopera -> u- + -no- + -pera)
    cl3_match = next(r for r in res_verb if r.controlling_class_id == "3")
    assert cl3_match.verdict == ValidationVerdict.AMBIGUOUS_MATCH
    assert cl3_match.extracted_stem == "pera"

    # The Class 1 branch reports mismatch against u-
    cl1_mismatch = next(r for r in res_verb if r.controlling_class_id == "1")
    assert cl1_mismatch.verdict == ValidationVerdict.CONCORD_MISMATCH


def test_unresolved_controller_noun(validator: ShonaAgreementValidator):
    # goridhe has no resolved noun class
    res = validator.validate("goridhe", "anofara", ConcordCategory.SUBJECT)
    assert len(res) == 1
    v = res[0]
    assert v.verdict == ValidationVerdict.UNRESOLVED_CONTROLLER
    assert v.certainty == CertaintyLevel.UNRESOLVED


def test_token_detailed_validation(validator: ShonaAgreementValidator):
    tokens = tokenize("Chikafu chinonaka.")
    res = validator.validate_token(tokens[0], tokens[1], ConcordCategory.SUBJECT)
    assert len(res) == 1
    assert res[0].verdict == ValidationVerdict.CONFIRMED_MATCH
    assert res[0].matched_prefix == "chi"
    assert res[0].extracted_stem == "naka"


# ============================================================================
# 5. Targeted Patch Regression Tests (Rocky 0.6 Refinements)
# ============================================================================


def test_class_9_blocks_unmutated_adjective_prefix(validator: ShonaAgreementValidator):
    # DEFECT 1: imba + huru is confirmed, but imba + ikuru MUST NOT be CONFIRMED_MATCH
    res_valid = validator.validate("imba", "huru", ConcordCategory.ADJECTIVE)
    assert res_valid[0].verdict == ValidationVerdict.CONFIRMED_MATCH

    res_invalid = validator.validate("imba", "ikuru", ConcordCategory.ADJECTIVE)
    assert res_invalid[0].verdict != ValidationVerdict.CONFIRMED_MATCH
    assert res_invalid[0].verdict == ValidationVerdict.CONCORD_MISMATCH
    assert "requires consonant mutation" in res_invalid[0].explanation


def test_possessive_category_explicitly_unsupported(validator: ShonaAgreementValidator):
    # DEFECT 2: POSSESSIVE must not silently become VERB
    res = validator.validate("chikafu", "changu", ConcordCategory.POSSESSIVE)
    assert len(res) == 1
    v = res[0]
    assert v.verdict == ValidationVerdict.UNSUPPORTED_SYNTACTIC_FORM
    assert v.verdict != ValidationVerdict.UNVERIFIED_STEM_MATCH
    assert "possessive" in v.explanation.lower()


def test_object_category_explicitly_unsupported(validator: ShonaAgreementValidator):
    # DEFECT 2: OBJECT must not silently become VERB
    res = validator.validate("munhu", "akamuona", ConcordCategory.OBJECT)
    assert len(res) == 1
    v = res[0]
    assert v.verdict == ValidationVerdict.UNSUPPORTED_SYNTACTIC_FORM
    assert "object" in v.explanation.lower()


def test_homograph_unknown_residue_diagnostic(validator: ShonaAgreementValidator):
    # DIAGNOSTIC IMPROVEMENT: munhu + aporo must be conservative and not assert residue is a verb
    res = validator.validate("munhu", "aporo", ConcordCategory.SUBJECT)
    assert len(res) == 1
    v = res[0]
    assert v.verdict != ValidationVerdict.CONFIRMED_MATCH
    assert v.verdict == ValidationVerdict.UNVERIFIED_STEM_MATCH
    assert "Prefix matching alone does not establish grammatical validity" in v.explanation
    assert "not asserting that the residue is a valid verb stem" in v.explanation