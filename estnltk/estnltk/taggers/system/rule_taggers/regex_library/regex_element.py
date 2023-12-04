from typing import Dict, Union

import regex

from pandas import DataFrame

def truncate_middle_text(text, max_length):
    """ Truncates text in the middle if text length exceeds max_length """
    if len(text) <= max_length or max_length <= 3:
        return text
    k = int(max_length/2) - 1
    return f'{text[:k]}...{text[-k:]}'


class RegexElement:
    """
    Wrapper class around Python regex library (https://pypi.org/project/regex/) that simplifies 
    documenting and testing regex patterns.
    Adds positive and negative test cases as way to document and automatically test regex patterns.
    Its subclasses add a structured way to construct regular expressions in an hierarchical manner
    together with test synthesis, which automatically combines existing tests of sub-expression.
    Use the function str(...) or the class method compile() to reveal the regular expression.

    The encapsulation makes it much safer to specify what should be matched by the regular expression,
    but it still has limitations. First, one cannot specify additional consistency constraints inside
    the hierarchical definition nor aggregate the contents of capture groups. If you need such features
    use grammar rules instead. Second, self-overlapping can cause subtle errors. This is particularly
    true in case of string replacement. One way to diagnose is to compare regex.sub(..., count=-1) and
    several invocations of regex.sub.(..., count=1) to see if there are some differences.
    """
    
    MAX_STRING_WIDTH = 50
    
    def __init__(self, pattern: str, group_name: str = None, description: str = None):
        """
        Encapsulates a regular expression, so it can be safely combined with other regular expressions.
        Adds a named capture group around the regex if `group_name` is provided. Note that the regular 
        expression pattern itself must not contain the `group_name`.
        Otherwise, if `group_name` is not provided, then the regex is placed inside a non-capture group.

        The description is used in the display and should concisely describe the intent behind the pattern.
        Additional information about the intent can be specified through examples which are also used in the display.

        The function checks only the validity of the regular expression, everything else is your responsibility.
        """
        try:
            temp_regex = regex.compile(pattern)
        except Exception:
            raise ValueError(f"Invalid regular expression: '{pattern}'")

        if isinstance(group_name, str):
            if group_name in temp_regex.groupindex.keys():
                raise ValueError(f'(!) pattern {pattern!r} must not contain group_name {group_name!r}.')

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
        Compiles regex. All arguments are passed to regex.compile() function.
        """
        # TODO: shouldn't all testing and validation methods compile via this method?
        return regex.compile(self.pattern, **kwargs)

    def _repr_html_(self):
        """
        TODO: Make a nice representation which also shows if the regex confirms to test cases
        """
        # regex & description
        regex_str = truncate_middle_text(self.pattern, self.MAX_STRING_WIDTH)
        regex_str = f'<b>regex:</b> {regex_str}<br/>'
        if isinstance(self.description, str):
            description_str = f'<b>description:</b> <p>{self.description}</p></br>'
        else:
            description_str = ''
        
        # testing results
        test_group_names = ['positive examples', 'negative examples', 'extraction tests']
        pos_examples_results = self.evaluate_positive_examples()
        neg_examples_results = self.evaluate_negative_examples()
        extraction_results   = self.evaluate_extraction_examples()
        test_groups = [pos_examples_results, neg_examples_results, extraction_results]
        eval_results = []
        for test_group_name, results_df in zip(test_group_names, test_groups):
            passed = results_df['Status'].value_counts().get('+', 0)
            failed = results_df['Status'].value_counts().get('F', 0)
            eval_results.append( [test_group_name, passed, failed] )
        eval_summary_df = DataFrame(columns=['Test group', 'passed', 'failed'], data=eval_results)
        eval_summary_df = (eval_summary_df.style
            .hide(axis='index')
            .set_caption('Testing results')
            .applymap(lambda x: 'color: green' if x > 0 else 'color: black', subset='passed')
            .applymap(lambda x: 'color: red' if x > 0 else 'color: black', subset='failed'))

        # examples
        examples_data = []
        has_descriptions = any([isinstance(example_desc, str) for (_, example_desc) in self.examples])
        for (example_str, example_desc) in self.examples:
            # Get the status of example (passed or failed)
            example_row = pos_examples_results.loc[pos_examples_results['Example'] == example_str]
            example_status = example_row.iloc[0]['Status']
            if example_desc is None:
                example_desc = ''
            if has_descriptions:
                examples_data.append( (example_str, example_desc, example_status) )
            else:
                examples_data.append( (example_str, example_status) )
        examples_df_columns = \
            ['Example', 'Description', 'Status'] if has_descriptions else ['Example', 'Status']
        examples_df = DataFrame(columns=examples_df_columns, data=examples_data)
        examples_df = (examples_df.style
            .hide(axis='index')
            .set_caption('Examples')
            .applymap(lambda x: 'color: red' if x == 'F' else 'color: green', subset='Status'))
        examples_str = examples_df.to_html(index=False) if len(examples_data) > 0 else ''

        return ('{regex}{description}{examples}{evaluation_summary}').format( \
                 regex=regex_str, 
                 description=description_str, 
                 examples=examples_str,
                 evaluation_summary=eval_summary_df.to_html(index=False))

    def no_match(self, negative_example: str, description: str = None):
        """
        Adds a negative test case for the regular expression.
        The correctness of these test cases will be tested during validation.
        These examples will not be included to the html representation of the regex in Jupyter notebooks.
        """
        self.negative_tests.append( (negative_example, description) )

    def example(self, positive_example: str, description: str = None):
        """
        Adds a distinct example that describes the essence of the regular expression.
        These examples will be included to the html representation of the regex in Jupyter notebooks.
        The example will be also added to the set of full matches.
        """
        self.examples.append( (positive_example, description))
        self.full_match(positive_example, description)

    def full_match(self, positive_example: str, description: str = None):
        """
        Adds a positive test case for the regular expression.
        The correctness of these test cases will be tested during validation.
        These examples will not be included to the html representation of the regex in Jupyter notebooks.
        """
        self.positive_tests.append( (positive_example, description) )

    def partial_match(self, text: str, target: Union[str, Dict[str, str]], description: str = None):
        """
        A positive test case for the regular expression which provides a way to specify matches for capture groups.
        The correctness of these test cases will be tested during validation.
        These examples will not be included to the html representation of the regex in Jupyter notebooks.

        If `target` is a string the match of the top capture group will be compared against the target.
        Otherwise, the dictionary specifies the target values for all capture groups specifies as keys.
        The string match test works even if the `group_name` is None. It meant to test maximality of the match.
        """
        if not isinstance(target, (str, dict)):
            raise TypeError(f'(!) Unexpected target type {type(target)!r}. Expected str or Dict[str, str].')
        self.extraction_tests.append( (text, target, description) )

    def test(self):
        for example, desc in self.positive_tests:
            assert regex.fullmatch(self.pattern, example) is not None, \
                f'pattern {self.pattern!r} did not match positive example {example!r}'

        for example, desc in self.negative_tests:
            assert regex.fullmatch(self.pattern, example) is None, \
                f'pattern {self.pattern!r} matched with the negative example {example!r}'

        for text, target, desc in self.extraction_tests:
            case = [text]
            match = regex.search(self.pattern, text)
            assert match is not None, \
                f'pattern {self.pattern!r} was not found in extraction example {text!r}'
            if isinstance(target, str):
                # TODO: top level group versus named group: which one to prefer?
                if self.group_name is None:
                    assert match.group(0) == target, \
                        f'top level group of pattern {self.pattern!r} did not match {target!r}'
                else:
                    assert match.group(self.group_name) == target, \
                        f'group {self.group_name!r} of pattern {self.pattern!r} did not match {target!r}'
            elif isinstance(target, dict):
                for (group_name, target_val) in target.items():
                    assert group_name in (match.groupdict()).keys(), \
                        f'group {group_name!r} of pattern {self.pattern!r} not found in {target_val!r}'
                    assert match.group(group_name) == target_val, \
                        f'group {group_name!r} of pattern {self.pattern!r} not found in {target_val!r}'

    def evaluate_negative_examples(self):
        """
        Returns a dataframe where each row describes the status of the corresponding test.
        There are two potential outcomes for each test:
        - outcome (+) means that the regex did not match the entire test string;
        - outcome (F) means that the regex matched the entire test string.
        """
        return DataFrame(
            columns=['Example', 'Status'],
            data=[[example, '+' if regex.fullmatch(self.pattern, example) is None else 'F']
                  for example, _ in self.negative_tests])

    def evaluate_positive_examples(self):
        """
        Returns a dataframe where each row describes the status of the corresponding test.
        There are two potential outcomes for each test:
        - outcome (+) means that the regex matched the entire test string;
        - outcome (F) means that the regex did not match the entire test string.
        """
        return DataFrame(
            columns=['Example', 'Status'],
            data=[[example, '+' if regex.fullmatch(self.pattern, example) else 'F']
                  for example, _ in self.positive_tests])

    def evaluate_extraction_examples(self):
        """
        Returns a dataframe where each row describes the status of the corresponding test.
        There are two potential outcomes for each test:
        - outcome (+) means that the desired outputs are extracted by specified capture groups;
        - outcome (F) means that some capture groups did not return the desired outcomes.
        """
        test_data = []
        for text, target, _ in self.extraction_tests:
            case = [text]
            match = regex.search(self.pattern, text)
            if match:
                if isinstance(target, str):
                    # TODO: top level group versus named group: which one to prefer?
                    if self.group_name is None:
                        final_outcome = '+' if match.group(0) == target else 'F'
                    else:
                        final_outcome = '+' if match.group(self.group_name) == target else 'F'
                elif isinstance(target, dict):
                    outcomes = []
                    for (group_name, target_val) in target.items():
                        if group_name in (match.groupdict()).keys():
                            outcome = '+' if match.group(group_name) == target_val else 'F'
                            outcomes.append(outcome)
                        else:
                            outcomes.append('F')
                    final_outcome = '+' if 'F' not in outcomes else 'F'
                case.append(final_outcome)
            else:
                case.append('F')
            test_data.append( case )
        return DataFrame(columns=['Example', 'Status'], data=test_data)
