from estnltk.taggers import WebTagger


class BertEmbeddingsWebTagger(WebTagger):
    """Tags BERT embeddings using EstNLTK web service.

    See also BertTagger documentation.

    """

    def __init__(self, url, output_layer='bert_embeddings'):
        self.url = url
        self.input_layers = ('sentences',)
        self.output_attributes = ['token', 'bert_embedding']
        self.output_layer = output_layer
