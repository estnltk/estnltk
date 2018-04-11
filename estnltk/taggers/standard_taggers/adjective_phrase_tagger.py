from estnltk.taggers import SpanTagger
from estnltk.text import Text
import re
from estnltk.finite_grammar import Rule, Grammar
from estnltk.taggers import Tagger
from estnltk.taggers import Atomizer
from estnltk.taggers import MergeTagger
from estnltk.taggers import GrammarParsingTagger
from estnltk.taggers import GapTagger
from os import path
from .adverbs import NOT_ADJ_MODIFIERS, CLASSES, WEIGHTS

class AdjectivePhrasePartTagger(Tagger):
    """
    Tags adjective phrases.
    """

    conf_param = ['adj_tagger','adv_tagger2', 'conj_tagger', 'adv_tagger', 'merge_tagger', 'atomizer1', 'atomizer2',
    'atomizer3', 'atomizer4', 'gaps_tagger', 'merge_tagger2']
    input_layers = []

    def __init__(self,
                 output_attributes=['grammar_symbol'],
                 output_layer: str = 'grammar_tags',
                 ):

        self.output_attributes = output_attributes
        self.output_layer = output_layer

        vocabulary = path.join(path.dirname(__file__), 'adj_modifiers.csv')
        

        self.adv_tagger = SpanTagger(output_layer='adv',
                    input_layer='morph_analysis',
                    input_attribute='lemma',
                    vocabulary=vocabulary,
                    output_attributes=['grammar_symbol'], # default: None
                    key='_token_', # default: '_token_'
                    ambiguous=False # default: False
                    )
                    
        adj_voc = [
        {'grammar_symbol': 'ADJ',
         '_token_': 'A'}, {'grammar_symbol': 'COMP', '_token_': 'C'}]
        
        self.adj_tagger = SpanTagger(output_layer='adj',
                    input_layer='morph_analysis',
                    input_attribute='partofspeech',
                    vocabulary=adj_voc,
                    output_attributes=['grammar_symbol'], # default: None
                    key='_token_', # default: '_token_'
                    ambiguous=False # default: False
                    )
                    
        adv_voc = [
        {'grammar_symbol': 'ADV2',
         '_token_': 'D'}]
        
        self.adv_tagger2 = SpanTagger(output_layer='adv2',
                    input_layer='morph_analysis',
                    input_attribute='partofspeech',
                    vocabulary=adv_voc,
                    output_attributes=['grammar_symbol'], # default: None
                    key='_token_', # default: '_token_'
                    ambiguous=False # default: False
                    )
        
        conj_voc = [
        {'grammar_symbol': 'CONJ',
         '_token_': 'J'}]
         
        self.conj_tagger = SpanTagger(output_layer='conj',
                    input_layer='morph_analysis',
                    input_attribute='partofspeech',
                    vocabulary=conj_voc,
                    output_attributes=['grammar_symbol'], # default: None
                    key='_token_', # default: '_token_'
                    ambiguous=False # default: False
                    )
        
        self.atomizer1 = Atomizer(output_layer='adv_',
                             input_layer='adv',
                             output_attributes=['grammar_symbol'],  # default: None
                             enveloping=None  # default: None
                             )
        self.atomizer2 = Atomizer(output_layer='adv2_',
                             input_layer='adv2',
                             output_attributes=['grammar_symbol'],  # default: None
                             enveloping=None  # default: None
                             )
        self.atomizer3 = Atomizer(output_layer='adj_',
                             input_layer='adj',
                             output_attributes=['grammar_symbol'],  # default: None
                             enveloping=None  # default: None
                             )
        self.atomizer4 = Atomizer(output_layer='conj_',
                             input_layer='conj',
                             output_attributes=['grammar_symbol'],  # default: None
                             enveloping=None  # default: None
                             )
        
        def gaps_decorator(text:str):
            return {'grammar_symbol': 'RANDOM_TEXT'}
        
        def trim(t:str) -> str:
            t = t.strip()
            return t
        
        self.gaps_tagger = GapTagger(output_layer='gaps',
                                 input_layers=['adv_', 'adv2_', 'adj_', 'conj_',],
                                 decorator=gaps_decorator,
                                 trim = trim,
                                 output_attributes=['grammar_symbol'])  
        
        self.merge_tagger = MergeTagger(output_layer='grammar_tags',
                           input_layers=['adv_', 'adv2_', 'adj_', 'conj_', 'gaps'],
                           output_attributes=['grammar_symbol'])
        
        self.merge_tagger2 = MergeTagger(output_layer='grammar_tags',
                           input_layers=['adv_', 'adv2_', 'adj_', 'conj_'],
                           output_attributes=['grammar_symbol'])
        
    def _make_layer(self, raw_text, layers, status):
        tmp_layers = layers.copy()
        tmp_layers['adv'] = self.adv_tagger.make_layer(raw_text, tmp_layers, status)
        tmp_layers['adj'] = self.adj_tagger.make_layer(raw_text, tmp_layers, status)
        tmp_layers['adv2'] = self.adv_tagger2.make_layer(raw_text, tmp_layers, status)
        tmp_layers['conj'] = self.conj_tagger.make_layer(raw_text, tmp_layers, status)
        tmp_layers['adv_'] = self.atomizer1.make_layer(raw_text, tmp_layers, status)
        tmp_layers['adv2_'] = self.atomizer2.make_layer(raw_text, tmp_layers, status)
        tmp_layers['adj_'] = self.atomizer3.make_layer(raw_text, tmp_layers, status)
        tmp_layers['conj_'] = self.atomizer4.make_layer(raw_text, tmp_layers, status) 
        
        s = 0 
        input_layers=['conj_', 'adv_', 'adv2_', 'adj_']
        
        for i in tmp_layers:
            if len(tmp_layers[i]) > 0 and i in input_layers:
                s = 1   
        if s == 1:      
            tmp_layers['gaps'] = self.gaps_tagger.make_layer(raw_text, tmp_layers, status)
        else:
            pass   
        if s == 1:     
            return self.merge_tagger.make_layer(raw_text, tmp_layers, status)
        else:
            return self.merge_tagger2.make_layer(raw_text, tmp_layers, status) 



class AdjectivePhraseGrammarTagger(Tagger):
    """Parses adjective phrases using grammar."""
    input_layers = ['grammar_tags']
    conf_param = ['temp_tagger', 'tagger']

    def adj_phrase_decorator(nodes):
        
        participle = False  
        
        from estnltk.resolve_layer_dag import make_resolver
        resolver = make_resolver(
                 disambiguate=False,
                 guess=False,
                 propername=False,
                 phonetic=False,
                 compound=True)
               
        possible_verb = Text(nodes[-1].text).analyse('morphology')#, resolver = resolver)
        if 'V' in possible_verb.partofspeech[0]:
            if possible_verb.text[-1] == 'v' or (possible_verb.text[-1] == 'd' and possible_verb.text[-2] == 'u'):
                participle = True
        
        adverb = nodes[0].text.lower()
        if adverb in CLASSES:
            adverb_class = CLASSES[adverb]
            adverb_weight = WEIGHTS[adverb_class]
        else:
            adverb_class = None
            adverb_weight = None
            
        if participle == False:    
            return {'type': 'adjective phrase', 'adverb_class': adverb_class, 'adverb_weight': adverb_weight}
        else:
            return {'type': 'participle phrase', 'adverb_class': adverb_class, 'adverb_weight': adverb_weight}

    def comp_phrase_decorator(nodes):
        adverb = nodes[0].text.lower()
        if adverb in CLASSES:
            adverb_class = CLASSES[adverb]
            adverb_weight = WEIGHTS[adverb_class]
        else:
            adverb_class = None
            adverb_weight = None
        return {'type': 'comparative phrase', 'adverb_class': adverb_class, 'adverb_weight': adverb_weight}

    def part_phrase_decorator(nodes):
        adverb = nodes[0].text.lower()
        if adverb in CLASSES:
            adverb_class = CLASSES[adverb]
            adverb_weight = WEIGHTS[adverb_class]
        else:
            adverb_class = None
            adverb_weight = None
        return {'type': 'participle phrase', 'adverb_class': adverb_class, 'adverb_weight': adverb_weight}
    
    def long_phrase_validator(nodes):
        if nodes[-2].text == 'kui':
            return False
        else:
            return True
    
    def part_phrase_validator(nodes):
        from estnltk.resolve_layer_dag import make_resolver
        resolver = make_resolver(
                 disambiguate=False,
                 guess=False,
                 propername=False,
                 phonetic=False,
                 compound=True)
        
        if nodes[0].text in NOT_ADJ_MODIFIERS:
            return False
            
        else:
            possible_verb = Text(nodes[-1].text).analyse('morphology')#, resolver = resolver)
            if 'V' in possible_verb.partofspeech[0]:
                if possible_verb.text[-1] == 'v' or (possible_verb.text[-1] == 'd' and possible_verb.text[-2] == 'u'):
                    return True
                else:
                    return False
            else:
                return False
                
    rules = []

    rules.append(Rule('ADJ_PHRASE', 'ADJ_M ADJ CONJ ADJ',
                    decorator = adj_phrase_decorator, validator = long_phrase_validator, group = 'g0', priority = -1))
    rules.append(Rule('ADJ_PHRASE', 'ADJ_M ADJ',
                    decorator = adj_phrase_decorator, group = 'g0', priority = 0))
    rules.append(Rule('ADJ_PHRASE', 'ADJ',
                    decorator = adj_phrase_decorator, group = 'g0', priority = 3))
    
    rules.append(Rule('COMP_PHRASE', 'COMP_M COMP CONJ COMP',
                    decorator = comp_phrase_decorator, validator = long_phrase_validator, group = 'g0', priority = -1))
    rules.append(Rule('COMP_PHRASE', 'COMP_M COMP',
                    decorator = comp_phrase_decorator, group = 'g0', priority = 0))
    rules.append(Rule('COMP_PHRASE', 'COMP',
                    decorator = comp_phrase_decorator, group = 'g0', priority = 2))
    
    rules.append(Rule('PART_PHRASE', 'ADV ADJ',
                    decorator = part_phrase_decorator, group = 'g0', priority = 1))  
    rules.append(Rule('PART_PHRASE', 'COMP_M ADJ',
                    decorator = part_phrase_decorator, group = 'g0', priority = 1))  
    rules.append(Rule('PART_PHRASE', 'ADV2 ADJ',
                decorator = part_phrase_decorator, validator = part_phrase_validator, group = 'g0', priority = 2))  

    grammar = Grammar(start_symbols=['ADJ_PHRASE', 'COMP_PHRASE', 'PART_PHRASE'

                                ], rules=rules,
                 legal_attributes=['type', 'adverb_class', 'adverb_weight'])
    
    
    def __init__(self,
                 output_layer='adjective_phrases',
                 input_layer='grammar_tags'):
        self.tagger = GrammarParsingTagger( 
            layer_name=output_layer,
            layer_of_tokens=input_layer,
            attributes=['type', 'adverb_class', 'adverb_weight'],
            grammar=self.grammar,
            output_nodes=['ADJ_PHRASE', 'COMP_PHRASE', 'PART_PHRASE'])
        self.input_layers = [input_layer]
        self.output_layer = output_layer

    def _make_layer(self, raw_text, layers, status):
        return self.tagger.make_layer(raw_text, layers, status)


class AdjectivePhraseTagger(Tagger):
    """
    Tags adjective phrases.
    """
    conf_param = []
    input_layers = []
    
    def __init__(self):
        """
        Tags adjective phrases
        """

    def tag(self, text):
        tagger1 = AdjectivePhrasePartTagger()
        tagger1.tag(text)
        tagger2 = AdjectivePhraseGrammarTagger()
        tagger2.tag(text)
        return text
    
    
