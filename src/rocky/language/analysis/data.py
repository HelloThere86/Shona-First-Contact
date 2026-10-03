"""Documented and verified linguistic dataset for Shona noun classes and relationships."""

from __future__ import annotations

from rocky.language.analysis.models import (
    MorphologicalRule,
    NounClass,
    NumberCategory,
    WordFormRelationship,
)
from rocky.language.analysis.registry import NounClassRegistry
from rocky.language.analysis.rules import RuleRegistry


def build_default_noun_class_registry() -> NounClassRegistry:
    """Build a registry populated with documented Bantu noun classes for Shona."""
    registry = NounClassRegistry()

    classes = [
        NounClass(
            identifier="1",
            prefix="mu",
            vowel_prefix="mw",
            number=NumberCategory.SINGULAR,
            paired_class_id="2",
            description="Personal class: human beings and agents (singular).",
            examples=("munhu", "mwana", "mukadzi", "murume"),
        ),
        NounClass(
            identifier="2",
            prefix="va",
            vowel_prefix="v",
            number=NumberCategory.PLURAL,
            paired_class_id="1",
            description="Personal class: plural of Class 1.",
            examples=("vanhu", "vana", "vakadzi", "varume"),
        ),
        NounClass(
            identifier="1a",
            prefix="Ø",
            number=NumberCategory.SINGULAR,
            paired_class_id="2a",
            description="Kinship terms, proper names, and honorifics (singular).",
            examples=("baba", "mai", "tete"),
        ),
        NounClass(
            identifier="2a",
            prefix="vana",
            number=NumberCategory.PLURAL,
            paired_class_id="1a",
            description="Plural and honorific forms for Class 1a.",
            examples=("vanababa", "vanamai"),
        ),
        NounClass(
            identifier="3",
            prefix="mu",
            vowel_prefix="mw",
            number=NumberCategory.SINGULAR,
            paired_class_id="4",
            description="Trees, plants, and natural entities (singular).",
            examples=("muti", "mwedzi", "munda", "muromo"),
        ),
        NounClass(
            identifier="4",
            prefix="mi",
            vowel_prefix="m",
            number=NumberCategory.PLURAL,
            paired_class_id="3",
            description="Plural of Class 3.",
            examples=("miti", "mwedzi", "minda", "miromo"),
        ),
        NounClass(
            identifier="5",
            prefix="ri",
            number=NumberCategory.SINGULAR,
            paired_class_id="6",
            description="Paired body parts, fruits, objects (often with zero prefix).",
            examples=("banga", "dombo", "ziso", "zano"),
        ),
        NounClass(
            identifier="6",
            prefix="ma",
            number=NumberCategory.PLURAL,
            paired_class_id="5",
            description="Plural of Class 5; mass nouns and liquids.",
            examples=("mapanga", "matombo", "maziso", "mukaka", "mvura"),
        ),
        NounClass(
            identifier="7",
            prefix="chi",
            vowel_prefix="ch",
            number=NumberCategory.SINGULAR,
            paired_class_id="8",
            description="Objects, instruments, languages, cultural customs (singular).",
            examples=("chikafu", "chigaro", "chitsva", "Chishona"),
        ),
        NounClass(
            identifier="8",
            prefix="zvi",
            vowel_prefix="zv",
            number=NumberCategory.PLURAL,
            paired_class_id="7",
            description="Plural of Class 7.",
            examples=("zvikafu", "zvigaro", "zvitsva"),
        ),
        NounClass(
            identifier="9",
            prefix="N",
            number=NumberCategory.SINGULAR,
            paired_class_id="10",
            description="Animals, household items, miscellaneous (nasal or zero prefix).",
            examples=("imba", "nzou", "imbwa", "mhepo"),
        ),
        NounClass(
            identifier="10",
            prefix="dzi",
            number=NumberCategory.PLURAL,
            paired_class_id="9",
            description="Plural of Class 9 and Class 11.",
            examples=("dzimba", "nzou", "imbwa"),
        ),
        NounClass(
            identifier="11",
            prefix="ru",
            vowel_prefix="rw",
            number=NumberCategory.SINGULAR,
            paired_class_id="10",
            description="Long, thin, extended, or abstract entities.",
            examples=("ruoko", "rurimi", "rwizi"),
        ),
        NounClass(
            identifier="12",
            prefix="ka",
            number=NumberCategory.SINGULAR,
            paired_class_id="13",
            description="Diminutives (singular).",
            examples=("kambwa", "kamwana"),
        ),
        NounClass(
            identifier="13",
            prefix="tu",
            vowel_prefix="tw",
            number=NumberCategory.PLURAL,
            paired_class_id="12",
            description="Diminutives (plural).",
            examples=("tumbwa", "tuvana"),
        ),
        NounClass(
            identifier="14",
            prefix="u",
            number=NumberCategory.INVARIABLE,
            paired_class_id=None,
            description="Abstract nouns, states of being, collective entities.",
            examples=("upenyu", "uswa", "uchi"),
        ),
        NounClass(
            identifier="15",
            prefix="ku",
            number=NumberCategory.INVARIABLE,
            paired_class_id=None,
            description="Infinitives, gerunds, verbal nouns, body parts.",
            examples=("kutaura", "kudya", "kuenda", "kuoko"),
        ),
        NounClass(
            identifier="16",
            prefix="pa",
            number=NumberCategory.UNSPECIFIED,
            paired_class_id=None,
            description="Locative: position at or upon.",
            examples=("patafura", "pamusha"),
        ),
        NounClass(
            identifier="17",
            prefix="ku",
            number=NumberCategory.UNSPECIFIED,
            paired_class_id=None,
            description="Locative: movement towards or general area.",
            examples=("kumunda", "kumba"),
        ),
        NounClass(
            identifier="18",
            prefix="mu",
            number=NumberCategory.UNSPECIFIED,
            paired_class_id=None,
            description="Locative: inside or interior.",
            examples=("mumba", "mumunda"),
        ),
    ]

    for nc in classes:
        registry.register(nc)

    return registry


def get_default_word_relationships() -> list[WordFormRelationship]:
    """Return initial verified word-form relationships for Shona."""
    return [
        WordFormRelationship(
            source_word="munhu",
            target_word="vanhu",
            relationship_type="singular_plural",
            source_class_id="1",
            target_class_id="2",
            stem="nhu",
            is_confirmed=True,
            notes="Consonant stem: mu-nhu / va-nhu.",
        ),
        WordFormRelationship(
            source_word="mwana",
            target_word="vana",
            relationship_type="singular_plural",
            source_class_id="1",
            target_class_id="2",
            stem="ana",
            is_confirmed=True,
            notes="Vowel stem with glide/contraction: mu-ana -> mwana, va-ana -> vana.",
        ),
        WordFormRelationship(
            source_word="imba",
            target_word="dzimba",
            relationship_type="singular_plural",
            source_class_id="9",
            target_class_id="10",
            stem="mba",
            is_confirmed=True,
            notes="Class 9/10 pairing with prefix dzi- in plural.",
        ),
        WordFormRelationship(
            source_word="muti",
            target_word="miti",
            relationship_type="singular_plural",
            source_class_id="3",
            target_class_id="4",
            stem="ti",
            is_confirmed=True,
            notes="Class 3/4 tree/plant pairing: mu-ti / mi-ti.",
        ),
        WordFormRelationship(
            source_word="chikafu",
            target_word="zvikafu",
            relationship_type="singular_plural",
            source_class_id="7",
            target_class_id="8",
            stem="kafu",
            is_confirmed=True,
            notes="Class 7/8 noun pairing: chi-kafu / zvi-kafu.",
        ),
        WordFormRelationship(
            source_word="mukaka",
            target_word="mukaka",
            relationship_type="invariable",
            source_class_id="6",
            target_class_id="6",
            stem="kaka",
            is_confirmed=True,
            notes="Mass liquid noun; invariable singular/plural usage.",
        ),
        WordFormRelationship(
            source_word="mvura",
            target_word="mvura",
            relationship_type="invariable",
            source_class_id="9",
            target_class_id="9",
            stem="vura",
            is_confirmed=True,
            notes="Mass noun (water/rain); invariable usage.",
        ),
        # Example of documented relationship with UNVERIFIED stem decomposition
        WordFormRelationship(
            source_word="chitsva",
            target_word="zvitsva",
            relationship_type="singular_plural",
            source_class_id="7",
            target_class_id="8",
            stem=None,
            is_confirmed=False,
            notes="Relationship documented without confirmed root stem decomposition.",
        ),
    ]


def build_default_rule_registry() -> RuleRegistry:
    """Build a registry of documented morphological rules."""
    registry = RuleRegistry()

    rules = [
        MorphologicalRule(
            rule_id="cl1_to_cl2_mu_va",
            description="Transform Class 1 personal noun (mu-) to Class 2 plural (va-).",
            source_prefix="mu",
            target_prefix="va",
            source_class_id="1",
            target_class_id="2",
            min_stem_length=2,
            notes="Applies to consonant-initial stems of Class 1.",
        ),
        MorphologicalRule(
            rule_id="cl2_to_cl1_va_mu",
            description="Transform Class 2 plural (va-) to Class 1 singular (mu-).",
            source_prefix="va",
            target_prefix="mu",
            source_class_id="2",
            target_class_id="1",
            min_stem_length=2,
            notes="Applies to consonant-initial stems of Class 2.",
        ),
        MorphologicalRule(
            rule_id="cl3_to_cl4_mu_mi",
            description="Transform Class 3 noun (mu-) to Class 4 plural (mi-).",
            source_prefix="mu",
            target_prefix="mi",
            source_class_id="3",
            target_class_id="4",
            min_stem_length=2,
            notes="Applies to consonant-initial stems of Class 3.",
        ),
        MorphologicalRule(
            rule_id="cl4_to_cl3_mi_mu",
            description="Transform Class 4 plural (mi-) to Class 3 singular (mu-).",
            source_prefix="mi",
            target_prefix="mu",
            source_class_id="4",
            target_class_id="3",
            min_stem_length=2,
            notes="Applies to consonant-initial stems of Class 4.",
        ),
        MorphologicalRule(
            rule_id="cl7_to_cl8_chi_zvi",
            description="Transform Class 7 object (chi-) to Class 8 plural (zvi-).",
            source_prefix="chi",
            target_prefix="zvi",
            source_class_id="7",
            target_class_id="8",
            min_stem_length=2,
            notes="Applies to consonant-initial stems of Class 7.",
        ),
        MorphologicalRule(
            rule_id="cl8_to_cl7_zvi_chi",
            description="Transform Class 8 plural (zvi-) to Class 7 singular (chi-).",
            source_prefix="zvi",
            target_prefix="chi",
            source_class_id="8",
            target_class_id="7",
            min_stem_length=2,
            notes="Applies to consonant-initial stems of Class 8.",
        ),
    ]

    for rule in rules:
        registry.register(rule)

    return registry