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


# Default verb features for adjectives
_adj_verb_features = [ \
  ('nud',    OrderedDict([('Voice','Act'), ('Tense','Past'), ('VerbForm','Part') ]) ), 
  ('tud',    OrderedDict([('Voice','Pass'), ('Tense','Past'), ('VerbForm','Part') ]) ), 
  ('dud',    OrderedDict([('Voice','Pass'), ('Tense','Past'), ('VerbForm','Part') ]) ), 
  ('v',      OrderedDict([('Voice','Act'), ('Tense','Pres'), ('VerbForm','Part')]) ), 
  ('tav',    OrderedDict([('Voice','Act'), ('Tense','Pres'), ('VerbForm','Part')]) ), 
  ('tav',    OrderedDict([('Voice','Pass'), ('Tense','Pres'), ('VerbForm','Part')]) ), 
]


# Adjectives which should not obtain any verb features
_adj_with_no_verb_features = \
 ['ebalev', 'huvitav', 'ihalev', 'kehtiv', 'kõdunev', 'loov', 'mõistev', 'mõjuv', 
  'osalev', 'palav', 'pädev', 'saav', 'sügav', 'tugev', 'võluv', 'ustav', 'alatu', 
  'kirev', 'ülev', 'tuttav', 'terav', 'mugav', 'põnev', 'kuiv', 'kehv', 'kõrvulukustav', 
  'igav', 'harv', 'pidev', 'kaitsetu', 'kärsitu']
# TODO: 'odav', 'erinev' have ambiguous participle interpretations in the corpus


def _has_postag(upostag, upostag_variants):
    '''Checks if the given upostag (which can be ambiguous) is upostag_variants.
       Returns True in case of any matches.
    '''
    if isinstance(upostag, str):
        return any([pos in upostag_variants for pos in upostag.split(',')])
    return False

def _participle_ending(lemma):
    '''Heuristic: returns possible participle ending of given lemma.
    Possible return values: ('nud', 'tud', 'dud', 'tav', 'v', '')
    '''
    if lemma[-3:] in ['nud', 'tud', 'dud', 'tav']:
        return lemma[-3:]
    elif lemma[-1] in ['v']:
        return lemma[-1]
    return ''

_dash_ending_word = re.compile("^([A-ZÖÄÜÕŽŠa-zöäüõžš]+)-$")

# ===================================================================
#   T h e   m a i n   c l a s s
# ===================================================================

class UDMorphConverter( Tagger ):
    """Converts morphological analyses from Vabamorf's format to Universal Dependencies (UD) format. 
       Note that the output will have additional ambiguities as the conversion does not involve 
       disambiguation.
       Stores results of the conversion on a new layer."""
    conf_param = [ 'remove_connegatives', \
                   # Names of the specific input layers
                   '_input_words_layer', \
                   '_input_sentences_layer', \
                   '_input_morph_analysis_layer', \
                   # Conversion rules imported from files
                   '_pos_lemma_conv_rules', \
                   '_lemma_conv_rules', \
                   # Constants: aux verb lemmas
                   '_aux_verb_lemmas', \
                   '_adj_with_no_verb_features'
                 ]

    def __init__(self, \
                 output_layer:str='ud_morph_analysis', \
                 input_words_layer:str='words', \
                 input_sentences_layer:str='sentences', \
                 input_morph_analysis_layer:str='morph_analysis', \
                 input_clauses_layer:str='clauses', \
                 conversion_rules_dir:str=None, \
                 add_deprel_attribs:bool=False, \
                 remove_connegatives:bool=False, \
                 adj_with_no_verb_features:list=_adj_with_no_verb_features ):
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
                each mapping Vabamorf's a lemma (and optionally part of speech) to 
                appropriate upostags and feats. 
                Each rules file should have .tab extension, files with other extensions 
                will be ignored.
                If provided, then conversion rules will be loaded from the directory 
                and applied as first the conversion step, before applying the default 
                rules.
            
            add_deprel_attribs: bool (default: False)
                If set, then the output layer will have full set of UD fields,
                including dependency syntax fields 'head', 'deprel', 'deps'. 
                However, dependency syntax fields will remain unfilled.
                Otherwise, syntax fields 'head', 'deprel', 'deps' will be 
                excluded from output attributes.
            
            remove_connegatives: bool (default: False)
                If True, then removes annotations with Connegative=Yes when 
                they are not preceded by words with Polarity=Neg annotations 
                in a sentence context. 
                Note: this is heuristic. If a connegative word is preceded by an 
                unrecognized negative word (such as a slang word '2ra', '2i' or 
                'äi'), then the deletion will be erroneous.

            adj_with_no_verb_features: list of str (default: _adj_with_no_verb_features)
                List of adjective lemmas, corresponding to adjectives which should 
                not obtain verb participle features. 
                Note that by default, all adjectives ending with 'tud', 'nud', 'v' or 
                'tav' will receive corresponding verb participle features.
                Use this list to avoid adding verb features to specific adjectives.
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
        self._lemma_conv_rules = {}
        self.remove_connegatives = remove_connegatives
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
        self._adj_with_no_verb_features = set(adj_with_no_verb_features)
        # Constants
        self._aux_verb_lemmas = set(['olema', 'saama', 'pidama', 'võima', 'tunduma', \
                                     'tohtima', 'paistma', 'näima'])

    def _load_pos_lemma_conv_rules_from_file( self, fpath ):
        '''
        Loads tabbed conversion rules from the given file.
        
        Expected file format: one rule per line with tab-separated values:
        <Vabamorf's lemma> \t <Vabamorf's postag (optional)> \t <UD postag> \t <UD features (optional)>
        Vabamorf's postag can be an empty value, in that case, postags are ignored and 
        only lemma match is checked.
        UD features can also be left empy, in that case, no features will be added and only UD 
        postag will be converted.
        
        Returns None. All loaded rules will be saved under the instance variables 
        `self._pos_lemma_conv_rules` and `self._lemma_conv_rules`.
        '''
        with open( fpath, 'r', encoding='utf-8' ) as in_f:
            for line in in_f:
                line = line.strip()
                if len(line) > 0:
                    line_parts = line.split('\t')
                    if len(line_parts) not in [3, 4]:
                        raise ValueError(('(!) Unexpected conversion rule {!r} in file {!r}.'+\
                                          ''.format(line, fpath)))
                    vm_lemma = line_parts[0]
                    vm_lemma = (vm_lemma.replace('_', '')).replace('=', '')
                    vm_pos = line_parts[1]
                    if len(vm_pos) != 0:
                        if vm_pos not in VABAMORF_POSTAGS:
                            raise ValueError(("(!) Unexpected Vabamorf's postag {!r} in rule: {!r}. "+\
                                              "").format(vm_pos, line))
                    ud_pos = line_parts[2]
                    ud_feats = None
                    if len(line_parts) == 4:
                        ud_feats_raw = line_parts[3]
                        if len(ud_feats_raw) > 0:
                            # parse features
                            ud_feats_parts = ud_feats_raw.split()
                            ud_feats_dict = OrderedDict()
                            for part in ud_feats_parts:
                                assert '=' in part
                                key, value = part.split('=')
                                ud_feats_dict[key] = value
                            ud_feats = ud_feats_dict
                    # add to dictonary
                    if len(vm_pos) != 0:
                        # vm pos is specified
                        if vm_pos not in self._pos_lemma_conv_rules:
                            self._pos_lemma_conv_rules[vm_pos] = {}
                        # note: there can be multiple rules per single VM lemma & postag;
                        # so, we use a list of dicts for storing rules
                        if vm_lemma not in self._pos_lemma_conv_rules[vm_pos]:
                            self._pos_lemma_conv_rules[vm_pos][vm_lemma] = [{}]
                        else:
                            self._pos_lemma_conv_rules[vm_pos][vm_lemma].append({})
                        self._pos_lemma_conv_rules[vm_pos][vm_lemma][-1]['upostag'] = ud_pos
                        if ud_feats is not None:
                            self._pos_lemma_conv_rules[vm_pos][vm_lemma][-1]['feats'] = ud_feats
                    else:
                        # vm pos is unspecified
                        # note: there can be multiple rules per single VM lemma;
                        # so, we use a list of dicts for storing rules
                        if vm_lemma not in self._lemma_conv_rules:
                            self._lemma_conv_rules[vm_lemma] = [{}]
                        else:
                            self._lemma_conv_rules[vm_lemma].append({})
                        self._lemma_conv_rules[vm_lemma][-1]['upostag'] = ud_pos
                        if ud_feats is not None:
                            self._lemma_conv_rules[vm_lemma][-1]['feats'] = ud_feats


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
            sent_ud_annotations = []
            for wid, word_span in enumerate(sentence_morph_words):
                base_span = word_span.base_span
                # Convert Vabamorf's annotations (without context)
                conv_annotations = []
                for old_ann in word_span.annotations:
                    if _is_empty_annotation( old_ann ):
                        # discard an empty annotation
                        continue
                    annotations = self._convert_annotation( word_span.text, 
                                                            dict(old_ann) )
                    if annotations:
                        conv_annotations.extend( annotations )
                # Make post-corrections on participles
                conv_annotations = \
                    self._postcorrect_participles(conv_annotations)
                if conv_annotations:
                    # Add (non-empty) annotations to the layer
                    for ann in conv_annotations:
                        ann['id'] = wid+1
                        sent_ud_annotations.append([base_span, ann])
                else:
                    # Add an empty annotation
                    empty_ud_annotation = \
                        {attr:None for attr in self.output_attributes}
                    empty_ud_annotation['id'] = wid+1
                    sent_ud_annotations.append([base_span, \
                                                empty_ud_annotation])
            # Apply contextual fixes
            if self.remove_connegatives:
                sent_ud_annotations = \
                    self._remove_connegatives_heuristic(sent_ud_annotations)
            # Finally, add annotations to the layer
            for [_base_span, _ud_annotation] in sent_ud_annotations:
                ud_morph.add_annotation(_base_span, _ud_annotation)
        return ud_morph


    def _generate_ambiguous_analyses(self, base_annotation:dict):
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

    def _convert_annotation(self, word_str:str, vm_annotation:dict):
        """
        Converts a single Vabamorf annotation to a list of UD annotations, 
        adding ambiguous analyses where necessary. 
        Returns list of UD annotation dictionaries.
        """
        first_base_ud_annotation = { attr:'' for attr in self.output_attributes}
        vm_pos   = vm_annotation['partofspeech']
        vm_form  = vm_annotation['form']
        vm_lemma = vm_annotation['lemma']
        vm_lemma_clean = (vm_annotation['lemma'].replace('_', '')).replace('=', '')
        first_base_ud_annotation['feats']   = OrderedDict()
        first_base_ud_annotation['xpostag'] = vm_pos
        first_base_ud_annotation['lemma']   = vm_lemma
        has_ambiguity = False

        _add_hyph_feat = (word_str == '--') or _dash_ending_word.match(word_str)

        # 0) Use dictionary-based conversions loaded from files as the first step
        # https://github.com/EstSyntax/EstUD/blob/master/cgmorf2conllu/cgmorf2conllu.py#L425-L432 
        ud_annotations = [first_base_ud_annotation]
        new_ud_annotations = []
        for base_ud_annotation in ud_annotations:
            annotations_added = False
            if vm_pos in self._pos_lemma_conv_rules:
                if vm_lemma_clean in self._pos_lemma_conv_rules[vm_pos]:
                    # Conversion rules based on vm_pos & vm_lemma.
                    # Note: there can be multiple UD annotations corresponding 
                    # to given VM annotation. Add them all:
                    for dict_rules in self._pos_lemma_conv_rules[vm_pos][vm_lemma_clean]:
                        # Copy base annotation
                        new_annotation = \
                            {k:base_ud_annotation[k] for k in base_ud_annotation.keys()}
                        new_annotation['feats'] = base_ud_annotation['feats'].copy()
                        if 'upostag' in dict_rules:
                            new_annotation['upostag'] = dict_rules['upostag']
                        if 'feats' in dict_rules:
                            for k, v in dict_rules['feats'].items():
                                new_annotation['feats'][k] = v
                        new_ud_annotations.append( new_annotation )
                        annotations_added = True
                if vm_lemma_clean in self._lemma_conv_rules:
                    # Conversion rules based on vm_lemma.
                    # Note: there can be multiple UD annotations corresponding 
                    # to given VM annotation. Add them all:
                    for dict_rules in self._lemma_conv_rules[vm_lemma_clean]:
                        # Copy base annotation
                        new_annotation = \
                            {k:base_ud_annotation[k] for k in base_ud_annotation.keys()}
                        new_annotation['feats'] = base_ud_annotation['feats'].copy()
                        if 'upostag' in dict_rules:
                            new_annotation['upostag'] = dict_rules['upostag']
                        if 'feats' in dict_rules:
                            for k, v in dict_rules['feats'].items():
                                new_annotation['feats'][k] = v
                        new_ud_annotations.append( new_annotation )
                        annotations_added = True
            if not annotations_added:
                new_ud_annotations.append( base_ud_annotation )
        
        # Use static conversion rules
        ud_annotations = new_ud_annotations
        new_ud_annotations = []
        for base_ud_annotation in ud_annotations:
            # 1) Convert part-of-speech, following: 
            # https://github.com/EstSyntax/EstUD/blob/master/cgmorf2conllu/cgmorf2conllu.py#L435-L538
            if base_ud_annotation['upostag'] == '':
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
                    # Fix: according to the UD corpus, the most frequent
                    # partofspeech for 'G' is actually 'ADJ', not 'NOUN';
                    base_ud_annotation['upostag'] = 'ADJ'
                    # TODO: should we really add Number/Case feats ?
                    # (these are not annotated in the corpus)
                    base_ud_annotation['feats']['Number'] = 'Sing'
                    base_ud_annotation['feats']['Case']   = 'Gen'

            # 2) Convert morphological features of nouns and declinable words: 
            
            # Number:
            # https://github.com/EstSyntax/EstUD/blob/master/cgmorf2conllu/cgmorf2conllu.py#L545-L551
            if ('sg' in vm_form or vm_form=='adt') and _has_postag(base_ud_annotation['upostag'], ['NOUN', 'PROPN', 'ADJ', 'DET', 'PRON', 'NUM']):
                base_ud_annotation['feats']['Number'] = 'Sing'
            elif 'pl' in vm_form and _has_postag(base_ud_annotation['upostag'], ['NOUN', 'PROPN', 'ADJ', 'DET', 'PRON', 'NUM']):
                base_ud_annotation['feats']['Number'] = 'Plur'

            # Case:
            # https://github.com/EstSyntax/EstUD/blob/master/cgmorf2conllu/cgmorf2conllu.py#L566-L620
            if _has_postag(base_ud_annotation['upostag'], ['NOUN', 'PROPN', 'ADJ', 'DET', 'PRON', 'NUM']):
                case = ''
                if len(vm_form.split()) > 1:
                    case = vm_to_ud_case_mapping.get(vm_form.split()[1], '')
                elif vm_form == 'adt':
                    case = vm_to_ud_case_mapping.get(vm_form)
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

            # Hyph=Yes:
            if _add_hyph_feat:
                base_ud_annotation['feats']['Hyph'] = 'Yes'

            # 3) Convert morphological features of verbs: 
            if _has_postag(base_ud_annotation['upostag'], ['VERB', 'AUX']):
                # Some exceptional verb forms
                if vm_lemma == 'ei':
                    # Add AUX annotation (primary interpretation)
                    base_ud_annotation['upostag'] = 'AUX'
                    base_ud_annotation['feats']['Polarity'] = 'Neg'
                    new_ud_annotations.append( base_ud_annotation )
                elif vm_lemma in ['kuulukse', 'tunnukse', 'näikse']:
                    base_ud_annotation['feats']['Tense'] = 'Pres'
                    base_ud_annotation['feats']['Mood'] = 'Ind'
                    base_ud_annotation['feats']['VerbForm']  = 'Fin'
                    new_ud_annotations.append( base_ud_annotation )
                else:
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
                    if all_form_annotations:
                        new_ud_annotations.extend( all_form_annotations )
                    else:
                        new_ud_annotations.append( base_ud_annotation )
            else:
                new_ud_annotations.append( base_ud_annotation )
        
        ud_annotations = new_ud_annotations
        if has_ambiguity:
            # if there were ambiguities (comma-separated variants), then generate all combinations
            new_ud_annotations = []
            for base_ud_annotation in ud_annotations:
                new_ud_annotations.extend( self._generate_ambiguous_analyses(base_ud_annotation) )
            ud_annotations = new_ud_annotations

        return ud_annotations


    def _postcorrect_participles(self, ud_annotations):
        '''
        Makes postcorrections to ambiguous participles. 
        
        Basically, detects if an adjective lemma has possible 
        participle ending ('nud', 'tud', 'tav' or 'v'), and if so, 
        and the adjective is not in self._adj_with_no_verb_features, 
        then adds features VerbForm, Voice, Tense to the adjective. 
        
        Note: this is a heuristic, which may add verb participle 
        features to incorrect adjectives. Use variable 
        self._adj_with_no_verb_features to specify, which adjectives 
        should not receive any verb features.
        
        Returns input ud_annotations with post-corrections (if any).
        '''
        new_annotations = []
        for ud_annotation in ud_annotations:
            if _has_postag(ud_annotation['upostag'], ['ADJ']):
                adj_lemma = ud_annotation['lemma']
                if adj_lemma in self._adj_with_no_verb_features:
                    # Skip adjectives that shouldn't 
                    # receive participle features
                    continue
                adj_ending = _participle_ending(adj_lemma)
                matching_feats = []
                for ending, feats in _adj_verb_features:
                    if adj_ending == ending:
                        matching_feats.append( feats )
                for fid, feats in enumerate(matching_feats):
                    if fid == 0:
                        # Add verb features to this annotation
                        for attr, key in feats.items():
                            ud_annotation['feats'][attr] = key
                    else:
                        # Create entirely new annotation
                        new_annotation = \
                            {k:ud_annotation[k] for k in ud_annotation.keys()}
                        new_annotation['feats'] = \
                            ud_annotation['feats'].copy()
                        for attr, key in feats.items():
                            new_annotation['feats'][attr] = key
                        new_annotations.append(new_annotation)
        ud_annotations.extend(new_annotations)
        return ud_annotations


    def _remove_connegatives_heuristic(self, sent_ud_annotations):
        '''
        Removes annotations with Connegative=Yes if:
        * they are not preceded by words with Polarity=Neg annotations;
        * at least 1 annotation remains to the span with Connegative=Yes;
        Returns sent_ud_annotations with modifications.
        
        Note: this is heuristic. If a connegative word is preceded 
        by an unrecognized negative word (such as a slang word '2ra', 
        '2i' or 'äi'), then the deletion will be erroneous.
        '''
        _polarity_neg = []
        _remove_connegatives = []
        for aid, _ud_annotation in enumerate(sent_ud_annotations):
            [base_span, ud_annotation] = _ud_annotation
            if ud_annotation['feats'].get('Polarity', None)=='Neg':
                _polarity_neg.append(aid)
            elif ud_annotation['feats'].get('Connegative', None)=='Yes':
                if len(_polarity_neg) == 0:
                    # If there is no word with Polarity=Neg before the 
                    # Connegative=Yes word, then we can remove 
                    # Connegative=Yes annotation altogether
                    # 1) Check that there is also an annotation without 
                    #    Connegative=Yes for the given base span
                    remaining_span_annotations = \
                        [u for u in sent_ud_annotations \
                           if u[0] == base_span and \
                           'Connegative' not in u[1]['feats']]
                    if len(remaining_span_annotations) > 0:
                        # 2) If at least one annotation remains after 
                        # removing Connegative=Yes annotation, we can 
                        # remove it safely
                        _remove_connegatives.append(aid)
        if _remove_connegatives:
            new_sent_ud_annotations=[]
            for aid, _ud_annotation in enumerate(sent_ud_annotations):
                if aid not in _remove_connegatives:
                    new_sent_ud_annotations.append(_ud_annotation)
            sent_ud_annotations=new_sent_ud_annotations
        return sent_ud_annotations