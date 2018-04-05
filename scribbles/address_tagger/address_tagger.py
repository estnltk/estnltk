from estnltk.taggers import RegexTagger, SpanTagger, PhraseTagger
import re
from estnltk.finite_grammar import Rule, Grammar
from estnltk.taggers import Tagger
from estnltk.taggers import Atomizer
from estnltk.taggers import MergeTagger
from estnltk.taggers import GrammarParsingTagger


class AddressPartTagger(Tagger):
    """
    Tags address parts.
    """

    conf_param = ['house_nr_tagger', 'spec_voc_tagger', 'place_name_tagger',
                  'atomizer2', 'atomizer3', 'merge_tagger']
    input_layers = []

    def __init__(self,
                 output_attributes=['grammar_symbol'],
                 # conflict_resolving_strategy: str = 'MAX',
                 # overlapped: bool = True,
                 output_layer: str = 'address_parts',
                 # output_nodes={'ADDRESS'}
                 ):

        self.output_attributes = output_attributes
        self.output_layer = output_layer
        # priority_attribute = '_priority_'

        house_nr_voc = [
        {'grammar_symbol': 'HOUSE',
         'regex_type': 'house_nr',
         '_regex_pattern_': r'([0-9]{1,3}([abcdefghijkABCDEFGHIJK])?/?){1,3}(\s*-\s*[0-9]{1,3})?',
         '_group_': 0,
         '_priority_': 1,
         '_validator_': lambda m: not re.search(r'[0-9]{4,}', m.group(0)),
         'value': lambda m: re.search(r'([0-9]{1,3}([abcdefghijkABCDEFGHIJK])?/?){1,3}(\s*-\s*[0-9]{1,3})?', 
                                      m.group(0)).group(0)}]

        self.house_nr_tagger = RegexTagger(output_layer='house_nr',
                                           vocabulary=house_nr_voc,
                                           output_attributes=('grammar_symbol', 'regex_type', 'value'))

        vocabulary_file = 'name_vocabulary.csv'

        self.place_name_tagger = PhraseTagger(output_layer='place_name',
                                         input_layer='words',
                                         input_attribute='text',
                                         vocabulary=vocabulary_file,
                                         output_attributes=['type', 'grammar_symbol'],
                                         conflict_resolving_strategy='ALL')

        spec_word_vocabulary = 'spec_word_voc.csv'

        self.spec_voc_tagger = SpanTagger(output_layer='spec_word',
                                     input_layer='words',
                                     input_attribute='text',
                                     output_attributes=('type', 'grammar_symbol'),
                                     vocabulary=spec_word_vocabulary)

        self.atomizer2 = Atomizer(output_layer='some_layer2',
                             input_layer='place_name',
                             output_attributes=['grammar_symbol', 'type'],  # default: None
                             enveloping=None  # default: None
                             )

        self.atomizer3 = Atomizer(output_layer='some_layer3',
                             input_layer='spec_word',
                             output_attributes=['grammar_symbol', 'type'],  # default: None
                             enveloping=None  # default: None
                             )

        self.merge_tagger = MergeTagger(output_layer=self.output_layer,
                                        input_layers=[
                                            'house_nr',
                                            'some_layer2',
                                            'some_layer3'],
                                        output_attributes=('grammar_symbol',))

    def _make_layer(self, raw_text, layers, status):
        tmp_layers = layers.copy()
        tmp_layers['house_nr'] = self.house_nr_tagger.make_layer(raw_text, tmp_layers, status)
        tmp_layers['place_name'] = self.place_name_tagger.make_layer(raw_text, tmp_layers, status)
        tmp_layers['spec_word'] = self.spec_voc_tagger.make_layer(raw_text, tmp_layers, status)
        tmp_layers['some_layer2'] = self.atomizer2.make_layer(raw_text, tmp_layers, status)
        tmp_layers['some_layer3'] = self.atomizer3.make_layer(raw_text, tmp_layers, status)
        return self.merge_tagger.make_layer(raw_text, tmp_layers, status)


class AddressGrammarTagger(Tagger):
    """Parses addresses using address grammar."""
    input_layers = ['address_parts']
    conf_param = ['tagger']

    def address_decorator(node):
        return {'grammar_symbol': 'ADDRESS'}

    grammar = Grammar(start_symbols=['ADDRESS'],
                      # max_depth = 4,
                      legal_attributes=['type', 'grammar_symbol'])  # , 'text1'

    grammar.add(Rule('ADDRESS',
                     'TÄNAV HOUSE',
                     decorator=address_decorator,
                     group='g0',
                     priority=5))

    grammar.add(Rule('ADDRESS',
                     'TÄNAV HOUSE LINN',
                     decorator=address_decorator,
                     group='g0',
                     priority=3))

    grammar.add(Rule('ADDRESS',
                     'TÄNAV SPEC HOUSE',
                     decorator=address_decorator))

    def __init__(self,
                 output_layer='addresses',
                 input_layer='address_parts'):
        self.tagger = GrammarParsingTagger(  # output_layer=self.output_layer,
            # output_attributes=self.output_attributes,#, 'unknown'],
            layer_name=output_layer,
            layer_of_tokens=input_layer,
            attributes=['grammar_symbol'],
            grammar=self.grammar,
            output_nodes=['ADDRESS'])
        self.input_layers = [input_layer]
        self.output_layer = output_layer

    def _make_layer(self, raw_text, layers, status):
        return self.tagger.make_layer(raw_text, layers, status)
