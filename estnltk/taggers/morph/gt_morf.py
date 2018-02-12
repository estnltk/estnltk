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

from estnltk.text import Span, Layer, Text
from estnltk.taggers import Tagger
from estnltk.taggers import VabamorfTagger

from estnltk.taggers.morph.morf_common import ESTNLTK_MORPH_ATTRIBUTES
from estnltk.taggers.morph.morf_common import _is_empty_span
from estnltk.taggers.morph.morf_common import _create_empty_morph_span

# =========================================================================================
#    Convert nominal categories
# =========================================================================================

_noun_conversion_rules = [ \
    ["pl n", "Pl Nom"],\
    ["sg n", "Sg Nom"],\
    ["pl g", "Pl Gen"],\
    ["sg g", "Sg Gen"],\
    ["pl p", "Pl Par"],\
    ["sg p", "Sg Par"],\
    ["pl ill", "Pl Ill"],\
    ["sg ill", "Sg Ill"],\
    ["adt",    "Sg Ill"],\
    ["pl in", "Pl Ine"],\
    ["sg in", "Sg Ine"],\
    ["pl el", "Pl Ela"],\
    ["sg el", "Sg Ela"],\
    ["pl all", "Pl All"],\
    ["sg all", "Sg All"],\
    ["pl ad", "Pl Ade"],\
    ["sg ad", "Sg Ade"],\
    ["pl abl", "Pl Abl"],\
    ["sg abl", "Sg Abl"],\
    ["pl tr", "Pl Tra"],\
    ["sg tr", "Sg Tra"],\
    ["pl ter", "Pl Trm"],\
    ["sg ter", "Sg Trm"],\
    ["pl es", "Pl Ess"],\
    ["sg es", "Sg Ess"],\
    ["pl ab", "Pl Abe"],\
    ["sg ab", "Sg Abe"],\
    ["pl kom", "Pl Com"],\
    ["sg kom", "Sg Com"],\
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
        analysis['form'] = re.sub( '^\s*neg ([^,]*)$',  '\\1 Neg',  analysis['form'] )
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


# =========================================================================================
#    Convert from Vabamorf's format to GT format
# =========================================================================================

def _convert_analysis( text: Text ):
    ''' Converts morphological analyses (in the layer 'morph_analysis') from FS's 
        Vabamorf's format to giellatekno's (GT) format. Returns a new list of 
        dictionaries, each corresponding to a single morphological analysis record;
        
        Note: due to one-to-many conversion rules, the number of analyses returned 
        by this method can be greater than the number of analyses in the input 
        layer 'morph_analysis'.  Converted  analyses  need  to  go  through  a 
        disambiguation process.
    '''
    # Check for required layers
    for req_layer in ['words', 'morph_analysis']:
        assert req_layer in text.layers, \
            '(!) The input text should contain "'+str(req_layer)+'" layer.'
    analysis_dicts = []
    morph_span_id = 0
    # Iterate over words in Text
    for word in text.words:
        wstart = word.start
        wend   = word.end
        # Find all Vabamorf's analyses corresponding to 
        # the current word
        while(morph_span_id < len(text.morph_analysis)):
            vabamorf_span = text.morph_analysis.spans[morph_span_id]
            vmstart = vabamorf_span.start
            vmend   = vabamorf_span.end
            if vmstart == wstart and vmend == wend:
                if not _is_empty_span( vabamorf_span.spans[0] ):
                    new_analyses = vabamorf_span.to_record()
                    # Convert noun categories
                    new_analyses = [ _convert_nominal_form( a ) for a in new_analyses ]
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
                    new_analyses = vabamorf_span.to_record()
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

def _disambiguate_neg( morph_dict_list:list ):
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


def _disambiguate_sid_ksid( morph_dict_list:list, text: Text, scope:str='clauses' ):
    ''' Disambiguates verb forms based on existence of 2nd person pronoun ('sina') 
        in given scope. The scope could be either 'clauses' or 'sentences'.
        
        Note: if 'clauses' or 'sentences' layers are missing, adds these layers 
              automatically;
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
    group_indices = get_unique_word_group_indices( text, word_group=scope )
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
#  Perform post-processing / fixing #2
# =====================================

def _make_postfixes_2( morph_dict_list:list ):
    ''' Provides some post-fixes after the disambiguation. '''
    for analysis in morph_dict_list:
        analysis['form'] = re.sub( '(Sg|Pl)([123])', '\\1 \\2', analysis['form'] )
    return morph_dict_list


# =====================================
#  Clause/sentence indices for words
# =====================================

def get_unique_word_group_indices( text: Text, word_group:str = 'clauses' ):
    ''' Returns a list of word group indices that contains a group index  
        for each word in the text.  A  group  index  tells which group a 
        word belongs to.
        Types of word groups: 'clauses', 'sentences';
        Group indices are unique over the whole text. 
    '''
    assert word_group in ['sentences', 'clauses'], \
           '(!) The word_group should be either "clauses" or "sentences".'
    # Add word group annotations (if missing)
    if word_group not in text.layers:
        text.tag_layer([word_group])
    # Collect (unique) word group indices over the whole text
    word_group_indices = []
    word_spans  = text['words'].spans
    group_spans = text[ word_group ].spans
    word_span_id  = 0
    #  Collect all words inside the group
    while word_span_id < len(word_spans):
        # Get word span
        word_span = word_spans[word_span_id]
        # Find group the word belongs to
        group_span_id = 0
        while group_span_id < len(group_spans):
            group_span = group_spans[group_span_id]
            if group_span.start <= word_span.start and \
               word_span.end <= group_span.end:
               # Record id of the group word belongs to
                word_group_indices.append( group_span_id )
                break
            group_span_id += 1
        word_span_id += 1
    assert len(word_group_indices) == len(word_spans), \
        '(!) Number of word group indices should match the number of words!'
    return word_group_indices


# =========================================================================================
#    Finalize: convert analyses from dicts to Spans
# =========================================================================================

def _create_spans( text: Text, morph_dict_list:list, layer:Layer = None ):
    '''Converts morphological analyses (from the list morph_dict_list) 
    from dict format to Spans. If layer is given, then attaches Spans to 
    the layer and returns the layer; otherwise, collects resulting Spans 
    into a list and returns the list.
    '''
    resulting_spans = []
    morph_span_id = 0
    # Iterate over words in Text
    for word in text.words:
        wstart = word.start
        wend   = word.end
        # Find all morphological analyses corresponding to the 
        # current word
        while(morph_span_id < len(morph_dict_list)):
            morph_dict = morph_dict_list[morph_span_id]
            if morph_dict['start'] == wstart and morph_dict['end'] == wend:
                span = None
                # Check for empty Span-s
                empty_attributes = []
                for attr in ESTNLTK_MORPH_ATTRIBUTES:
                    empty_attributes.append( morph_dict[attr] is None or \
                                             len(morph_dict[attr]) == 0 )
                if empty_attributes.count(True) > len(empty_attributes)/2:
                    # If most of the attributes have been set 
                    # to '', then we have an empty Span (unknown word)
                    current_attributes = layer.attributes if layer else None
                    span = \
                        _create_empty_morph_span(word, \
                                                 layer_attributes=current_attributes)
                else:
                    # The Span corresponds to word with full analyses
                    # Create corresponding Span-s
                    span = Span( parent=word )
                    for attr in morph_dict.keys():
                        if attr in ['start', 'end', 'text']:
                            continue
                        if attr == 'root_tokens':
                            # make it hashable for Span.__hash__
                            setattr(span, attr, tuple(morph_dict[attr]))
                        else:
                            setattr(span, attr, morph_dict[attr])
                assert span is not None
                # If layer has been provided, attach the span to the layer
                if layer:
                    layer.add_span( span )
                else:
                    resulting_spans.append( span )
                morph_span_id += 1
            else:
                break
    # Return either list of created spans or a layer augmented with spans
    return resulting_spans if not layer else layer

# ===================================================================

class GTMorphConverter(Tagger):
    description   = "Converts morphological analyses from Vabamorf's format to Giellatekno's (GT) format."
    layer_name    = None
    attributes    = VabamorfTagger.attributes
    depends_on    = None
    configuration = None
    
    def __init__(self, \
                 disambiguate_neg:bool = True, \
                 disambiguate_sid_ksid:bool = True, \
                 layer_name:str='gt_morph_analysis', **kwargs):
        ''' Initializes this GTMorphConverter.
            
            Parameters
            -----------
            disambiguate_neg : bool
                Whether the conversion is followed by disambiguation of verb 
                categories related to negation;
                Default: True;

            disambiguate_sid_ksid : bool
                Whether the conversion is followed by disambiguation of verb 
                categories 'Pers Prt Ind Pl3 Aff' and 'Pers Prt Ind Sg2 Aff';
                Note: if clause annotations are missing and this flag is switched
                on, then clause annotations will be automatically added;
                Default: True;

            layer_name : str
                Name of the layer on which converted morphological analyses are 
                stored.
                Default: 'gt_morph_analysis';
        '''
        self.kwargs = kwargs
        self.layer_name = layer_name
        
        self.configuration = {'disambiguate_neg': disambiguate_neg,\
                              'disambiguate_sid_ksid': disambiguate_sid_ksid }
        self.configuration.update(self.kwargs)

        self.depends_on = ['words', 'sentences', 'morph_analysis']


    def tag(self, text:Text, return_layer:bool=False) -> Text:
        ''' Converts morphological analyses (in the layer 'morph_analysis') from 
            FS Vabamorf's format to giellatekno's (GT) format. Creates a new layer
            containing the results of the conversion. If return_layer==True, then
            returns the new layer, otherwise attaches the new layer to the Text 
            object and returns the Text object.
            
            Parameters
            -----------
            text : estnltk.text.Text
                Text object in which morphological annotations are converted from 
                FS format to GT format. Text object must have layers 'words' and 
                'morph_analysis';
            
            return_layer : bool
                If True, then the new layer is returned; otherwise the new layer 
                is attached to the Text object, and the Text object is returned;
                Default: False;
        '''
        gt_morph = Layer(name=self.layer_name,
                         parent='morph_analysis',
                         ambiguous=True,
                         attributes=self.attributes
                   )

        # 1) Perform the conversion
        new_morph_dicts = _convert_analysis( text )
        
        # 2) Perform some context-specific disambiguation
        if self.configuration['disambiguate_neg']:
            _disambiguate_neg( new_morph_dicts )
        if self.configuration['disambiguate_sid_ksid']:
            _disambiguate_sid_ksid( new_morph_dicts, text, scope='clauses' )
            _disambiguate_sid_ksid( new_morph_dicts, text, scope='sentences' )
        _make_postfixes_2( new_morph_dicts )
        
        # 3) Convert analysis dicts to Spans, and attach to the layer
        _create_spans( text, new_morph_dicts, layer = gt_morph )

        if return_layer:
            return gt_morph
        text[self.layer_name] = gt_morph
        return text

