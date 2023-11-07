from typing import List
from regex_library.regex_element import RegexElement
from regex_library.string_list  import StringList


class ChoiceGroup(RegexElement):
    """
    A `RegexElement` meant for defining a choice between the list of sub-expressions.

    The order of sub-expressions matters as in the standard choice group.
    It does not guarantee that the match corresponds to the subpattern with the longest match.

    TODO: Add automatic test generation
    TODO: Add extra checks for string lists. Then it can be guaranteed!
    TODO: Add automatic example collection!
    """

    def __init__(self, patterns: List[RegexElement], group_name: str = None):
        self.patterns = patterns
        self.group_name = group_name
        # merge positve negative and partial cases

    def __str__(self):
        # Safe union exists for compatible string lists
        if self.patterns_are_compatible_string_lists():
            return str(StringList(
                strings=sum([pattern.strings for pattern in self.patterns], []),
                group_name=self.group_name,
                replacements=self.patterns[0].replacements))

        name_prefix = '?:' if self.group_name is None else f'?P<{self.group_name}>'
        return f"({name_prefix}{'|'.join(str(pattern) for pattern in self.patterns)})"

    def patterns_are_compatible_string_lists(self):
        if len(self.patterns) == 0:
            return False

        for pattern in self.patterns:
            if not isinstance(pattern, StringList):
                return False

        if len(self.patterns) == 1:
            return True

        replacements = self.patterns[0].replacements
        for pattern in self.patterns:
            if pattern.replacements != replacements:
                return False

        return True

