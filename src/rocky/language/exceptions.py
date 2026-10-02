"""Custom exception hierarchy for the Rocky vocabulary engine."""


class VocabularyError(Exception):
    """Base exception for all vocabulary engine errors."""


class ValidationError(VocabularyError, ValueError):
    """Raised when word or meaning inputs violate validation rules."""


class WordNotFoundError(VocabularyError, KeyError):
    """Raised when attempting to lookup, update, or remove a nonexistent word."""


class DuplicateWordError(VocabularyError, ValueError):
    """Raised when attempting to add a word that already exists in vocabulary."""


class StorageError(VocabularyError, OSError):
    """Raised when saving or loading vocabulary fails (I/O, formatting, corruption)."""


class StorageFileNotFoundError(StorageError, FileNotFoundError):
    """Raised when the specified vocabulary storage file does not exist."""