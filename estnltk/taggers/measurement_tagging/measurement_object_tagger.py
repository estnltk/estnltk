from estnltk.taggers import RegexTagger
from estnltk.taggers.tagger_new import TaggerNew

from .measurement_object_vocabulary import vocabulary as voc


class MeasurementObjectTagger(TaggerNew):
    """
    Tags measurement objects.
    """
    description = 'Tags measurement objects.'
    layer_name = None
    attributes = []
    depends_on = []
    conf_param = ['tagger']

    def __init__(self,
                 attributes=('grammar_symbol', 'regex_type', 'value'),
                 conflict_resolving_strategy='MAX',
                 overlapped=True,
                 layer_name='measurement_objects',
                 ):
        self.attributes = attributes
        self.layer_name = layer_name
        self.tagger = RegexTagger(voc,
                                  attributes,
                                  conflict_resolving_strategy,
                                  overlapped,
                                  layer_name)

    def change_layer(self, raw_text, input_layers, status):
        raise NotImplementedError()

    def make_layer(self, raw_text, input_layers, status):
        return self.tagger.make_layer(raw_text, status=status)
