"""Automated tests for Rocky 0.3 Text Processing Engine."""

import pytest

from rocky.language import (
    ProcessedText,
    Sentence,
    TextProcessor,
    Token,
    normalize_text,
    process_text,
    segment_sentences,
    tokenize,
)


# ============================================================================
# 1. Normalization Tests
# ============================================================================


def test_normalize_basic_whitespace():
    raw = "   Mhoro   shamwari,    uri   sei?   "
    expected = "Mhoro shamwari, uri sei?"
    assert normalize_text(raw) == expected


def test_normalize_newlines_and_tabs():
    raw = "Mhoro\t\nshamwari.\n\nNdiri\t\tkufara."
    expected = "Mhoro shamwari. Ndiri kufara."
    assert normalize_text(raw) == expected


def test_normalize_capitalization():
    raw = "Mhoro Shamwari Nhasi"
    assert normalize_text(raw, lowercase=False) == "Mhoro Shamwari Nhasi"
    assert normalize_text(raw, lowercase=True) == "mhoro shamwari nhasi"


def test_normalize_punctuation_spacing_without_merging():
    # Tests that punctuation directly attached to next word is separated
    raw = "mhoro,shamwari!ndiri pano;chokwadi"
    expected = "mhoro, shamwari! ndiri pano; chokwadi"
    assert normalize_text(raw) == expected


def test_normalize_preserves_intra_word_characters():
    # Compound words and apostrophes within words must not be split
    raw = "mangwanani-ngwanani nd'ani ch'akanaka"
    assert normalize_text(raw) == "mangwanani-ngwanani nd'ani ch'akanaka"


def test_normalize_empty_and_whitespace():
    assert normalize_text("") == ""
    assert normalize_text("    ") == ""
    assert normalize_text("\t\n\r") == ""


# ============================================================================
# 2. Tokenization Tests
# ============================================================================


def test_tokenize_basic_sentence():
    text = "Mhoro, shamwari!"
    tokens = tokenize(text)

    assert len(tokens) == 4
    assert [t.text for t in tokens] == ["Mhoro", ",", "shamwari", "!"]
    assert [t.normalized for t in tokens] == ["mhoro", ",", "shamwari", "!"]
    assert [t.is_punctuation for t in tokens] == [False, True, False, True]


def test_tokenize_token_spans():
    text = "Uri sei?"
    tokens = tokenize(text)

    assert tokens[0].text == "Uri"
    assert tokens[0].start_char == 0
    assert tokens[0].end_char == 3

    assert tokens[1].text == "sei"
    assert tokens[1].start_char == 4
    assert tokens[1].end_char == 7

    assert tokens[2].text == "?"
    assert tokens[2].start_char == 7
    assert tokens[2].end_char == 8


def test_tokenize_handles_punctuation_without_merging():
    # Even if words touch punctuation, tokenization separates them
    text = "chikafu,mukaka;mvura"
    tokens = tokenize(text)
    assert [t.text for t in tokens] == ["chikafu", ",", "mukaka", ";", "mvura"]


def test_tokenize_handles_ellipsis():
    text = "Zvichida... handizive."
    tokens = tokenize(text)
    assert [t.text for t in tokens] == ["Zvichida", "...", "handizive", "."]
    assert tokens[1].is_punctuation is True


def test_tokenize_handles_shona_compounds_and_contractions():
    text = "Mangwanani-ngwanani, nd'ani auya?"
    tokens = tokenize(text)
    words = [t.text for t in tokens if not t.is_punctuation]
    assert words == ["Mangwanani-ngwanani", "nd'ani", "auya"]


def test_tokenize_empty_and_whitespace():
    assert tokenize("") == []
    assert tokenize("   \n\t  ") == []


# ============================================================================
# 3. Sentence Segmentation Tests
# ============================================================================


def test_segment_single_sentence():
    text = "Mhoro shamwari."
    assert segment_sentences(text) == ["Mhoro shamwari."]


def test_segment_multiple_sentences():
    text = "Mhoro shamwari. Uri sei nhasi? Ndiri kufara!"
    sentences = segment_sentences(text)
    assert sentences == [
        "Mhoro shamwari.",
        "Uri sei nhasi?",
        "Ndiri kufara!",
    ]


def test_segment_repeated_terminal_punctuation():
    text = "Zvichida kwete... Ko iwe?! Handizive."
    sentences = segment_sentences(text)
    assert sentences == [
        "Zvichida kwete...",
        "Ko iwe?!",
        "Handizive.",
    ]


def test_segment_sentence_without_ending_punctuation():
    text = "Mhoro shamwari. Ndiri pano"
    sentences = segment_sentences(text)
    assert sentences == ["Mhoro shamwari.", "Ndiri pano"]


def test_segment_empty_and_whitespace():
    assert segment_sentences("") == []
    assert segment_sentences("   \t  \n ") == []


# ============================================================================
# 4. Input Validation & Error Handling
# ============================================================================


@pytest.mark.parametrize(
    "invalid_input",
    [None, 123, 45.67, ["list"], {"dict": "val"}, True],
)
def test_validation_type_error(invalid_input):
    with pytest.raises(TypeError, match="Text input must be a string"):
        normalize_text(invalid_input)

    with pytest.raises(TypeError, match="Text input must be a string"):
        segment_sentences(invalid_input)

    with pytest.raises(TypeError, match="Text input must be a string"):
        tokenize(invalid_input)

    with pytest.raises(TypeError, match="Text input must be a string"):
        process_text(invalid_input)


# ============================================================================
# 5. Unicode and Shona Characters
# ============================================================================


def test_unicode_and_special_orthography():
    text = "Mhoro vēse! Ñyika yeZimbabwe yakànaka."
    processed = process_text(text)
    words = processed.words()
    assert "vēse" in words
    assert "Ñyika" in words
    assert "yakànaka" in words


# ============================================================================
# 6. Structured ProcessedText Pipeline & Class Engine
# ============================================================================


def test_process_text_structure():
    raw = "Mhoro shamwari. Uri sei?"
    doc = process_text(raw)

    assert isinstance(doc, ProcessedText)
    assert doc.original == raw
    assert doc.normalized == "Mhoro shamwari. Uri sei?"
    assert len(doc.sentences) == 2

    sent1 = doc.sentences[0]
    assert isinstance(sent1, Sentence)
    assert sent1.text == "Mhoro shamwari."
    assert [t.text for t in sent1.tokens] == ["Mhoro", "shamwari", "."]

    assert doc.words() == ["Mhoro", "shamwari", "Uri", "sei"]
    assert doc.words(lowercase=True) == ["mhoro", "shamwari", "uri", "sei"]
    assert doc.token_texts() == ["Mhoro", "shamwari", ".", "Uri", "sei", "?"]


def test_text_processor_class():
    processor = TextProcessor(default_lowercase=True)

    norm = processor.normalize("  MHORO   SHAMWARI  ")
    assert norm == "mhoro shamwari"

    tokens = processor.tokenize("Uri sei?")
    assert [t.normalized for t in tokens] == ["uri", "sei", "?"]

    sentences = processor.segment_sentences("Chikafu chiripi? Mvura iripi!")
    assert len(sentences) == 2

    doc = processor.process("Mhoro shamwari.")
    assert doc.words(lowercase=True) == ["mhoro", "shamwari"]