from estnltk.taggers import RegexTagger
from estnltk.taggers.tagger_new import TaggerNew

from .unit_vocabulary import vocabulary


class UnitTagger(TaggerNew):
    """
    Tags units.
    """
    description = 'Tags units.'
    depends_on = []
    conf_param = ['tagger']

    def __init__(self,
                 attributes=('grammar_symbol', 'regex_type', 'value'),
                 conflict_resolving_strategy='MAX',
                 overlapped=True,
                 layer_name='units',
                 ):
        self.attributes = attributes
        self.layer_name = layer_name
        self.tagger = RegexTagger(vocabulary,
                                  attributes,
                                  conflict_resolving_strategy,
                                  overlapped,
                                  layer_name)

    def make_layer(self, raw_text, input_layers, status):
        return self.tagger.make_layer(raw_text, status=status)
