"""Documented and verified concord agreement records for Shona.

Sources:
    - Fortune, George (1980/1984). Shona Grammatical Constructions, Vol. 1 & 2.
      Harare: Mercury Press. (Noun classes, subject prefixes, and concords).
    - Hannan, M. (1984). Standard Shona Dictionary. Harare: College Press.
    - Dale, Desmond (1972). Shona Companion. Gweru: Mambo Press.
"""

from __future__ import annotations

from rocky.language.analysis.concord_models import ConcordCategory, ConcordRecord
from rocky.language.analysis.concord_registry import ConcordRegistry
from rocky.language.analysis.models import CertaintyLevel

STANDARD_GRAMMAR_CITATION = "Fortune (1984) Shona Grammatical Constructions, Vol. 1, pp. 77-111"


def build_default_concord_registry() -> ConcordRegistry:
    """Build a concord registry populated with documented Shona agreement markers."""
    registry = ConcordRegistry()

    # 1. Subject Concords (SC) — Fortune (1984), pp. 77-80
    subject_concords = [
        ("1", "a", "w", "Subject prefix for Class 1 (e.g., mwana anorara)."),
        ("1a", "a", "w", "Subject prefix for Class 1a kinship/names (e.g., baba vanouya / anouya)."),
        ("2", "va", "v", "Subject prefix for Class 2 plural (e.g., vanhu vanotamba)."),
        ("2a", "va", "v", "Subject prefix for Class 2a honorific/plural (e.g., vanababa vanouya)."),
        ("3", "u", "w", "Subject prefix for Class 3 trees/plants (e.g., muti unokura)."),
        ("4", "i", "y", "Subject prefix for Class 4 plural trees/plants (e.g., miti inokura)."),
        ("5", "ri", "r", "Subject prefix for Class 5 objects (e.g., banga rinocheka)."),
        ("6", "a", "w", "Subject prefix for Class 6 plural/mass (e.g., mapanga anocheka, mukaka unovava)."),
        ("7", "chi", "ch", "Subject prefix for Class 7 objects/tools (e.g., chikafu chinonaka)."),
        ("8", "zvi", "zv", "Subject prefix for Class 8 plural objects (e.g., zvikafu zvinonaka)."),
        ("9", "i", "y", "Subject prefix for Class 9 animals/items/mass (e.g., imba inodziya, mvura inonaya)."),
        ("10", "dzi", "dz", "Subject prefix for Class 10 plural items (e.g., dzimba dzinodziya)."),
        ("11", "ru", "rw", "Subject prefix for Class 11 extended objects (e.g., ruoko runorwadza)."),
        ("12", "ka", "k", "Subject prefix for Class 12 diminutives (e.g., kambwa kanomhanya)."),
        ("13", "tu", "tw", "Subject prefix for Class 13 plural diminutives (e.g., tumbwa tunomhanya)."),
        ("14", "u", "hw", "Subject prefix for Class 14 abstract nouns (e.g., upenyu hwakanaka)."),
        ("15", "ku", "kw", "Subject prefix for Class 15 infinitives/body parts (e.g., kudya kunonaka)."),
        ("16", "pa", "p", "Subject prefix for Class 16 locative at/on (e.g., patafura panotonhora)."),
        ("17", "ku", "kw", "Subject prefix for Class 17 locative to/towards (e.g., kumunda kunofadza)."),
        ("18", "mu", "mw", "Subject prefix for Class 18 locative in/inside (e.g., mumba munodziya)."),
    ]

    for class_id, prefix, var, notes in subject_concords:
        registry.register(
            ConcordRecord(
                noun_class_id=class_id,
                category=ConcordCategory.SUBJECT,
                concord_prefix=prefix,
                variant_prefix=var,
                certainty=CertaintyLevel.CONFIRMED,
                source=STANDARD_GRAMMAR_CITATION,
                notes=notes,
            )
        )

    # 2. Adjective Concords (AC) — Fortune (1984), pp. 109-111; Dale (1972)
    # Adjective prefixes in Shona closely mirror nominal class prefixes
    adjective_concords = [
        ("1", "mu", None, "Adjective prefix for Class 1 (e.g., munhu mukuru)."),
        ("1a", "mu", None, "Adjective prefix for Class 1a (e.g., baba mukuru)."),
        ("2", "va", None, "Adjective prefix for Class 2 (e.g., vanhu vakuru)."),
        ("2a", "va", None, "Adjective prefix for Class 2a (e.g., vanababa vakuru)."),
        ("3", "mu", None, "Adjective prefix for Class 3 (e.g., muti mukuru)."),
        ("4", "mi", None, "Adjective prefix for Class 4 (e.g., miti mikuru)."),
        ("5", "ri", None, "Adjective prefix for Class 5 (e.g., banga refu; note voicing on stems like guru)."),
        ("6", "ma", None, "Adjective prefix for Class 6 (e.g., mapanga makuru)."),
        ("7", "chi", None, "Adjective prefix for Class 7 (e.g., chikafu chikuru)."),
        ("8", "zvi", None, "Adjective prefix for Class 8 (e.g., zvikafu zvikuru)."),
        ("9", "i", None, "Adjective prefix for Class 9 (e.g., imba nhete; nasal mutation on stems like huru)."),
        ("10", "dzi", None, "Adjective prefix for Class 10 (e.g., dzimba nhete)."),
        ("11", "ru", None, "Adjective prefix for Class 11 (e.g., ruoko rukuru)."),
        ("12", "ka", None, "Adjective prefix for Class 12 (e.g., kambwa kadiki)."),
        ("13", "tu", None, "Adjective prefix for Class 13 (e.g., tumbwa tudiki)."),
        ("14", "u", None, "Adjective prefix for Class 14 (e.g., uswa hurefu)."),
        ("15", "ku", None, "Adjective prefix for Class 15 (e.g., kudya kukuru)."),
        ("16", "pa", None, "Adjective prefix for Class 16 (e.g., pamusha pakuru)."),
        ("17", "ku", None, "Adjective prefix for Class 17 (e.g., kumunda kukuru)."),
        ("18", "mu", None, "Adjective prefix for Class 18 (e.g., mumba mukuru)."),
    ]

    for class_id, prefix, var, notes in adjective_concords:
        registry.register(
            ConcordRecord(
                noun_class_id=class_id,
                category=ConcordCategory.ADJECTIVE,
                concord_prefix=prefix,
                variant_prefix=var,
                certainty=CertaintyLevel.CONFIRMED,
                source=STANDARD_GRAMMAR_CITATION,
                notes=notes,
            )
        )

    # 3. Possessive Concords (PC) — Fortune (1984), pp. 110-112
    # Combined with possessive formative -a
    possessive_concords = [
        ("1", "wa", "w", "Possessive marker for Class 1 (e.g., mwana waamai)."),
        ("1a", "wa", "w", "Possessive marker for Class 1a (e.g., baba vake / waamai)."),
        ("2", "va", "v", "Possessive marker for Class 2 (e.g., vana vaamai)."),
        ("2a", "va", "v", "Possessive marker for Class 2a (e.g., vanababa vedu)."),
        ("3", "wa", "w", "Possessive marker for Class 3 (e.g., muti wangu)."),
        ("4", "ya", "y", "Possessive marker for Class 4 (e.g., miti yangu)."),
        ("5", "ra", "r", "Possessive marker for Class 5 (e.g., banga rangu)."),
        ("6", "a", "w", "Possessive marker for Class 6 (e.g., mapanga angu)."),
        ("7", "cha", "ch", "Possessive marker for Class 7 (e.g., chikafu changu)."),
        ("8", "zva", "zv", "Possessive marker for Class 8 (e.g., zvikafu zvangu)."),
        ("9", "ya", "y", "Possessive marker for Class 9 (e.g., imba yangu, mvura yedu)."),
        ("10", "dza", "dz", "Possessive marker for Class 10 (e.g., dzimba dzedu)."),
        ("11", "rwa", "rw", "Possessive marker for Class 11 (e.g., ruoko rwangu)."),
        ("12", "ka", "k", "Possessive marker for Class 12 (e.g., kambwa kangu)."),
        ("13", "twa", "tw", "Possessive marker for Class 13 (e.g., tumbwa twangu)."),
        ("14", "hwa", "hw", "Possessive marker for Class 14 (e.g., uswa hwangu)."),
        ("15", "kwa", "kw", "Possessive marker for Class 15 (e.g., kudya kwangu)."),
        ("16", "pa", "p", "Possessive marker for Class 16 (e.g., pamusha pangu)."),
        ("17", "kwa", "kw", "Possessive marker for Class 17 (e.g., kumunda kwangu)."),
        ("18", "mwa", "mw", "Possessive marker for Class 18 (e.g., mumba mwangu)."),
    ]

    for class_id, prefix, var, notes in possessive_concords:
        registry.register(
            ConcordRecord(
                noun_class_id=class_id,
                category=ConcordCategory.POSSESSIVE,
                concord_prefix=prefix,
                variant_prefix=var,
                certainty=CertaintyLevel.CONFIRMED,
                source=STANDARD_GRAMMAR_CITATION,
                notes=notes,
            )
        )

    return registry