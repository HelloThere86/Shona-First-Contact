"""Shona linguistic analysis and concord agreement subpackage."""

from rocky.language.analysis.analyzer import ShonaLinguisticAnalyzer
from rocky.language.analysis.concord_analyzer import ShonaConcordAnalyzer
from rocky.language.analysis.concord_data import build_default_concord_registry
from rocky.language.analysis.concord_models import (
    AgreementValidationResult,
    ConcordAnalysis,
    ConcordCategory,
    ConcordRecord,
)
from rocky.language.analysis.concord_registry import ConcordRegistry
from rocky.language.analysis.data import (
    build_default_noun_class_registry,
    build_default_rule_registry,
    get_default_word_relationships,
)
from rocky.language.analysis.models import (
    CertaintyLevel,
    MorphologicalRule,
    NounClass,
    NumberCategory,
    WordAnalysis,
    WordFormRelationship,
)
from rocky.language.analysis.registry import NounClassRegistry
from rocky.language.analysis.rules import RuleRegistry

__all__ = [
    # Rocky 0.4 models and analyzers
    "CertaintyLevel",
    "NumberCategory",
    "NounClass",
    "WordFormRelationship",
    "MorphologicalRule",
    "WordAnalysis",
    "NounClassRegistry",
    "RuleRegistry",
    "ShonaLinguisticAnalyzer",
    "build_default_noun_class_registry",
    "build_default_rule_registry",
    "get_default_word_relationships",
    # Rocky 0.5 concord agreement models and analyzers
    "ConcordCategory",
    "ConcordRecord",
    "ConcordAnalysis",
    "AgreementValidationResult",
    "ConcordRegistry",
    "ShonaConcordAnalyzer",
    "build_default_concord_registry",
]