"""Registry for storing, querying, and validating Shona concord records."""

from __future__ import annotations

from typing import Iterator

from rocky.language.analysis.concord_models import ConcordCategory, ConcordRecord
from rocky.language.analysis.registry import NounClassRegistry
from rocky.language.exceptions import (
    DuplicateConcordError,
    InvalidConcordError,
    UnsupportedCategoryError,
)


class ConcordRegistry:
    """In-memory registry of documented concord agreement records."""

    def __init__(self) -> None:
        # Key: (noun_class_id, category) -> ConcordRecord
        self._records: dict[tuple[str, ConcordCategory], ConcordRecord] = {}

    def register(self, record: ConcordRecord) -> None:
        """Register a new concord record.

        Args:
            record: ConcordRecord instance to register.

        Raises:
            InvalidConcordError: If input is not a ConcordRecord.
            DuplicateConcordError: If a record for this class and category already exists.
        """
        if not isinstance(record, ConcordRecord):
            raise InvalidConcordError(
                f"Expected ConcordRecord instance, received {type(record).__name__}."
            )

        key = (record.noun_class_id, record.category)
        if key in self._records:
            raise DuplicateConcordError(
                f"Concord record for Class '{record.noun_class_id}' in category "
                f"'{record.category.value}' is already registered."
            )

        self._records[key] = record

    def get(self, noun_class_id: str, category: ConcordCategory) -> ConcordRecord | None:
        """Retrieve a concord record by noun class ID and category."""
        if not isinstance(noun_class_id, str):
            return None
        if not isinstance(category, ConcordCategory):
            return None
        return self._records.get((noun_class_id.strip(), category))

    def get_or_raise(self, noun_class_id: str, category: ConcordCategory) -> ConcordRecord:
        """Retrieve a concord record or raise InvalidConcordError if not found."""
        if not isinstance(category, ConcordCategory):
            raise UnsupportedCategoryError(
                f"Unsupported concord category: {category}."
            )
        record = self.get(noun_class_id, category)
        if record is None:
            raise InvalidConcordError(
                f"No concord record found for Class '{noun_class_id}' and category '{category.value}'."
            )
        return record

    def has_concord(self, noun_class_id: str, category: ConcordCategory) -> bool:
        """Check whether a concord record exists for a class and category."""
        return self.get(noun_class_id, category) is not None

    def list_records(self) -> list[ConcordRecord]:
        """Return all registered concord records."""
        return list(self._records.values())

    def count(self) -> int:
        """Return total number of registered concord records."""
        return len(self._records)

    def validate(self, class_registry: NounClassRegistry) -> list[str]:
        """Validate that all registered concord records reference known noun classes."""
        issues: list[str] = []
        for (class_id, category), record in self._records.items():
            if not class_registry.has_class(class_id):
                issues.append(
                    f"Concord record for category '{category.value}' references "
                    f"unregistered noun class '{class_id}'."
                )
        return issues

    def __len__(self) -> int:
        return self.count()

    def __iter__(self) -> Iterator[ConcordRecord]:
        return iter(self.list_records())