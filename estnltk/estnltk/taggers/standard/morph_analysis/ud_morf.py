#
#  Converts morphological analyses categories from Vabamorf's / Filosoft's format 
#  to Universal Dependencies (UD) format.
# 
#  !!! WORK IN PROGRESS !!!
#  

import re
import itertools
import os, os.path

from collections import OrderedDict

from estnltk import Layer, Text

from estnltk.taggers import Tagger

from estnltk.taggers.standard.morph_analysis.morf_common import VABAMORF_POSTAGS
from estnltk.taggers.standard.morph_analysis.morf_common import _is_empty_annotation

# Default rules for converting (vm_pos, vm_lemma) to (ud_pos, ud_feats)
DEFAULT_VM_CONV_RULES_DIR = \
    os.path.join( os.path.dirname(__file__), 'ud_conv_rules' )

# Mapping noun cases from Vabamorf to UD
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

# Mapping verb forms from Vabamorf to UD
# Based on:  https://cl.ut.ee/ressursid/morfo-systeemid/
# For ambiguous form categories, there are multiple entries per category
_verb_form_conversion_rules = [ \
  ('da',   OrderedDict([('VerbForm','Inf')]) ),
  ('des',  OrderedDict([('VerbForm','Conv')]) ),
  ('ma',   OrderedDict([('Voice','Act'), ('VerbForm','Sup'), ('Case','Ill')]) ),
  ('mas',  OrderedDict([('Voice','Act'), ('VerbForm','Sup'), ('Case','Ine')]) ),
  ('mast', OrderedDict([('Voice','Act'), ('VerbForm','Sup'), ('Case','Ela')]) ),
  ('maks', OrderedDict([('Voice','Act'), ('VerbForm','Sup'), ('Case','Tra')]) ),
  ('mata', OrderedDict([('Voice','Act'), ('VerbForm','Sup'), ('Case','Abe')]) ),

  ('n', OrderedDict([('Voice','Act'), ('Tense','Pres'), ('Mood','Ind'), ('VerbForm','Fin'), ('Number','Sing'), ('Person','1')]) ),
  ('d', OrderedDict([('Voice','Act'), ('Tense','Pres'), ('Mood','Ind'), ('VerbForm','Fin'), ('Number','Sing'), ('Person','2')]) ),
  ('b', OrderedDict([('Voice','Act'), ('Tense','Pres'), ('Mood','Ind'), ('VerbForm','Fin'), ('Number','Sing'), ('Person','3')]) ),
  ('me',  OrderedDict([('Voice','Act'), ('Tense','Pres'), ('Mood','Ind'), ('VerbForm','Fin'), ('Number','Plur'), ('Person','1')]) ),
  ('te',  OrderedDict([('Voice','Act'), ('Tense','Pres'), ('Mood','Ind'), ('VerbForm','Fin'), ('Number','Plur'), ('Person','2')]) ),
  ('vad', OrderedDict([('Voice','Act'), ('Tense','Pres'), ('Mood','Ind'), ('VerbForm','Fin'), ('Number','Plur'), ('Person','3')]) ),
  
  ('o', OrderedDict([('Voice','Act'), ('Tense','Pres'), ('Mood','Ind'), ('VerbForm','Fin'), ('Connegative','Yes')]) ),   # ambiguous
  
  ('ksin', OrderedDict([('Voice','Act'), ('Tense','Pres'), ('Mood','Cnd'), ('VerbForm','Fin'), ('Number','Sing'), ('Person','1')]) ),
  ('ksid', OrderedDict([('Voice','Act'), ('Tense','Pres'), ('Mood','Cnd'), ('VerbForm','Fin'), ('Number','Sing'), ('Person','2')]) ),  # ambiguous
  ('ks',   OrderedDict([('Voice','Act'), ('Tense','Pres'), ('Mood','Cnd'), ('VerbForm','Fin'), ('Number','Sing') ]) ),
  ('ksime', OrderedDict([('Voice','Act'), ('Tense','Pres'), ('Mood','Cnd'), ('VerbForm','Fin'), ('Number','Plur'), ('Person','1')]) ),
  ('ksite', OrderedDict([('Voice','Act'), ('Tense','Pres'), ('Mood','Cnd'), ('VerbForm','Fin'), ('Number','Plur'), ('Person','2')]) ),
  ('ksid',  OrderedDict([('Voice','Act'), ('Tense','Pres'), ('Mood','Cnd'), ('VerbForm','Fin'), ('Number','Plur'), ('Person','3')]) ), # ambiguous
  
  ('o',   OrderedDict([('Voice','Act'), ('Tense','Pres'), ('Mood','Imp'), ('VerbForm','Fin'), ('Number','Sing'), ('Person','2') ]) ),                         # ambiguous
  ('o',   OrderedDict([('Voice','Act'), ('Tense','Pres'), ('Mood','Imp'), ('VerbForm','Fin'), ('Number','Sing'), ('Person','2'), ('Connegative','Yes')]) ),   # ambiguous
  ('gu',  OrderedDict([('Voice','Act'), ('Tense','Pres'), ('Mood','Imp'), ('VerbForm','Fin') ]) ),                                                                # ambiguous
  ('gu',  OrderedDict([('Voice','Act'), ('Tense','Pres'), ('Mood','Imp'), ('VerbForm','Fin'), ('Connegative','Yes') ]) ),                                         # ambiguous
  ('gu',  OrderedDict([('Voice','Act'), ('Tense','Pres'), ('Mood','Imp'), ('VerbForm','Fin'), ('Number','Sing,Plur'), ('Person','3') ]) ),                        # ambiguous
  ('gu',  OrderedDict([('Voice','Act'), ('Tense','Pres'), ('Mood','Imp'), ('VerbForm','Fin'), ('Number','Sing,Plur'), ('Person','3'), ('Connegative','Yes') ]) ), # ambiguous
  ('gem', OrderedDict([('Voice','Act'), ('Tense','Pres'), ('Mood','Imp'), ('VerbForm','Fin'), ('Number','Plur'), ('Person','1') ]) ),  
  ('gem', OrderedDict([('Voice','Act'), ('Tense','Pres'), ('Mood','Imp'), ('VerbForm','Fin'), ('Number','Plur'), ('Person','1'), ('Connegative','Yes') ]) ),
  ('ge',  OrderedDict([('Voice','Act'), ('Tense','Pres'), ('Mood','Imp'), ('VerbForm','Fin'), ('Number','Plur'), ('Person','2') ]) ),  
  ('ge',  OrderedDict([('Voice','Act'), ('Tense','Pres'), ('Mood','Imp'), ('VerbForm','Fin'), ('Number','Plur'), ('Person','2'), ('Connegative','Yes') ]) ),
  
  ('vat',  OrderedDict([('Voice','Act'), ('Tense','Pres'), ('Mood','Qot'), ('VerbForm','Fin') ]) ),  
  ('vat',  OrderedDict([('Voice','Act'), ('Tense','Pres'), ('Mood','Qot'), ('VerbForm','Fin'), ('Connegative','Yes') ]) ),

  ('v',    OrderedDict([('Voice','Act'), ('Tense','Pres'), ('VerbForm','Part')]) ),
  
  ('sin',  OrderedDict([('Voice','Act'), ('Tense','Past'), ('Mood','Ind'), ('VerbForm','Fin'), ('Number','Sing'), ('Person','1')]) ),
  ('sid',  OrderedDict([('Voice','Act'), ('Tense','Past'), ('Mood','Ind'), ('VerbForm','Fin'), ('Number','Sing'), ('Person','2')]) ), # ambiguous
  ('s',    OrderedDict([('Voice','Act'), ('Tense','Past'), ('Mood','Ind'), ('VerbForm','Fin'), ('Number','Sing'), ('Person','3')]) ),
  ('sime', OrderedDict([('Voice','Act'), ('Tense','Past'), ('Mood','Ind'), ('VerbForm','Fin'), ('Number','Plur'), ('Person','1')]) ),
  ('site', OrderedDict([('Voice','Act'), ('Tense','Past'), ('Mood','Ind'), ('VerbForm','Fin'), ('Number','Plur'), ('Person','2')]) ),
  ('sid',  OrderedDict([('Voice','Act'), ('Tense','Past'), ('Mood','Ind'), ('VerbForm','Fin'), ('Number','Plur'), ('Person','3')]) ), # ambiguous
  ('nud',  OrderedDict([('Voice','Act'), ('Tense','Past'), ('Mood','Ind'), ('VerbForm','Fin'), ('Connegative','Yes') ]) ), # ambiguous
  
  ('nuksin',  OrderedDict([('Voice','Act'), ('Tense','Past'), ('Mood','Cnd'), ('VerbForm','Fin'), ('Number','Sing'), ('Person','1')]) ),
  ('nuksid',  OrderedDict([('Voice','Act'), ('Tense','Past'), ('Mood','Cnd'), ('VerbForm','Fin'), ('Number','Sing'), ('Person','2')]) ),  # ambiguous
  ('nuks',    OrderedDict([('Voice','Act'), ('Tense','Past'), ('Mood','Cnd'), ('VerbForm','Fin'), ('Number','Sing') ]) ),
  ('nuks',    OrderedDict([('Voice','Act'), ('Tense','Past'), ('Mood','Cnd'), ('VerbForm','Fin'), ('Number','Sing'), ('Connegative','Yes') ]) ),
  ('nuksime', OrderedDict([('Voice','Act'), ('Tense','Past'), ('Mood','Cnd'), ('VerbForm','Fin'), ('Number','Plur'), ('Person','1')]) ),
  ('nuksite', OrderedDict([('Voice','Act'), ('Tense','Past'), ('Mood','Cnd'), ('VerbForm','Fin'), ('Number','Plur'), ('Person','2')]) ),
  ('nuksid',  OrderedDict([('Voice','Act'), ('Tense','Past'), ('Mood','Cnd'), ('VerbForm','Fin'), ('Number','Plur'), ('Person','3')]) ),  # ambiguous
  
  ('nuvat',  OrderedDict([('Voice','Act'), ('Tense','Past'), ('Mood','Qot'), ('VerbForm','Fin') ]) ),  
  ('nuvat',  OrderedDict([('Voice','Act'), ('Tense','Past'), ('Mood','Qot'), ('VerbForm','Fin'), ('Connegative','Yes') ]) ),
  ('nud',    OrderedDict([('Voice','Act'), ('Tense','Past'), ('VerbForm','Part') ]) ), # ambiguous

  ('tama',   OrderedDict([('Voice','Pass'), ('VerbForm','Sup') ]) ),  
  ('takse',  OrderedDict([('Voice','Pass'), ('Tense','Pres'), ('Mood','Ind'), ('VerbForm','Fin') ]) ),  
  ('ta',     OrderedDict([('Voice','Pass'), ('Tense','Pres'), ('Mood','Ind'), ('VerbForm','Fin'), ('Connegative','Yes') ]) ),
  ('taks',   OrderedDict([('Voice','Pass'), ('Tense','Pres'), ('Mood','Cnd'), ('VerbForm','Fin') ]) ),
  ('taks',   OrderedDict([('Voice','Pass'), ('Tense','Pres'), ('Mood','Cnd'), ('VerbForm','Fin'), ('Connegative','Yes') ]) ),
  ('tagu',   OrderedDict([('Voice','Pass'), ('Tense','Pres'), ('Mood','Imp'), ('VerbForm','Fin') ]) ),
  ('tagu',   OrderedDict([('Voice','Pass'), ('Tense','Pres'), ('Mood','Imp'), ('VerbForm','Fin'), ('Connegative','Yes') ]) ),
  ('tavat',  OrderedDict([('Voice','Pass'), ('Tense','Pres'), ('Mood','Qot'), ('VerbForm','Fin') ]) ),
  ('tavat',  OrderedDict([('Voice','Pass'), ('Tense','Pres'), ('Mood','Qot'), ('VerbForm','Fin'), ('Connegative','Yes') ]) ),

  ('tav',    OrderedDict([('Voice','Pass'), ('Tense','Pres'), ('VerbForm','Part')]) ),

  ('ti',    OrderedDict([('Voice','Pass'), ('Tense','Past'), ('Mood','Ind'), ('VerbForm','Fin') ]) ),  
  ('tud',   OrderedDict([('Voice','Pass'), ('Tense','Past'), ('Mood','Ind'), ('VerbForm','Fin'), ('Connegative','Yes') ]) ),  # ambiguous 
  ('tuks',  OrderedDict([('Voice','Pass'), ('Tense','Past'), ('Mood','Cnd'), ('VerbForm','Fin') ]) ),  
  ('tuks',  OrderedDict([('Voice','Pass'), ('Tense','Past'), ('Mood','Cnd'), ('VerbForm','Fin'), ('Connegative','Yes') ]) ),  
  ('tud',   OrderedDict([('Voice','Pass'), ('Tense','Past'), ('VerbForm','Part') ]) ),  # ambiguous 
  
  ('neg o',    OrderedDict([('Voice','Act'), ('Tense','Pres'), ('Mood','Ind'), ('VerbForm','Fin'), ('Polarity','Neg') ]) ),  # ambiguous 
  ('neg ks',   OrderedDict([('Voice','Act'), ('Tense','Pres'), ('Mood','Cnd'), ('VerbForm','Fin'), ('Polarity','Neg') ]) ),
  ('neg o',    OrderedDict([('Voice','Act'), ('Tense','Pres'), ('Mood','Imp'), ('VerbForm','Fin'), ('Number','Sing'), ('Person','2'), ('Polarity','Neg') ]) ),  # ambiguous 
  ('neg gu',   OrderedDict([('Voice','Act'), ('Tense','Pres'), ('Mood','Imp'), ('VerbForm','Fin'), ('Number','Sing,Plur'), ('Person','3'), ('Polarity','Neg') ]) ),
  ('neg gem',  OrderedDict([('Voice','Act'), ('Tense','Pres'), ('Mood','Imp'), ('VerbForm','Fin'), ('Number','Plur'), ('Person','1'), ('Polarity','Neg') ]) ),
  ('neg me',   OrderedDict([('Voice','Act'), ('Tense','Pres'), ('Mood','Imp'), ('VerbForm','Fin'), ('Polarity','Neg') ]) ),
  ('neg ge',   OrderedDict([('Voice','Act'), ('Tense','Pres'), ('Mood','Imp'), ('VerbForm','Fin'), ('Number','Plur'), ('Person','2'), ('Polarity','Neg') ]) ),
  ('neg vat',  OrderedDict([('Voice','Act'), ('Tense','Pres'), ('Mood','Qot'), ('VerbForm','Fin'), ('Polarity','Neg') ]) ),  
  ('neg nud',  OrderedDict([('Voice','Act'), ('Tense','Past'), ('Mood','Ind'), ('VerbForm','Fin'), ('Polarity','Neg') ]) ),  
  ('neg nuks', OrderedDict([('Voice','Act'), ('Tense','Pres'), ('Mood','Cnd'), ('VerbForm','Fin'), ('Polarity','Neg') ]) ),
  ('neg da',   OrderedDict([('Voice','Pass'), ('Tense','Pres'), ('Mood','Ind'), ('VerbForm','Fin'), ('Polarity','Neg') ]) ),
  ('neg tud',  OrderedDict([('Voice','Pass'), ('Tense','Past'), ('Mood','Ind'), ('VerbForm','Part'), ('Polarity','Neg') ]) ), 
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
                   # Rules: vm_pos, vm_lemma to upostag & feats
                   '_pos_lemma_conv_rules', \
                   # Constants: aux verb lemmas
                   '_aux_verb_lemmas'
                 ]

    def __init__(self, \
                 output_layer:str='ud_morph_analysis', \
                 input_words_layer:str='words', \
                 input_sentences_layer:str='sentences', \
                 input_morph_analysis_layer:str='morph_analysis', \
                 input_clauses_layer:str='clauses', \
                 conversion_rules_dir:str=None, \
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
            
            conversion_rules_dir: str (default: None)
                Directory containing *.tab files with dictionary-based conversions, 
                each mapping a lemma to appropriate upostags and feats. 
                If provided, then conversion rules will be loaded from the directory 
                and applied as first the conversion step, before applying the default 
                rules.
                For examples about conversion files, see: 
                https://github.com/EstSyntax/EstUD/tree/master/cgmorf2conllu/POS_LEMMA_RULES
            
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
        self._pos_lemma_conv_rules = {}
        if conversion_rules_dir is not None:
            # Load conversion rules
            assert os.path.exists(conversion_rules_dir), \
                '(!) Non-existent conversion rules directory: {!r} '.format(conversion_rules_dir)
            assert os.path.isdir(conversion_rules_dir), \
                '(!) {!r} should be a directory.'.format(conversion_rules_dir)
            for fname in os.listdir(conversion_rules_dir):
                if fname.endswith('.tab'):
                    fpath=os.path.join(conversion_rules_dir, fname)
                    self._load_pos_lemma_conv_rules_from_file( fpath )
        # Constants
        self._aux_verb_lemmas = set(['olema', 'saama', 'pidama', 'võima', 'tunduma', \
                                     'tohtima', 'paistma', 'näima'])

    def _load_pos_lemma_conv_rules_from_file( self, fpath ):
        '''
        Loads tabbed conversion rules from the given file.
        
        Rules file name should start with an abbreviation of Vabamorf's 
        postag, e.g. file "P_PRON.tab" contains rules for converting lemmas 
        with Vabamorf's postag "P". 
        
        Expected file format: one rule per line with tab-separated values:
        <Vabamorf's lemma> \t <UD postag> \t <UD features (optional)>
        For example files, see:
        https://github.com/EstSyntax/EstUD/tree/master/cgmorf2conllu/POS_LEMMA_RULES
        
        Returns None. All loaded rules will be saved under the instance variable 
        `self._pos_lemma_conv_rules`.
        '''
        _, fname = os.path.split(fpath)
        if fname[0] not in VABAMORF_POSTAGS:
            raise ValueError(('(!) Unexpected conversion rules file name: {!r}. '+\
                             "The name should start with a Vabamorf's postag.").format(fname))
        vm_pos = fname[0]
        with open( fpath, 'r', encoding='utf-8' ) as in_f:
            for line in in_f:
                line = line.strip()
                if len(line) > 0:
                    line_parts = line.split('\t')
                    if len(line_parts) not in [2,3]:
                        raise ValueError(('(!) Unexpected conversion rule {!r} in file {!r}.'+\
                                          ''.format(line, fpath)))
                    vm_lemma = line_parts[0]
                    ud_pos = line_parts[1]
                    ud_feats = None
                    if len(line_parts) == 3:
                        ud_feats = line_parts[2]
                        # parse features
                        ud_feats_parts = ud_feats.split()
                        ud_feats_dict = OrderedDict()
                        for part in ud_feats_parts:
                            assert '=' in part
                            key, value = part.split('=')
                            ud_feats_dict[key] = value
                        ud_feats = ud_feats_dict
                    # add to dictonary
                    if vm_pos not in self._pos_lemma_conv_rules:
                        self._pos_lemma_conv_rules[vm_pos] = {}
                    # note: if there are multiple rules per VM lemma & postag
                    # overwrite previous rules
                    self._pos_lemma_conv_rules[vm_pos][vm_lemma] = {}
                    self._pos_lemma_conv_rules[vm_pos][vm_lemma]['upostag'] = ud_pos
                    if ud_feats is not None:
                        self._pos_lemma_conv_rules[vm_pos][vm_lemma]['feats'] = ud_feats


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
                # Convert Vabamorf's annotations (without context)
                conv_annotations = []
                for old_ann in word_span.annotations:
                    annotations = self._convert_annotation(dict(old_ann))
                    if annotations:
                        conv_annotations.extend( annotations )
                # Make post-corrections on participles
                conv_annotations = \
                    self._postcorrect_participles(conv_annotations)
                # Add annotations to the layer
                for ann in conv_annotations:
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
                    values = [v.strip() for v in values]
                    ambiguous[attr] = values
                else:
                    non_ambiguous[attr] = value
            elif isinstance(value, OrderedDict):
                for attr2, value2 in value.items():
                    key = attr+':::'+attr2
                    if ',' in value2:
                        values2 = value2.split(',')
                        values2 = [v.strip() for v in values2]
                        ambiguous[key] = values2
                    else:
                        non_ambiguous[key] = value2
                if len(value.items()) == 0:
                    # empty features
                    non_ambiguous[attr] = value
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
        
        ud_annotations = []
        # 0) Use dictionary-based conversions as the first step
        # https://github.com/EstSyntax/EstUD/blob/master/cgmorf2conllu/cgmorf2conllu.py#L425-L432
        if vm_pos in self._pos_lemma_conv_rules:
            if vm_lemma in self._pos_lemma_conv_rules[vm_pos]:
                dict_rules = self._pos_lemma_conv_rules[vm_pos][vm_lemma]
                if 'upostag' in dict_rules:
                    base_ud_annotation['upostag'] = dict_rules['upostag']
                if 'feats' in dict_rules:
                    for k, v in dict_rules['feats'].items():
                        base_ud_annotation['feats'][k] = v
        
        if base_ud_annotation['upostag'] == '':
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
                # aux, mod, main
                if vm_lemma == 'ära':
                    base_ud_annotation['upostag'] = 'AUX'
                elif vm_lemma in self._aux_verb_lemmas:
                    base_ud_annotation['upostag'] = 'VERB,AUX'
                else:
                    base_ud_annotation['upostag'] = 'VERB'
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

        # 2) Convert morphological features of nouns and declinable words: 
        
        # Number:
        # https://github.com/EstSyntax/EstUD/blob/master/cgmorf2conllu/cgmorf2conllu.py#L545-L551
        if 'sg' in vm_form and _has_postag(base_ud_annotation['upostag'], ['NOUN', 'PROPN', 'ADJ', 'DET', 'PRON', 'NUM']):
            base_ud_annotation['feats']['Number'] = 'Sing'
        elif 'pl' in vm_form and _has_postag(base_ud_annotation['upostag'], ['NOUN', 'PROPN', 'ADJ', 'DET', 'PRON', 'NUM']):
            base_ud_annotation['feats']['Number'] = 'Plur'

        # Case:
        # https://github.com/EstSyntax/EstUD/blob/master/cgmorf2conllu/cgmorf2conllu.py#L566-L620
        if _has_postag(base_ud_annotation['upostag'], ['NOUN', 'PROPN', 'ADJ', 'DET', 'PRON', 'NUM']):
            case = ''
            if len(vm_form.split()) > 1:
                case = vm_to_ud_case_mapping.get(vm_form.split()[1], '')
            if case:
                base_ud_annotation['feats']['Case'] = case

        # Degree:
        # https://github.com/EstSyntax/EstUD/blob/master/cgmorf2conllu/cgmorf2conllu.py#L622-L628
        if _has_postag(base_ud_annotation['upostag'], ['ADJ']):
            if vm_pos == 'A':
                base_ud_annotation['feats']['Degree'] = 'Pos'
            elif vm_pos == 'C':
                base_ud_annotation['feats']['Degree'] = 'Cmp'
            elif vm_pos == 'U':
                base_ud_annotation['feats']['Degree'] = 'Sup'
        
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

        # 3) Convert morphological features of verbs: 

        if _has_postag(base_ud_annotation['upostag'], ['VERB', 'AUX']):
            # Some exceptional verb forms
            if vm_lemma == 'ei':
                # Add AUX annotation (primary interpretation)
                base_ud_annotation['upostag'] = 'AUX'
                base_ud_annotation['feats']['Polarity'] = 'Neg'
                ud_annotations.append( base_ud_annotation )
            elif vm_lemma in ['kuulukse', 'tunnukse', 'näikse']:
                base_ud_annotation['feats']['Tense'] = 'Pres'
                base_ud_annotation['feats']['Mood'] = 'Ind'
                base_ud_annotation['feats']['VerbForm']  = 'Fin'
                ud_annotations.append( base_ud_annotation )

            # Person, Polarity, Voice, Tense, Mood, VerbForm
            # https://github.com/EstSyntax/EstUD/blob/master/cgmorf2conllu/cgmorf2conllu.py#L552-L563
            # https://github.com/EstSyntax/EstUD/blob/master/cgmorf2conllu/cgmorf2conllu.py#L647-L758
            # https://cl.ut.ee/ressursid/morfo-systeemid/

            # Use rule-based conversion for most of the verbs
            # Note that this can produce ambiguous annotations
            all_form_annotations = []
            for (form, features) in _verb_form_conversion_rules:
                if vm_form == form:
                    # Copy base annotation
                    new_annotation = {k:base_ud_annotation[k] for k in base_ud_annotation.keys()}
                    new_annotation['feats'] = base_ud_annotation['feats'].copy()
                    # Add new features
                    for attr, key in features.items():
                        new_annotation['feats'][attr] = key
                    all_form_annotations.append(new_annotation)
            ud_annotations.extend( all_form_annotations )
        
        if len(ud_annotations) == 0:
            ud_annotations = [base_ud_annotation]

        if has_ambiguity:
            # if there were ambiguities, then generate all combinations
            new_ud_annotations = []
            for base_ud_annotation in ud_annotations:
                new_ud_annotations.extend( self._generate_ambiguous_analyses(base_ud_annotation) )
            ud_annotations = new_ud_annotations

        return ud_annotations


    def _postcorrect_participles(self, ud_annotations):
        '''
        Makes postcorrections to ambiguous participles. 
        
        Basically, if annotations contain verb participle features 
        (VerbForm=Part, Voice=Act,Pass, Tense=Past,Pres), and there 
        are also adjective annotations, then carry over verb 
        participle features to adjective annotations (so, adjectives
        will obtain features VerbForm, Voice, Tense).
        
        Returns input ud_annotations with post-corrections (if any).
        
        TODO: a number of adjectives in UD corpus do not have 
        verb participle features, e.g. "huvitav", "loov", "tugev", 
        "sügav".
        Add some lexicon-based exclusion ?!
        '''
        voice = None
        tense = None
        verbForm = None
        # Find participle verb features
        for ud_annotation in ud_annotations:
            if 'VerbForm' in ud_annotation['feats'] and \
               ud_annotation['feats']['VerbForm'] == 'Part':
                verbForm = ud_annotation['feats']['VerbForm']
                if 'Voice' in ud_annotation['feats']:
                    voice = ud_annotation['feats']['Voice']
                if 'Tense' in ud_annotation['feats']:
                    tense = ud_annotation['feats']['Tense']
        # Carry over verb participle features (if any) to adj
        if verbForm or voice or tense:
            for ud_annotation in ud_annotations:
                if _has_postag(ud_annotation['upostag'], ['ADJ']):
                    if voice:
                        ud_annotation['feats']['Voice'] = voice
                    if verbForm:
                        ud_annotation['feats']['VerbForm'] = verbForm
                    if tense:
                        ud_annotation['feats']['Tense'] = tense
        return ud_annotations