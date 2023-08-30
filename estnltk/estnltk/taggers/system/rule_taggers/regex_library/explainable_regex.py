import re

from pandas import DataFrame


def truncate_middle_text(text, max_length):
    """ Truncates text in the middle if text length exceeds max_length """
    if len(text) <= max_length or max_length <= 3:
        return text

    k = int(max_length/2) - 1
    return f'{text[:k]}...{text[-k:]}'


class ExplainableRegex:
    """
    Wrapper class around Python regex library that simplifies documenting and testing regex patterns.
    Adds positive and negative examples as way to document and test regex patterns.
    """

    MAX_STRING_WIDTH = 50

    def __init__(self, regex, description=''):
        """
        Takes a standard Python regex as an argument together with the human-readable description of the regex pattern
        which should concisely describe the intent behind the pattern. More detailed documentation should be specified
        through the list of positive and negative examples that can automatically checked against the current pattern.
        """
        self.regex = regex
        self.positive_test_list = []
        self.negative_tests = []
        self.group_test_list = []
        self.negative_partial_test_list = []
        self.description = description

    def no_match(self, negative_example, description=''):
        self.negative_tests.append(negative_example)

    @property
    def negative_examples(self):
        return [example for example,_ in self.negative_tests]

    def evaluate_negative_examples(self):
        """
        Returns a dataframe where each row describes the status of the corresponding test.
        There are two potential outcomes for each test:
        - outcome (+) means that regex was not found in the example;
        - outcome (F) means that regex was found at least once in the example.
        """
        return DataFrame(
            columns=['Example', 'Status'],
            data=[[example, '+' if re.search(self.regex, example) is None else 'F']
                  for example, _ in self.negative_tests])

    def display_status_of_negative_examples(self):
        """
        Produces pretty-printed outcomes of the function evaluate_negative_examples.
        """
        return (self.evaluate_negative_examples().reset_index(names='ID').style
                .hide(axis='index')
                .set_caption('Negative examples')
                .set_table_styles([dict(
                    selector='caption',
                    props=[('font-weight', 'normal'), ('font-size', '110%'), ('color', 'black')])])
                .applymap(lambda x: 'text-align: left', subset='Example')
                .applymap(lambda x: 'font-weight: bold', subset='Status')
                .applymap(lambda x: 'color: red' if x == 'F' else 'color: green', subset='Status'))

    def _repr_html_(self):

        regex = truncate_middle_text(self.regex, self.MAX_STRING_WIDTH)
        description = self.description
        if len(description) > self.MAX_STRING_WIDTH:
            description = '<p>' + self.description + '</p>'
        else:
            description = description + '<br>'

        negative_examples = DataFrame({'example': self.negative_tests}).assign(status='Untested').to_html(index=False)
        positive_examples = DataFrame({'full matches': self.positive_test_list}).assign(status='Untested').to_html(index=False)

        return (
            '<b>regex:</b> {regex}<br/></br>'
            '<b>description:</b> {description}</br>'
            f'<b>positive examples</b><br/> {positive_examples} <br/></br>'
            '<b>negative examples</b><br/> {negative_examples} <br/>'
        ).format(self=self, description=description, regex=regex, positive_examples=positive_examples, negative_examples=negative_examples)

    def compile(self):
        return re.compile(self.regex)

    def full_match(self, full_pattern):
        self.positive_test_list.append(full_pattern)

    def partial_match(self, pattern, match=None, group_name=0):
        self.group_test_list.append((pattern, match, group_name))


    def test(self):
        for pattern in self.positive_test_list:
            assert re.fullmatch(self.regex, pattern) is not None

        for pattern in self.negative_tests:
            assert re.fullmatch(self.regex, pattern) is None

        for pattern, match, group_name in self.group_test_list:
            if match is None:
                assert re.search(self.regex,pattern).group(group_name) is not None
            assert re.search(self.regex, pattern).group(group_name) == match

        for pattern in self.negative_partial_test_list:
            assert re.search(self.regex,pattern) is None


#    def __repr__(self):
#        if self.description != '':
#            return self.description + '\n' + self.regex
#        else:
#            return self.regex



