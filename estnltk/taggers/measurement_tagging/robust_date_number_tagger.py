from estnltk.taggers import RegexTagger
from estnltk.taggers.tagger_new import TaggerNew

from .robust_date_number_vocabulary import vocabulary as voc


class RobustDateNumberTagger(TaggerNew):
    """
    Tags dates and numbers.
    """
    description = 'Tags dates and numbers.'
    depends_on = []
    conf_param = ['tagger']

    def __init__(self,
                 attributes=('grammar_symbol', 'regex_type', 'value'),
                 conflict_resolving_strategy='MAX',
                 overlapped=True,
                 layer_name='dates_numbers',
                 ):
        self.attributes = attributes
        self.layer_name = layer_name
        self.tagger = RegexTagger(voc,
                                  attributes,
                                  conflict_resolving_strategy,
                                  overlapped,
                                  layer_name)

    def make_layer(self, text, input_layers, status):
        return self.tagger.make_layer(text, status=status)
