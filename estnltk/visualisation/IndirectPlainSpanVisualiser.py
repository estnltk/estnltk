from estnltk.visualisation.span_decorator import SpanDecorator


class IndirectPlainSpanVisualiser(SpanDecorator):
    
    def __init__(self, id_mapping=None, class_mapping=None, fill_empty_spans=False):
        self.id_mapping = id_mapping
        self.class_mapping = class_mapping
        self.fill_empty_spans = fill_empty_spans
        pass
    
    def __call__(self, segment):
        
        output = ''
    
        # Simple text no span to fill
        if not self.fill_empty_spans and self.is_pure_text(segment):
            output += segment[0]
        else:
            # There is a span to decorate
            output += '<span'
            if self.id_mapping is not None:
                output += ' id=' + self.id_mapping(segment)
            if self.class_mapping is not None:
                output += ' class='+ self.class_mapping(segment)
            output += '>'
            output += segment[0]
            output += '</span>'

        return output
    
    def is_pure_text(self,segment):
        return len(segment[1]) == 0
