from estnltk.visualisation.span_visualiser.fancy_span_visualisation import DisplaySpans
from estnltk.visualisation.span_visualiser.direct_plain_span_visualiser import DirectPlainSpanVisualiser
from typing import Tuple, List, Union
from estnltk import Text, Layer
from collections import defaultdict
import re

class DisplayNounCases(DisplaySpans):
    """
    Visualizes case information in a text

    Default background color scheme is following:
    * case_coloring[str]
    * span_coloring[int]

    The first coloring controls how spans with different cases are colored.
    Default coloring can be changed by assigning appropriate entries, e.g.
    case_coloring['kom'] = 'black'.

    The second controls how span overlaps are colored. The tokenization
    into the words can be ambiguous. By default, overlaps are colored
    in two shades of red. This can be changed by assigning appropriate
    entries, e.g. span_coloring[2] = 'blue'.

    To redefine the entire color scheme, the entire colouring attribute
    must be redefined. The assigned object must support indexing with
    any string for type_coloring and any int for span_coloring.

    As a word can have multiple analyses, coloring is done in two phases:
    1. list of case tags is aggregated into a new string label
    2. case tag coloring is used to determine the background color

    The default aggregator removes number information from the case label
    and marks all ambigious labellings with '*'. It is possible to customise
    this by redefining ambiguity_resolver.
    """

    def __init__(self, layer: str = 'morph_analysis', ambiguity_resolver: callable = None):
        super(DisplayNounCases, self).__init__(styling="direct")

        # Hack to get it working by replacing a wrong base class
        self.span_decorator = DirectPlainSpanVisualiser()

        self.morph_layer = layer
        self.__default_resolver = ambiguity_resolver or self.__default_ambiguity_resolver
        self.restore_defaults()

    def restore_defaults(self):

        self.ambiguity_resolver = self.__default_ambiguity_resolver
        self.span_decorator.bg_mapping = self.__bg_mapper

        # Define two shades of red for overlapping tokenization
        self.span_coloring = defaultdict(lambda: '#FF0000')
        self.span_coloring[2] = '#FF5050'

        # Define coloring for different types of compounds
        self.case_coloring = defaultdict(lambda: '#ffffff00')

        # By default, we color only the first four cases
        self.case_coloring['n'] = 'orange'
        self.case_coloring['g'] = 'yellow'
        self.case_coloring['p'] = 'lightgreen'
        self.case_coloring['adt'] = 'pink'
        self.case_coloring['*'] = 'gray'
        self.case_coloring['_'] = '#ffffff00'

    def __call__(self, object: Union[Text, Layer]) -> str:
        if isinstance(object, Text):
            return super(DisplayNounCases, self).__call__(object[self.morph_layer])
        elif isinstance(object, Layer):
            return super(DisplayNounCases, self).__call__(object)
        else:
            raise ValueError('Invalid input')

    def __default_ambiguity_resolver(self, span) -> str:

        cases = {re.sub('^sg |^pl ', '', an.form) for an in span.annotations if an.partofspeech in {'S', 'H', 'P'}}

        if len(cases) == 0:
            return '_'

        if len(cases) == 1:
            return next(iter(cases));

        return '*'

    def __bg_mapper(self, segment: Tuple[str, List[int]], spans) -> str:

        if len(segment[1]) != 1:
            return self.span_coloring[len(segment[1])]

        return self.case_coloring[self.ambiguity_resolver(spans[segment[1][0]])]