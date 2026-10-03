"""Automated tests for Rocky 0.2 Interactive Vocabulary CLI."""

from pathlib import Path
from typing import Iterator
import pytest

from rocky.language import VocabularyManager
from rocky.ui.cli import VocabularyCLI


class MockIO:
    """Helper to mock sequential user input and record CLI terminal outputs."""

    def __init__(self, inputs: list[str]) -> None:
        self._inputs: Iterator[str] = iter(inputs)
        self.outputs: list[str] = []

    def mock_input(self, prompt: str = "") -> str:
        try:
            return next(self._inputs)
        except StopIteration:
            raise EOFError("Mock input stream exhausted.")

    def mock_output(self, message: str = "") -> None:
        self.outputs.append(str(message))

    def get_output_text(self) -> str:
        return "\n".join(self.outputs)


def test_cli_graceful_exit():
    mock_io = MockIO(["10"])
    cli = VocabularyCLI(
        storage_path=None,
        input_func=mock_io.mock_input,
        output_func=mock_io.mock_output,
    )
    cli.run()
    output = mock_io.get_output_text()
    assert "Rocky: Shona-English Vocabulary CLI" in output
    assert "Exiting Rocky Vocabulary CLI. Goodbye." in output


def test_cli_invalid_menu_choice_and_empty_input():
    mock_io = MockIO(["", "99", "abc", "10"])
    cli = VocabularyCLI(
        storage_path=None,
        input_func=mock_io.mock_input,
        output_func=mock_io.mock_output,
    )
    cli.run()
    output = mock_io.get_output_text()
    assert "Error: Please enter a choice between 1 and 10." in output
    assert "Invalid option '99'." in output
    assert "Invalid option 'abc'." in output


def test_cli_add_entry_success_and_duplicate():
    mock_io = MockIO([
        "1", "mvura", "water",         # Add entry
        "1", "MVURA", "rainwater",     # Duplicate attempt
        "10",                          # Exit
    ])
    cli = VocabularyCLI(
        storage_path=None,
        input_func=mock_io.mock_input,
        output_func=mock_io.mock_output,
    )
    cli.run()
    output = mock_io.get_output_text()
    assert "Added entry: 'mvura' -> 'water'." in output
    assert "Word 'mvura' already exists" in output
    assert cli.manager.count() == 1


def test_cli_add_empty_inputs():
    mock_io = MockIO([
        "1", "",                       # Empty Shona
        "1", "mukaka", "",             # Empty English
        "10",
    ])
    cli = VocabularyCLI(
        storage_path=None,
        input_func=mock_io.mock_input,
        output_func=mock_io.mock_output,
    )
    cli.run()
    output = mock_io.get_output_text()
    assert "Error: Shona word cannot be empty." in output
    assert "Error: English meaning cannot be empty." in output
    assert cli.manager.count() == 0


def test_cli_search_bidirectional():
    manager = VocabularyManager()
    manager.add("mukaka", "milk")

    mock_io = MockIO([
        "2", "mukaka",                 # Shona -> English found
        "2", "banga",                  # Shona -> English not found
        "3", "milk",                   # English -> Shona found
        "3", "knife",                  # English -> Shona not found
        "10",
    ])
    cli = VocabularyCLI(
        manager=manager,
        storage_path=None,
        input_func=mock_io.mock_input,
        output_func=mock_io.mock_output,
    )
    cli.run()
    output = mock_io.get_output_text()
    assert "Result: 'mukaka' -> 'milk'" in output
    assert "Word 'banga' was not found" in output
    assert "Result: 'milk' -> 'mukaka'" in output
    assert "No Shona word found for English meaning 'knife'" in output


def test_cli_update_entry():
    manager = VocabularyManager()
    manager.add("chikafu", "food")

    mock_io = MockIO([
        "4", "chikafu", "nourishment",  # Valid update
        "4", "banga",                   # Nonexistent update
        "10",
    ])
    cli = VocabularyCLI(
        manager=manager,
        storage_path=None,
        input_func=mock_io.mock_input,
        output_func=mock_io.mock_output,
    )
    cli.run()
    output = mock_io.get_output_text()
    assert "Updated entry: 'chikafu' -> 'nourishment'." in output
    assert "Word 'banga' does not exist in vocabulary." in output
    assert manager.get_english("chikafu") == "nourishment"


def test_cli_remove_entry_confirmation():
    manager = VocabularyManager()
    manager.add("imba", "house")
    manager.add("munhu", "person")

    mock_io = MockIO([
        "5", "imba", "n",               # Cancel removal
        "5", "imba", "y",               # Confirm removal
        "5", "nonexistent",             # Remove missing
        "10",
    ])
    cli = VocabularyCLI(
        manager=manager,
        storage_path=None,
        input_func=mock_io.mock_input,
        output_func=mock_io.mock_output,
    )
    cli.run()
    output = mock_io.get_output_text()
    assert "Removal cancelled." in output
    assert "Removed entry for 'imba'." in output
    assert "Word 'nonexistent' does not exist in vocabulary." in output
    assert not manager.has_word("imba")
    assert manager.has_word("munhu")


def test_cli_list_all_and_count():
    manager = VocabularyManager()
    mock_io = MockIO([
        "6",                            # List when empty
        "7",                            # Count when empty
        "1", "mvura", "water",
        "6",                            # List populated
        "7",                            # Count populated
        "10",
    ])
    cli = VocabularyCLI(
        manager=manager,
        storage_path=None,
        input_func=mock_io.mock_input,
        output_func=mock_io.mock_output,
    )
    cli.run()
    output = mock_io.get_output_text()
    assert "Vocabulary is currently empty." in output
    assert "Total vocabulary entries: 0" in output
    assert "Stored Vocabulary (1 total):" in output
    assert "mvura" in output and "water" in output
    assert "Total vocabulary entries: 1" in output


def test_cli_save_and_load(tmp_path: Path):
    target_file = tmp_path / "vocab_cli.json"

    # Session 1: Add and save
    mock_io_1 = MockIO([
        "1", "chikafu", "food",
        "8", str(target_file),          # Save to path
        "10",
    ])
    cli_1 = VocabularyCLI(
        storage_path=target_file,
        input_func=mock_io_1.mock_input,
        output_func=mock_io_1.mock_output,
    )
    cli_1.run()
    assert target_file.exists()

    # Session 2: Fresh CLI loading saved file
    mock_io_2 = MockIO([
        "7",                            # Check count from auto_load
        "10",
    ])
    cli_2 = VocabularyCLI(
        storage_path=target_file,
        input_func=mock_io_2.mock_input,
        output_func=mock_io_2.mock_output,
    )
    cli_2.run()
    output_2 = mock_io_2.get_output_text()
    assert f"Loaded 1 entries from '{target_file}'." in output_2
    assert "Total vocabulary entries: 1" in output_2


def test_cli_load_nonexistent_and_corrupt(tmp_path: Path):
    missing_file = tmp_path / "does_not_exist.json"
    corrupt_file = tmp_path / "corrupt.json"
    corrupt_file.write_text("invalid json content", encoding="utf-8")

    mock_io = MockIO([
        "9", str(missing_file),         # Attempt loading missing
        "9", str(corrupt_file),         # Attempt loading corrupt
        "10",
    ])
    cli = VocabularyCLI(
        storage_path=None,
        input_func=mock_io.mock_input,
        output_func=mock_io.mock_output,
    )
    cli.run()
    output = mock_io.get_output_text()
    assert f"Error: File not found at '{missing_file}'." in output
    assert "Failed to load vocabulary: Malformed JSON" in output


def test_cli_interrupt_handling():
    def interrupting_input(_prompt: str = "") -> str:
        raise KeyboardInterrupt()

    outputs = []
    cli = VocabularyCLI(
        storage_path=None,
        input_func=interrupting_input,
        output_func=lambda msg: outputs.append(str(msg)),
    )
    cli.run()
    assert any("Session interrupted. Exiting gracefully." in m for m in outputs)