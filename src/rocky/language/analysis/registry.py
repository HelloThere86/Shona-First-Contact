"""Registry for storing, looking up, and validating Bantu noun-class definitions."""

from __future__ import annotations

from typing import Iterator

from rocky.language.analysis.models import NounClass
from rocky.language.exceptions import DuplicateNounClassError, InvalidNounClassError


class NounClassRegistry:
    """In-memory registry of documented noun classes."""

    def __init__(self) -> None:
        self._classes: dict[str, NounClass] = {}

    def register(self, noun_class: NounClass) -> None:
        """Register a new noun class.

        Args:
            noun_class: NounClass instance to register.

        Raises:
            InvalidNounClassError: If input is not a NounClass instance.
            DuplicateNounClassError: If a class with the same identifier is already registered.
        """
        if not isinstance(noun_class, NounClass):
            raise InvalidNounClassError(
                f"Expected NounClass instance, received {type(noun_class).__name__}."
            )

        if noun_class.identifier in self._classes:
            raise DuplicateNounClassError(
                f"Noun class '{noun_class.identifier}' is already registered."
            )

        self._classes[noun_class.identifier] = noun_class

    def get(self, identifier: str) -> NounClass | None:
        """Look up a noun class by identifier."""
        if not isinstance(identifier, str):
            return None
        return self._classes.get(identifier.strip())

    def get_or_raise(self, identifier: str) -> NounClass:
        """Look up a noun class or raise an exception if missing."""
        result = self.get(identifier)
        if result is None:
            raise InvalidNounClassError(f"Noun class '{identifier}' not found in registry.")
        return result

    def get_paired_class(self, identifier: str) -> NounClass | None:
        """Retrieve the paired singular or plural class for a given class."""
        target_class = self.get(identifier)
        if target_class is None or not target_class.paired_class_id:
            return None
        return self.get(target_class.paired_class_id)

    def has_class(self, identifier: str) -> bool:
        """Check if a noun class identifier exists in the registry."""
        return self.get(identifier) is not None

    def list_classes(self) -> list[NounClass]:
        """Return all registered noun classes."""
        return list(self._classes.values())

    def count(self) -> int:
        """Return total number of registered noun classes."""
        return len(self._classes)

    def validate(self) -> list[str]:
        """Check for integrity issues, such as broken paired class references."""
        issues: list[str] = []
        for cls in self._classes.values():
            if cls.paired_class_id and cls.paired_class_id not in self._classes:
                issues.append(
                    f"Class '{cls.identifier}' references non-existent paired class '{cls.paired_class_id}'."
                )
        return issues

    def __len__(self) -> int:
        return self.count()

    def __contains__(self, identifier: str) -> bool:
        return self.has_class(identifier)

    def __iter__(self) -> Iterator[NounClass]:
        return iter(self.list_classes())