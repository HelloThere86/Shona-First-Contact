"""Linguistic representations, vocabulary management, text processing, and analysis."""

from rocky.language.analysis import (
    CertaintyLevel,
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
    get_default_word_relationships,
)
from rocky.language.entry import VocabularyEntry
from rocky.language.exceptions import (
    DuplicateNounClassError,
    DuplicateRuleError,
    DuplicateWordError,
    InvalidNounClassError,
    InvalidRuleError,
    LinguisticError,
    StorageError,
    StorageFileNotFoundError,
    ValidationError,
    VocabularyError,
    WordNotFoundError,
)
from rocky.language.manager import VocabularyManager
from rocky.language.storage import JsonVocabularyStorage
from rocky.language.text import (
    ProcessedText,
    Sentence,
    TextProcessor,
    Token,
    normalize_text,
    process_text,
    segment_sentences,
    tokenize,
)

__all__ = [
    # Vocabulary components
    "VocabularyEntry",
    "VocabularyManager",
    "JsonVocabularyStorage",
    "VocabularyError",
    "ValidationError",
    "WordNotFoundError",
    "DuplicateWordError",
    "StorageError",
    "StorageFileNotFoundError",
    # Text processing components
    "Token",
    "Sentence",
    "ProcessedText",
    "TextProcessor",
    "normalize_text",
    "segment_sentences",
    "tokenize",
    "process_text",
    # Linguistic analysis components
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
    "LinguisticError",
    "DuplicateNounClassError",
    "InvalidNounClassError",
    "DuplicateRuleError",
    "InvalidRuleError",
]