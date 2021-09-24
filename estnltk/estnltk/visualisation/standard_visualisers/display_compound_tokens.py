from estnltk.visualisation.span_visualiser.fancy_span_visualisation import DisplaySpans
from estnltk.visualisation.span_visualiser.direct_plain_span_visualiser import DirectPlainSpanVisualiser
from typing import Tuple, List, Union
from estnltk import Text, Layer
from collections import defaultdict

class DisplayCompoundTokens(DisplaySpans):
    """
    Visualizes subtypes of compound tokens in a text

    Default background color scheme is following:
    * type_coloring[str]
    * span_coloring[int]

    The first coloring controls how spans with different compound tokens
    are colored. Default coloring can be changed by assigning appropriate
    entries, e.g. type_coloring['numeric'] = 'black'.

    The second controls how span overlaps are colored. Tokenization
    into words can be ambiguous. By default, overlaps are colored
    in two shades of red. This can be changed by assigning appropriate
    entries, e.g. span_coloring[2] = 'blue'.

    To redefine the entire color scheme, the entire colouring attribute
    must be redefined. The assigned object must support indexing with
    any string for type_coloring and any int for span_coloring.

    As a compound can have multiple type labels, colouring is done in two phases:
    1. list of type tags is aggregated into a new string label
    2. type tag coloring is used to determine the background color

    The default aggregator removes 'sign' attribute and marks all ambigious
    labellings with '*'. It is possible to customize this by redefining
    ambiguity_resolver.
    """

    def __init__(self, layer: str = 'compound_tokens', ambiguity_resolver: callable = None):
        super(DisplayCompoundTokens, self).__init__(styling="direct")

        # Hack to get it working by replacing a wrong base class
        self.span_decorator = DirectPlainSpanVisualiser()

        self.compound_layer = layer
        self.__default_ambiguity_resolver = ambiguity_resolver or self.__default_ambiguity_resolver
        self.restore_defaults()

    def restore_defaults(self):
        """Restore default coloring scheme for compound tokens and ambiguity resolver for compound subtypes"""

        self.ambiguity_resolver = self.__default_ambiguity_resolver
        self.span_decorator.bg_mapping = self.__bg_mapper

        # Define two shades of red for overlapping tokenisation
        self.span_coloring = defaultdict(lambda: '#FF0000')
        self.span_coloring[2] = '#FF5050'

        # Define coloring for different types of compounds
        self.type_coloring = defaultdict(lambda: '#ffffff00')

        # Proper names
        self.type_coloring['name_with_initial'] = '#6CA390'
        self.type_coloring['case_ending'] = '#6CA390'

        # Rare wordforms
        self.type_coloring['hyphenation'] = '#306754'

        # Numbers and units
        self.type_coloring['numeric_date'] = '#9DC209'
        self.type_coloring['numeric'] = '#9DC209'
        self.type_coloring['percentage'] = '#9DC209'
        self.type_coloring['unit'] = '#759A00'

        # Abbrevations
        self.type_coloring['non_ending_abbreviation'] = '#BCE954'
        self.type_coloring['abbreviation'] = '#BCE954'

        # Web specific compounds
        self.type_coloring['xml_tag'] = '#5E5A80'
        self.type_coloring['email'] = '#908CB2'
        self.type_coloring['www_address'] = '#908CB2'

        # Emotiocons
        self.type_coloring['emoticon'] = '#FFDB58'

        # All the rest
        self.type_coloring['*'] = '#FFA62F'

    def __call__(self, object: Union[Text, Layer]) -> str:
        if isinstance(object, Text):
            return super(DisplayCompoundTokens, self).__call__(object[self.compound_layer])
        elif isinstance(object, Layer):
            return super(DisplayCompoundTokens, self).__call__(object)
        else:
            raise ValueError('Invalid input')

    def __default_ambiguity_resolver(self, span) -> str:

        types = set(span.type)
        types.discard('sign')
        if len(types) == 1:
            return next(iter(types));
        return '*'

    def __bg_mapper(self, segment: Tuple[str, List[int]], spans) -> str:

        if len(segment[1]) != 1:
            return self.span_coloring[len(segment[1])]

        return self.type_coloring[self.ambiguity_resolver(spans[segment[1][0]])]