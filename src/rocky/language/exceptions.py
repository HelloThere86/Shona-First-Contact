"""Custom exception hierarchy for Rocky language and vocabulary components."""


# ============================================================================
# Vocabulary Exceptions (Rocky 0.1)
# ============================================================================


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


# ============================================================================
# Linguistic Analysis Exceptions (Rocky 0.4)
# ============================================================================


class LinguisticError(VocabularyError):
    """Base exception for all linguistic analysis and registry errors."""


class DuplicateNounClassError(LinguisticError, ValueError):
    """Raised when registering a noun class with an identifier that already exists."""


class InvalidNounClassError(LinguisticError, ValueError):
    """Raised when a noun class definition is incomplete, malformed, or missing."""


class DuplicateRuleError(LinguisticError, ValueError):
    """Raised when registering a morphological rule with an ID that already exists."""


class InvalidRuleError(LinguisticError, ValueError):
    """Raised when a morphological rule definition is malformed or invalid."""