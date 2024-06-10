import regex
from copy import copy
from pandas import read_csv
from pandas import DataFrame

from typing import Dict
from typing import List
from typing import Union

from estnltk.taggers.system.rule_taggers.regex_library.regex_element import RegexElement


class StringList(RegexElement):
    r"""
    A `RegexElement` meant for defining a choice between the list of strings.
    Guarantees that the resulting regular expression matches the longest matching string in the list.
    All special characters are escaped and each string matches its literal representation.

    It is possible to tame unnecessary complexity of string variations by specifying the 'replacements' attribute,
    which is a dictionary of character to regex replacements that is applied to all strings.
    For instance, we can specify a substitution ' ' --> '\s+' to cover possible variations of white space symbols.
    The left hand of the rule can be only a single character that is interpreted as a plain character.
    For instance, a rule '.' --> '\s*\.\s*' is applicable for '.' characters inside the strings.
    Proper escaping of special symbols on the right-hand side of the rule is a responsibility of the user.

    TODO: Emphasise the use of negative examples and positive examples!
    """

    def __init__(self,
                 strings: List[str],
                 group_name: str = None,
                 description: str = None,
                 replacements: Dict[str, str] = None,
                 ignore_case: bool = False,
                 ignore_case_flags: List[bool] = None, 
                 autogenerate_tests: bool = False):
        '''
        Initializes new StringList based on the given list of strings.
        
        Parameters
        ----------
        strings: List[str]
            The list of strings for the choice group. Strings in the 
            list will processed so that the matching with the special 
            characters and with the the longest string is guaranteed. 
        group_name: str
            Name for the capturing group. The group_name appears in 
            string representation of this expression, but it is not 
            encoded into pattern of this expression (self.pattern).
        description: str
            Description for this regular expression (optional).
        replacements: Dict[str, str]
            Optional. A dictionary of character to regex replacements 
            that is applied to all strings. For instance, you can 
            specify a substitution `{' ' : '\s+'}` to cover possible 
            variations of white space symbols. The left hand of the 
            rule can be only a single character that is interpreted 
            as a plain character, not regex meta character. Proper 
            escaping of special symbols on the right-hand side of 
            the rule is a responsibility of the user.
            By default, `replacements` is set to `None`.
        ignore_case: bool
            Optional. Converts all strings to case-insensitive 
            format, that is, replaces all alphabetic characters 
            with a set of characters containing an uppercase 
            and a lowercase variant of the character. 
            Note that this only works if `replacements` do not 
            introduce any regexes containing letters with non-
            literal meanings, such as named choice groups, sets 
            of characters or flag letters, which could break the 
            logic. Avoiding conflicts between the ignore_case 
            conversion and `replacements` is a responsibility 
            of the user. 
            Note that the effect of `ignore_case` will be overridden 
            by `ignore_case_flags` if provided. 
            By default, `ignore_case` is set to `False`.
        ignore_case_flags: List[bool]
            Optional. Individual ignore_case flags for each string. 
            Allows to selectively control, which of the strings should 
            be case sensitive (`False`) and which should be converted 
            to case in-sensitive format (`True`).
            If `ignore_case_flags` are provided, then they will 
            override the effect of flag `ignore_case`. 
            By default, `ignore_case_flags` is set to `None`.
        autogenerate_tests: bool
            Optional. If set, then adds input strings as positive test 
            examples of this StringList. Use this to test that pattern 
            modifications from `replacements` do not mess up matching 
            with the original strings.
            By default, `autogenerate_tests` is set to `False`.
        '''
        object.__setattr__(self, '_initialized', False)
        self.strings = list(strings)
        self.replacements = {} if replacements is None else copy(replacements)
        if ignore_case_flags is None:
            # Create default ignore_case_flags
            if ignore_case:
                ignore_case_flags = [True for i in range(len(self.strings))]
            else:
                ignore_case_flags = [False for i in range(len(self.strings))]
        else:
            # Validate given ignore_case_flags
            assert isinstance(ignore_case_flags, list), \
                '(!) ignore_case_flags should be a list of bool, '+\
                f'not {type(ignore_case_flags)}.'
        assert len(ignore_case_flags) == len(self.strings), \
            '(!) ignore_case_flags should have the same length as strings.'
        self.ignore_case_flags = ignore_case_flags
        super().__init__(pattern=self.__make_choice_group(), 
                         group_name=group_name, 
                         description=description)
        if autogenerate_tests:
            self.__autogenerate_tests()
        object.__setattr__(self, '_initialized', True)

    def __setattr__(self, key, value):
        # Do not allow changing system variables after the initialization
        if key in ['_initialized', 'pattern', 'strings', 'replacements', 'ignore_case_flags']:
            if self._initialized:
                raise AttributeError('changing of the attribute {} after initialization not allowed in {}'.format(
                            key, self.__class__.__name__))
        if key == 'replacements':
            # [During the initialization]: Validate the right-hand side expression for replacement attribute
            if not isinstance(value, dict):
                raise ValueError('Expecting a dictionary of substitutions of type dict[str, str]')
            for k, v in value.items():
                if not isinstance(k, str) or not isinstance(v, str):
                    raise ValueError('Expecting a dictionary of substitutions of type dict[str, str]')
                if len(k) != 1:
                    raise ValueError(f"Left-hand side of a substitution '{k}' --> '{v}' must be a single character")
                try:
                    regex.compile(v)
                except Exception:
                    raise ValueError(f"Right-hand side of a substitution '{k}' --> '{v}' is invalid regular expression")
        super().__setattr__(key, value)

    @staticmethod
    def make_case_insensitive(pattern: str):
        '''Converts given pattern to a case insensitive pattern. 
           For that, replaces all alphabet letters with a set of characters 
           containing an uppercase and a lowercase variant of the character. 
           Exceptions are letters preceded by '\\', which will be ignored.
           Note that for this to work, pattern needs to be restricted so 
           that is does not contain: sets of characters, flag letters and 
           named capturing groups.
        '''
        new_pattern = []
        prev_char = ''
        for c in pattern:
            if c.isalpha() and prev_char != '\\':
                new_pattern.append(f'[{c.upper()}{c.lower()}]')
            else:
                new_pattern.append(c)
            prev_char = c
        return ''.join(new_pattern)

    def __make_choice_group(self):
        '''Creates and returns unparenthesized choice group corresponding to this string list. 
           Drops duplicates and sorts original strings according to the length, escapes special 
           characters. 
           Depending on the `self.ignore_case_flags`, each string is either converted to a 
           case-insensitive pattern or preserves its case-sensitivity. 
           If self.replacements is defined, then applies character to regex replacements to all 
           strings. 
           Only for internal usage. 
        '''
        # Sort original strings according to the length
        choices = []
        seen_strings = set()
        for str_id, string in sorted(list(enumerate(self.strings)), key=lambda x: (-len(x[1]), x[1])):
            original_string = string
            # Skip duplicate string
            if original_string in seen_strings:
                continue
            # Escape meta symbols
            string = regex.escape(string)
            # Convert to a case insensitive format (if required)
            if self.ignore_case_flags[str_id]:
                string = StringList.make_case_insensitive(string)
            choices.append(string)
            seen_strings.add(original_string)
        if len(self.replacements) == 0:
            return f"{'|'.join(choices)}"
        # Build a replacement dictionary that contains escaped characters as we first escape and then replace
        replacement_dict = {regex.escape(k): f'(?:{v})' for k, v in self.replacements.items()}
        # Build a compound regex to match all escaped replacement characters. We need double escaped characters
        loc_regex = regex.compile('|'.join(regex.escape(regex.escape(k)) for k in self.replacements.keys()), flags=regex.UNICODE)
        # Perform all substitutions. The order of strings still guarantees that maximal match is chosen
        choices = map(lambda x: loc_regex.sub(lambda mo: replacement_dict[mo.group()], x), choices)
        return f"{'|'.join(choices)}"

    def __autogenerate_tests(self):
        '''
        Automatically generates positive test examples from the input strings. 
        This method can be called only once, during the initialization of the 
        StringList, as later calling could result in duplicate tests.
        '''
        if self._initialized:
            raise Exception('(!) Cannot autogenerate tests after the initialization.')
        seen_examples = set()
        for string in self.strings:
            if string in seen_examples:
                # Avoid duplicates
                continue
            self.full_match(string, description='autogenerated test')
            seen_examples.add(string)

    def to_csv(self, file: str, column: str = None):
        """
        Exports strings of this StringList to a CSV file. 
        Note that this method saves plain strings, without any post-processing 
        (that is: no sorting, removal of duplicates, nor applying replacements).
        """
        assert isinstance(file, str), \
            f'(!) Unexpected file argument type {type(file)}, expected str'
        # Save strings into csv file
        df = DataFrame({(column if column is not None else 'string_list'): self.strings})
        df.to_csv(file, index=False, header=True)

    @staticmethod
    def from_file(file: Union[str, List[str]],
                  column: str = None,
                  group_name: str = None,
                  description: str = None,
                  replacements: Dict[str, str] = None,
                  ignore_case: bool = False,
                  ignore_case_flags: List[bool] = None, 
                  autogenerate_tests: bool = False,
                  **kwargs):
        """
        Given a list of string in a file or list of files generates a corresponding regular expression.
        Knows how to handle string lists in txt-files or csv-files.

        In csv-files, the string list must be specified as a column.
        Additional arguments can be used to control the csv parsing with pandas.read_csv function.

        In txt-files, each row will be parsed as an element of the string list.
        As a result, newline symbols cannot be part of a string.
        """

        # Process a file
        if isinstance(file, str) and file[-4:] == '.csv':
            df = read_csv(file, **kwargs)
            column = df.columns[0] if column is None else column
            if column not in df.columns:
                raise ValueError(f'Csv file {file} does not contain column {column}')
            return StringList(df[column], group_name=group_name, description=description, 
                              replacements=replacements, ignore_case=ignore_case, 
                              ignore_case_flags=ignore_case_flags,
                              autogenerate_tests=autogenerate_tests)

        if isinstance(file, str) and file[-4:] == '.txt':
            with open(file, "rt") as ifile:
                return StringList([line.rstrip('\n') for line in ifile],
                                  group_name=group_name, description=description, 
                                  replacements=replacements, ignore_case=ignore_case, 
                                  ignore_case_flags=ignore_case_flags, 
                                  autogenerate_tests=autogenerate_tests )

        if not isinstance(file, list):
            raise ValueError(f'Invalid file argument {file}')

        # Process a list of files
        string_lists = [None] * len(file)
        for i, input_file in enumerate(file):

            if isinstance(input_file, str) and input_file[-4:] == '.csv':
                df = read_csv(input_file, **kwargs)
                column = df.columns[0] if column is None else column
                if column not in df.columns:
                    raise ValueError(f'Csv file {file} does not contain column {column}')
                string_lists[i] = df[column].to_list()
                continue

            if isinstance(input_file, str) and input_file[-4:] == '.txt':
                with open(input_file, "rt") as ifile:
                    string_lists[i] = [line.rstrip('\n') for line in ifile]
                continue

            raise ValueError(f'Invalid input file {input_file}')

        return StringList(sum(string_lists, []), group_name=group_name, 
                          description=description, replacements=replacements, 
                          ignore_case=ignore_case, 
                          ignore_case_flags=ignore_case_flags, 
                          autogenerate_tests=autogenerate_tests)
