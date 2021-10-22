from estnltk.web_taggers import WebTagger


class SoftmaxEmbTagSumWebTagger(WebTagger):
    """Performs neural morphological tagging using EstNLTK web service.

    See also SoftmaxEmbTagSumTagger documentation.
    """

    def __init__(self, url, output_layer='neural_morph_analysis'):
        self.url = url
        self.input_layers = ('morph_analysis', 'sentences', 'words')
        self.output_attributes = ('morphtag', 'pos', 'form')
        self.output_layer = output_layer
