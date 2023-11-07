import re
from copy import copy
from regex_library.regex_element import RegexElement
from pandas import read_csv

from typing import Dict
from typing import List
from typing import Union


class StringList(RegexElement):
    """
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
                 replacements: Dict[str, str] = None):
        self.strings = list(strings)
        self.group_name = group_name
        self.description = description
        self.replacements = {} if replacements is None else copy(replacements)

    def __setattr__(self, key, value):
        # Validate the right-hand side expression for replacement attribute
        if key == 'replacements':
            if not isinstance(value, dict):
                raise ValueError('Expecting a dictionary of substitutions of type dict[str, str]')
            for k, v in value.items():
                if not isinstance(k, str) or not isinstance(v, str):
                    raise ValueError('Expecting a dictionary of substitutions of type dict[str, str]')
                if len(k) != 1:
                    raise ValueError(f"Left-hand side of a substitution '{k}' --> '{v}' must be a single character")
                try:
                    re.compile(v)
                except Exception:
                    raise ValueError(f"Right-hand side of a substitution '{k}' --> '{v}' is invalid regular expression")

        super().__setattr__(key, value)

    def __str__(self):
        name_prefix = '?:' if self.group_name is None else f'?P<{self.group_name}>'

        # Drop duplicates and sort original strings according to the length and escape special characters
        choices = map(lambda x: re.escape(x), sorted(set(self.strings), key=lambda x: (-len(x), x)))
        if len(self.replacements) == 0:
            return f"({name_prefix}{'|'.join(choices)})"

        # Build a replacement dictionary that contains escaped characters as we first escape and then replace
        replacement_dict = {re.escape(k): f'(?:{v})' for k, v in self.replacements.items()}
        # Build a compound regex to match all escaped replacement characters. We need double escaped characters
        loc_regex = re.compile('|'.join(re.escape(re.escape(k)) for k in self.replacements.keys()), flags=re.UNICODE)
        # Perform all substitutions. The order of strings still guarantees that maximal match is chosen
        choices = map(lambda x: loc_regex.sub(lambda mo: replacement_dict[mo.group()], x), choices)
        return f"({name_prefix}{'|'.join(choices)})"

    def compile(self, **kwargs):
        """
        Compiles regex. All arguments are passed to re.compile() function.
        """
        return re.compile(str(self), **kwargs)

    def to_csv(self, file: str):
        """
        Exports to file
        TODO: Complete this
        """
        pass

    @staticmethod
    def from_file(file: Union[str, List[str]],
                  column: str = None,
                  group_name: str = None,
                  description: str = None,
                  replacements: Dict[str, str] = None,
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
            return StringList(df[column], group_name=group_name, description=description, replacements=replacements)

        if isinstance(file, str) and file[-4:] == '.txt':
            with open(file, "rt") as ifile:
                return StringList([line.rstrip('\n') for line in ifile],
                                  group_name=group_name, description=description, replacements=replacements)

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
                          description=description, replacements=replacements)
