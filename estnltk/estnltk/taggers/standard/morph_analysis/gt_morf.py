#
#  Converts morphological analyses categories from Vabamorf's / Filosoft's format 
#  to giellatekno's (GT) format.
#
#  Most of the logic builds upon EstNLTK 1.4.1's gt_conversion:
#  https://github.com/estnltk/estnltk/blob/3ba73f8fa397f34cd55b1203026819c79486dffd/estnltk/converters/gt_conversion.py
#
# 

import regex as re
from collections import OrderedDict

from estnltk_core.converters import span_to_records

from estnltk import Layer, Text

from estnltk.taggers import Tagger
from estnltk.taggers import VabamorfTagger

from estnltk.taggers.standard.morph_analysis.morf_common import ESTNLTK_MORPH_ATTRIBUTES
from estnltk.taggers.standard.morph_analysis.morf_common import _is_empty_annotation
from estnltk.taggers.standard.morph_analysis.morf_common import _create_empty_morph_record

# =========================================================================================
#    Convert nominal categories
# =========================================================================================

_noun_conversion_rules = [
    ["pl n", "Pl Nom"],
    ["sg n", "Sg Nom"],
    ["pl g", "Pl Gen"],
    ["sg g", "Sg Gen"],
    ["pl p", "Pl Par"],
    ["sg p", "Sg Par"],
    ["pl ill", "Pl Ill"],
    ["sg ill", "Sg Ill"],
    ["adt",    "Sg Ill"],
    ["pl in", "Pl Ine"],
    ["sg in", "Sg Ine"],
    ["pl el", "Pl Ela"],
    ["sg el", "Sg Ela"],
    ["pl all", "Pl All"],
    ["sg all", "Sg All"],
    ["pl ad", "Pl Ade"],
    ["sg ad", "Sg Ade"],
    ["pl abl", "Pl Abl"],
    ["sg abl", "Sg Abl"],
    ["pl tr", "Pl Tra"],
    ["sg tr", "Sg Tra"],
    ["pl ter", "Pl Trm"],
    ["sg ter", "Sg Trm"],
    ["pl es", "Pl Ess"],
    ["sg es", "Sg Ess"],
    ["pl ab", "Pl Abe"],
    ["sg ab", "Sg Abe"],
    ["pl kom", "Pl Com"],
    ["sg kom", "Sg Com"],
]

def _convert_nominal_form( analysis ):
    ''' Converts nominal categories of the input analysis. 
        Performs one-to-one conversions only. '''
    assert 'form' in analysis, '(!) The input analysis does not contain "form" key.'
    for idx, pattern_items in enumerate(_noun_conversion_rules):
        pattern_str, replacement = pattern_items
        if pattern_str in analysis['form']:
           analysis['form'] = analysis['form'].replace( pattern_str, replacement )
    return analysis


# =========================================================================================
#    Convert verbal categories
# =========================================================================================

# ===================================
#    One - to - many
# ===================================

_amb_verb_conversion_rules = [ \
     [".r[^ ]*", "V", "(neg) o",   ['\\1 Pers Prs Imprt Sg2']], \
     ["ol[^ ]*", "V", "(neg) o",   ['\\1 Pers Prs Ind Neg']], \
     ["ol[^ ]*", "V", "(neg) nud", ['\\1 Pers Prt Ind Neg']], \
     ["ol[^ ]*", "V", "(neg) tud", ['\\1 Impers Prt Ind Neg']], \

     ["[^ ]*", "V", "([ neg]*)ksid",   ['\\1 Pers Prs Cond Pl3 Aff', '\\1 Pers Prs Cond Sg2 Aff']], \
     ["[^ ]*", "V", "([ neg]*)nuksid", ['\\1 Pers Prt Cond Pl3 Aff', '\\1 Pers Prt Cond Sg2 Aff']], \
     ["[^ ]*", "V", "([ neg]*)tud",    ['\\1 Impers Prt Ind Neg',    '\\1 Impers Prt Prc']], \

     ["mine[^ ]*", "V", "o",          ['Pers Prs Imprt Sg2']], \
     ["mine[^ ]*", "V", "(neg) o",    ['Pers Prs Ind Neg']], \

     ["[^ ]*", "V", "nud",   ['Pers Prt Imprt', 'Pers Prt Ind Neg', 'Pers Prt Prc']], \
     ["[^ ]*", "V", "o",     ['Pers Prs Imprt Sg2', 'Pers Prs Ind Neg']], \
     ["[^ ]*", "V", "sid",   ['Pers Prt Ind Pl3 Aff', 'Pers Prt Ind Sg2 Aff']], \
]

def _convert_amb_verbal_form( analysis ):
    ''' Converts ambiguous verbal categories of the input analysis. 
        Performs one-to-many conversions. '''
    assert 'form' in analysis, '(!) The input analysis does not contain "form" key.'
    results = []
    for root_pat, pos, form_pat, replacements in _amb_verb_conversion_rules:
        if analysis['partofspeech'] == pos and \
           re.match(root_pat, analysis['root']) and \
           re.match(form_pat, analysis['form']):
            for replacement in replacements:
                new_analysis = analysis.copy()
                new_form = re.sub(form_pat, replacement, analysis['form'])
                new_analysis['form'] = new_form
                results.append( new_analysis )
            # break after the replacement has been made
            # ( to avoid over-generation )
            break
    if not results:
       results.append( analysis )
    return results

# ===================================
#    One - to - one
# ===================================

_verb_conversion_rules = [ \
    ["neg da",	"Impers Prs Ind Neg"], \
    ["b",	"Pers Prs Ind Sg3 Aff"], \
    ["da",	"Inf"], \
    ["des",	"Ger"], \
    ["d",	"Pers Prs Ind Sg2 Aff"], \
    ["gem",	"Pers Prs Imprt Pl1"], \
    ["ge",	"Pers Prs Imprt Pl2"], \
    ["gu",	"Pers Prs Imprt"], \
    ["ksime",	"Pers Prs Cond Pl1 Aff"], \
    ["ksin",	"Pers Prs Cond Sg1 Aff"], \
    ["ksite",	"Pers Prs Cond Pl2 Aff"], \
    ["ks",	"Pers Prs Cond"], \
    ["maks",	"Pers Sup Tra"], \
    ["mast",	"Pers Sup Ela"], \
    ["mas",	"Pers Sup Ine"], \
    ["mata",	"Pers Sup Abe"], \
    ["ma",	"Pers Sup Ill"], \
    ["me",	"Pers Prs Ind Pl1 Aff"], \
    ["nuksime",	"Pers Prt Cond Pl1 Aff"], \
    ["nuksin",	"Pers Prt Cond Sg1 Aff"], \
    ["nuksite",	"Pers Prt Cond Pl2 Aff"], \
    ["nuks",	"Pers Prt Cond"], \
    ["nuvat",	"Pers Prt Quot"], \
    ["n",	"Pers Prs Ind Sg1 Aff"], \
    ["sime",	"Pers Prt Ind Pl1 Aff"], \
    ["sin",	"Pers Prt Ind Sg1 Aff"], \
    ["site",	"Pers Prt Ind Pl2 Aff"], \
    ["s",	"Pers Prt Ind Sg3 Aff"], \
    ["tagu",	"Impers Prs Imprt"], \
    ["takse",	"Impers Prs Ind Aff"], \
    ["taks",	"Impers Prs Cond"], \
    ["tama",	"Impers Sup"], \
    ["tavat",	"Impers Prs Quot"], \
    ["ta",	"Impers Prs Ind Neg"], \
    ["tav",	"Impers Prs Prc"], \
    ["te",	"Pers Prs Ind Pl2 Aff"], \
    ["ti",	"Impers Prt Ind Aff"], \
    ["tuks",	"Impers Prt Cond"], \
    ["vad",	"Pers Prs Ind Pl3 Aff"], \
    ["vat",	"Pers Prs Quot"], \
    ["v",	"Pers Prs Prc"], \
]

def _convert_verbal_form( analysis ):
    ''' Converts ordinary verbal categories of the input analysis. 
        Performs one-to-one conversions. '''
    assert 'form' in analysis, '(!) The input analysis does not contain "form" key.'
    for form, replacement in _verb_conversion_rules:
        # Exact match
        if analysis['form'] == form:
           assert analysis['partofspeech'] == 'V', \
               '(!) Expected analysis of verb, but got analysis of "'+str(analysis['partofspeech'])+'" instead.'
           analysis['form'] = replacement
        # Inclusion :   the case of some_prefix+' '+form ;
        elif analysis['form'].endswith(' '+form):
           parts  = analysis['form'].split()
           prefix = ' '.join( parts[:len(parts)-1] )
           analysis['form'] = prefix+' '+replacement
    return analysis


# =====================================
#  Perform post-processing / fixing #1
# =====================================

def _make_postfixes_1( analysis ):
    ''' Provides some post-fixes. '''
    assert 'form' in analysis, '(!) The input analysis does not contain "form" key.'
    if 'neg' in analysis['form']:
        analysis['form'] = re.sub( r'^\s*neg ([^,]*)$',  '\\1 Neg',  analysis['form'] )
    analysis['form'] = re.sub( ' Neg Neg$',  ' Neg',  analysis['form'] )
    analysis['form'] = re.sub( ' Aff Neg$',  ' Neg',  analysis['form'] )
    analysis['form'] = re.sub( 'neg',  'Neg',  analysis['form'] )
    analysis['form'] = analysis['form'].rstrip().lstrip()
    assert 'neg' not in analysis['form'], \
                '(!) The label "neg" should be removed by now.'
    assert 'Neg' not in analysis['form'] or \
                ('Neg' in analysis['form'] and analysis['form'].endswith('Neg')), \
                 '(!) The label "Neg" should end the analysis line: '+str(analysis['form'])
    return analysis


# =====================================
#  Perform post-processing / fixing #2
# =====================================

def _make_postfixes_2( morph_dict_list:list ):
    ''' Provides some post-fixes after the disambiguation. '''
    for analysis in morph_dict_list:
        analysis['form'] = re.sub( '(Sg|Pl)([123])', '\\1 \\2', analysis['form'] )
    return morph_dict_list



# ===================================================================
#   T h e   m a i n   c l a s s
# ===================================================================

class GTMorphConverter( Tagger ):
    """Converts morphological analyses from Vabamorf's format to Giellatekno's (GT) format. 
       Stores results of the conversion on a new layer."""
    output_layer      = 'gt_morph_analysis'
    output_attributes = VabamorfTagger.output_attributes
    input_layers      = ['words', 'sentences', 'morph_analysis']
    conf_param = [ # Configuration flags
                   'disambiguate_neg', 'disambiguate_sid_ksid', \
                   # Names of the specific input layers
                   '_input_words_layer', \
                   '_input_sentences_layer', \
                   '_input_morph_analysis_layer', \
                   '_input_clauses_layer', \
                 ]

    def __init__(self, \
                 output_layer:str='gt_morph_analysis', \
                 input_words_layer:str='words', \
                 input_sentences_layer:str='sentences', \
                 input_morph_analysis_layer:str='morph_analysis', \
                 input_clauses_layer:str='clauses', \
                 disambiguate_neg:bool = True, \
                 disambiguate_sid_ksid:bool = True ):
        ''' Initializes this GTMorphConverter.
            
            Parameters
            -----------
            output_layer: str (default: 'gt_morph_analysis')
                Name for the gt_morph_analysis layer;
            
            input_words_layer: str (default: 'words')
                Name of the input words layer;

            input_sentences_layer: str (default: 'sentences')
                Name of the input sentences layer;
            
            input_morph_analysis_layer: str (default: 'morph_analysis')
                Name of the input morph_analysis layer;
            
            input_clauses_layer: str (default: 'clauses')
                Name of the input clauses layer;
            
            disambiguate_neg : bool
                Whether the conversion is followed by disambiguation of verb 
                categories related to negation;
                Default: True;

            disambiguate_sid_ksid : bool
                Whether the conversion is followed by disambiguation of verb 
                categories 'Pers Prt Ind Pl3 Aff' and 'Pers Prt Ind Sg2 Aff';
                Default: True;
        '''
        # Set input/output layer names
        self.output_layer = output_layer
        self._input_words_layer          = input_words_layer
        self._input_sentences_layer      = input_sentences_layer
        self._input_morph_analysis_layer = input_morph_analysis_layer
        self._input_clauses_layer        = input_clauses_layer
        self.input_layers = [input_words_layer, input_sentences_layer, input_morph_analysis_layer]
        # Set configuration flags
        self.disambiguate_neg = disambiguate_neg
        self.disambiguate_sid_ksid = disambiguate_sid_ksid
        # Adjust input requirements
        if self.disambiguate_sid_ksid:
            self.input_layers.append( input_clauses_layer )


    def _make_layer_template(self):
        """Creates and returns a template of the layer."""
        return Layer(name=self.output_layer,
                     parent=self._input_morph_analysis_layer,
                     text_object=None,
                     ambiguous=True,
                     attributes=self.output_attributes)


    def _make_layer(self, text, layers, status: dict):
        """Creates gt_morph_analysis layer.
        
        Parameters
        ----------
        text: Text
           Text object that will be tagged;
          
        layers: MutableMapping[str, Layer]
           Layers of the text. Contains mappings from the 
           name of the layer to the Layer object. Must contain
           words, sentences, and morph_analysis. If
           disambiguate_sid_ksid is turned on, clauses layer
           is also required;
          
        status: dict
           This can be used to store metadata on layer tagging.
        """
        # 0) Create an empty layer
        gt_morph = self._make_layer_template()
        gt_morph.text_object = text

        # 1) Perform the conversion
        new_morph_dicts = self._convert_analysis( text, layers, status )
        
        # 2) Perform some context-specific disambiguation
        if self.disambiguate_neg:
            self._disambiguate_neg( new_morph_dicts )
        if self.disambiguate_sid_ksid:
            self._disambiguate_sid_ksid( new_morph_dicts, text, layers, status, 
                                         scope = self._input_clauses_layer )
            self._disambiguate_sid_ksid( new_morph_dicts, text, layers, status, 
                                         scope = self._input_sentences_layer )
        
        _make_postfixes_2( new_morph_dicts )
        
        # 3) Convert analysis dicts to Spans, and attach to the layer
        self._attach_annotations( text, layers, status, new_morph_dicts, new_layer=gt_morph)
        

        # 4) Return the layer
        return gt_morph



    # =========================================================================================
    #    Convert from Vabamorf's format to GT format
    # =========================================================================================

    def _convert_analysis( self, text:Text, layers, status: dict ):
        ''' Converts morphological analyses (in the morph_analysis layer) from FS's 
            Vabamorf's format to giellatekno's (GT) format. Returns a new list of 
            dictionaries, each corresponding to a single morphological analysis record;
            
            Note: due to one-to-many conversion rules, the number of analyses returned 
            by this method can be greater than the number of analyses in the input 
            morph_analysis layer .   Converted  analyses  need  to  go  through  a 
            disambiguation process.
        '''
        # Check for required layers
        for req_layer in [ self._input_words_layer, self._input_morph_analysis_layer ]:
            assert req_layer in layers.keys(), \
                '(!) The input text should contain "'+str(req_layer)+'" layer.'
        analysis_dicts = []
        morph_span_id  = 0
        # Iterate over the words layer
        words = layers[ self._input_words_layer ]
        morph_analysis = layers[ self._input_morph_analysis_layer ]
        for word in words:
            wstart = word.start
            wend   = word.end
            # Find all Vabamorf's analyses corresponding to 
            # the current word
            while(morph_span_id < len(morph_analysis)):
                vabamorf_span = morph_analysis[morph_span_id]
                vmstart = vabamorf_span.start
                vmend   = vabamorf_span.end
                if vmstart == wstart and vmend == wend:
                    if not _is_empty_annotation(vabamorf_span.annotations[0]):
                        new_analyses = span_to_records( vabamorf_span )
                        # Convert noun categories
                        new_analyses = [_convert_nominal_form( a ) for a in new_analyses ]
                        # Convert ambiguous verb categories
                        new_analyses = [_convert_amb_verbal_form( a ) for a in new_analyses]
                        new_analyses = sum(new_analyses, [])  # Flatten the list
                        # Convert remaining verbal categories
                        new_analyses = [_convert_verbal_form( a ) for a in new_analyses]
                        # Make postfixes
                        new_analyses = [_make_postfixes_1( a ) for a in new_analyses]
                        # Append new analyses
                        analysis_dicts.extend( new_analyses )
                    else:
                        # Analysis is empty (an unknown word)
                        new_analyses = span_to_records( vabamorf_span )
                        # Convert None to empty string
                        for analysis in new_analyses:
                            for key in analysis.keys():
                                if analysis[key] is None:
                                    analysis[key] = ''
                        # Append new analyses
                        analysis_dicts.extend( new_analyses )
                    morph_span_id += 1
                else:
                    break
        return analysis_dicts


    # =====================================
    #  Initial disambiguation in GT format
    # =====================================

    def _disambiguate_neg( self, morph_dict_list:list ):
        ''' Disambiguates forms ambiguous between multiword negation and some 
            other form;
        '''
        # ids of the analyses of the current word:
        cur_word_analyses_ids = [] 
        # lemma of the previous word:
        prev_word_lemma       = ''
        # ids of the analyses that should be deleted:
        analyses_to_delete = OrderedDict()
        #
        # Iterate over all analyses, group analyses by words, and decide, 
        # which analyses need to be deleted 
        #
        for aid, analysis_dict in enumerate(morph_dict_list):
            word_start = analysis_dict['start']
            word_end   = analysis_dict['end']
            if not cur_word_analyses_ids:
                # Collect the analysis
                cur_word_analyses_ids.append( aid )
            else:
                # Check if this analysis and the previous analysis
                # belong to the same word
                last_analysis = morph_dict_list[cur_word_analyses_ids[-1]]
                if word_start == last_analysis['start'] and \
                   word_end == last_analysis['end']:
                    # Collect the analysis id
                    cur_word_analyses_ids.append( aid )
                else:
                    # Analyses belong to different words
                    
                    # A. Analyse the collected analyses and decide which 
                    #    ones should be removed; record id-s of analyses
                    #    that are to be removed
                    forms = [ morph_dict_list[cwaid]['form'] for cwaid in cur_word_analyses_ids ]
                    if ('Pers Prs Imprt Sg2' in forms and 'Pers Prs Ind Neg' in forms):
                        if (prev_word_lemma == "ei" or prev_word_lemma == "ega"):
                            # ei saa, ei tee ==>
                            # keep 'Pers Prs Ind Neg'
                            # delete 'Pers Prs Imprt Sg2'
                            for cwaid in cur_word_analyses_ids:
                                cur_word_analysis = morph_dict_list[cwaid]
                                if cur_word_analysis['form'] == 'Pers Prs Imprt Sg2':
                                    analyses_to_delete[cwaid] = True
                        else:
                            # saa! tee! ==>
                            # keep 'Pers Prs Imprt Sg2'
                            # delete 'Pers Prs Ind Neg'
                            for cwaid in cur_word_analyses_ids:
                                cur_word_analysis = morph_dict_list[cwaid]
                                if cur_word_analysis['form'] == 'Pers Prs Ind Neg':
                                    analyses_to_delete[cwaid] = True
                    if ('Pers Prt Imprt' in forms and 'Pers Prt Ind Neg' in forms and \
                        'Pers Prt Prc' in forms):
                        if (prev_word_lemma == "ei" or prev_word_lemma == "ega"):
                            # ei saanud, ei teinud ==>
                            # keep 'Pers Prt Ind Neg'
                            # delete 'Pers Prt Imprt','Pers Prt Prc'
                            for cwaid in cur_word_analyses_ids:
                                cur_word_analysis = morph_dict_list[cwaid]
                                if cur_word_analysis['form'] in ['Pers Prt Imprt','Pers Prt Prc']:
                                    analyses_to_delete[cwaid] = True
                        else:
                            # on, oli saanud teinud; kukkunud õun; ... ==>
                            # keep 'Pers Prt Prc'
                            # delete 'Pers Prt Imprt','Pers Prt Ind Neg'
                            for cwaid in cur_word_analyses_ids:
                                cur_word_analysis = morph_dict_list[cwaid]
                                if cur_word_analysis['form'] in ['Pers Prt Imprt','Pers Prt Ind Neg']:
                                    analyses_to_delete[cwaid] = True
                    if ('Impers Prt Ind Neg' in forms and 'Impers Prt Prc' in forms):
                        if (prev_word_lemma == "ei" or prev_word_lemma == "ega"):
                            # ei saadud, ei tehtud ==> 
                            # keep 'Impers Prt Ind Neg'
                            # delete 'Impers Prt Prc'
                            for cwaid in cur_word_analyses_ids:
                                cur_word_analysis = morph_dict_list[cwaid]
                                if cur_word_analysis['form'] == 'Impers Prt Prc':
                                    analyses_to_delete[cwaid] = True
                        else:
                            # on, oli saadud tehtud; saadud õun; ... ==>
                            # keep 'Impers Prt Prc'
                            # delete 'Impers Prt Ind Neg'
                            for cwaid in cur_word_analyses_ids:
                                cur_word_analysis = morph_dict_list[cwaid]
                                if cur_word_analysis['form'] == 'Impers Prt Ind Neg':
                                    analyses_to_delete[cwaid] = True

                    # B. Record lemma of the previous word
                    cur_word_analysis = morph_dict_list[cur_word_analyses_ids[0]]
                    prev_word_lemma = cur_word_analysis['root']
                    
                    # C. Finally: reset the list of analyses id-s
                    cur_word_analyses_ids = [] 
                    # And collect the new analysis id
                    cur_word_analyses_ids.append( aid )
        
        # Finally, perform the deletion
        if len(analyses_to_delete.keys()) > 0:
            to_delete = list( analyses_to_delete.keys() )
            to_delete.reverse()
            for aid in to_delete:
                del morph_dict_list[aid]

        return morph_dict_list



    def _disambiguate_sid_ksid(self, morph_dict_list:list, text:Text, layers, status: dict, \
                                     scope:str='clauses' ):
        ''' Disambiguates verb forms based on existence of 2nd person pronoun ('sina') 
            in given scope. The scope could be either 'clauses' or 'sentences'.
        '''
        assert scope in ['clauses', 'sentences'], \
               '(!) The scope should be either "clauses" or "sentences".'
        
        # 1) Find word id-s corresponding to morph analyses dicts
        morph_dict_word_ids = []
        current_word_id = 0
        for aid, analysis_dict in enumerate( morph_dict_list ):
            word_start = analysis_dict['start']
            word_end   = analysis_dict['end']
            if aid - 1 > -1:
                last_word_start = morph_dict_list[aid-1]['start']
                last_word_end   = morph_dict_list[aid-1]['end']
                if last_word_start != word_start and \
                   last_word_end != word_end:
                    # Advance with word_id
                    current_word_id += 1
            morph_dict_word_ids.append(current_word_id)
        assert len(morph_dict_word_ids) == len(morph_dict_list)
        
        # 2) Disambiguate 
        group_indices = self._get_unique_word_group_indices( text, layers, status, 
                                                             word_group=scope )
        # ids of the analyses of the current word:
        cur_word_analyses_ids = []
        # ids of the analyses that should be deleted:
        analyses_to_delete = OrderedDict()
        # record if group of the current word contains 2nd person pronoun
        gr_2nd_person_pron = {}
        for aid, analysis_dict in enumerate( morph_dict_list ):
            # word index for the current analysis
            current_word_id = morph_dict_word_ids[aid]
            # group index for the current word
            gr_index = group_indices[current_word_id]
            
            # Analyse word's group
            if gr_index not in gr_2nd_person_pron:
                # 1) Find out whether the current group (clause or sentence) contains "sina"
                j = aid
                gr_2nd_person_pron_found = False
                words_passed = 0
                last_word_id_2 = current_word_id
                while j < len( morph_dict_list ):
                    current_word_id_2 = morph_dict_word_ids[j]
                    if last_word_id_2 != current_word_id_2:
                        words_passed += 1
                    if group_indices[current_word_id_2] == gr_index:
                        forms  = [ morph_dict_list[j]['form'] ]
                        lemmas = [ morph_dict_list[j]['root'] ]
                        if 'sina' in lemmas and 'Sg Nom' in forms:
                            gr_2nd_person_pron_found = True
                            break
                    if words_passed >= 10:  # do not venture too far ...
                        break
                    j += 1
                    last_word_id_2 = current_word_id_2
                gr_2nd_person_pron[gr_index] = gr_2nd_person_pron_found
            
            # Collect analysis of the current word 
            cur_word_analyses_ids.append( aid )
            
            # Determine next word id 
            next_word_id = \
                morph_dict_word_ids[aid+1] if aid+1 < len(morph_dict_word_ids) else -1
            
            if next_word_id == -1 or current_word_id != next_word_id:
                # We have last analysis or the next analysis belongs to a new word
                # 2) Disambiguate verb forms based on existence of 'sina' in the word group
                forms = [ morph_dict_list[cwaid]['form'] for cwaid in cur_word_analyses_ids ]
                if ('Pers Prt Ind Pl3 Aff' in forms and 'Pers Prt Ind Sg2 Aff' in forms):
                   if not gr_2nd_person_pron[ gr_index ]:
                        # -sid , "sina" missing ==> 
                        # keep 'Pers Prt Ind Pl3 Aff'
                        # delete 'Pers Prt Ind Sg2 Aff'
                        for cwaid in cur_word_analyses_ids:
                            cur_word_analysis = morph_dict_list[cwaid]
                            if cur_word_analysis['form'] == 'Pers Prt Ind Sg2 Aff':
                                analyses_to_delete[cwaid] = True
                   else:
                        # -sid , "sina" exists ==> 
                        # keep 'Pers Prt Ind Sg2 Aff'
                        # delete 'Pers Prt Ind Pl3 Aff'
                        for cwaid in cur_word_analyses_ids:
                            cur_word_analysis = morph_dict_list[cwaid]
                            if cur_word_analysis['form'] == 'Pers Prt Ind Pl3 Aff':
                                analyses_to_delete[cwaid] = True
                if ('Pers Prs Cond Pl3 Aff' in forms and 'Pers Prs Cond Sg2 Aff' in forms):
                   if not gr_2nd_person_pron[ gr_index ]:
                        # -ksid , "sina" missing ==> 
                        # keep 'Pers Prs Cond Pl3 Aff'
                        # delete 'Pers Prs Cond Sg2 Aff'
                        for cwaid in cur_word_analyses_ids:
                            cur_word_analysis = morph_dict_list[cwaid]
                            if cur_word_analysis['form'] == 'Pers Prs Cond Sg2 Aff':
                                analyses_to_delete[cwaid] = True
                   else:
                        # -ksid , "sina" exists ==> 
                        # keep 'Pers Prs Cond Sg2 Aff'
                        # delete 'Pers Prs Cond Pl3 Aff'
                        for cwaid in cur_word_analyses_ids:
                            cur_word_analysis = morph_dict_list[cwaid]
                            if cur_word_analysis['form'] == 'Pers Prs Cond Pl3 Aff':
                                analyses_to_delete[cwaid] = True
                if ('Pers Prt Cond Pl3 Aff' in forms and 'Pers Prt Cond Sg2 Aff' in forms):
                   if not gr_2nd_person_pron[ gr_index ]:
                        # -nuksid , "sina" missing ==> 
                        # keep 'Pers Prt Cond Pl3 Aff'
                        # delete 'Pers Prt Cond Sg2 Aff'
                        for cwaid in cur_word_analyses_ids:
                            cur_word_analysis = morph_dict_list[cwaid]
                            if cur_word_analysis['form'] == 'Pers Prt Cond Sg2 Aff':
                                analyses_to_delete[cwaid] = True
                   else:
                        # -nuksid , "sina" exists ==> 
                        # keep 'Pers Prt Cond Sg2 Aff'
                        # delete 'Pers Prt Cond Pl3 Aff'
                        for cwaid in cur_word_analyses_ids:
                            cur_word_analysis = morph_dict_list[cwaid]
                            if cur_word_analysis['form'] == 'Pers Prt Cond Pl3 Aff':
                                analyses_to_delete[cwaid] = True
                cur_word_analyses_ids = []

        # 3) Finally, perform the deletion
        if len(analyses_to_delete.keys()) > 0:
            to_delete = list(analyses_to_delete.keys())
            to_delete.reverse()
            for aid in to_delete:
                del morph_dict_list[aid]

        return morph_dict_list

    # =====================================
    #  Clause/sentence indices for words
    # =====================================

    def _get_unique_word_group_indices( self, text:Text, layers, status: dict, \
                                              word_group:str = 'clauses' ):
        ''' Returns a list of word group indices that contains a group index  
            for each word in the text.  A  group  index  tells which group a 
            word belongs to.
            Types of word groups: clauses, sentences;
            Group indices are unique over the whole text. 
        '''
        assert word_group in [self._input_sentences_layer, self._input_clauses_layer], \
               '(!) The word_group should be either {} or {}.'.format( \
                        self._input_sentences_layer, self._input_clauses_layer )
        assert word_group in layers
        # Collect (unique) word group indices over the whole text
        word_group_indices = []
        word_layer = layers[self._input_words_layer]
        word_group_layer = layers[word_group]
        word_span_id  = 0
        #  Collect all words inside the group
        while word_span_id < len(word_layer):
            # Get word span
            word_span = word_layer[word_span_id]
            # Find group the word belongs to
            group_span_id = 0
            while group_span_id < len(word_group_layer):
                group_span = word_group_layer[group_span_id]
                if group_span.start <= word_span.start and \
                   word_span.end <= group_span.end:
                   # Record id of the group word belongs to
                    word_group_indices.append( group_span_id )
                    break
                group_span_id += 1
            word_span_id += 1
        assert len(word_group_indices) == len(word_layer), \
            '(!) Number of word group indices should match the number of words!'
        return word_group_indices

    # =========================================================================================
    #    Finalize: convert analyses from dicts to Spans
    # =========================================================================================

    def _attach_annotations( self, text: Text, layers, status:dict, morph_dict_list:list, new_layer:Layer = None ):
        '''Converts morphological analyses (in the list morph_dict_list) 
           from dict format to (Ambiguous)Spans, and attaches spans to the 
           new_layer.
        '''
        assert new_layer is not None
        current_attributes = new_layer.attributes
        morph_span_id = 0
        # Iterate over (morph_analysis) words in Text
        record_groupings = 0
        for morph_word in layers[ self._input_morph_analysis_layer ]:
            wstart = morph_word.start
            wend   = morph_word.end
            # Find all morphological analyses corresponding to the 
            # current word
            current_records = []
            while( morph_span_id < len( morph_dict_list ) ):
                morph_dict = morph_dict_list[morph_span_id]
                if morph_dict['start'] == wstart and morph_dict['end'] == wend:
                    current_records.append( morph_dict )
                else:
                    break
                morph_span_id += 1
            assert len(current_records) > 0, \
                   '(!) Did not find any records corresponding to the morph_analysis_word at location {},{}'.format( wstart, wend )
            for record in current_records:
                # Check for emptiness of the record
                empty_attributes = []
                for attr in ESTNLTK_MORPH_ATTRIBUTES:
                    empty_attributes.append( record[attr] is None or \
                                             len(record[attr]) == 0 )
                if empty_attributes.count(True) > len(empty_attributes)/2:
                     # If most of the attributes have been set to '', 
                     # then we have an empty record (unknown word)
                     record = _create_empty_morph_record(morph_word,
                                                         layer_attributes=current_attributes)
                else:
                    # The record corresponds to word with full analyses
                    #     fix format of root_tokens
                    record['root_tokens'] = tuple(record['root_tokens'])
                # Finally, add annotation to the layer
                new_layer.add_annotation(morph_word, **record)
            record_groupings += 1
        # Sanity check: all morph_analysis words should have been converted
        assert record_groupings == len( layers[ self._input_morph_analysis_layer ].spans )
        # Return the layer augmented with spans
        return new_layer
