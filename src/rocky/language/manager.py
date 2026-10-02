"""Management operations for Shona-English vocabulary."""

from __future__ import annotations

from pathlib import Path
from typing import Iterator

from rocky.language.entry import VocabularyEntry
from rocky.language.exceptions import (
    DuplicateWordError,
    ValidationError,
    WordNotFoundError,
)
from rocky.language.storage import JsonVocabularyStorage


class VocabularyManager:
    """Manages storage, retrieval, and modification of Shona-English vocabulary."""

    def __init__(self, storage: JsonVocabularyStorage | None = None) -> None:
        """Initialize the vocabulary manager.

        Args:
            storage: Optional persistence handler. Defaults to JsonVocabularyStorage.
        """
        self._storage = storage or JsonVocabularyStorage()
        # Primary lookup table: normalized Shona word -> VocabularyEntry
        self._entries: dict[str, VocabularyEntry] = {}

    @staticmethod
    def _normalize(text: str, field_name: str) -> str:
        """Normalize a string input and ensure it is non-empty.

        Args:
            text: Input text to normalize.
            field_name: Name of the field for error reporting.

        Raises:
            ValidationError: If input is not a string or is empty/whitespace.
        """
        if not isinstance(text, str):
            raise ValidationError(
                f"{field_name} must be a string, received {type(text).__name__}."
            )
        cleaned = text.strip().lower()
        if not cleaned:
            raise ValidationError(f"{field_name} cannot be empty or blank.")
        return cleaned

    def add(self, shona: str, english: str) -> VocabularyEntry:
        """Add a new Shona-English vocabulary entry.

        Args:
            shona: The Shona word.
            english: The primary English meaning.

        Returns:
            The created VocabularyEntry.

        Raises:
            ValidationError: If word or meaning is invalid/empty.
            DuplicateWordError: If the Shona word already exists.
        """
        norm_shona = self._normalize(shona, "Shona word")
        norm_english = self._normalize(english, "English meaning")

        if norm_shona in self._entries:
            raise DuplicateWordError(
                f"Word '{norm_shona}' already exists in vocabulary. Use update() to alter its meaning."
            )

        entry = VocabularyEntry(shona=norm_shona, english=norm_english)
        self._entries[norm_shona] = entry
        return entry

    def get_english(self, shona: str) -> str:
        """Retrieve the English meaning of a Shona word.

        Args:
            shona: The Shona word to look up.

        Returns:
            The English meaning.

        Raises:
            ValidationError: If input is invalid.
            WordNotFoundError: If the Shona word is not found.
        """
        return self.get_entry(shona).english

    def get_shona(self, english: str) -> str:
        """Retrieve the Shona word associated with an English meaning.

        Args:
            english: The English meaning to look up.

        Returns:
            The corresponding Shona word.

        Raises:
            ValidationError: If input is invalid.
            WordNotFoundError: If no entry matching the English meaning is found.

        Note:
            If multiple Shona words share an English meaning, this returns the first
            matching word. Future versions will support multi-word lookup mappings.
        """
        norm_english = self._normalize(english, "English meaning")
        for entry in self._entries.values():
            if entry.english == norm_english:
                return entry.shona

        raise WordNotFoundError(
            f"No Shona word found for English meaning '{norm_english}'."
        )

    def get_entry(self, shona: str) -> VocabularyEntry:
        """Retrieve the full entry object for a given Shona word.

        Args:
            shona: The Shona word to look up.

        Raises:
            ValidationError: If input is invalid.
            WordNotFoundError: If the Shona word is not found.
        """
        norm_shona = self._normalize(shona, "Shona word")
        if norm_shona not in self._entries:
            raise WordNotFoundError(f"Shona word '{norm_shona}' not found in vocabulary.")
        return self._entries[norm_shona]

    def update(self, shona: str, english: str) -> VocabularyEntry:
        """Update the English meaning of an existing Shona word.

        Args:
            shona: The Shona word to update.
            english: The new English meaning.

        Returns:
            The updated VocabularyEntry.

        Raises:
            ValidationError: If inputs are invalid.
            WordNotFoundError: If the Shona word does not exist.
        """
        norm_shona = self._normalize(shona, "Shona word")
        norm_english = self._normalize(english, "English meaning")

        if norm_shona not in self._entries:
            raise WordNotFoundError(
                f"Cannot update '{norm_shona}': word does not exist in vocabulary."
            )

        updated_entry = VocabularyEntry(shona=norm_shona, english=norm_english)
        self._entries[norm_shona] = updated_entry
        return updated_entry

    def remove(self, shona: str) -> VocabularyEntry:
        """Remove a Shona word from vocabulary.

        Args:
            shona: The Shona word to remove.

        Returns:
            The removed VocabularyEntry.

        Raises:
            ValidationError: If input is invalid.
            WordNotFoundError: If the Shona word does not exist.
        """
        norm_shona = self._normalize(shona, "Shona word")
        if norm_shona not in self._entries:
            raise WordNotFoundError(
                f"Cannot remove '{norm_shona}': word does not exist in vocabulary."
            )
        return self._entries.pop(norm_shona)

    def has_word(self, shona: str) -> bool:
        """Check whether a Shona word exists in the vocabulary.

        Args:
            shona: The Shona word to check.

        Returns:
            True if word exists, False otherwise.
        """
        try:
            norm_shona = self._normalize(shona, "Shona word")
        except ValidationError:
            return False
        return norm_shona in self._entries

    def get_all(self) -> list[VocabularyEntry]:
        """Return all stored vocabulary entries sorted alphabetically by Shona word."""
        return sorted(self._entries.values(), key=lambda entry: entry.shona)

    def count(self) -> int:
        """Return total count of stored vocabulary entries."""
        return len(self._entries)

    def save_to_file(self, file_path: str | Path) -> None:
        """Persist current vocabulary entries to a JSON file.

        Args:
            file_path: Destination path.

        Raises:
            StorageError: If writing to the file fails.
        """
        self._storage.save(list(self._entries.values()), file_path)

    def load_from_file(self, file_path: str | Path, clear_existing: bool = True) -> None:
        """Load vocabulary entries from a JSON file.

        Args:
            file_path: Path to the JSON file.
            clear_existing: If True (default), replaces current in-memory entries.
                           If False, merges entries from file (conflicts raise DuplicateWordError).

        Raises:
            StorageFileNotFoundError: If the file is not found.
            StorageError: If parsing or loading fails.
            DuplicateWordError: If clear_existing is False and incoming keys collide.
        """
        loaded = self._storage.load(file_path)

        if clear_existing:
            new_entries: dict[str, VocabularyEntry] = {}
            for entry in loaded:
                new_entries[entry.shona] = entry
            self._entries = new_entries
        else:
            for entry in loaded:
                if entry.shona in self._entries:
                    raise DuplicateWordError(
                        f"Conflict while loading: '{entry.shona}' already exists."
                    )
                self._entries[entry.shona] = entry

    def __len__(self) -> int:
        """Return total count of entries."""
        return self.count()

    def __contains__(self, shona: str) -> bool:
        """Support `shona_word in manager` syntax."""
        return self.has_word(shona)

    def __iter__(self) -> Iterator[VocabularyEntry]:
        """Iterate over all stored vocabulary entries."""
        return iter(self.get_all())