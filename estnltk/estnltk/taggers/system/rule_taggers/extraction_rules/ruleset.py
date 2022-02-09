from typing import List, Union

from estnltk.taggers.system.rule_taggers.extraction_rules.ambiguous_ruleset import AmbiguousRuleset, ExtractionRule


class Ruleset(AmbiguousRuleset):

    def __init__(self, rules: List[ExtractionRule] = ()):
        super().__init__(rules)

        if not self.is_valid:
            raise ValueError("Two rules in ruleset give a conflicting attribute definition for the same pattern but "
                             "ambiguous ruleset is not allowed.")

    def add_rules(self, rules: List[ExtractionRule]):

        super().add_rules(rules)

        if not self.is_valid:
            raise ValueError("Two rules in ruleset give a conflicting attribute definition for the same pattern but "
                             "ambiguous ruleset is not allowed.")

    def load(self, file_name: str, key_column: Union[str, int] = 0, group_column: Union[str, int] = None,
             priority_column: Union[str, int] = None, mode: str = 'overwrite', **kwargs) -> None:
        super().load(file_name, key_column, group_column, priority_column, mode, **kwargs)

        if not self.is_valid:
            raise ValueError("Two rules in ruleset give a conflicting attribute definition for the same pattern but "
                             "ambiguous ruleset is not allowed.")

    @property
    def is_valid(self):
        """
        Returns true if the ruleset does not contain conflicting attribute definitions for the same pattern.
        That is, two rules of the same type cannot have the same left-hand-side.
        """

        patterns = set()
        for rule in self.static_rules:
            if rule.pattern in patterns:
                return False
            patterns.add(rule.pattern)

        patterns = set()
        for rule in self.dynamic_rules:
            if rule.pattern in patterns:
                return False
            patterns.add(rule.pattern)

        return True
