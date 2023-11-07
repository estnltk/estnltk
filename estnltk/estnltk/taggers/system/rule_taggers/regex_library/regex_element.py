import re

from typing import Dict
from typing import Union


class RegexElement:
    """
    Wrapper class around Python regex library that simplifies documenting and testing regex patterns.
    Adds positive and negative test cases as way to document and automatically test regex patterns.
    Its subclasses add a structured way to construct regular expressions in an hierarchical manner
    together with test synthesis, which automatically combines existing tests of sub-expression.
    Use the function str(...) or the class method compile() to reveal the regular expression.

    The encapsulation makes it much safer to specify what should be matched by the regular expression,
    but it still has limitations. First, one cannot specify additional consistency constraints inside
    the hierarchical definition nor aggregate the contents of capture groups. If you need such features
    use grammar rules instead. Second, self-overlapping can cause subtle errors. This is particularly
    true in case of string replacement. One way to diagnose is to compare re.sub(..., count=-1) and
    several invocations of re.sub.(..., count=1) to see if there are some differences.
    """
    def __init__(self, pattern: str, group_name: str = None, description: str = None):
        """
        Encapsulates a regular expression, so it can be safely combined with other regular expressions.
        Adds a named capture group around the regex if `group_name` is provided.
        Otherwise, the regex is placed inside a non-capture group.

        The description is used in the display and should concisely describe the intent behind the pattern.
        Additional information about the intent can be specified through examples which are also used in the display.

        The function checks only the validity of the regular expression, everything else is your responsibility.
        """
        try:
            re.compile(pattern)
        except Exception:
            raise ValueError(f"Invalid regular expression: '{pattern}'")

        self.pattern = pattern
        self.group_name = group_name
        self.description = description

        self.examples = []
        self.negative_tests = []
        self.positive_tests = []
        self.extraction_tests = []

    def __str__(self):
        name_prefix = '?:' if self.group_name is None else f'?P<{self.group_name}>'
        return f"({name_prefix}{self.pattern})"

    def compile(self, **kwargs):
        """
        TODO: make it possible to use regex library
        Compiles regex. All arguments are passed to re.compile() or regex.compile() functions.
        """
        return re.compile(str(self), **kwargs)

    def _repr_html_(self):
        """
        TODO: Make a nice representation which also shows if the regex confirms to test cases
        """
        pass

    def no_match(self, negative_example: str, description: str = None):
        """
        A negative test case for the regular expression.
        The correctness of these test cases will be tested during validation.
        These examples will not be included to the html representation of the regex in Jupyter notebooks.
        """
        pass

    def example(self, positive_example: str, description: str = None):
        """
        A distinct example that describes the essence of the regular expression.
        These examples will be included to the html representation of the regex in Jupyter notebooks.
        The example will be also added to the set of full matches.
        """
        pass

    def full_match(self, positive_example: str, description: str = None):
        """
        A positive test case for the regular expression.
        The correctness of these test cases will be tested during validation.
        These examples will not be included to the html representation of the regex in Jupyter notebooks.
        """
        pass

    def partial_match(self, text: str,  target: Union[str, Dict[str, str]], description: str = None):
        """
        A positive test case for the regular expression which provides a way to specify matches for capture groups.
        The correctness of these test cases will be tested during validation.
        These examples will not be included to the html representation of the regex in Jupyter notebooks.

        If `target` is a string the match of the top capture group will be compared against the target.
        Otherwise, the dictionary specifies the target values for all capture groups specifies as keys.
        The string match test works even if the `group_name` is None. It meant to test maximality of the match.
        """
        pass

    def test(self):
        """
        TODO: make it work with pytest so that it would provide concise and meaningful error message
        """
        pass

    def evaluate_negative_examples(self):
        """
        Returns a dataframe where each row describes the status of the corresponding test.
        There are two potential outcomes for each test:
        - outcome (+) means that the regex was not found in the example;
        - outcome (F) means that the regex was found at least once in the example.
        """
        pass

    def evaluate_positive_examples(self):
        """
        Returns a dataframe where each row describes the status of the corresponding test.
        There are two potential outcomes for each test:
        - outcome (+) means that the regex matched the entire test string;
        - outcome (F) means that the regex did not match the entire test string.
        """
        pass

    def evaluate_extraction_examples(self):
        """
        Returns a dataframe where each row describes the status of the corresponding test.
        There are two potential outcomes for each test:
        - outcome (+) means that the desired outputs are extracted by specified capture groups;
        - outcome (F) means that some capture groups did not return the desired outcomes.
        """
        pass
