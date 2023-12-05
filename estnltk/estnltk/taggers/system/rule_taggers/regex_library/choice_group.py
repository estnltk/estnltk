from typing import List
from typing import Union

from estnltk.taggers.system.rule_taggers.regex_library.regex_element import RegexElement
from estnltk.taggers.system.rule_taggers.regex_library.string_list import StringList


class ChoiceGroup(RegexElement):
    """
    A `RegexElement` meant for defining a choice between the list of sub-expressions.

    The order of sub-expressions matters as in the standard choice group.
    It does not guarantee that the match corresponds to the subpattern with the longest match.

    TODO: Add automatic test generation
    TODO: Add extra checks for string lists. Then it can be guaranteed!
    TODO: Add automatic example collection!
    """

    def __init__(self, patterns: List[Union[RegexElement, str]], group_name: str = None, description: str = None):
        object.__setattr__(self, '_initialized', False)
        self.patterns = patterns
        super().__init__(pattern=self.__make_choice_group(), group_name=group_name, description=description)
        # TODO: merge positve negative and partial cases ?!
        object.__setattr__(self, '_initialized', True)

    def __setattr__(self, key, value):
        # Do not allow changing system variables after the initialization
        if key in ['_initialized', 'pattern', 'patterns']:
            if self._initialized:
                raise AttributeError('changing of the attribute {} after initialization not allowed in {}'.format(
                            key, self.__class__.__name__))
        super().__setattr__(key, value)

    def __make_choice_group(self):
        '''Based on the format of self.patterns, creates and returns unparenthesized choice group. 
           If self.patterns is a list of strings, then creates a StringList and returns its pattern. 
           If self.patterns is a list of compatible StringList-s, then concatenates all strings into 
           one list, creates a StringList and returns its pattern. 
           Otherwise, creates a choice group based on the given regex patterns. 
           Only for internal usage. 
        '''
        if self.patterns_are_plain_strings():
            # All patterns are strings (assume: plain text strings)
            return StringList(
                       strings=self.patterns,
                       group_name=self.group_name).pattern
        
        if self.patterns_are_compatible_string_lists():
            # Safe union exists for compatible string lists
            return StringList(
                       strings=sum([pattern.strings for pattern in self.patterns], []),
                       group_name=self.group_name,
                       replacements=self.patterns[0].replacements).pattern
        
        # All patterns are RegexElement-s
        return f"{'|'.join(str(pattern) for pattern in self.patterns)}"

    def patterns_are_plain_strings(self):
        if len(self.patterns) == 0:
            return False        

        for pattern in self.patterns:
            if isinstance(pattern, RegexElement) or not isinstance(pattern, str):
                return False
        
        return True

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

