#
#  Converts morphological analyses categories from Vabamorf's / Filosoft's format 
#  to Universal Dependencies (UD) format.
# 
#  !!! WORK IN PROGRESS !!!
#  

import re
import itertools

from collections import OrderedDict

from estnltk import Layer, Text

from estnltk.taggers import Tagger

from estnltk.taggers.standard.morph_analysis.morf_common import _is_empty_annotation

# Mapping cases from Vabamorf to UD
vm_to_ud_case_mapping = {
    'n':'Nom', 
    'g':'Gen',
    'p':'Par',
    'ill':'Ill',
    'in':'Ine',
    'el':'Ela',
    'all':'All',
    'ad':'Ade',
    'abl':'Abl',
    'tr':'Tra',
    'ter':'Ter',
    'es':'Ess',
    'ab':'Abe',
    'kom':'Com',
    # aditiiv
    'adt':'Add'
}

# Based on:  https://cl.ut.ee/ressursid/morfo-systeemid/
_verb_conversion_rules = [ \
  ('n', OrderedDict([('Voice','Act'), ('Tense','Pres'), ('Mood','Ind'), ('VerbForm','Fin'), ('Number','Sing'), ('Person','1')]) ),
  ('d', OrderedDict([('Voice','Act'), ('Tense','Pres'), ('Mood','Ind'), ('VerbForm','Fin'), ('Number','Sing'), ('Person','2')]) ),
  ('b', OrderedDict([('Voice','Act'), ('Tense','Pres'), ('Mood','Ind'), ('VerbForm','Fin'), ('Number','Sing'), ('Person','3')]) ),
  ('me',  OrderedDict([('Voice','Act'), ('Tense','Pres'), ('Mood','Ind'), ('VerbForm','Fin'), ('Number','Plur'), ('Person','1')]) ),
  ('te',  OrderedDict([('Voice','Act'), ('Tense','Pres'), ('Mood','Ind'), ('VerbForm','Fin'), ('Number','Plur'), ('Person','2')]) ),
  ('vad', OrderedDict([('Voice','Act'), ('Tense','Pres'), ('Mood','Ind'), ('VerbForm','Fin'), ('Number','Plur'), ('Person','3')]) ),
  
  ('ksin', OrderedDict([('Voice','Act'), ('Tense','Pres'), ('Mood','Cnd'), ('VerbForm','Fin'), ('Number','Sing'), ('Person','1')]) ),
  ('ksid', OrderedDict([('Voice','Act'), ('Tense','Pres'), ('Mood','Cnd'), ('VerbForm','Fin'), ('Number','Sing'), ('Person','2')]) ),  # TODO: ambiguous
  ('ks',   OrderedDict([('Voice','Act'), ('Tense','Pres'), ('Mood','Cnd'), ('VerbForm','Fin'), ('Number','Sing') ]) ),
  ('ksime', OrderedDict([('Voice','Act'), ('Tense','Pres'), ('Mood','Cnd'), ('VerbForm','Fin'), ('Number','Plur'), ('Person','1')]) ),
  ('ksite', OrderedDict([('Voice','Act'), ('Tense','Pres'), ('Mood','Cnd'), ('VerbForm','Fin'), ('Number','Plur'), ('Person','2')]) ),
  ('ksid',  OrderedDict([('Voice','Act'), ('Tense','Pres'), ('Mood','Cnd'), ('VerbForm','Fin'), ('Number','Plur'), ('Person','3')]) ), # TODO: ambiguous
  
  ('sin',  OrderedDict([('Voice','Act'), ('Tense','Past'), ('Mood','Ind'), ('VerbForm','Fin'), ('Number','Sing'), ('Person','1')]) ),
  ('sid',  OrderedDict([('Voice','Act'), ('Tense','Past'), ('Mood','Ind'), ('VerbForm','Fin'), ('Number','Sing'), ('Person','2')]) ), # TODO: ambiguous
  ('s',    OrderedDict([('Voice','Act'), ('Tense','Past'), ('Mood','Ind'), ('VerbForm','Fin'), ('Number','Sing'), ('Person','3')]) ),
  ('sime', OrderedDict([('Voice','Act'), ('Tense','Past'), ('Mood','Ind'), ('VerbForm','Fin'), ('Number','Plur'), ('Person','1')]) ),
  ('site', OrderedDict([('Voice','Act'), ('Tense','Past'), ('Mood','Ind'), ('VerbForm','Fin'), ('Number','Plur'), ('Person','2')]) ),
  ('sid',  OrderedDict([('Voice','Act'), ('Tense','Past'), ('Mood','Ind'), ('VerbForm','Fin'), ('Number','Plur'), ('Person','3')]) ), # TODO: ambiguous
]

def _has_postag(upostag, upostag_variants):
    '''Checks if the given upostag (which can be ambiguous) is upostag_variants.
       Returns True in case of any matches.
    '''
    if isinstance(upostag, str):
        return any([pos in upostag_variants for pos in upostag.split(',')])
    return False


# ===================================================================
#   T h e   m a i n   c l a s s
# ===================================================================

class UDMorphConverter( Tagger ):
    """Converts morphological analyses from Vabamorf's format to Universal Dependencies (UD) format. 
       Note that the output will have additional ambiguities as the conversion does not involve 
       disambiguation.
       Stores results of the conversion on a new layer."""
    conf_param = [ # Names of the specific input layers
                   '_input_words_layer', \
                   '_input_sentences_layer', \
                   '_input_morph_analysis_layer', \
                 ]

    def __init__(self, \
                 output_layer:str='ud_morph_analysis', \
                 input_words_layer:str='words', \
                 input_sentences_layer:str='sentences', \
                 input_morph_analysis_layer:str='morph_analysis', \
                 input_clauses_layer:str='clauses',
                 add_deprel_attribs:bool=False ):
        ''' Initializes this UDMorphConverter.
            
            Parameters
            -----------
            output_layer: str (default: 'ud_morph_analysis')
                Name for the ud_morph_analysis layer;
            
            input_words_layer: str (default: 'words')
                Name of the input words layer;

            input_sentences_layer: str (default: 'sentences')
                Name of the input sentences layer;
            
            input_morph_analysis_layer: str (default: 'morph_analysis')
                Name of the input morph_analysis layer;
            
            add_deprel_attribs: bool (default: False)
                If set, then the output layer will have full set of UD fields,
                including dependency syntax fields 'head', 'deprel', 'deps'. 
                However, dependency syntax fields will remain unfilled.
                Otherwise, syntax fields 'head', 'deprel', 'deps' will be 
                excluded from output attributes.
        '''
        # Set input/output layer names
        self.output_layer = output_layer
        self._input_words_layer          = input_words_layer
        self._input_sentences_layer      = input_sentences_layer
        self._input_morph_analysis_layer = input_morph_analysis_layer
        self.input_layers = [input_words_layer, input_sentences_layer, input_morph_analysis_layer]
        if add_deprel_attribs:
            self.output_attributes = ('id', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps', 'misc')
        else:
            self.output_attributes = ('id', 'lemma', 'upostag', 'xpostag', 'feats', 'misc')


    def _make_layer_template(self):
        """Creates and returns a template of the layer."""
        return Layer(name=self.output_layer,
                     parent=self._input_morph_analysis_layer,
                     text_object=None,
                     ambiguous=True,
                     attributes=self.output_attributes)


    def _make_layer(self, text, layers, status: dict):
        """Creates ud_morph_analysis layer.
        
        Parameters
        ----------
        text: Text
           Text object that will be tagged;
          
        layers: MutableMapping[str, Layer]
           Layers of the text. Contains mappings from the 
           name of the layer to the Layer object. Must contain
           words, sentences, and morph_analysis.
          
        status: dict
           This can be used to store metadata on layer tagging.
        """
        # 0) Create an empty layer
        ud_morph = self._make_layer_template()
        ud_morph.text_object = text
        
        # 1) Perform simple conversion
        morph_layer = layers[self._input_morph_analysis_layer]
        word_id = 0
        for sentence in layers[self._input_sentences_layer]:
            sentence_morph_words = []
            while word_id < len(morph_layer):
                word_span = morph_layer[word_id]
                if word_span.start >= sentence.end:
                    break
                sentence_morph_words.append(word_span)
                word_id += 1
            for wid, word_span in enumerate(sentence_morph_words):
                base_span = word_span.base_span
                for old_ann in word_span.annotations:
                    conv_anns = self._convert_annotation(dict(old_ann))
                    for ann in conv_anns:
                        ann['id'] = wid+1
                        ud_morph.add_annotation( base_span, ann )
        return ud_morph


    def _generate_ambiguous_analyses(self, base_annotation):
        '''
        Generates all ambiguous analyses from base_annotation 
        that has ambiguous attribute values.
        Returns a list of annotations (dictionaries).
        Basically, generates all combinations of ambiguous values,
        and then creates a new annotation for each combination.
        '''
        # 1) Distinguish ambiguous and non-ambiguous attributes
        #    (ambiguous values contain comma-separated elements)
        ambiguous = OrderedDict()
        non_ambiguous = dict()
        for attr, value in base_annotation.items():
            if isinstance(value, str):
                if ',' in value:
                    values = value.split(',')
                    ambiguous[attr] = values
                else:
                    non_ambiguous[attr] = value
            elif isinstance(value, OrderedDict):
                for attr2, value2 in value.items():
                    key = attr+':::'+attr2
                    if ',' in value2:
                        values2 = value2.split(',')
                        ambiguous[key] = values2
                    else:
                        non_ambiguous[key] = value2
            else:
                non_ambiguous[attr] = value
        if len(ambiguous.keys()) == 0:
            # No ambiguities here, return input
            return [base_annotation]
        # 2) Generate all combinations of ambiguous values
        #    Create a new annotation for each combination
        ud_annotations = []
        for amb_values in list(itertools.product(*[ambiguous[k] for k in ambiguous.keys()])):
            new_annotation = {}
            assert len(amb_values) == len(ambiguous.keys())
            for aid, amb_attr in enumerate(ambiguous.keys()):
                if ':::' in amb_attr:
                    key, subkey = amb_attr.split(':::')
                    if key not in new_annotation:
                        new_annotation[key] = OrderedDict()
                    new_annotation[key][subkey] = \
                                        amb_values[aid]
                else:
                    new_annotation[amb_attr] = amb_values[aid]
            for attr, value in non_ambiguous.items():
                if ':::' in attr:
                    key, subkey = attr.split(':::')
                    if key not in new_annotation:
                        new_annotation[key] = OrderedDict()
                    new_annotation[key][subkey] = value
                else:
                    new_annotation[attr] = value
            ud_annotations.append( new_annotation )
        return ud_annotations

    def _convert_annotation(self, vm_annotation):
        """
        Converts a single Vabamorf annotation to a list of UD annotations, 
        adding ambiguous analyses where necessary. 
        Returns list of UD annotation dictionaries.
        """
        base_ud_annotation = { attr:'' for attr in self.output_attributes}
        vm_pos   = vm_annotation['partofspeech']
        vm_form  = vm_annotation['form']
        vm_lemma = vm_annotation['lemma']
        base_ud_annotation['feats']   = OrderedDict()
        base_ud_annotation['xpostag'] = vm_pos
        base_ud_annotation['lemma']   = vm_lemma
        has_ambiguity = False
        
        # 0) TODO: Use dictionary-based conversions as the first step
        #
        
        # 1) Convert part-of-speech, following: 
        # https://github.com/EstSyntax/EstUD/blob/master/cgmorf2conllu/cgmorf2conllu.py#L435-L538
        # S
        if vm_pos == 'S':
            base_ud_annotation['upostag'] = 'NOUN'
        elif vm_pos == 'H':
            base_ud_annotation['upostag'] = 'PROPN'

        ## A
        elif vm_pos == 'A':
            base_ud_annotation['upostag'] = 'ADJ'
            base_ud_annotation['feats']['Degree'] = 'Pos'
        elif vm_pos == 'C':
            base_ud_annotation['upostag'] = 'ADJ'
            base_ud_annotation['feats']['Degree'] = 'Cmp'
        elif vm_pos == 'U':
            base_ud_annotation['upostag'] = 'ADJ'
            base_ud_annotation['feats']['Degree'] = 'Sup'

        ## P
        elif vm_pos == 'P':
            base_ud_annotation['upostag'] = 'PRON'
            base_ud_annotation['feats']['PronType'] = 'Dem,Int,Ind,Prs,Rcp,Rel,Tot'
            has_ambiguity = True

        ## N
        elif vm_pos == 'N':
            base_ud_annotation['upostag'] = 'NUM'
            base_ud_annotation['feats']['NumType'] = 'Card'
        elif vm_pos == 'O':
            base_ud_annotation['upostag'] = 'NUM'
            base_ud_annotation['feats']['NumType'] = 'Ord'

        ## K
        elif vm_pos == 'K':
            base_ud_annotation['upostag'] = 'ADP'
            base_ud_annotation['feats']['AdpType'] = 'Prep,Post'
            has_ambiguity = True

        ## D
        elif vm_pos == 'D':
            base_ud_annotation['upostag'] = 'ADV'

        ## V
        elif vm_pos == 'V':
            base_ud_annotation['upostag'] = 'VERB,AUX'  # main, aux, mod
            has_ambiguity = True

        ## J
        elif vm_pos == 'J':
            base_ud_annotation['upostag'] = 'CCONJ,SCONJ'  # crd, sub
            has_ambiguity = True

        ## Y
        elif vm_pos == 'Y' and re.search('[A-ZÜÕÖÜ]', vm_lemma):
            base_ud_annotation['upostag'] = 'PROPN'
            base_ud_annotation['feats']['Abbr'] = 'Yes'
        elif vm_pos == 'Y':
            base_ud_annotation['upostag'] = 'SYM'
            base_ud_annotation['feats']['Abbr'] = 'Yes'

        ## X
        elif vm_pos == 'X':
            base_ud_annotation['upostag'] = 'ADV'

        ## Z
        elif vm_pos == 'Z':
            base_ud_annotation['upostag'] = 'PUNCT'

        ## T
        elif vm_pos == 'T':
            base_ud_annotation['upostag'] = 'X'

        ## I
        elif vm_pos == 'I':
            base_ud_annotation['upostag'] = 'INTJ'

        ## B
        elif vm_pos == 'B':
            base_ud_annotation['upostag'] = 'PART'

        ## E
        elif vm_pos == 'E':
            base_ud_annotation['upostag'] = 'SYM'

        ## G
        elif vm_pos == 'G':
            base_ud_annotation['upostag'] = 'NOUN'
            base_ud_annotation['feats']['Number'] = 'Sing'
            base_ud_annotation['feats']['Case']   = 'Gen'

        # 2) Convert morphological features: 
        
        # Number:
        # https://github.com/EstSyntax/EstUD/blob/master/cgmorf2conllu/cgmorf2conllu.py#L545-L551
        if 'sg' in vm_form and base_ud_annotation['upostag'] in ['NOUN', 'PROPN', 'ADJ', 'DET', 'PRON', 'NUM']:
            base_ud_annotation['feats']['Number'] = 'Sing'
        elif 'pl' in vm_form and base_ud_annotation['upostag'] in ['NOUN', 'PROPN', 'ADJ', 'DET', 'PRON', 'NUM']:
            base_ud_annotation['feats']['Number'] = 'Plur'
        # TODO: Number for VERB and AUX

        # VerbForm:
        # https://github.com/EstSyntax/EstUD/blob/master/cgmorf2conllu/cgmorf2conllu.py#L552-L563
        # https://cl.ut.ee/ressursid/morfo-systeemid/
        if vm_form == 'da':
            base_ud_annotation['feats']['VerbForm'] = 'Inf'
        elif vm_form == 'des':
            base_ud_annotation['feats']['VerbForm'] = 'Conv'
        elif vm_form in ['ma', 'mas', 'mast', 'maks', 'mata'] and \
             _has_postag(base_ud_annotation['upostag'], ['VERB', 'AUX']):
            base_ud_annotation['feats']['VerbForm'] = 'Sup'
            # Add case information
            if vm_form == 'ma':
                base_ud_annotation['feats']['Case'] = 'Ill'
            elif vm_form == 'mas':
                base_ud_annotation['feats']['Case'] = 'Ine'
            elif vm_form == 'mast':
                base_ud_annotation['feats']['Case'] = 'Ela'
            elif vm_form == 'maks':
                base_ud_annotation['feats']['Case'] = 'Tra'
            elif vm_form == 'mata':
                base_ud_annotation['feats']['Case'] = 'Abe'
        elif vm_form in ['v', 'nud', 'tud', 'tav'] and \
             _has_postag(base_ud_annotation['upostag'], ['VERB', 'AUX']):
            base_ud_annotation['feats']['VerbForm'] = 'Part'
        
        # Case:
        # https://github.com/EstSyntax/EstUD/blob/master/cgmorf2conllu/cgmorf2conllu.py#L566-L620
        if base_ud_annotation['upostag'] in ['NOUN', 'PROPN', 'ADJ', 'DET', 'PRON', 'NUM']:
            case = ''
            if len(vm_form.split()) > 1:
                case = vm_to_ud_case_mapping.get(vm_form.split()[1], '')
            if case:
                base_ud_annotation['feats']['Case'] = case

        # Degree: (this has already been converted previously)
        # https://github.com/EstSyntax/EstUD/blob/master/cgmorf2conllu/cgmorf2conllu.py#L622-L628
        
        # NumForm:
        # https://github.com/EstSyntax/EstUD/blob/master/cgmorf2conllu/cgmorf2conllu.py#L630-L636
        if base_ud_annotation['upostag'] == 'NUM' or \
           (base_ud_annotation['upostag'] == 'ADJ' and base_ud_annotation['feats'].get('NumType', None) == 'Ord'):
            if vm_lemma.isdigit() or (len(vm_lemma) > 1 and vm_lemma[0].isdigit()):
                # Is digit or starts with digit
                base_ud_annotation['feats']['NumForm'] = 'Digit'
            else:
                base_ud_annotation['feats']['NumForm'] = 'Word'
            # TODO: add regex for detecting roman numerals or something

        # Person, Polarity, Voice, Tense, Mood, VerbForm
        # https://github.com/EstSyntax/EstUD/blob/master/cgmorf2conllu/cgmorf2conllu.py#L647-L758
        # https://cl.ut.ee/ressursid/morfo-systeemid/
        if _has_postag(base_ud_annotation['upostag'], ['VERB', 'AUX']):
            # Use rule-based conversion for most of the verbs
            for (form, features) in _verb_conversion_rules:
                if vm_form == form:
                    for attr, key in features.items():
                        base_ud_annotation['feats'][attr] = key
            

        ud_annotations = []
        if has_ambiguity:
            # if there were ambiguities, then generate all combinations
            ud_annotations = self._generate_ambiguous_analyses(base_ud_annotation)
        else:
            ud_annotations.append( base_ud_annotation )
        return ud_annotations