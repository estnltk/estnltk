from estnltk.visualisation.span_visualiser.fancy_span_visualisation import DisplaySpans
from estnltk.visualisation.span_visualiser.direct_plain_span_visualiser import DirectPlainSpanVisualiser
from typing import Tuple, List, Union
from estnltk import Text, Layer
from collections import defaultdict

class DisplayCompoundWords(DisplaySpans):
    """
    Visualizes compound words in a text

    Default background color scheme is following:
    * word_coloring[str]
    * span_coloring[int]

    The first coloring controls how simple and compound words are colored.
    Default coloring can be changed by assigning appropriate entries, e.g.
    case_coloring['simple'] = 'blue'.

    The second controls how span overlaps are colored. Tokenization
    into words can be ambiguous. By default, overlaps are colored
    in two shades of red. This can be changed by assigning appropriate
    entries, e.g. span_coloring[2] = 'blue'.

    To redefine the entire color scheme, the entire colouring attribute
    must be redefined. The assigned object must support indexing with
    any string for type_coloring and any int for span_coloring.

    As a word can have multiple analyses, coloring is done in two phases:
    1. list of root_word tags is aggregated into a new string label
    2. case tag coloring is used to determine the background color

    The default aggregator marks a word as a compound if it is a compound
    according to at least one analysis. It is possible to customise
    this by redefining ambiguity_resolver.
    """

    def __init__(self, layer: str = 'morph_analysis', ambiguity_resolver: callable = None):
        super(DisplayCompoundWords, self).__init__(styling="direct")

        # Hack to get it working by replacing a wrong base class
        self.span_decorator = DirectPlainSpanVisualiser()

        self.morph_layer = layer
        self.__default_resolver = ambiguity_resolver or self.__default_ambiguity_resolver
        self.restore_defaults()

    def restore_defaults(self):

        self.ambiguity_resolver = self.__default_ambiguity_resolver
        self.span_decorator.bg_mapping = self.__bg_mapper

        # Define two shades of red for overlapping tokenisation
        self.span_coloring = defaultdict(lambda: '#FF0000')
        self.span_coloring[2] = '#FF5050'

        # Define coloring for different types of compounds
        self.word_coloring = defaultdict(lambda: '#ffffff00')

        # Colors compound words in millennial pink
        self.word_coloring['simple'] = '#ffffff00'
        self.word_coloring['compound'] = '#ffb6c1'

    def __call__(self, object: Union[Text, Layer]) -> str:
        if isinstance(object, Text):
            return super(DisplayCompoundWords, self).__call__(object[self.morph_layer])
        elif isinstance(object, Layer):
            return super(DisplayCompoundWords, self).__call__(object)
        else:
            raise ValueError('Invalid input')

    def __default_ambiguity_resolver(self, span) -> str:

        compound_counts = max(len(an.root_tokens) for an in span.annotations)

        if compound_counts == 1:
            return 'simple'
        else:
            return 'compound'

    def __bg_mapper(self, segment: Tuple[str, List[int]], spans) -> str:

        if len(segment[1]) != 1:
            return self.span_coloring[len(segment[1])]

        return self.word_coloring[self.ambiguity_resolver(spans[segment[1][0]])]