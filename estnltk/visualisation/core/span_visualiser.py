class SpanDecorator:
    """Superclass of plain_span_visualisers, defining functions for both of them"""
    default_conf_colour = "red"
    js_file=""

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

    def js(self):
        with open(self.js_file) as js_file:
            contents = js_file.read()
            output = ''.join(["<script>\n", contents, "</script>"])
        return output

    def default_class_mapper(self, segment):
        if len(segment[1]) > 1:
            return "overlapping-span"
        return "span"