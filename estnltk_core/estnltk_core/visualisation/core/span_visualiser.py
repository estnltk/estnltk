class SpanVisualiser:
    """Superclass of plain_span_visualisers, defining functions for both of them"""
    default_conf_colour = "red"

    def default_bg_mapping(self, segment):
        if len(segment[1]) > 1:
            return self.default_conf_colour

        return "yellow"

    def is_pure_text(self, segment):
        if len(segment[1]) > 0:
            return False
        return True

    def default_class_mapper(self, segment, index):
        if type(segment[1]) is list:
            if len(segment[1]) > 1:
                return "'span"+index+ " overlapping-span"+index+"'"
        elif len(segment[1].annotations) > 1:
            return "'span"+index+ " overlapping-span"+index+"'"
        return "'span"+index+ " plain-span"+index+"'"
