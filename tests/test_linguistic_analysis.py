"""Tests for Rocky 0.4 Shona Linguistic Analysis."""

import pytest

from rocky.language import (
    CertaintyLevel,
    DuplicateNounClassError,
    DuplicateRuleError,
    InvalidNounClassError,
    InvalidRuleError,
    MorphologicalRule,
    NounClass,
    NounClassRegistry,
    NumberCategory,
    RuleRegistry,
    ShonaLinguisticAnalyzer,
    WordAnalysis,
    WordFormRelationship,
    build_default_noun_class_registry,
    build_default_rule_registry,
    tokenize,
)


# ============================================================================
# 1. Linguistic Data Model Validation Tests
# ============================================================================


def test_noun_class_model_valid():
    nc = NounClass(
        identifier="7",
        prefix="chi",
        number=NumberCategory.SINGULAR,
        paired_class_id="8",
        description="Objects",
    )
    assert nc.identifier == "7"
    assert nc.prefix == "chi"
    assert nc.number == NumberCategory.SINGULAR
    assert nc.paired_class_id == "8"


@pytest.mark.parametrize(
    "identifier, prefix, number",
    [
        ("", "chi", NumberCategory.SINGULAR),
        ("   ", "chi", NumberCategory.SINGULAR),
        ("7", "", NumberCategory.SINGULAR),
        ("7", "   ", NumberCategory.SINGULAR),
        ("7", "chi", "not_an_enum"),
    ],
)
def test_noun_class_model_invalid(identifier, prefix, number):
    with pytest.raises(InvalidNounClassError):
        NounClass(identifier=identifier, prefix=prefix, number=number)


def test_word_form_relationship_model_validation():
    rel = WordFormRelationship(
        source_word=" Munhu ",
        target_word=" Vanhu ",
        source_class_id="1",
        target_class_id="2",
        stem=" Nhu ",
    )
    assert rel.source_word == "munhu"
    assert rel.target_word == "vanhu"
    assert rel.stem == "nhu"

    with pytest.raises(ValueError):
        WordFormRelationship(source_word="", target_word="vanhu")

    with pytest.raises(ValueError):
        WordFormRelationship(source_word="munhu", target_word="")


def test_morphological_rule_model_validation():
    rule = MorphologicalRule(
        rule_id="cl7_cl8",
        description="test rule",
        source_prefix="chi",
        target_prefix="zvi",
        source_class_id="7",
        target_class_id="8",
    )
    assert rule.can_apply("chikafu") is True
    assert rule.extract_candidate_stem("chikafu") == "kafu"
    assert rule.transform("chikafu") == "zvikafu"
    assert rule.can_apply("banga") is False

    with pytest.raises(InvalidRuleError):
        MorphologicalRule(
            rule_id="",
            description="",
            source_prefix="chi",
            target_prefix="zvi",
            source_class_id="7",
            target_class_id="8",
        )


# ============================================================================
# 2. Noun-Class Registry Operations
# ============================================================================


def test_noun_class_registry_operations():
    registry = NounClassRegistry()
    nc1 = NounClass(identifier="1", prefix="mu", number=NumberCategory.SINGULAR, paired_class_id="2")
    nc2 = NounClass(identifier="2", prefix="va", number=NumberCategory.PLURAL, paired_class_id="1")

    registry.register(nc1)
    registry.register(nc2)

    assert registry.count() == 2
    assert "1" in registry
    assert registry.get("1") == nc1
    assert registry.get_paired_class("1") == nc2
    assert registry.get_paired_class("2") == nc1
    assert registry.get("nonexistent") is None
    assert len(registry.validate()) == 0


def test_noun_class_registry_duplicate_rejection():
    registry = NounClassRegistry()
    nc1 = NounClass(identifier="1", prefix="mu", number=NumberCategory.SINGULAR)
    nc1_dup = NounClass(identifier="1", prefix="mu", number=NumberCategory.SINGULAR)

    registry.register(nc1)
    with pytest.raises(DuplicateNounClassError, match="already registered"):
        registry.register(nc1_dup)


def test_noun_class_registry_validation_warning():
    registry = NounClassRegistry()
    broken = NounClass(identifier="1", prefix="mu", number=NumberCategory.SINGULAR, paired_class_id="99")
    registry.register(broken)

    issues = registry.validate()
    assert len(issues) == 1
    assert "references non-existent paired class '99'" in issues[0]


# ============================================================================
# 3. Rule Registry Operations
# ============================================================================


def test_rule_registry_operations():
    registry = RuleRegistry()
    rule = MorphologicalRule(
        rule_id="r1",
        description="rule 1",
        source_prefix="chi",
        target_prefix="zvi",
        source_class_id="7",
        target_class_id="8",
    )
    registry.register(rule)

    assert registry.get("r1") == rule
    assert len(registry.find_matching_rules("chikafu")) == 1
    assert len(registry.find_matching_rules("vanhu")) == 0

    with pytest.raises(DuplicateRuleError):
        registry.register(rule)


# ============================================================================
# 4. Known Word-Form Analysis (Verified Dataset)
# ============================================================================


@pytest.fixture
def analyzer() -> ShonaLinguisticAnalyzer:
    return ShonaLinguisticAnalyzer()


def test_known_word_munhu_vanhu(analyzer: ShonaLinguisticAnalyzer):
    # Singular check
    res_sg = analyzer.analyze_word("munhu")
    assert len(res_sg) == 1
    a_sg = res_sg[0]
    assert a_sg.certainty == CertaintyLevel.CONFIRMED
    assert a_sg.noun_class is not None and a_sg.noun_class.identifier == "1"
    assert a_sg.stem == "nhu"
    assert a_sg.prefix == "mu"
    assert a_sg.number == NumberCategory.SINGULAR
    assert a_sg.paired_form == "vanhu"

    # Plural check
    res_pl = analyzer.analyze_word("vanhu")
    assert len(res_pl) == 1
    a_pl = res_pl[0]
    assert a_pl.certainty == CertaintyLevel.CONFIRMED
    assert a_pl.noun_class is not None and a_pl.noun_class.identifier == "2"
    assert a_pl.stem == "nhu"
    assert a_pl.prefix == "va"
    assert a_pl.number == NumberCategory.PLURAL
    assert a_pl.paired_form == "munhu"


def test_known_word_mwana_vana(analyzer: ShonaLinguisticAnalyzer):
    res = analyzer.analyze_word("mwana")
    assert len(res) == 1
    a = res[0]
    assert a.certainty == CertaintyLevel.CONFIRMED
    assert a.noun_class.identifier == "1"
    assert a.stem == "ana"
    assert a.paired_form == "vana"


def test_known_word_imba_dzimba(analyzer: ShonaLinguisticAnalyzer):
    res_sg = analyzer.analyze_word("imba")
    assert res_sg[0].certainty == CertaintyLevel.CONFIRMED
    assert res_sg[0].noun_class.identifier == "9"
    assert res_sg[0].paired_form == "dzimba"

    res_pl = analyzer.analyze_word("dzimba")
    assert res_pl[0].certainty == CertaintyLevel.CONFIRMED
    assert res_pl[0].noun_class.identifier == "10"
    assert res_pl[0].paired_form == "imba"


def test_invariable_mass_noun(analyzer: ShonaLinguisticAnalyzer):
    res = analyzer.analyze_word("mvura")
    assert len(res) == 1
    a = res[0]
    assert a.certainty == CertaintyLevel.CONFIRMED
    assert a.noun_class.identifier == "9"
    assert a.number == NumberCategory.INVARIABLE


def test_unverified_stem_relationship(analyzer: ShonaLinguisticAnalyzer):
    # chitsva has a documented relationship, but stem decomposition is marked unverified
    res = analyzer.analyze_word("chitsva")
    assert len(res) == 1
    a = res[0]
    assert a.certainty == CertaintyLevel.TENTATIVE
    assert a.stem is None  # Must NOT hallucinate stem
    assert a.paired_form == "zvitsva"


# ============================================================================
# 5. Unknown Words & Ambiguity Tests
# ============================================================================


def test_unknown_word_multiple_analyses(analyzer: ShonaLinguisticAnalyzer):
    # 'mufaro' is not in the verified lexicon.
    # It starts with 'mu-', so rules for Class 1 (mu->va) and Class 3 (mu->mi) match.
    analyses = analyzer.analyze_word("mufaro")
    assert len(analyses) == 2
    assert all(a.certainty == CertaintyLevel.TENTATIVE for a in analyses)

    classes_matched = {a.noun_class.identifier for a in analyses if a.noun_class}
    assert classes_matched == {"1", "3"}

    stems = {a.stem for a in analyses}
    assert stems == {"faro"}


def test_unknown_word_unresolved_handling(analyzer: ShonaLinguisticAnalyzer):
    # 'goridhe' has no matching documented prefix rule or lexicon entry
    analyses = analyzer.analyze_word("goridhe")
    assert len(analyses) == 1
    a = analyses[0]
    assert a.certainty == CertaintyLevel.UNRESOLVED
    assert a.noun_class is None
    assert a.stem is None
    assert a.prefix is None
    assert "No verified lexical entry" in a.explanation


# ============================================================================
# 6. Input Validation & Edge Cases
# ============================================================================


def test_analyzer_input_validation(analyzer: ShonaLinguisticAnalyzer):
    with pytest.raises(TypeError, match="Word must be a string"):
        analyzer.analyze_word(None)

    with pytest.raises(TypeError, match="Word must be a string"):
        analyzer.analyze_word(123)

    with pytest.raises(ValueError, match="cannot be empty"):
        analyzer.analyze_word("")

    with pytest.raises(ValueError, match="cannot be empty"):
        analyzer.analyze_word("   \t  ")


def test_analyzer_case_and_whitespace_normalization(analyzer: ShonaLinguisticAnalyzer):
    res = analyzer.analyze_word("  MUNHU  ")
    assert res[0].word == "munhu"
    assert res[0].certainty == CertaintyLevel.CONFIRMED


def test_unicode_and_special_orthography(analyzer: ShonaLinguisticAnalyzer):
    analyses = analyzer.analyze_word("chigaro")
    assert len(analyses) >= 1
    assert any(a.paired_form == "zvigaro" for a in analyses)


# ============================================================================
# 7. Integration & Token Analysis
# ============================================================================


def test_analyze_tokens_integration(analyzer: ShonaLinguisticAnalyzer):
    tokens = tokenize("Munhu ane chikafu.")
    results = analyzer.analyze_tokens(tokens)

    # 3 word tokens (punctuation '.' is excluded)
    assert len(results) == 3
    t_munhu, a_munhu = results[0]
    assert t_munhu.text == "Munhu"
    assert a_munhu[0].certainty == CertaintyLevel.CONFIRMED
    assert a_munhu[0].paired_form == "vanhu"


def test_separation_of_data_and_logic():
    # Verify custom registries can be injected cleanly without modifying analyzer
    custom_classes = NounClassRegistry()
    custom_classes.register(
        NounClass(identifier="X", prefix="ka", number=NumberCategory.SINGULAR)
    )
    custom_rules = RuleRegistry()
    custom_rules.register(
        MorphologicalRule(
            rule_id="custom_r",
            description="custom",
            source_prefix="ka",
            target_prefix="tu",
            source_class_id="X",
            target_class_id="Y",
        )
    )

    custom_analyzer = ShonaLinguisticAnalyzer(
        class_registry=custom_classes,
        rule_registry=custom_rules,
        relationships=[],
    )

    analyses = custom_analyzer.analyze_word("kamwana")
    assert len(analyses) == 1
    assert analyses[0].noun_class.identifier == "X"
    assert analyses[0].paired_form == "tumwana"