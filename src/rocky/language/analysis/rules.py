"""Registry for managing morphological prefix transformation rules."""

from __future__ import annotations

from typing import Iterator

from rocky.language.analysis.models import MorphologicalRule
from rocky.language.exceptions import DuplicateRuleError, InvalidRuleError


class RuleRegistry:
    """In-memory registry of documented morphological transformation rules."""

    def __init__(self) -> None:
        self._rules: dict[str, MorphologicalRule] = {}

    def register(self, rule: MorphologicalRule) -> None:
        """Register a morphological rule.

        Args:
            rule: MorphologicalRule instance to register.

        Raises:
            InvalidRuleError: If input is not a MorphologicalRule.
            DuplicateRuleError: If rule ID is already registered.
        """
        if not isinstance(rule, MorphologicalRule):
            raise InvalidRuleError(
                f"Expected MorphologicalRule instance, received {type(rule).__name__}."
            )

        if rule.rule_id in self._rules:
            raise DuplicateRuleError(f"Morphological rule '{rule.rule_id}' is already registered.")

        self._rules[rule.rule_id] = rule

    def get(self, rule_id: str) -> MorphologicalRule | None:
        """Look up a rule by identifier."""
        if not isinstance(rule_id, str):
            return None
        return self._rules.get(rule_id.strip())

    def get_or_raise(self, rule_id: str) -> MorphologicalRule:
        """Look up a rule by identifier or raise InvalidRuleError."""
        result = self.get(rule_id)
        if result is None:
            raise InvalidRuleError(f"Morphological rule '{rule_id}' not found in registry.")
        return result

    def find_matching_rules(self, word: str) -> list[MorphologicalRule]:
        """Find all registered rules whose prefix condition matches the word."""
        return [rule for rule in self._rules.values() if rule.can_apply(word)]

    def list_rules(self) -> list[MorphologicalRule]:
        """Return all registered morphological rules."""
        return list(self._rules.values())

    def count(self) -> int:
        """Return total count of registered rules."""
        return len(self._rules)

    def __len__(self) -> int:
        return self.count()

    def __iter__(self) -> Iterator[MorphologicalRule]:
        return iter(self.list_rules())