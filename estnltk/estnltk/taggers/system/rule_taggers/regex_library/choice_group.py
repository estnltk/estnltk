from typing import List

from estnltk.taggers.system.rule_taggers.regex_library.regex_element import RegexElement
from estnltk.taggers.system.rule_taggers.regex_library.string_list import StringList


class ChoiceGroup(RegexElement):
    """
    A `RegexElement` meant for defining a choice between the list of sub-expressions.

    The order of sub-expressions matters as in the standard choice group. 
    It does not guarantee that the match corresponds to the subpattern with the longest match. 
    An exception is the case when all sub-expressions are compatible StringList-s: 
    then strings of all StringList-s will be automatically sorted by their length, so 
    that the matching with the longest string is guaranteed.
    """

    def __init__(self, patterns: List[RegexElement], 
                       group_name: str = None, 
                       description: str = None, 
                       merge_positive_tests: bool = False,
                       merge_negative_tests: bool = False,
                       merge_extraction_tests: bool = False):
        '''
        Initializes new ChoiceGroup based on the given list of patterns.
        
        Parameters
        ----------
        patterns: List[RegexElement]
            The list of sub-expressions for the choice group. Note 
            that the order of sub-expressions matters: sub-expressions 
            capturing longer matches should come first. In general, it 
            is responsibility of the user to ensure correct order.
            An exception is the case when all elements of the list are 
            compatible StringList-s: then strings of all StringList-s 
            will be automatically sorted by their length, so that 
            matching with the longest string is guaranteed.
        group_name: str
            Name for the capturing group. The group_name appears in 
            string representation of this expression, but it is not 
            encoded into pattern of this expression (self.pattern).
        description: str
            Description for this regular expression (optional).
        merge_positive_tests: bool
            Optional. If set, then collects unique positive tests 
            from all input patterns, and adds as corresponding tests 
            of this ChoiceGroup. 
            By default, `merge_positive_tests` is set to `False`.
        merge_negative_tests: bool
            Optional. If set, then collects unique negative tests 
            from all input patterns, and adds as corresponding tests 
            of this ChoiceGroup. 
            By default, `merge_negative_tests` is set to `False`.
        merge_extraction_tests: bool
            Optional. If set, then collects unique extraction tests 
            from all input patterns, and adds as corresponding tests 
            of this ChoiceGroup. 
            By default, `merge_extraction_tests` is set to `False`.
        '''
        object.__setattr__(self, '_initialized', False)
        self.patterns = patterns
        super().__init__(pattern=self.__make_choice_group(), group_name=group_name, description=description)
        if merge_positive_tests or merge_negative_tests or merge_extraction_tests:
            self.__merge_tests(positive=merge_positive_tests, 
                               negative=merge_negative_tests, 
                               extraction=merge_extraction_tests)
        object.__setattr__(self, '_initialized', True)

    def __setattr__(self, key, value):
        # Do not allow changing system variables after the initialization
        if key in ['_initialized', 'pattern', 'patterns']:
            if self._initialized:
                raise AttributeError('changing of the attribute {} after initialization not allowed in {}'.format(
                            key, self.__class__.__name__))
        super().__setattr__(key, value)

    def __make_choice_group(self):
        '''Based on the format of self.patterns, creates and returns unparenthesized 
           choice group. 
           If self.patterns is a list of compatible StringList-s, then concatenates 
           all strings into one list, creates a StringList and returns its pattern. 
           Otherwise, creates a choice group based on the given regex patterns. 
           Only for internal usage. 
        '''
        if self.patterns_are_compatible_string_lists():
            # Safe union exists for compatible string lists
            # Collect strings and ignore_case_flags
            all_strings = []
            all_ignore_case_flags = []
            for pattern in self.patterns:
                all_strings.extend( pattern.strings )
                all_ignore_case_flags.extend( pattern.ignore_case_flags )
            # Create new StringList
            return StringList( strings=all_strings, 
                               ignore_case_flags=all_ignore_case_flags, 
                               replacements=self.patterns[0].replacements).pattern
        
        # All patterns are RegexElement-s
        return f"{'|'.join(str(pattern) for pattern in self.patterns)}"

    def __merge_tests(self, positive=True, negative=True, extraction=True):
        '''Collects positive, negative and/or extractions tests of self.patterns, 
           and adds as tests of this ChoiceGroup.
           Flags `positive`, `negative` and `extraction` can be used to include/
           exclude different types of tests from merging.
           Automatically detects and removes duplicates among collected tests. 
           This method can be called only once, during the initialization of the 
           ChoiceGroup, as later calling could result in duplicate tests. 
           Only for internal usage. 
        '''
        if self._initialized:
            raise Exception('(!) Cannot merge tests after the initialization.')
        seen_examples_pos = set()
        seen_examples_neg = set()
        seen_examples_part = set()
        
        # Make a new description for test, 
        # showing its auto-merged
        def _new_description(old_desc):
            if desc is not None:
                if desc.endswith('(auto-merged test)'):
                    return desc
                else:
                    return f'{desc} (auto-merged test)'
            else:
                return '(auto-merged test)'
        
        for pattern in self.patterns:
            if isinstance(pattern, RegexElement):
                if positive:
                    for example, desc in pattern.positive_tests:
                        if example in seen_examples_pos:
                            # Avoid duplicates
                            continue
                        self.full_match(example, 
                                        description=_new_description(desc))
                        seen_examples_pos.add(example)
                if negative:
                    for example, desc in pattern.negative_tests:
                        if example in seen_examples_neg:
                            # Avoid duplicates
                            continue
                        self.no_match(example, 
                                      description=_new_description(desc))
                        seen_examples_neg.add(example)
                if extraction:
                    for text, target, desc in pattern.extraction_tests:
                        if f'{text}|{target}' in seen_examples_part:
                            # Avoid duplicates
                            continue
                        self.partial_match(text, target, 
                                           description=_new_description(desc))
                        seen_examples_part.add(f'{text}|{target}')

    def patterns_are_compatible_string_lists(self):
        '''Checks whether self.patterns is a list of 
           compatible StringList-s. Constraints:
           * there is at least one pattern;
           * each pattern is StringList;
           * all patterns have the same sets of replacements. 
        '''
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

