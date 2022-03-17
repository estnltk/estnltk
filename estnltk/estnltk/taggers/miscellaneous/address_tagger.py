from estnltk.legacy.dict_taggers.span_tagger import SpanTagger
from estnltk.legacy.dict_taggers.regex_tagger import RegexTagger
from estnltk.legacy.dict_taggers.phrase_tagger import PhraseTagger
import re
from estnltk.taggers.system.grammar_taggers.finite_grammar import Rule, Grammar
from estnltk.taggers import Tagger
from estnltk.taggers import Atomizer
from estnltk.taggers import MergeTagger
from estnltk.taggers import GrammarParsingTagger
from estnltk.taggers import GapTagger
from os import path


class AddressPartTagger(Tagger):
    """
    Tags address parts.
    """

    conf_param = ['house_nr_tagger','zip_code_tagger', 'spec_voc_tagger', 'street_name_tagger', 'place_name_tagger',
                  'atomizer2', 'atomizer2a', 'atomizer3', 'gaps_tagger', 'merge_tagger',
                  'merge_tagger2']

    def __init__(self,
                 output_attributes=('grammar_symbol', 'type'),
                 # conflict_resolving_strategy: str = 'MAX',
                 # overlapped: bool = True,
                 output_layer: str = 'address_parts',
                 input_words_layer: str = 'words',
                 # output_nodes={'ADDRESS'}
                 ):
        self.input_layers = [input_words_layer]
        self.output_attributes = tuple(output_attributes)
        self.output_layer = output_layer
        # priority_attribute = '_priority_'

        house_nr_voc = [
        {'grammar_symbol': 'MAJA',
         'regex_type': 'house_nr',
         '_regex_pattern_': r'([0-9]{1,3}([abcdefghijkABCDEFGHIJK])?/?){1,3}(\s*-\s*[0-9]{1,3})?',
         '_group_': 0,
         '_priority_': 1,
         '_validator_': lambda m: not re.search(r'[0-9]{4,}', m.group(0)),
         'value': lambda m: re.search(r'([0-9]{1,3}([abcdefghijkABCDEFGHIJK])?/?){1,3}(\s*-\s*[0-9]{1,3})?', 
                                      m.group(0)).group(0)}]

        self.house_nr_tagger = RegexTagger(output_layer='house_nr',
                                           vocabulary=house_nr_voc,
                                           ambiguous=True,
                                           output_attributes=('grammar_symbol', 'regex_type', 'value'))
        
        zip_code_voc = [
        {'grammar_symbol': 'INDEKS',
         'regex_type': 'zip_code',
         '_regex_pattern_': r'[0-9]{5}',
         '_group_': 0,
         '_priority_': 1,
         '_validator_': lambda m: True,
         'value': lambda m: m.group(0)}]
        
        self.zip_code_tagger = RegexTagger(output_layer='zip_code',
                                           vocabulary=zip_code_voc,
                                           ambiguous=True,
                                           output_attributes=('grammar_symbol', 'regex_type', 'value'))
        
        vocabulary_file1 = path.join(path.dirname(__file__), 'asula_vocabulary.csv')

        self.place_name_tagger = PhraseTagger(output_layer='place_name',
                                              input_layer=input_words_layer,
                                              input_attribute='text',
                                              vocabulary=vocabulary_file1,
                                              key='_phrase_',
                                              output_ambiguous=True,
                                              output_attributes=['type', 'grammar_symbol'],
                                              conflict_resolving_strategy='MAX')
        
        vocabulary_file2 = path.join(path.dirname(__file__), 'street_vocabulary.csv')

        self.street_name_tagger = PhraseTagger(output_layer='street_name',
                                         input_layer=input_words_layer,
                                         input_attribute='text',
                                         vocabulary=vocabulary_file2,
                                         key='_phrase_',
                                         output_ambiguous=True,
                                         output_attributes=['type', 'grammar_symbol'],
                                         conflict_resolving_strategy='MAX') 
                                         
        '''vocabulary_file3 = path.join(path.dirname(__file__), 'farm_vocabulary.csv')

        self.farm_name_tagger = PhraseTagger(output_layer='farm_name',
                                         input_layer=input_words_layer,
                                         input_attribute='text',
                                         vocabulary=vocabulary_file3,
                                         key='_phrase_',
                                         output_ambiguous=True,
                                         output_attributes=['type', 'grammar_symbol'],
                                         conflict_resolving_strategy='MAX')  '''                                                                  

        spec_word_vocabulary = path.join(path.dirname(__file__), 'spec_word_voc.csv')

        self.spec_voc_tagger = SpanTagger(output_layer='spec_word',
                                          input_layer=input_words_layer,
                                          input_attribute='text',
                                          ambiguous=True,
                                          output_attributes=('type', 'grammar_symbol'),
                                          vocabulary=spec_word_vocabulary)

        self.atomizer2 = Atomizer(output_layer='some_layer2',
                             input_layer='place_name',
                             output_attributes=['grammar_symbol', 'type'],  # default: None
                             enveloping=None  # default: None
                             )
        self.atomizer2a = Atomizer(output_layer='some_layer2a',
                             input_layer='street_name',
                             output_attributes=['grammar_symbol', 'type'],  # default: None
                             enveloping=None  # default: None
                             )
                             
        '''self.atomizer2b = Atomizer(output_layer='some_layer2b',
                             input_layer='farm_name',
                             output_attributes=['grammar_symbol', 'type'],  # default: None
                             enveloping=None  # default: None
                             )   '''                                         

        self.atomizer3 = Atomizer(output_layer='some_layer3',
                             input_layer='spec_word',
                             output_attributes=['grammar_symbol', 'type'],  # default: None
                             enveloping=None  # default: None
                             )
        
        def gaps_decorator(text:str):
            return {'gap_length':len(text), 'grammar_symbol': 'RANDOM_TEXT'}
        
        def trim(t: str) -> str:
            # t = re.sub('[-\.,;!:? ]', '', t)
            t = t.strip(r'[]-\.,;!:?\n\t ')
            return t
        
        self.gaps_tagger = GapTagger(output_layer='gaps',
                                 input_layers=[
                                            'house_nr',
                                            'zip_code',
                                            'some_layer2',
                                            'some_layer2a',
                                            #'some_layer2b',
                                            'some_layer3'
                                              ],
                                 #enveloped_layer='morph_analysis',
                                 decorator=gaps_decorator,
                                 trim = trim,
                                 ambiguous=True,
                                 output_attributes=['grammar_symbol']) 
        
        self.merge_tagger = MergeTagger(output_layer=self.output_layer,
                                        input_layers=[
                                            'house_nr',
                                            'zip_code',
                                            'some_layer2',
                                            'some_layer2a',
                                            #'some_layer2b',
                                            'some_layer3',
                                            'gaps'],
                                        output_attributes=self.output_attributes)
        self.merge_tagger2 = MergeTagger(output_layer=self.output_layer,
                                        input_layers=[
                                            'house_nr',
                                            'zip_code',
                                            'some_layer2',
                                            'some_layer2a',
                                            #'some_layer2b',
                                            'some_layer3'],
                                            #'gaps'],
                                        output_attributes=self.output_attributes)

    def _make_layer_template(self):
        return self.merge_tagger._make_layer_template()

    def _make_layer(self, text, layers, status):
        raw_text = text.text
        tmp_layers = layers.copy()
        tmp_layers['house_nr'] = self.house_nr_tagger.make_layer(text=text, layers=tmp_layers, status=status)
        tmp_layers['zip_code'] = self.zip_code_tagger.make_layer(text=text, layers=tmp_layers, status=status)
        tmp_layers['place_name'] = self.place_name_tagger.make_layer(text=text, layers=tmp_layers, status=status)
        tmp_layers['street_name'] = self.street_name_tagger.make_layer(text=text, layers=tmp_layers, status=status)
        #tmp_layers['farm_name'] = self.farm_name_tagger.make_layer(raw_text, tmp_layers, status)
        tmp_layers['spec_word'] = self.spec_voc_tagger.make_layer(text=text, layers=tmp_layers, status=status)
        tmp_layers['some_layer2'] = self.atomizer2.make_layer(text=text, layers=tmp_layers, status=status)
        tmp_layers['some_layer2a'] = self.atomizer2a.make_layer(text=text, layers=tmp_layers, status=status)
        #tmp_layers['some_layer2b'] = self.atomizer2b.make_layer(raw_text, tmp_layers, status)
        tmp_layers['some_layer3'] = self.atomizer3.make_layer(text=text, layers=tmp_layers, status=status)
        tmp_layers['gaps'] = self.gaps_tagger.make_layer(text=text, layers=tmp_layers, status=status)
  
        return self.merge_tagger.make_layer(text=text, layers=tmp_layers, status=status)


class AddressGrammarTagger(Tagger):
    """Parses addresses using address grammar."""
    input_layers = ['address_parts']
    conf_param = ['tagger']

    def address_decorator(nodes):
        #composition = {}
        asula = ''
        maakond = ''
        t2nav = ''
        indeks = ''
        maja = ''
        for node in nodes:   
            if node.name == 'ASULA':
                asula = node.text
            elif node.name == 'TÄNAV':
                t2nav = node.text
            elif node.name == 'MAAKOND':
                maakond = node.text
            elif node.name == 'MAJA':
                maja = node.text  
            elif node.name == 'INDEKS':
                indeks = node.text    
            #if node.name != 'SPEC':
            #    composition[node.name] = node.text
        return {'grammar_symbol': 'ADDRESS', 'ASULA': asula, 'TÄNAV': t2nav, 'INDEKS': indeks, 'MAAKOND': maakond, 'MAJA': maja}


    grammar = Grammar(start_symbols=[ 'ADDRESS'],
                       depth_limit = 4,
                      legal_attributes=['type', 'grammar_symbol', 'composition', 'ASULA', 'TÄNAV', 'INDEKS', 'MAAKOND', 'MAJA'])  # , 'text1'

    
    grammar.add(Rule('ADDRESS',
                     'TÄNAV MAJA',
                     decorator=address_decorator,
                     group='g0',
                     priority=5))

    grammar.add(Rule('ADDRESS',
                     'TÄNAV MAJA ASULA',
                     decorator=address_decorator,
                     group='g0',
                     priority=3))
    
    grammar.add(Rule('ADDRESS',
                     'TÄNAV MAJA ASULA INDEKS',
                     decorator=address_decorator,
                     group='g0',
                     priority=2))

    grammar.add(Rule('ADDRESS',
                     'TÄNAV MAJA ASULA INDEKS MAAKOND',
                     decorator=address_decorator,
                     group='g0',
                     priority=1))
    
    grammar.add(Rule('ADDRESS',
                     'TÄNAV MAJA INDEKS ASULA MAAKOND',
                     decorator=address_decorator,
                     group='g0', priority = 1))
    
    grammar.add(Rule('ADDRESS',
                     'TÄNAV MAJA INDEKS ASULA',
                     decorator=address_decorator,
                     group='g0', priority = 2))
    
    grammar.add(Rule('ADDRESS',
                     'TÄNAV SPEC MAJA',
                     decorator=address_decorator, group = 'g0', priority = 4))
    grammar.add(Rule('ADDRESS',
                     'TÄNAV SPEC MAJA ASULA',
                     decorator=address_decorator, group = 'g0', priority = 2))
    
    grammar.add(Rule('ADDRESS',
                     'ASULA TÄNAV MAJA',
                     decorator=address_decorator,
                     group='g0',
                     priority=3))
    
    grammar.add(Rule('ADDRESS',
                     'MAAKOND ASULA TÄNAV MAJA',
                     decorator=address_decorator,
                     group='g0',
                     priority=2))
    
    grammar.add(Rule('ADDRESS',
                     'ASULA MAAKOND',
                     decorator=address_decorator,
                     group='g0',
                     priority=10))
    
    #grammar.add(Rule('ADDRESS',
    #                 'ASULA ASULA MAAKOND',
    #                 decorator=address_decorator,
    #                 group='g0',
    #                 priority=9))  
    
    grammar.add(Rule('ADDRESS',
                     'INDEKS ASULA MAAKOND',
                     decorator=address_decorator,
                     group='g0',
                     priority=9))
    
    #grammar.add(Rule('ADDRESS',
    #                 'ASULA',
    #                 decorator=address_decorator,
    #                 group='g0',
    #                 priority=11))
    
    def __init__(self,
                 output_layer='addresses',
                 input_layer='address_parts'):
        self.output_attributes = ('grammar_symbol', 'TÄNAV', 'MAJA', 'ASULA', 'MAAKOND', 'INDEKS')
        self.tagger = GrammarParsingTagger(  # output_layer=self.output_layer,
            # output_attributes=self.output_attributes,#, 'unknown'],
            output_layer=output_layer,
            layer_of_tokens=input_layer,
            attributes=self.output_attributes,
            grammar=self.grammar,
            output_nodes=['ADDRESS'],
            output_ambiguous=True)
        self.input_layers = [input_layer]
        self.output_layer = output_layer

    def _make_layer_template(self):
        return self.tagger._make_layer_template()

    def _make_layer(self, text, layers, status):
        return self.tagger.make_layer(text=text, layers=layers, status=status)
