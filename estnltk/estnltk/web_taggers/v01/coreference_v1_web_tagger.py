from typing import MutableMapping

from estnltk import Text
from estnltk import Layer
from estnltk.web_taggers import BatchProcessingWebRelationTagger

class CoreferenceV1WebRelationTagger( BatchProcessingWebRelationTagger ):
    """Tags pronominal coreference relations using EstNLTK CoreferenceTagger's webservice.

    See also CoreferenceTagger's documentation:
    https://github.com/estnltk/estnltk/blob/b8ad0932a852daedb1e3eddeb02c944dd1f292ee/tutorials/nlp_pipeline/D_information_extraction/04_pronominal_coreference.ipynb
    """

    def __init__(self, url, output_layer='coreference_v1'):
        self.url = url
        self.output_layer = output_layer
        self.output_span_names = ('pronoun', 'mention')	
        self.output_attributes = ()
        self.input_layers = []
        self.batch_max_size = 175000
        self.batch_layer = None
        self.batch_enveloping_layer = None


