#class DirectPlainSpanVisualiser(SpanDecorator):
class DirectPlainSpanVisualiser():
    
    default_conf_colour = "red"
    
    def __init__(self, colour_mapping=None, bg_mapping=None, fill_empty_spans=False):
        self.bg_mapping = bg_mapping or self.default_bg_mapping
        self.colour_mapping = colour_mapping
        self.fill_empty_spans = fill_empty_spans
        #self.colour_mapping = colour_mapping or default_color_mapping
        pass
    
    def __call__(self, segment):
        
        output=''
    
        # Simple text no span to fill
        if not self.fill_empty_spans and self.is_pure_text(segment):
            output+=segment[0]
        else:
            # There is a span to decorate
            output += '<span style='
            if self.colour_mapping is not None:
                output += 'color:' + self.color_mapping(segment)
            if self.bg_mapping is not None:
                output += 'background:'+ self.bg_mapping(segment)
            output += '>'
            output += segment[0]
            output += '</span>'

        return output

    def default_bg_mapping(self, segment):
        if len(segment[1]) > 1:
            return self.default_conf_colour
    
        return "yellow"
    
    def is_pure_text(self,segment):
        if len(segment[1])>0:
            return False
        return True
