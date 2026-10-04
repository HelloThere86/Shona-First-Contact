"""Automated tests for Rocky 0.5 Concord Agreement and Linguistic Validation."""

import pytest

from rocky.language import (
    AgreementValidationResult,
    CertaintyLevel,
    ConcordAnalysis,
    ConcordCategory,
    ConcordRecord,
    ConcordRegistry,
    DuplicateConcordError,
    InvalidConcordError,
    NounClass,
    NounClassRegistry,
    NumberCategory,
    ShonaConcordAnalyzer,
    ShonaLinguisticAnalyzer,
    UnsupportedCategoryError,
    build_default_concord_registry,
    build_default_noun_class_registry,
    tokenize,
)


# ============================================================================
# 1. Concord Model Validation Tests
# ============================================================================


def test_concord_record_valid():
    record = ConcordRecord(
        noun_class_id="7",
        category=ConcordCategory.SUBJECT,
        concord_prefix="chi",
        source="Fortune (1984)",
    )
    assert record.noun_class_id == "7"
    assert record.category == ConcordCategory.SUBJECT
    assert record.concord_prefix == "chi"
    assert record.certainty == CertaintyLevel.CONFIRMED


@pytest.mark.parametrize(
    "class_id, category, prefix, match",
    [
        ("", ConcordCategory.SUBJECT, "chi", "Noun class ID must be a non-empty string"),
        ("   ", ConcordCategory.SUBJECT, "chi", "Noun class ID must be a non-empty string"),
        ("7", "not_a_category", "chi", "Concord category must be a ConcordCategory enum"),
        ("7", ConcordCategory.SUBJECT, "", "Concord prefix must be a non-empty string"),
        ("7", ConcordCategory.SUBJECT, "   ", "Concord prefix must be a non-empty string"),
    ],
)
def test_concord_record_invalid(class_id, category, prefix, match):
    with pytest.raises(InvalidConcordError, match=match):
        ConcordRecord(noun_class_id=class_id, category=category, concord_prefix=prefix)


# ============================================================================
# 2. Concord Registry Operations Tests
# ============================================================================


def test_concord_registry_operations():
    registry = ConcordRegistry()
    r1 = ConcordRecord(noun_class_id="1", category=ConcordCategory.SUBJECT, concord_prefix="a")
    r2 = ConcordRecord(noun_class_id="1", category=ConcordCategory.POSSESSIVE, concord_prefix="wa")

    registry.register(r1)
    registry.register(r2)

    assert registry.count() == 2
    assert registry.has_concord("1", ConcordCategory.SUBJECT) is True
    assert registry.has_concord("1", ConcordCategory.ADJECTIVE) is False
    assert registry.get("1", ConcordCategory.SUBJECT) == r1
    assert registry.get("1", ConcordCategory.POSSESSIVE) == r2
    assert registry.get("99", ConcordCategory.SUBJECT) is None


def test_concord_registry_duplicate_rejection():
    registry = ConcordRegistry()
    r1 = ConcordRecord(noun_class_id="1", category=ConcordCategory.SUBJECT, concord_prefix="a")
    r2 = ConcordRecord(noun_class_id="1", category=ConcordCategory.SUBJECT, concord_prefix="a")

    registry.register(r1)
    with pytest.raises(DuplicateConcordError, match="already registered"):
        registry.register(r2)


def test_concord_registry_validate_with_noun_classes():
    registry = ConcordRegistry()
    registry.register(ConcordRecord(noun_class_id="99", category=ConcordCategory.SUBJECT, concord_prefix="x"))

    class_reg = build_default_noun_class_registry()
    issues = registry.validate(class_reg)
    assert len(issues) == 1
    assert "references unregistered noun class '99'" in issues[0]


# ============================================================================
# 3. Known Concord Lookups across Categories
# ============================================================================


@pytest.fixture
def concord_analyzer() -> ShonaConcordAnalyzer:
    return ShonaConcordAnalyzer()


def test_subject_concord_confirmed_nouns(concord_analyzer: ShonaConcordAnalyzer):
    # Class 1 (munhu -> a-)
    res_munhu = concord_analyzer.analyze_agreement("munhu", ConcordCategory.SUBJECT, target_stem="nofara")
    assert len(res_munhu) == 1
    assert res_munhu[0].concord_prefix == "a"
    assert res_munhu[0].agreement_form == "anofara"
    assert res_munhu[0].certainty == CertaintyLevel.CONFIRMED

    # Class 2 (vanhu -> va-)
    res_vanhu = concord_analyzer.analyze_agreement("vanhu", ConcordCategory.SUBJECT, target_stem="nofara")
    assert len(res_vanhu) == 1
    assert res_vanhu[0].concord_prefix == "va"
    assert res_vanhu[0].agreement_form == "vanofara"
    assert res_vanhu[0].certainty == CertaintyLevel.CONFIRMED

    # Class 7 (chikafu -> chi-)
    res_chikafu = concord_analyzer.analyze_agreement("chikafu", ConcordCategory.SUBJECT, target_stem="nonaka")
    assert len(res_chikafu) == 1
    assert res_chikafu[0].concord_prefix == "chi"
    assert res_chikafu[0].agreement_form == "chinonaka"

    # Class 9 (mvura -> i-)
    res_mvura = concord_analyzer.analyze_agreement("mvura", ConcordCategory.SUBJECT, target_stem="nonaya")
    assert len(res_mvura) == 1
    assert res_mvura[0].concord_prefix == "i"
    assert res_mvura[0].agreement_form == "inonaya"


def test_adjective_and_possessive_concords(concord_analyzer: ShonaConcordAnalyzer):
    # Class 1 Adjective (munhu -> mu-)
    res_adj = concord_analyzer.analyze_agreement("munhu", ConcordCategory.ADJECTIVE, target_stem="kuru")
    assert res_adj[0].concord_prefix == "mu"
    assert res_adj[0].agreement_form == "mukuru"

    # Class 7 Possessive (chikafu -> cha-)
    res_poss = concord_analyzer.analyze_agreement("chikafu", ConcordCategory.POSSESSIVE, target_stem="amai")
    assert res_poss[0].concord_prefix == "cha"
    assert res_poss[0].agreement_form == "chaamai"


# ============================================================================
# 4. Ambiguity and Uncertainty Preservation
# ============================================================================


def test_ambiguous_noun_preserves_multiple_concords(concord_analyzer: ShonaConcordAnalyzer):
    # 'mufaro' is not in the verified lexicon, and matches Class 1 and Class 3 prefix rules
    results = concord_analyzer.analyze_agreement("mufaro", ConcordCategory.SUBJECT, target_stem="nopera")
    assert len(results) == 2
    assert all(r.certainty == CertaintyLevel.TENTATIVE for r in results)
    assert all(r.is_ambiguous is True for r in results)

    # One candidate is Class 1 (a-), another is Class 3 (u-)
    prefixes = {r.concord_prefix for r in results}
    assert prefixes == {"a", "u"}


def test_unresolved_noun_returns_unresolved_concord(concord_analyzer: ShonaConcordAnalyzer):
    # 'goridhe' has no matching noun class in the engine
    results = concord_analyzer.analyze_agreement("goridhe", ConcordCategory.SUBJECT)
    assert len(results) == 1
    r = results[0]
    assert r.certainty == CertaintyLevel.UNRESOLVED
    assert r.concord_prefix is None
    assert "unresolved" in r.explanation


# ============================================================================
# 5. Syntactic Agreement Validation
# ============================================================================


def test_validation_successful_matches(concord_analyzer: ShonaConcordAnalyzer):
    # Class 1: munhu + anofara
    v1 = concord_analyzer.validate_agreement("munhu", "anofara", ConcordCategory.SUBJECT)[0]
    assert v1.is_valid is True
    assert v1.matched_concord == "a"
    assert v1.certainty == CertaintyLevel.CONFIRMED

    # Class 2: vanhu + vakuru
    v2 = concord_analyzer.validate_agreement("vanhu", "vakuru", ConcordCategory.ADJECTIVE)[0]
    assert v2.is_valid is True
    assert v2.matched_concord == "va"

    # Class 7: chikafu + changu
    v3 = concord_analyzer.validate_agreement("chikafu", "changu", ConcordCategory.POSSESSIVE)[0]
    assert v3.is_valid is True
    assert v3.matched_concord == "cha"


def test_validation_concord_mismatch(concord_analyzer: ShonaConcordAnalyzer):
    # Subject mismatch: Class 1 munhu with Class 2 verb vanofara
    v = concord_analyzer.validate_agreement("munhu", "vanofara", ConcordCategory.SUBJECT)[0]
    assert v.is_valid is False
    assert v.matched_concord is None
    assert v.expected_concords == ("a",)
    assert "Concord mismatch" in v.explanation


def test_validation_with_tokens(concord_analyzer: ShonaConcordAnalyzer):
    tokens = tokenize("Chikafu chinonaka.")
    # tokens: [Token('Chikafu'), Token('chinonaka'), Token('.')]
    v_results = concord_analyzer.validate_token_agreement(tokens[0], tokens[1], ConcordCategory.SUBJECT)
    assert len(v_results) == 1
    assert v_results[0].is_valid is True
    assert v_results[0].matched_concord == "chi"


# ============================================================================
# 6. Input Validation & Edge Cases
# ============================================================================


def test_analyzer_input_validation(concord_analyzer: ShonaConcordAnalyzer):
    with pytest.raises(TypeError, match="Noun word must be a string"):
        concord_analyzer.analyze_agreement(None, ConcordCategory.SUBJECT)

    with pytest.raises(ValueError, match="cannot be empty"):
        concord_analyzer.analyze_agreement("   ", ConcordCategory.SUBJECT)

    with pytest.raises(UnsupportedCategoryError, match="Expected ConcordCategory enum"):
        concord_analyzer.analyze_agreement("munhu", "invalid_category")

    with pytest.raises(TypeError, match="Target word must be a string"):
        concord_analyzer.validate_agreement("munhu", 123, ConcordCategory.SUBJECT)


def test_custom_concord_registry_injection():
    # Test separation of data and logic via custom registry injection
    custom_reg = ConcordRegistry()
    custom_reg.register(
        ConcordRecord(noun_class_id="1", category=ConcordCategory.SUBJECT, concord_prefix="custom_prefix")
    )
    custom_analyzer = ShonaConcordAnalyzer(concord_registry=custom_reg)
    res = custom_analyzer.analyze_agreement("munhu", ConcordCategory.SUBJECT)
    assert res[0].concord_prefix == "custom_prefix"