"""Representation of an individual vocabulary entry."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from rocky.language.exceptions import ValidationError


@dataclass(frozen=True)
class VocabularyEntry:
    """Represents an association between a Shona word and its English meaning.

    Attributes:
        shona: The normalized Shona word.
        english: The primary English meaning.

    Note:
        Current version (Rocky 0.1) supports one primary English meaning
        per Shona word. Future milestones will extend this to multiple meanings,
        grammatical tags, and context examples without altering this base model.
    """

    shona: str
    english: str

    def __post_init__(self) -> None:
        """Validate input types and values upon instantiation."""
        if not isinstance(self.shona, str):
            raise ValidationError(
                f"Shona word must be a string, received {type(self.shona).__name__}."
            )
        if not isinstance(self.english, str):
            raise ValidationError(
                f"English meaning must be a string, received {type(self.english).__name__}."
            )

        cleaned_shona = self.shona.strip().lower()
        cleaned_english = self.english.strip().lower()

        if not cleaned_shona:
            raise ValidationError("Shona word cannot be empty or blank.")
        if not cleaned_english:
            raise ValidationError("English meaning cannot be empty or blank.")

        # Bypass frozen dataclass immutability to store cleaned, normalized strings
        object.__setattr__(self, "shona", cleaned_shona)
        object.__setattr__(self, "english", cleaned_english)

    def to_dict(self) -> dict[str, str]:
        """Serialize the entry to a dictionary."""
        return {
            "shona": self.shona,
            "english": self.english,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VocabularyEntry:
        """Create a VocabularyEntry instance from a dictionary.

        Args:
            data: Dictionary containing 'shona' and 'english' keys.

        Raises:
            ValidationError: If required keys are missing or values are invalid.
        """
        if not isinstance(data, dict):
            raise ValidationError(
                f"Entry data must be a dictionary, received {type(data).__name__}."
            )
        if "shona" not in data or "english" not in data:
            raise ValidationError(
                "Entry dictionary must contain both 'shona' and 'english' keys."
            )
        return cls(shona=data["shona"], english=data["english"])