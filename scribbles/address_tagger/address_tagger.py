from estnltk import Text
from estnltk.taggers import RegexTagger, SpanTagger, PhraseTagger
import csv
import re
from collections import defaultdict, Counter
from estnltk.finite_grammar import Rule, Grammar
from estnltk.taggers import Vocabulary
from estnltk.taggers import TaggerOld
from estnltk.taggers import Atomizer
from estnltk.taggers import MergeTagger
from estnltk.taggers import GrammarParsingTagger
                              
class AddressTagger(TaggerOld):
    """
    Tags addresses.
    """
    #input_layers = ['words']
    #conf_param = ['tagger']
    
    description = 'xxx'
    attributes = None
    configuration = {}
    depends_on = []
    layer_name = ''
    
    

    def __init__(self,
				layer_name = 'addresses',
                 #output_attributes: ('grammar_symbol',),
                 conflict_resolving_strategy: str = 'MAX',
                 overlapped: bool = True,
                 #output_layer: str = 'addresses',
                 output_nodes={'ADDRESS'}
                 ):

        #self.output_attributes = output_attributes
        #self.output_layer = output_layer
        #priority_attribute = '_priority_'
        
        
        house_nr_voc = [
        {'grammar_symbol': 'HOUSE',
         'regex_type': 'house_nr',
         '_regex_pattern_': r'([0-9]{1,3}([abcdefghijkABCDEFGHIJK])?/?){1,3}(\s*-\s*[0-9]{1,3})?',
         '_group_': 0,
         '_priority_': 1,
         '_validator_': lambda m: not re.search(r'[0-9]{4,}', m.group(0)),
         'value': lambda m: re.search(r'([0-9]{1,3}([abcdefghijkABCDEFGHIJK])?/?){1,3}(\s*-\s*[0-9]{1,3})?', 
                                      m.group(0)).group(0)}]
        
        
        house_nr_tagger = RegexTagger(vocabulary = house_nr_voc, output_attributes = ('grammar_symbol', 'regex_type', 'value'))
        
        
        vocabulary_file = 'name_vocabulary.csv'
        
        place_name_tagger = PhraseTagger(output_layer='phrases',
                      input_layer='words',
                      input_attribute='text',
                      vocabulary=vocabulary_file,
                      output_attributes=['type', 'grammar_symbol'],
                      conflict_resolving_strategy='ALL')
                      
        spec_word_vocabulary = 'spec_word_voc.csv'
        
        spec_voc_tagger = SpanTagger(
            output_layer='spec_word',
            input_layer = 'words', 
            input_attribute = 'text',
            output_attributes = ('type', 'grammar_symbol'),
            vocabulary = spec_word_vocabulary)              
        
        
        def tag_sent(sent):
            t = Text(sent).analyse('segmentation')
            house_nr_tagger.tag(t)
            place_name_tagger.tag(t)
            spec_voc_tagger.tag(t)
            #merge_tagger.tag(t)
            return t    
            
        rules = []

        def address_decorator(node):
            return {'grammar_symbol': 'ADDRESS'}

        rules.append(Rule('ADDRESS', 'TÄNAV HOUSE',
                       decorator = address_decorator, group = 'g0', priority = 5))

        rules.append(Rule('ADDRESS', 'TÄNAV HOUSE LINN',
                       decorator = address_decorator,group = 'g0', priority = 3))
            
        rules.append(Rule('ADDRESS', 'TÄNAV SPEC HOUSE',
                       decorator = address_decorator))

        grammar = Grammar(start_symbols=['ADDRESS'
                                        
                                        ], rules=rules, #max_depth = 4, 
                         legal_attributes=['type', 'grammar_symbol'])#, 'text1'    
                         
        self._tagger = GrammarParsingTagger(#output_layer=self.output_layer,
                                   #output_attributes=self.output_attributes,#, 'unknown'],
                                      layer_name = 'addresses',
                                      layer_of_tokens='grammar_tags',
                                      attributes = ['grammar_symbol'],
                                      grammar=grammar,
                                     output_nodes={'ADDRESS'})       
                                     
        

        #self.configuration = self._tagger.configuration                             
                                                                  
    
    def _make_layer(self, raw_text, layers, status):
        return self._tagger.make_layer(raw_text, layers, status)
    
    def tag(self, text, return_layer=False):
        """
        xx
        """
        return self._tagger.tag(text, return_layer=return_layer)
