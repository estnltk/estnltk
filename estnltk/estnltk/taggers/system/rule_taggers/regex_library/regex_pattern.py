from typing import Dict
from regex_library.regex_element import RegexElement


class RegexPattern(RegexElement):
    """
    A `RegexElement` meant for defining a regular expression in terms of named sub-expressions.

    Automatic generation of positive tests is not possible in general as the pattern template
    may contain raw regex elements for which there are no base-level test cases. Thus, automatic
    test generation is possible only for a restricted set of pattern templates.
    """

    def __init__(self, pattern: str, group_name: str = None):
        self.pattern = pattern
        self.group_name = group_name

    def format(self, **kwargs: Dict[str, RegexElement]):
        return RegexElement(pattern=self.pattern.format(**kwargs), group_name=self.group_name)

    def generate_full_match_examples(self):
        """
        If possible returns a list of positive full match examples.
        """
        pass
