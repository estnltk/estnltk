class SpanDecorator:
    default_conf_colour = "red"
    def default_bg_mapping(self, segment):
        if len(segment[1]) > 1:
            return self.default_conf_colour

        return "yellow"

    def is_pure_text(self, segment):
        if len(segment[1]) > 0:
            return False
        return True
    # call
    def css(self):
        return ''
