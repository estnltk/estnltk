from estnltk.web_taggers import WebTagger


class VabamorfWebTagger(WebTagger):
    """Tags morphological analysis using EstNLTK web service."""

    def __init__(self, url, output_layer='morph_analysis'):
        self.input_layers = ('words', 'sentences', 'compound_tokens')
        self.output_layer = output_layer
        self.output_attributes = ('normalized_text', 'lemma', 'root', 'root_tokens', 'ending', 'clitic', 'form',
                                  'partofspeech')
        self.url = url
