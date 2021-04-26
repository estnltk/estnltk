from typing import MutableMapping

from estnltk.text import Text
from estnltk.layer.layer import Layer
from estnltk.taggers import WebTagger

class BertEmbeddingsRequestTooLarge(Exception):
    pass

class BertEmbeddingsWebTagger(WebTagger):
    """Tags BERT embeddings using EstNLTK web service.

    See also BertTagger documentation.
    """

    def __init__(self, url, output_layer='bert_embeddings'):
        self.url = url
        self.input_layers = ('sentences',)
        self.output_attributes = ['token', 'bert_embedding']
        self.output_layer = output_layer

    def _make_layer(self, text: Text, layers: MutableMapping[str, Layer], status: dict):
        # Check the Text object size
        # Currently, the size limit is set to 150 words, which should result 
        # in Bert embedding sizes up to 20 MB (by a very rough estimation)
        number_of_words = len([w for sentence in layers['sentences'] for w in sentence])
        if number_of_words > 150:
            raise BertEmbeddingsRequestTooLarge('(!) The request Text object exceeds the web service '+\
            'limit 150 words per text. Please use EstNLTK\'s methods extract_sections or split_by to split '+\
            'the Text object into smaller Texts, and proceed by processing smaller Texts with the web service. '+\
            'More information about Text splitting: '+
            'https://github.com/estnltk/estnltk/blob/version_1.6/tutorials/system/layer_operations.ipynb ')
        return super()._make_layer(text, layers, status)

