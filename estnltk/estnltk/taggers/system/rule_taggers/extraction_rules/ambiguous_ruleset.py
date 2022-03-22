import regex as re

from csv import Error as CSVError
from csv import reader as read_csv
from typing import List, Union, Dict

from .static_extraction_rule import StaticExtractionRule
from .dynamic_extraction_rule import DynamicExtractionRule

ExtractionRule = Union[StaticExtractionRule, DynamicExtractionRule]

CONVERSION_MAP = {
    'int': lambda x: int(x),
    'float': lambda x: float(x),
    'regex': lambda x: re.compile(x),
    'string': lambda x: str(x),
    'callable': lambda x: eval(x),
    'expression': lambda x: eval(x)
}


class AmbiguousRuleset:
    """
    Specifies extraction rules for many standard taggers:
    * SubstringTagger
    * RegexTagger
    * PhraseTagger
    * SpanTagger

    Each extraction rule specifies a pattern for extracting a relevant text span and a method for adding attributes
    to the extracted span. Further details can be found in the documentation of individual rule classes.

    By convention each rule can be specified by two rules:
    * A static extraction rule fixes initial value of attributes.
    * A dynamic extraction rule allows to update initial values of attributes.
    However, you do not have to specify both rules.

    Raises ValueError if two rules of the same type have the same left-hand-side.
    There can be static and a dynamic extraction rule with the same left-hand-side.

    """

    def __init__(self, rules: List[ExtractionRule] = ()):
        """
        Creates an empty ruleset unless the list of rules is explicitly given.
        The standard way to specify rules is via the load method that reads csv files in simple format.
        The more direct approach is needed when extraction rules use functions to dynamically compute attribute values.
        """

        if len(rules) == 0:
            self.static_rules: List[StaticExtractionRule] = list()
            self.dynamic_rules: List[DynamicExtractionRule] = list()
            return

        self.static_rules = []
        self.dynamic_rules = []
        for rule in rules:
            if isinstance(rule, StaticExtractionRule):
                self.static_rules.append(rule)
            elif isinstance(rule, DynamicExtractionRule):
                self.dynamic_rules.append(rule)
            else:
                raise ValueError("All rules must be of type StaticExtractionRule or DynamicExtractionRule")


    def add_rules(self, rules: List[ExtractionRule]):
        """
        Adds rules to existing ruleset.
        Raises ValueError if two rules of the same type have the same left-hand-side.
        There can be static and a dynamic extraction rule with the same left-hand-side.
        """

        for rule in rules:
            if isinstance(rule, StaticExtractionRule):
                self.static_rules.append(rule)
            elif isinstance(rule, DynamicExtractionRule):
                self.dynamic_rules.append(rule)
            else:
                raise ValueError("All rules must be of type StaticExtractionRule or DynamicExtractionRule")

    def load(
            self,
            file_name: str,
            key_column: Union[str, int] = 0,
            group_column: Union[str, int] = None,
            priority_column: Union[str, int] = None,
            mode: str = 'overwrite',
            **kwargs) -> None:
        """
        Adds static extraction rules to the ruleset by parsing the input file.
        Raises various errors with appropriate diagnostic messages when parsing fails.
        Debugging tip: A parsing error does not flush rules that have been parsed so far.

        Parameters
        ----------
        file_name:
            A csv file to be parsed
        key_column:
            Determines which column is used as the pattern. By default it is the first column.
        group_column:
            Determines which column is used as a group attribute for rule. Will be excluded from attributes.
        priority_column:
            Determines which column is used as a priority attribute for rule. Will be excluded from attributes.
        mode: 'overwrite', 'append' (default: 'overwrite')
            Determines what will be done with with existing rules
            'append': rules are added to existing ruleset.
            'overwrite': all rules including dynamic rules are flushed and a new ruleset is created.
        **kwargs:
            Additional named arguments to be passed to csv.reader, i.e. one can specify various configuration options.

        File format
        -----------

        The csv file must have the following format:
        * The first header row must contain attribute names for rules.
        * The second header row must contain attribute types for each column.
        * Attribute type must be int, float, regex, string, expression, callable.
        * Corresponding conversion rules is given by the global mapping CONVERSION_MAP.
        * The remaining rows must be the rules. All columns must be filled.
        """

        try:
            csv_file = open(file_name, 'rt', encoding='utf-8')
            csv_buffer = read_csv(csv_file, **kwargs)
        except FileNotFoundError:
            raise ValueError("File '{}' does not exist".format(file_name))
        except PermissionError:
            raise ValueError("Do not have permissions to read the rule file '{}'".format(file_name))
        except CSVError:
            # noinspection PyUnboundLocalVariable
            csv_file.close()
            raise ValueError("Invalid file format: File is not in CSV format")

        # When needed flush existing rules
        if mode == 'overwrite':
            self.static_rules = []
            self.dynamic_rules = []
        elif mode != 'append':
            csv_file.close()
            raise ValueError("Invalid parsing mode '{}'".format(mode))

        # The first row must contain attribute names
        column_names = next(csv_buffer, None)
        if column_names is None:
            csv_file.close()
            raise ValueError('Invalid file format: Line 1: The first header row is missing')
        column_names = list(column_names)

        # The second row must contain column types
        column_types = next(csv_buffer, None)
        if column_types is None:
            csv_file.close()
            raise ValueError('Invalid file format: Line 2: The second header row is missing')
        column_types = list(column_types)

        if len(column_names) != len(column_types):
            csv_file.close()
            raise ValueError('Invalid file format: Line 2: Header rows have different length')

        # Define corresponding data converters for each column
        n = len(column_names)
        converters = [None] * n
        for i, column_type in enumerate(column_types):
            converters[i] = CONVERSION_MAP.get(column_type, None)
            if converters[i] is None:
                csv_file.close()
                raise ValueError("Invalid file format: Line 2: Unknown data type {}".format(column_type))

        # Locate the pattern column when specified
        if isinstance(key_column, int):
            if key_column < 0 or key_column >= n:
                csv_file.close()
                raise ValueError('Key column is out of range')
        else:
            key_column = next((i for i, x in enumerate(column_names) if x == key_column), None)
            if key_column is None:
                csv_file.close()
                raise ValueError("Key column '{}' is missing from the file header".format(key_column))

        # Locate the group column when specified
        if isinstance(group_column, int):
            if group_column < 0 or group_column >= n:
                csv_file.close()
                raise ValueError('Group column is out of range')
            elif group_column == key_column:
                csv_file.close()
                raise ValueError('Group column cannot coincide with key column')
        elif group_column is not None:
            group_column = next((i for i, x in enumerate(column_names) if x == group_column), None)
            if group_column is None:
                csv_file.close()
                raise ValueError("Group column '{}' is missing from the file header".format(key_column))
            elif group_column == key_column:
                csv_file.close()
                raise ValueError('Group column cannot coincide with key column')

        # Locate the priority column when specified
        if isinstance(priority_column, int):
            if priority_column < 0 or priority_column >= n:
                csv_file.close()
                raise ValueError('Priority column is out of range')
            elif priority_column == key_column:
                csv_file.close()
                raise ValueError('Prior column cannot coincide with key column')
            elif priority_column == group_column:
                csv_file.close()
                raise ValueError('Prior column cannot coincide with group column')
        elif priority_column is not None:
            priority_column = next((i for i, x in enumerate(column_names) if x == priority_column), None)
            if priority_column is None:
                csv_file.close()
                raise ValueError("Priority column '{}' is missing from the file header".format(key_column))
            elif priority_column == key_column:
                csv_file.close()
                raise ValueError('Priority column cannot coincide with key column')
            elif priority_column == group_column:
                csv_file.close()
                raise ValueError('Priority column cannot coincide with group column')

        # This can contain Nones. This is not a problem
        non_attributes = [key_column, group_column, priority_column]

        i = 3
        row = next(csv_buffer, None)

        try:
            if group_column is None and priority_column is None:
                while row:
                    if len(row) != n:
                        csv_file.close()
                        raise ValueError("Invalid file format: Line {}: all rows must contain {} elements".format(i, n))

                    # noinspection PyCallingNonCallable
                    row = list(f(x) for f, x in zip(converters, row))
                    self.static_rules.append(
                        StaticExtractionRule(
                            pattern=row[key_column],
                            attributes={column_names[i]: x for i, x in enumerate(row) if i not in non_attributes}
                        )
                    )

                    row = next(csv_buffer, None)
                    i += 1
            elif group_column is None and priority_column is not None:
                while row:
                    if len(row) != n:
                        csv_file.close()
                        raise ValueError("Invalid file format: Line {}: all rows must contain {} elements".format(i, n))

                    # noinspection PyCallingNonCallable
                    row = list(f(x) for f, x in zip(converters, row))
                    self.static_rules.append(
                        StaticExtractionRule(
                            pattern=row[key_column],
                            attributes={column_names[i]: x for i, x in enumerate(row) if i not in non_attributes},
                            priority=row[priority_column]
                        )
                    )

                    row = next(csv_buffer, None)
                    i += 1
            elif group_column is not None and priority_column is None:
                while row:
                    if len(row) != n:
                        csv_file.close()
                        raise ValueError("Invalid file format: Line {}: all rows must contain {} elements".format(i, n))

                    # noinspection PyCallingNonCallable
                    row = list(f(x) for f, x in zip(converters, row))
                    self.static_rules.append(
                        StaticExtractionRule(
                            pattern=row[key_column],
                            attributes={column_names[i]: x for i, x in enumerate(row) if i not in non_attributes},
                            group=row[group_column]
                        )
                    )

                    row = next(csv_buffer, None)
                    i += 1
            else:
                while row:
                    if len(row) != n:
                        csv_file.close()
                        raise ValueError("Invalid file format: Line {}: all rows must contain {} elements".format(i, n))

                    # noinspection PyCallingNonCallable
                    row = list(f(x) for f, x in zip(converters, row))
                    self.static_rules.append(
                        StaticExtractionRule(
                            pattern=row[key_column],
                            attributes={column_names[i]: x for i, x in enumerate(row) if i not in non_attributes},
                            group=row[group_column],
                            priority=row[priority_column]
                        )
                    )

                    row = next(csv_buffer, None)
                    i += 1

        except CSVError:
            csv_file.close()
            raise ValueError("Invalid file format: Line {}: File is not in CSV format".format(i))

    @property
    def rule_map(self) -> Dict[str, List[Union[List[StaticExtractionRule], List[DynamicExtractionRule]]]]:
        """
        Maps all patterns to rules
        Returns Dict(str, [[StaticExtractionRule], [DynamicExtractionRule]])
        The str is pattern and it is mapped to a list of (static_rules,dynamic_rules)
        """

        mapping = {}
        for rule in self.static_rules:
            if rule.pattern in mapping.keys():
                mapping[rule.pattern][0].append(rule)
            else:
                mapping[rule.pattern] = [[rule], []]
        for rule in self.dynamic_rules:
            if rule.pattern in mapping.keys():
                mapping[rule.pattern][1].append(rule)
            else:
                mapping[rule.pattern] = [[], [rule]]

        return mapping

    @property
    def output_attributes(self):
        """
        Returns the list of all attributes defined by the static rules.
        """
        result = set().union(*[set(rule.attributes) for rule in self.static_rules])
        return result

    @property
    def missing_attributes(self):
        """
        Returns true if some static rule does not define all output attributes.
        """
        if len(self.static_rules) <= 1:
            return False

        output_attributes = set(self.static_rules[0].attributes)
        for rule in self.static_rules:
            if output_attributes != set(rule.attributes):
                return True

        return False

