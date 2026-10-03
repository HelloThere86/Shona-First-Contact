"""Text processing engine for normalization, sentence segmentation, and tokenization."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Sequence


@dataclass(frozen=True)
class Token:
    """Represents an individual token extracted from text.

    Attributes:
        text: Original token text as it appeared in source.
        normalized: Cleaned, lowercased form of the token.
        is_punctuation: True if the token consists entirely of punctuation marks.
        start_char: 0-based character start index in source text.
        end_char: 0-based character end index in source text.
    """

    text: str
    normalized: str
    is_punctuation: bool
    start_char: int
    end_char: int


@dataclass(frozen=True)
class Sentence:
    """Represents a segmented sentence containing tokens.

    Attributes:
        text: Raw sentence text.
        normalized: Normalized sentence text.
        tokens: Tuple of Token instances contained in the sentence.
        start_char: 0-based character start index in source text.
        end_char: 0-based character end index in source text.
    """

    text: str
    normalized: str
    tokens: tuple[Token, ...]
    start_char: int
    end_char: int


@dataclass(frozen=True)
class ProcessedText:
    """Structured representation of fully processed text.

    Attributes:
        original: Original raw input text.
        normalized: Cleaned and normalized text representation.
        sentences: Tuple of Sentence instances.
        tokens: Tuple of all Token instances across all sentences.
    """

    original: str
    normalized: str
    sentences: tuple[Sentence, ...]
    tokens: tuple[Token, ...]

    def words(self, lowercase: bool = False) -> list[str]:
        """Return word tokens excluding punctuation.

        Args:
            lowercase: If True, returns normalized lowercase strings.
        """
        if lowercase:
            return [t.normalized for t in self.tokens if not t.is_punctuation]
        return [t.text for t in self.tokens if not t.is_punctuation]

    def token_texts(self, lowercase: bool = False) -> list[str]:
        """Return string values for all tokens, including punctuation.

        Args:
            lowercase: If True, returns normalized lowercase strings.
        """
        if lowercase:
            return [t.normalized for t in self.tokens]
        return [t.text for t in self.tokens]


# Token regex matching:
# 1. Multi-dot ellipses (...)
# 2. Words with optional internal hyphens or apostrophes (e.g. mangwanani-ngwanani, nd'ani)
# 3. Individual punctuation and symbols
TOKEN_PATTERN = re.compile(
    r"""
    (?P<ellipsis>\.{3,})                   | # Ellipsis (...)
    (?P<word>[\w]+(?:['’\-][\w]+)*)        | # Word token (with optional internal hyphen/apostrophe)
    (?P<punctuation>[^\w\s])                 # Punctuation mark or symbol
    """,
    re.VERBOSE | re.UNICODE,
)

# Sentence boundary regex: captures sequences up to terminal punctuation followed by space or end
SENTENCE_PATTERN = re.compile(r"(.+?[.!?]+)(?=(?:\s+|$))|(.+?$)", re.DOTALL)


def _validate_input_string(text: str) -> None:
    """Validate that input is a string instance."""
    if not isinstance(text, str):
        raise TypeError(f"Text input must be a string, received {type(text).__name__}.")


def _normalize_punctuation_spacing(text: str) -> str:
    """Ensure punctuation does not merge adjacent words while preserving internal hyphens/apostrophes."""
    # Ensure space after commas, semicolons, colons, exclamation marks, question marks
    text = re.sub(r"([,;:!?])([^\s\d])", r"\1 \2", text)
    # Ensure space after single period if followed by a letter (avoids decimals like 3.14 and ellipses ...)
    text = re.sub(r"(?<!\.)\.(?!\.)(?=[A-Za-z\u00C0-\u024F\u1E00-\u1EFF])", ". ", text)
    return text


def normalize_text(text: str, lowercase: bool = False) -> str:
    """Normalize whitespace, punctuation spacing, and casing.

    Args:
        text: Raw input string.
        lowercase: If True, converts result to lowercase.

    Returns:
        Cleaned, normalized string with single spaces between words.

    Raises:
        TypeError: If input is not a string.
    """
    _validate_input_string(text)

    cleaned = text.strip()
    if not cleaned:
        return ""

    cleaned = _normalize_punctuation_spacing(cleaned)
    # Collapse tabs, newlines, and repeated spaces into a single space
    cleaned = re.sub(r"\s+", " ", cleaned)

    if lowercase:
        cleaned = cleaned.lower()

    return cleaned


def segment_sentences(text: str) -> list[str]:
    """Segment input text into individual sentences based on terminal punctuation.

    Args:
        text: Raw input string.

    Returns:
        List of sentence strings.

    Raises:
        TypeError: If input is not a string.
    """
    _validate_input_string(text)

    cleaned = text.strip()
    if not cleaned:
        return []

    sentences: list[str] = []
    pos = 0
    while pos < len(cleaned):
        match = SENTENCE_PATTERN.search(cleaned, pos)
        if not match:
            break

        sentence = match.group(0).strip()
        if sentence:
            sentences.append(sentence)

        pos = match.end()
        while pos < len(cleaned) and cleaned[pos].isspace():
            pos += 1

    return sentences


def tokenize(text: str, lowercase: bool = False) -> list[Token]:
    """Tokenize a string into individual word and punctuation tokens.

    Args:
        text: Input string to tokenize.
        lowercase: If True, normalizes token text to lowercase.

    Returns:
        List of Token instances preserving character offsets and punctuation flags.

    Raises:
        TypeError: If input is not a string.
    """
    _validate_input_string(text)

    if not text.strip():
        return []

    tokens: list[Token] = []
    for match in TOKEN_PATTERN.finditer(text):
        raw_token = match.group(0)
        is_punct = bool(match.group("punctuation") or match.group("ellipsis"))
        norm_token = raw_token.lower() if lowercase else raw_token.lower()

        tokens.append(
            Token(
                text=raw_token,
                normalized=norm_token,
                is_punctuation=is_punct,
                start_char=match.start(),
                end_char=match.end(),
            )
        )

    return tokens


def process_text(text: str, lowercase: bool = False) -> ProcessedText:
    """Perform full text pipeline: normalization, sentence segmentation, and tokenization.

    Args:
        text: Raw input text.
        lowercase: If True, lowercase normalized representations.

    Returns:
        Structured ProcessedText instance.

    Raises:
        TypeError: If input is not a string.
    """
    _validate_input_string(text)

    normalized_full = normalize_text(text, lowercase=lowercase)
    if not normalized_full:
        return ProcessedText(
            original=text,
            normalized="",
            sentences=(),
            tokens=(),
        )

    raw_sentences = segment_sentences(text)
    sentence_objects: list[Sentence] = []
    all_tokens: list[Token] = []

    search_cursor = 0
    for raw_sentence in raw_sentences:
        start_idx = text.find(raw_sentence, search_cursor)
        end_idx = start_idx + len(raw_sentence) if start_idx != -1 else search_cursor
        search_cursor = end_idx

        sent_tokens = tokenize(raw_sentence, lowercase=lowercase)
        # Adjust token offsets relative to original document text
        adjusted_tokens = tuple(
            Token(
                text=t.text,
                normalized=t.normalized,
                is_punctuation=t.is_punctuation,
                start_char=start_idx + t.start_char if start_idx != -1 else t.start_char,
                end_char=start_idx + t.end_char if start_idx != -1 else t.end_char,
            )
            for t in sent_tokens
        )

        norm_sentence = normalize_text(raw_sentence, lowercase=lowercase)
        sentence_objects.append(
            Sentence(
                text=raw_sentence,
                normalized=norm_sentence,
                tokens=adjusted_tokens,
                start_char=start_idx,
                end_char=end_idx,
            )
        )
        all_tokens.extend(adjusted_tokens)

    return ProcessedText(
        original=text,
        normalized=normalized_full,
        sentences=tuple(sentence_objects),
        tokens=tuple(all_tokens),
    )


class TextProcessor:
    """Configurable text processing engine for Shona and bilingual text."""

    def __init__(self, default_lowercase: bool = False) -> None:
        """Initialize the text processor.

        Args:
            default_lowercase: Default casing flag for normalization and tokenization.
        """
        self.default_lowercase = default_lowercase

    def normalize(self, text: str, lowercase: bool | None = None) -> str:
        """Normalize text whitespace, spacing, and casing."""
        lc = self.default_lowercase if lowercase is None else lowercase
        return normalize_text(text, lowercase=lc)

    def segment_sentences(self, text: str) -> list[str]:
        """Split text into sentences."""
        return segment_sentences(text)

    def tokenize(self, text: str, lowercase: bool | None = None) -> list[Token]:
        """Split text into structured tokens."""
        lc = self.default_lowercase if lowercase is None else lowercase
        return tokenize(text, lowercase=lc)

    def process(self, text: str, lowercase: bool | None = None) -> ProcessedText:
        """Run full processing pipeline and return structured document object."""
        lc = self.default_lowercase if lowercase is None else lowercase
        return process_text(text, lowercase=lc)