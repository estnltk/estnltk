from estnltk.visualisation.span_visualiser.fancy_span_visualisation import DisplaySpans
from collections import defaultdict
from estnltk.visualisation.span_visualiser.direct_plain_span_visualiser import DirectPlainSpanVisualiser
from typing import Tuple, List


class DisplayAmbiguousSpans(DisplaySpans):
    """
    Displays overlaps between spans and spans with multiple annotations

    Default background color scheme is following:
    * normal spans are transparent
    * overlapping spans are red
    * ambiguous spans are orange

    The opacity level indicates the number of overlaps and annotations

    Color scheme is controlled by two dictionary-like class attributes
    * span_coloring[int]
    * annotation_coloring[int]

    Assigning corresponding elements redefines the coloring for a particular
    number of annotations or spans, e.g. span_coloring[2] = 'blue'.

    Assigning corresponding attributes redefines the entire color scheme.
    The assigned object must support indexing with any int.
    """

    def __init__(self):
        super(DisplayAmbiguousSpans, self).__init__(styling="direct")

        # Hack to get it working by replacing a wrong base class
        self.span_decorator = DirectPlainSpanVisualiser()

        self.restore_defaults()
        self.span_decorator.bg_mapping = self.__bg_mapper

    def restore_defaults(self):
        """Restore default coloring scheme for overlaps and ambigous spans"""

        # Define two shades of red for overlaps
        self.span_coloring = defaultdict(lambda: '#FF0000')
        self.span_coloring[2] = '#FF5050'

        # Define transparent + two shades of orange for ambigious annotations
        self.annotation_coloring = defaultdict(lambda: '#F59B00')
        self.annotation_coloring[1] = '#FFA50000'
        self.annotation_coloring[2] = '#FFA500'

    def __bg_mapper(self, segment: Tuple[str, List[int]], spans) -> str:
        if len(segment[1]) != 1:
            return self.span_coloring[segment[1]]

        return self.annotation_coloring[len(spans[segment[1][0]].annotations)]