"""Linguistic representations, vocabulary management, and text processing."""

from rocky.language.entry import VocabularyEntry
from rocky.language.exceptions import (
    DuplicateWordError,
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
    "VocabularyEntry",
    "VocabularyManager",
    "JsonVocabularyStorage",
    "VocabularyError",
    "ValidationError",
    "WordNotFoundError",
    "DuplicateWordError",
    "StorageError",
    "StorageFileNotFoundError",
    "Token",
    "Sentence",
    "ProcessedText",
    "TextProcessor",
    "normalize_text",
    "segment_sentences",
    "tokenize",
    "process_text",
]