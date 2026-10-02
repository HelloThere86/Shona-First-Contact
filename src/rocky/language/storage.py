"""JSON-based persistence handler for vocabulary entries."""

from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
from typing import Iterable, Sequence

from rocky.language.entry import VocabularyEntry
from rocky.language.exceptions import (
    StorageError,
    StorageFileNotFoundError,
    ValidationError,
)

STORAGE_FORMAT_VERSION = "1.0"


class JsonVocabularyStorage:
    """Handles reading and writing vocabulary entries to and from JSON files.

    Provides atomic file writing to prevent data corruption during write failures.
    """

    def save(self, entries: Sequence[VocabularyEntry], file_path: str | Path) -> None:
        """Save a collection of vocabulary entries to a JSON file atomically.

        Args:
            entries: Sequence of VocabularyEntry instances to persist.
            file_path: Destination path for the JSON file.

        Raises:
            StorageError: If directory creation fails, disk write fails, or serialization fails.
        """
        target_path = Path(file_path).resolve()
        target_dir = target_path.parent

        try:
            target_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise StorageError(
                f"Failed to create directory '{target_dir}': {exc}"
            ) from exc

        payload = {
            "version": STORAGE_FORMAT_VERSION,
            "count": len(entries),
            "entries": [entry.to_dict() for entry in entries],
        }

        # Write to a temporary file in the same filesystem directory, then rename atomically
        temp_file = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=target_dir,
                delete=False,
                prefix=".tmp_vocab_",
            ) as temp_file:
                json.dump(payload, temp_file, indent=2, ensure_ascii=False)
                temp_file.flush()
                os.fsync(temp_file.fileno())

            # Atomic rename (POSIX rename / Windows replace)
            os.replace(temp_file.name, target_path)

        except (OSError, TypeError) as exc:
            if temp_file and os.path.exists(temp_file.name):
                try:
                    os.unlink(temp_file.name)
                except OSError:
                    pass
            raise StorageError(
                f"Failed to save vocabulary to '{target_path}': {exc}"
            ) from exc

    def load(self, file_path: str | Path) -> list[VocabularyEntry]:
        """Load vocabulary entries from a JSON file.

        Args:
            file_path: Path to the JSON file to read.

        Returns:
            A list of validated VocabularyEntry instances.

        Raises:
            StorageFileNotFoundError: If the target file does not exist.
            StorageError: If the JSON is malformed or structure is invalid.
        """
        target_path = Path(file_path).resolve()

        if not target_path.exists():
            raise StorageFileNotFoundError(
                f"Vocabulary file not found: '{target_path}'"
            )

        if not target_path.is_file():
            raise StorageError(
                f"Specified path is not a file: '{target_path}'"
            )

        try:
            with open(target_path, "r", encoding="utf-8") as f:
                content = json.load(f)
        except json.JSONDecodeError as exc:
            raise StorageError(
                f"Malformed JSON in vocabulary file '{target_path}': {exc}"
            ) from exc
        except OSError as exc:
            raise StorageError(
                f"Failed to read vocabulary file '{target_path}': {exc}"
            ) from exc

        raw_entries: list[dict]
        if isinstance(content, dict):
            if "entries" not in content or not isinstance(content["entries"], list):
                raise StorageError(
                    f"Invalid vocabulary file schema in '{target_path}': missing 'entries' list."
                )
            raw_entries = content["entries"]
        elif isinstance(content, list):
            # Backward-compatible fallback for flat lists of entry dicts
            raw_entries = content
        else:
            raise StorageError(
                f"Invalid vocabulary file structure in '{target_path}': expected object or list."
            )

        loaded_entries: list[VocabularyEntry] = []
        for index, item in enumerate(raw_entries):
            try:
                loaded_entries.append(VocabularyEntry.from_dict(item))
            except ValidationError as exc:
                raise StorageError(
                    f"Corrupt entry at index {index} in '{target_path}': {exc}"
                ) from exc

        return loaded_entries