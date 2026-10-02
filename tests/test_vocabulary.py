"""Comprehensive tests for Rocky 0.1 Vocabulary Engine."""

from pathlib import Path
import pytest

from rocky.language import (
    DuplicateWordError,
    JsonVocabularyStorage,
    StorageError,
    StorageFileNotFoundError,
    ValidationError,
    VocabularyEntry,
    VocabularyManager,
    WordNotFoundError,
)

SAMPLE_FIXTURES = [
    ("mvura", "water"),
    ("mukaka", "milk"),
    ("chikafu", "food"),
    ("imba", "house"),
    ("munhu", "person"),
]


@pytest.fixture
def empty_manager() -> VocabularyManager:
    """Provide an empty VocabularyManager instance."""
    return VocabularyManager()


@pytest.fixture
def populated_manager() -> VocabularyManager:
    """Provide a VocabularyManager pre-populated with standard sample fixtures."""
    manager = VocabularyManager()
    for shona, english in SAMPLE_FIXTURES:
        manager.add(shona, english)
    return manager


# ============================================================================
# 1. Entry Creation and Validation Tests
# ============================================================================


def test_entry_valid():
    entry = VocabularyEntry(shona="Mvura", english=" Water ")
    assert entry.shona == "mvura"
    assert entry.english == "water"
    assert entry.to_dict() == {"shona": "mvura", "english": "water"}


@pytest.mark.parametrize(
    "shona, english, match",
    [
        ("", "water", "Shona word cannot be empty"),
        ("   ", "water", "Shona word cannot be empty"),
        ("mvura", "", "English meaning cannot be empty"),
        ("mvura", "   ", "English meaning cannot be empty"),
        (None, "water", "Shona word must be a string"),
        ("mvura", 123, "English meaning must be a string"),
        ({}, "water", "Shona word must be a string"),
    ],
)
def test_entry_invalid_inputs(shona, english, match):
    with pytest.raises(ValidationError, match=match):
        VocabularyEntry(shona=shona, english=english)


def test_entry_from_dict():
    data = {"shona": "mukaka", "english": "milk"}
    entry = VocabularyEntry.from_dict(data)
    assert entry.shona == "mukaka"
    assert entry.english == "milk"


def test_entry_from_dict_invalid():
    with pytest.raises(ValidationError, match="Entry data must be a dictionary"):
        VocabularyEntry.from_dict(["not", "a", "dict"])

    with pytest.raises(ValidationError, match="must contain both 'shona' and 'english'"):
        VocabularyEntry.from_dict({"shona": "mukaka"})


# ============================================================================
# 2. Add and Lookup Tests
# ============================================================================


def test_add_and_lookup_shona(empty_manager: VocabularyManager):
    entry = empty_manager.add("mvura", "water")
    assert entry.shona == "mvura"
    assert entry.english == "water"

    assert empty_manager.get_english("mvura") == "water"
    assert empty_manager.get_entry("mvura") == entry


def test_lookup_english(empty_manager: VocabularyManager):
    empty_manager.add("mukaka", "milk")
    assert empty_manager.get_shona("milk") == "mukaka"


def test_lookup_case_normalization(empty_manager: VocabularyManager):
    empty_manager.add("  Chikafu  ", " FOOD ")
    assert empty_manager.get_english("chikafu") == "food"
    assert empty_manager.get_english("CHIKAFU") == "food"
    assert empty_manager.get_shona("Food") == "chikafu"
    assert empty_manager.has_word("CHIKAFU") is True


def test_lookup_nonexistent_shona(empty_manager: VocabularyManager):
    with pytest.raises(WordNotFoundError, match="Shona word 'banga' not found"):
        empty_manager.get_english("banga")


def test_lookup_nonexistent_english(empty_manager: VocabularyManager):
    with pytest.raises(WordNotFoundError, match="No Shona word found for English meaning 'knife'"):
        empty_manager.get_shona("knife")


# ============================================================================
# 3. Update and Remove Tests
# ============================================================================


def test_update_entry(populated_manager: VocabularyManager):
    updated = populated_manager.update("mvura", "rainwater")
    assert updated.english == "rainwater"
    assert populated_manager.get_english("mvura") == "rainwater"


def test_update_nonexistent_entry(empty_manager: VocabularyManager):
    with pytest.raises(WordNotFoundError, match="Cannot update 'banga'"):
        empty_manager.update("banga", "knife")


def test_remove_entry(populated_manager: VocabularyManager):
    assert populated_manager.has_word("mvura") is True
    removed = populated_manager.remove("mvura")
    assert removed.shona == "mvura"
    assert populated_manager.has_word("mvura") is False

    with pytest.raises(WordNotFoundError):
        populated_manager.get_english("mvura")


def test_remove_nonexistent_entry(empty_manager: VocabularyManager):
    with pytest.raises(WordNotFoundError, match="Cannot remove 'banga'"):
        empty_manager.remove("banga")


# ============================================================================
# 4. Duplicate and Edge Validation Tests
# ============================================================================


def test_duplicate_add_fails(empty_manager: VocabularyManager):
    empty_manager.add("imba", "house")
    with pytest.raises(DuplicateWordError, match="Word 'imba' already exists"):
        empty_manager.add("IMBA", "building")


@pytest.mark.parametrize(
    "bad_input",
    ["", "   ", None, 42, []],
)
def test_manager_add_invalid_inputs(empty_manager: VocabularyManager, bad_input):
    with pytest.raises(ValidationError):
        empty_manager.add(bad_input, "valid_meaning")

    with pytest.raises(ValidationError):
        empty_manager.add("valid_shona", bad_input)


# ============================================================================
# 5. Collection and Counting Tests
# ============================================================================


def test_count_and_len(populated_manager: VocabularyManager):
    assert populated_manager.count() == 5
    assert len(populated_manager) == 5

    populated_manager.remove("imba")
    assert populated_manager.count() == 4
    assert len(populated_manager) == 4


def test_get_all_sorting(populated_manager: VocabularyManager):
    all_entries = populated_manager.get_all()
    shona_words = [e.shona for e in all_entries]
    assert shona_words == sorted(["mvura", "mukaka", "chikafu", "imba", "munhu"])


def test_contains_operator(populated_manager: VocabularyManager):
    assert "chikafu" in populated_manager
    assert "CHIKAFU" in populated_manager
    assert "banga" not in populated_manager
    assert 123 not in populated_manager  # Returns False on invalid type without crashing


# ============================================================================
# 6. Persistence Tests
# ============================================================================


def test_save_and_load_roundtrip(populated_manager: VocabularyManager, tmp_path: Path):
    file_path = tmp_path / "vocab.json"
    populated_manager.save_to_file(file_path)
    assert file_path.exists()

    new_manager = VocabularyManager()
    new_manager.load_from_file(file_path)

    assert len(new_manager) == 5
    assert new_manager.get_english("mvura") == "water"
    assert new_manager.get_english("mukaka") == "milk"
    assert new_manager.get_shona("person") == "munhu"


def test_load_nonexistent_file(tmp_path: Path):
    storage = JsonVocabularyStorage()
    nonexistent = tmp_path / "missing.json"

    with pytest.raises(StorageFileNotFoundError, match="Vocabulary file not found"):
        storage.load(nonexistent)

    manager = VocabularyManager()
    with pytest.raises(StorageFileNotFoundError):
        manager.load_from_file(nonexistent)


def test_load_malformed_json(tmp_path: Path):
    bad_file = tmp_path / "corrupt.json"
    bad_file.write_text("{ this is not valid json : [", encoding="utf-8")

    manager = VocabularyManager()
    with pytest.raises(StorageError, match="Malformed JSON"):
        manager.load_from_file(bad_file)


def test_load_invalid_schema(tmp_path: Path):
    invalid_schema_file = tmp_path / "bad_schema.json"
    invalid_schema_file.write_text('{"unrelated_key": 123}', encoding="utf-8")

    manager = VocabularyManager()
    with pytest.raises(StorageError, match="Invalid vocabulary file schema"):
        manager.load_from_file(invalid_schema_file)


def test_atomic_save_protects_existing_file_on_failure(populated_manager: VocabularyManager, tmp_path: Path):
    file_path = tmp_path / "safe.json"
    populated_manager.save_to_file(file_path)
    original_content = file_path.read_text(encoding="utf-8")

    # Inject an invalid non-serializable object into storage to simulate write failure
    storage = JsonVocabularyStorage()
    corrupt_entry = VocabularyEntry("banga", "knife")
    # Force an object that cannot serialize
    object.__setattr__(corrupt_entry, "shona", object())

    with pytest.raises(StorageError):
        storage.save([corrupt_entry], file_path)

    # Confirm original file content remains intact and uncorrupted
    assert file_path.read_text(encoding="utf-8") == original_content