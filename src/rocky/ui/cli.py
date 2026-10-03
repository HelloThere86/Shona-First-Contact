"""Interactive terminal user interface for Rocky vocabulary management."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Callable

from rocky.language import (
    DuplicateWordError,
    StorageError,
    StorageFileNotFoundError,
    ValidationError,
    VocabularyManager,
    WordNotFoundError,
)

DEFAULT_STORAGE_PATH = Path("data/vocabulary.json")


class VocabularyCLI:
    """Command-line interface for managing Shona-English vocabulary."""

    def __init__(
        self,
        manager: VocabularyManager | None = None,
        storage_path: Path | str | None = DEFAULT_STORAGE_PATH,
        input_func: Callable[[str], str] = input,
        output_func: Callable[[str], None] = print,
    ) -> None:
        """Initialize the CLI interface.

        Args:
            manager: Existing VocabularyManager instance or None.
            storage_path: Default file path for saving and loading vocabulary.
            input_func: Callable for reading user input (defaults to built-in input).
            output_func: Callable for writing messages (defaults to built-in print).
        """
        self.manager = manager or VocabularyManager()
        self.storage_path = Path(storage_path) if storage_path else None
        self._input = input_func
        self._output = output_func
        self._running = False

    def display_welcome(self) -> None:
        """Print application header and startup details."""
        self._output("========================================")
        self._output("  Rocky: Shona-English Vocabulary CLI   ")
        self._output("========================================")

    def display_menu(self) -> None:
        """Display the main numbered menu."""
        self._output("")
        self._output("Menu:")
        self._output("  1. Add word pair")
        self._output("  2. Search Shona to English")
        self._output("  3. Search English to Shona")
        self._output("  4. Update word meaning")
        self._output("  5. Remove word")
        self._output("  6. List all vocabulary")
        self._output("  7. Total word count")
        self._output("  8. Save vocabulary to file")
        self._output("  9. Load vocabulary from file")
        self._output(" 10. Exit")
        self._output("")

    def auto_load(self) -> None:
        """Load vocabulary from default storage path if the file exists."""
        if not self.storage_path:
            return

        if self.storage_path.exists():
            try:
                self.manager.load_from_file(self.storage_path)
                self._output(
                    f"Loaded {self.manager.count()} entries from '{self.storage_path}'."
                )
            except StorageError as exc:
                self._output(
                    f"Error loading vocabulary from '{self.storage_path}': {exc}"
                )
                self._output("Starting with an empty vocabulary.")
        else:
            self._output(
                f"No existing file found at '{self.storage_path}'. Starting with an empty vocabulary."
            )

    def handle_add(self) -> None:
        """Prompt user for a Shona-English word pair and add it to vocabulary."""
        shona = self._input("Enter Shona word: ").strip()
        if not shona:
            self._output("Error: Shona word cannot be empty.")
            return

        english = self._input("Enter English meaning: ").strip()
        if not english:
            self._output("Error: English meaning cannot be empty.")
            return

        try:
            entry = self.manager.add(shona, english)
            self._output(f"Added entry: '{entry.shona}' -> '{entry.english}'.")
        except DuplicateWordError:
            self._output(
                f"Error: Word '{shona.lower()}' already exists. Use update option to change it."
            )
        except ValidationError as exc:
            self._output(f"Validation error: {exc}")

    def handle_search_shona(self) -> None:
        """Look up the English translation of a Shona word."""
        shona = self._input("Enter Shona word to search: ").strip()
        if not shona:
            self._output("Error: Search query cannot be empty.")
            return

        try:
            english = self.manager.get_english(shona)
            self._output(f"Result: '{shona.lower()}' -> '{english}'")
        except WordNotFoundError:
            self._output(f"Word '{shona.lower()}' was not found in vocabulary.")
        except ValidationError as exc:
            self._output(f"Validation error: {exc}")

    def handle_search_english(self) -> None:
        """Look up the Shona word for a given English meaning."""
        english = self._input("Enter English meaning to search: ").strip()
        if not english:
            self._output("Error: Search query cannot be empty.")
            return

        try:
            shona = self.manager.get_shona(english)
            self._output(f"Result: '{english.lower()}' -> '{shona}'")
        except WordNotFoundError:
            self._output(f"No Shona word found for English meaning '{english.lower()}'.")
        except ValidationError as exc:
            self._output(f"Validation error: {exc}")

    def handle_update(self) -> None:
        """Prompt user to update the English translation of an existing Shona word."""
        shona = self._input("Enter Shona word to update: ").strip()
        if not shona:
            self._output("Error: Shona word cannot be empty.")
            return

        if not self.manager.has_word(shona):
            self._output(f"Word '{shona.lower()}' does not exist in vocabulary.")
            return

        english = self._input("Enter new English meaning: ").strip()
        if not english:
            self._output("Error: English meaning cannot be empty.")
            return

        try:
            entry = self.manager.update(shona, english)
            self._output(f"Updated entry: '{entry.shona}' -> '{entry.english}'.")
        except ValidationError as exc:
            self._output(f"Validation error: {exc}")

    def handle_remove(self) -> None:
        """Prompt user and confirm deletion of a word pair."""
        shona = self._input("Enter Shona word to remove: ").strip()
        if not shona:
            self._output("Error: Shona word cannot be empty.")
            return

        if not self.manager.has_word(shona):
            self._output(f"Word '{shona.lower()}' does not exist in vocabulary.")
            return

        confirm = self._input(
            f"Are you sure you want to remove '{shona.lower()}'? (y/n): "
        ).strip().lower()

        if confirm in ("y", "yes"):
            try:
                self.manager.remove(shona)
                self._output(f"Removed entry for '{shona.lower()}'.")
            except WordNotFoundError:
                self._output(f"Word '{shona.lower()}' not found.")
        else:
            self._output("Removal cancelled.")

    def handle_list_all(self) -> None:
        """Display all stored vocabulary in an organized table."""
        entries = self.manager.get_all()
        if not entries:
            self._output("Vocabulary is currently empty.")
            return

        max_shona_len = max(max(len(e.shona) for e in entries), 12)
        max_english_len = max(max(len(e.english) for e in entries), 15)

        header = f"{'Shona':<{max_shona_len}} | {'English':<{max_english_len}}"
        divider = "-" * len(header)

        self._output(f"\nStored Vocabulary ({len(entries)} total):")
        self._output(divider)
        self._output(header)
        self._output(divider)
        for entry in entries:
            self._output(f"{entry.shona:<{max_shona_len}} | {entry.english:<{max_english_len}}")
        self._output(divider)

    def handle_count(self) -> None:
        """Display the total number of entries in memory."""
        self._output(f"Total vocabulary entries: {self.manager.count()}")

    def handle_save(self) -> None:
        """Save the in-memory vocabulary to a specified JSON file."""
        default_str = str(self.storage_path) if self.storage_path else "data/vocabulary.json"
        target_input = self._input(f"Enter save file path [default: {default_str}]: ").strip()
        save_path = Path(target_input) if target_input else Path(default_str)

        try:
            self.manager.save_to_file(save_path)
            self._output(
                f"Successfully saved {self.manager.count()} entries to '{save_path}'."
            )
            self.storage_path = save_path
        except StorageError as exc:
            self._output(f"Failed to save vocabulary: {exc}")

    def handle_load(self) -> None:
        """Load vocabulary from a specified JSON file."""
        default_str = str(self.storage_path) if self.storage_path else "data/vocabulary.json"
        target_input = self._input(f"Enter load file path [default: {default_str}]: ").strip()
        load_path = Path(target_input) if target_input else Path(default_str)

        try:
            self.manager.load_from_file(load_path)
            self._output(
                f"Successfully loaded {self.manager.count()} entries from '{load_path}'."
            )
            self.storage_path = load_path
        except StorageFileNotFoundError:
            self._output(f"Error: File not found at '{load_path}'.")
        except StorageError as exc:
            self._output(f"Failed to load vocabulary: {exc}")

    def run(self) -> None:
        """Run the main interactive CLI loop."""
        self.display_welcome()
        self.auto_load()
        self._running = True

        actions = {
            "1": self.handle_add,
            "2": self.handle_search_shona,
            "3": self.handle_search_english,
            "4": self.handle_update,
            "5": self.handle_remove,
            "6": self.handle_list_all,
            "7": self.handle_count,
            "8": self.handle_save,
            "9": self.handle_load,
        }

        while self._running:
            self.display_menu()
            try:
                choice = self._input("Select an option (1-10): ").strip()
            except (KeyboardInterrupt, EOFError):
                self._output("\nSession interrupted. Exiting gracefully. Goodbye.")
                break

            if choice == "10":
                self._output("Exiting Rocky Vocabulary CLI. Goodbye.")
                self._running = False
            elif choice in actions:
                try:
                    actions[choice]()
                except (KeyboardInterrupt, EOFError):
                    self._output("\nOperation cancelled by user.")
                except Exception as exc:
                    self._output(f"An unexpected error occurred: {exc}")
            elif not choice:
                self._output("Error: Please enter a choice between 1 and 10.")
            else:
                self._output(f"Invalid option '{choice}'. Please select a number from 1 to 10.")


def main(argv: list[str] | None = None) -> int:
    """Parse CLI arguments and start the interactive terminal session."""
    parser = argparse.ArgumentParser(
        description="Rocky 0.2: Interactive Shona-English Vocabulary CLI"
    )
    parser.add_argument(
        "-f",
        "--file",
        type=Path,
        default=DEFAULT_STORAGE_PATH,
        help="Path to default vocabulary JSON file (default: data/vocabulary.json)",
    )
    args = parser.parse_args(argv)

    cli = VocabularyCLI(storage_path=args.file)
    cli.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())