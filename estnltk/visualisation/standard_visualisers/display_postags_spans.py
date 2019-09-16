from estnltk.visualisation.span_visualiser.fancy_span_visualisation import DisplaySpans
from estnltk.visualisation.span_visualiser.direct_plain_span_visualiser import DirectPlainSpanVisualiser
from typing import Tuple, List, Union
from estnltk import Text, Layer

class DisplayPostagsSpans(DisplaySpans):
    """
    Visualises different part-of-speech tags in a text

    Provides default background colourschme for EstMorf and GT tagsets.
    Color scheme is controlled by two dictionary-like class attributes
    * pos_coloring[str]
    * span_coloring[int]

    The first coloring controls how spans with different POS-tags are
    colored. Default coloring can be changed by assigning appropriate
    entries, e.g. pos_coloring['V'] = 'black'.

    The second controls how span overlaps are colored. The tokenization
    into the words can be ambiguous. By default, overlaps are colored
    by two shades of red. This can be changed by assigning appropriate
    entries, e.g. span_coloring[2] = 'blue'.

    To redefine the entire color scheme, the entire colouring attribute
    must be redefined. The assigned object must support indexing with
    any string for pos_coloring and any int for span_coloring.

    As POS-tagging may be ambiguous, coloring is done in two phases:
    1. list of POS-tags is aggregated into a new string label
    2. POS-tag coloring is used to determine the background color

    The default aggregator marks all ambigious labellings with '*'.
    It is possible to customise this by redefining ambiguity_resolver.
    """

    def __init__(self, layer: str = 'morph_analysis', tagset: str = 'EstMorf', ambiguity_resolver: callable = None):
        super(DisplayPostagsSpans, self).__init__(styling="direct")

        # Hack to get it working by replacing a wrong base class
        self.span_decorator = DirectPlainSpanVisualiser()

        self.morph_layer = layer
        self.tagset = tagset
        self.__default_ambiguity_resolver = ambiguity_resolver or self.__default_ambiguity_resolver
        self.span_decorator.bg_mapping = self.__bg_mapper
        self.restore_defaults()

    def restore_defaults(self):
        """Restore default coloring scheme for part-of-speech tags and token overlaps and ambiguity resolver"""

        self.ambiguity_resolver = self.__default_ambiguity_resolver

        self.pos_coloring = {}
        if self.tagset == 'EstMorf' or self.tagset == 'GT':
            self.pos_coloring['S'] = 'orange'
            self.pos_coloring['H'] = 'orange'
            self.pos_coloring['A'] = 'yellow'
            self.pos_coloring['U'] = 'yellow'
            self.pos_coloring['C'] = 'yellow'
            self.pos_coloring['N'] = 'yellow'
            self.pos_coloring['O'] = 'yellow'
            self.pos_coloring['V'] = 'lime'
            self.pos_coloring['*'] = 'gray'

        # Define two shades of red for overlapping tokenization
        self.span_coloring = {2: '#FF5050'}

    def __call__(self, object: Union[Text, Layer]) -> str:
        if isinstance(object, Text):
            return super(DisplayPostagsSpans, self).__call__(object[self.morph_layer])
        elif isinstance(object, Layer):
            return super(DisplayPostagsSpans, self).__call__(object)
        else:
            raise ValueError('Invalid input')

    def __default_ambiguity_resolver(self, span) -> str:
        pos_tags = set(span['partofspeech'])
        if len(pos_tags) == 1:
            return next(iter(pos_tags));
        return '*'

    def __bg_mapper(self, segment: Tuple[str, List[int]], spans) -> str:

        if len(segment[1]) != 1:
            return self.span_coloring.get(len(segment[1]), '#FF0000')

        return self.pos_coloring.get(self.ambiguity_resolver(spans[segment[1][0]]), '#ffffff00')