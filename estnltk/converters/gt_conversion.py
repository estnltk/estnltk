# -*- coding: utf-8 -*- 
#
#    Module for converting morphological categories from Filosoft's Vabamorf format to 
#   Giellatekno's format (the gt format);
#
#    Example usage:
#
#      from estnltk.converters.gt_conversion import convert_to_gt
#
#      text=Text('Rändur võttis seljakotist vilepilli ja tõstis huultele.')
#      text.tag_analysis()
#      convert_to_gt( text, layer_name='words' )
#      print( text.get.word_texts.postags.forms.as_dataframe )
#

from __future__ import unicode_literals, print_function

from estnltk.names import *

import re
import codecs

# =========================================================================================
#    Utils
# =========================================================================================

def copy_analysis_dict( analysis ):
    ''' Creates a copy from given analysis dict. '''
    assert isinstance(analysis, dict), "(!) Input 'analysis' should be a dict!"
    new_dict = { POSTAG: analysis[POSTAG],\
                 ROOT: analysis[ROOT],\
                 FORM: analysis[FORM],\
                 CLITIC: analysis[CLITIC],\
                 ENDING: analysis[ENDING] }
    if LEMMA in analysis:
       new_dict[LEMMA] = analysis[LEMMA]
    if ROOT_TOKENS in analysis:
       new_dict[ROOT_TOKENS] = analysis[ROOT_TOKENS]
    return new_dict 


def get_unique_clause_indices( text ):
    ''' Returns a list of clause indices for the whole text. For each token in text, 
        the list contains index of the clause the word belongs to, and the indices
        are unique over the whole text. '''
    # Add clause boundary annotation (if missing)
    if not text.is_tagged( CLAUSES ):
        text.tag_clauses()
    # Collect (unique) clause indices over the whole text
    clause_indices = []
    sent_id = 0
    for sub_text in text.split_by( SENTENCES ):
        for word, cl_index in zip( sub_text.words, sub_text.clause_indices ):
            clause_indices.append( sent_id+cl_index )
        nr_of_clauses = len(set(sub_text.clause_indices))
        sent_id += nr_of_clauses
    assert len(clause_indices) == len(text.words), '(!) Number of clause indices should match nr of words!'
    return clause_indices


def get_unique_sentence_indices( text ):
    ''' Returns a list of sentence indices for the whole text. For each token in text, 
        the list contains index of the sentence the word belongs to, and the indices
        are unique over the whole text. '''
    # Add sentence annotation (if missing)
    if not text.is_tagged( SENTENCES ):
        text.tokenize_sentences()
    # Collect (unique) sent indices over the whole text
    sent_indices = []
    sent_id = 0
    for sub_text in text.split_by( SENTENCES ):
        for word in sub_text.words:
            sent_indices.append( sent_id )
        sent_id += 1
    assert len(sent_indices) == len(text.words), '(!) Number of sent indices should match nr of words!'
    return sent_indices


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
    assert FORM in analysis, '(!) The input analysis does not contain "'+FORM+'" key.'
    for idx, pattern_items in enumerate(_noun_conversion_rules):
        pattern_str, replacement = pattern_items
        if pattern_str in analysis[FORM]:
           analysis[FORM] = analysis[FORM].replace( pattern_str, replacement )
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
    assert FORM in analysis, '(!) The input analysis does not contain "'+FORM+'" key.'
    results = []
    for root_pat, pos, form_pat, replacements in _amb_verb_conversion_rules:
        if analysis[POSTAG] == pos and re.match(root_pat, analysis[ROOT]) and \
           re.match(form_pat, analysis[FORM]):
           for replacement in replacements:
               new_analysis = copy_analysis_dict( analysis )
               new_form = re.sub(form_pat, replacement, analysis[FORM])
               new_analysis[FORM] = new_form
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
    assert FORM in analysis, '(!) The input analysis does not contain "'+FORM+'" key.'
    for form, replacement in _verb_conversion_rules:
        # Exact match
        if analysis[FORM] == form:
           assert analysis[POSTAG] == 'V', \
               '(!) Expected analysis of verb, but got analysis of "'+str(analysis[POSTAG])+'" instead.'
           analysis[FORM] = replacement
        # Inclusion :   the case of some_prefix+' '+form ;
        elif analysis[FORM].endswith(' '+form):
           parts  = analysis[FORM].split()
           prefix = ' '.join( parts[:len(parts)-1] )
           analysis[FORM] = prefix+' '+replacement
    return analysis

# =====================================
#  Perform post-processing / fixing #1
# =====================================

def _make_postfixes_1( analysis ):
    ''' Provides some post-fixes. '''
    assert FORM in analysis, '(!) The input analysis does not contain "'+FORM+'" key.'
    if 'neg' in analysis[FORM]:
        analysis[FORM] = re.sub( '^\s*neg ([^,]*)$',  '\\1 Neg',  analysis[FORM] )
    analysis[FORM] = re.sub( ' Neg Neg$',  ' Neg',  analysis[FORM] )
    analysis[FORM] = re.sub( ' Aff Neg$',  ' Neg',  analysis[FORM] )
    analysis[FORM] = re.sub( 'neg',  'Neg',  analysis[FORM] )
    analysis[FORM] = analysis[FORM].rstrip().lstrip()
    assert 'neg' not in analysis[FORM], \
                 '(!) The label "neg" should be removed by now.'
    assert 'Neg' not in analysis[FORM] or ('Neg' in analysis[FORM] and analysis[FORM].endswith('Neg')), \
                 '(!) The label "Neg" should end the analysis line: '+str(analysis[FORM])
    return analysis

# =====================================
#  Initial disambiguation in GT format
# =====================================

def _keep_analyses( analyses, keep_forms, target_forms ):
    ''' Filters the given list of *analyses* by morphological forms: 
        deletes analyses that are listed in *target_forms*, but not in 
        *keep_forms*. '''
    to_delete = []
    for aid, analysis in enumerate(analyses):
        delete = False
        for target in target_forms:
            if (target == analysis[FORM] and not analysis[FORM] in keep_forms):
               delete = True
        if delete:
            to_delete.append( aid )
    if to_delete:
       to_delete.reverse()
       for aid in to_delete:
           del analyses[aid]

def _disambiguate_neg( words_layer ):
    ''' Disambiguates forms ambiguous between multiword negation and some 
        other form;
    '''
    prev_word_lemma = ''
    for word_dict in words_layer:
        forms = [ a[FORM] for a in word_dict[ANALYSIS] ]
        if ('Pers Prs Imprt Sg2' in forms and 'Pers Prs Ind Neg' in forms):
           if (prev_word_lemma == "ei" or prev_word_lemma == "ega"):
               # ei saa, ei tee
               _keep_analyses( word_dict[ANALYSIS], ['Pers Prs Ind Neg'], ['Pers Prs Imprt Sg2', 'Pers Prs Ind Neg'] )
           else:
               # saa! tee! 
               _keep_analyses( word_dict[ANALYSIS], ['Pers Prs Imprt Sg2'], ['Pers Prs Imprt Sg2', 'Pers Prs Ind Neg'] )
        if ('Pers Prt Imprt' in forms and 'Pers Prt Ind Neg' in forms and 'Pers Prt Prc' in forms):
           if (prev_word_lemma == "ei" or prev_word_lemma == "ega"):
               # ei saanud, ei teinud
               _keep_analyses( word_dict[ANALYSIS], ['Pers Prt Ind Neg'], ['Pers Prt Imprt','Pers Prt Ind Neg','Pers Prt Prc'] )
           else:
               # on, oli saanud teinud; kukkunud õun; ...
               _keep_analyses( word_dict[ANALYSIS], ['Pers Prt Prc'], ['Pers Prt Imprt','Pers Prt Ind Neg','Pers Prt Prc'] )
        if ('Impers Prt Ind Neg' in forms and 'Impers Prt Prc' in forms):
           if (prev_word_lemma == "ei" or prev_word_lemma == "ega"):
               # ei saadud, ei tehtud
               _keep_analyses( word_dict[ANALYSIS], ['Impers Prt Ind Neg'], ['Impers Prt Ind Neg','Impers Prt Prc'] )
           else:
               # on, oli saadud tehtud; saadud õun; ...
               _keep_analyses( word_dict[ANALYSIS], ['Impers Prt Prc'], ['Impers Prt Ind Neg','Impers Prt Prc'] )
        prev_word_lemma = word_dict[ANALYSIS][0][ROOT]


def _disambiguate_sid_ksid( words_layer, text, scope=CLAUSES ):
    ''' Disambiguates verb forms based on existence of 2nd person pronoun ('sina') in given scope.
        The scope could be either CLAUSES or SENTENCES.
    '''
    assert scope in [CLAUSES, SENTENCES], '(!) The scope should be either "clauses" or "sentences".'
    group_indices = get_unique_clause_indices( text ) if scope==CLAUSES else get_unique_sentence_indices( text )
    i = 0
    gr_2nd_person_pron = {}
    while i < len( words_layer ):
        gr_index = group_indices[i]
        if gr_index not in gr_2nd_person_pron:
            # 1) Find out whether the current group (clause or sentence) contains "sina"
            j = i
            gr_2nd_person_pron_found = False
            while j < len( words_layer ):
                 if group_indices[j] == gr_index:
                     forms  = [ a[FORM] for a in words_layer[j][ANALYSIS] ]
                     lemmas = [ a[ROOT] for a in words_layer[j][ANALYSIS] ]
                     if 'sina' in lemmas and 'Sg Nom' in forms:
                        gr_2nd_person_pron_found = True
                        break
                 if group_indices[j] >= gr_index+10:  # do not venture too far ...
                     break
                 j += 1
            gr_2nd_person_pron[gr_index] = gr_2nd_person_pron_found
        forms = [ a[FORM] for a in words_layer[i][ANALYSIS] ]
        # 2) Disambiguate verb forms based on existence of 'sina' in the clause
        if ('Pers Prt Ind Pl3 Aff' in forms and 'Pers Prt Ind Sg2 Aff' in forms):    # -sid
           if not gr_2nd_person_pron[ gr_index ]:
               _keep_analyses( words_layer[i][ANALYSIS], ['Pers Prt Ind Pl3 Aff'], ['Pers Prt Ind Pl3 Aff', 'Pers Prt Ind Sg2 Aff'] )
           else:
               _keep_analyses( words_layer[i][ANALYSIS], ['Pers Prt Ind Sg2 Aff'], ['Pers Prt Ind Pl3 Aff', 'Pers Prt Ind Sg2 Aff'] )
        if ('Pers Prs Cond Pl3 Aff' in forms and 'Pers Prs Cond Sg2 Aff' in forms):  # -ksid
           if not gr_2nd_person_pron[ gr_index ]:
               _keep_analyses( words_layer[i][ANALYSIS], ['Pers Prs Cond Pl3 Aff'], ['Pers Prs Cond Pl3 Aff', 'Pers Prs Cond Sg2 Aff'] )
           else:
               _keep_analyses( words_layer[i][ANALYSIS], ['Pers Prs Cond Sg2 Aff'], ['Pers Prs Cond Pl3 Aff', 'Pers Prs Cond Sg2 Aff'] )
        if ('Pers Prt Cond Pl3 Aff' in forms and 'Pers Prt Cond Sg2 Aff' in forms):  # -nuksid
           if not gr_2nd_person_pron[ gr_index ]:
               _keep_analyses( words_layer[i][ANALYSIS], ['Pers Prt Cond Pl3 Aff'], ['Pers Prt Cond Pl3 Aff', 'Pers Prt Cond Sg2 Aff'] )
           else:
               _keep_analyses( words_layer[i][ANALYSIS], ['Pers Prt Cond Sg2 Aff'], ['Pers Prt Cond Pl3 Aff', 'Pers Prt Cond Sg2 Aff'] )
        i += 1

# =====================================
#  Perform post-processing / fixing #2
# =====================================

def _make_postfixes_2( words_layer ):
    ''' Provides some post-fixes after the disambiguation. '''
    for word_dict in words_layer:
        for analysis in word_dict[ANALYSIS]:
          analysis[FORM] = re.sub( '(Sg|Pl)([123])', '\\1 \\2', analysis[FORM] )
    return words_layer


# =========================================================================================
#    Convert from Vabamorf's format to GT format
# =========================================================================================

def convert_analysis( analyses ):
    ''' Converts a list of analyses (list of dict objects) from FS's vabamorf format to 
        giellatekno (GT) format. 
        Due to one-to-many conversion rules, the number of analyses returned by this method
        can be greater than the number of analyses in the input list.
    '''
    resulting_analyses = []
    for analysis in analyses:
        # Make a copy of the analysis
        new_analyses = [ copy_analysis_dict( analysis ) ]
        # Convert noun categories
        new_analyses[0] = _convert_nominal_form( new_analyses[0] )
        # Convert ambiguous verb categories
        new_analyses = _convert_amb_verbal_form( new_analyses[0] )
        # Convert remaining verbal categories
        new_analyses = [_convert_verbal_form( a ) for a in new_analyses]
        # Make postfixes
        new_analyses = [_make_postfixes_1( a ) for a in new_analyses]
        resulting_analyses.extend( new_analyses )
    return resulting_analyses


def convert_to_gt( text, layer_name=GT_WORDS ):
    ''' Converts all words in a morphologically analysed Text from FS format to 
        giellatekno (GT) format, and stores in a new layer named GT_WORDS. 
        If the keyword argument *layer_name=='words'* , overwrites the old 'words' 
        layer with the new layer containing GT format annotations. 

        Parameters
        -----------
        text : estnltk.text.Text
            Morphologically annotated text that needs to be converted from FS format 
            to GT format;
        
        layer_name : str
            Name of the Text's layer in which GT format morphological annotations 
            are stored; 
            Defaults to GT_WORDS;
    '''
    assert WORDS in text, \
        '(!) The input text should contain "'+str(WORDS)+'" layer.'
    assert len(text[WORDS])==0 or (len(text[WORDS])>0 and ANALYSIS in text[WORDS][0]), \
        '(!) Words in the input text should contain "'+str(ANALYSIS)+'" layer.'
    new_words_layer = []
    # 1) Perform the conversion
    for word in text[WORDS]:
        new_analysis = []
        new_analysis.extend( convert_analysis( word[ANALYSIS] ) )
        new_words_layer.append( {TEXT:word[TEXT], ANALYSIS:new_analysis, START:word[START], END:word[END]} )
    # 2) Perform some context-specific disambiguation
    _disambiguate_neg( new_words_layer )
    _disambiguate_sid_ksid( new_words_layer, text, scope=CLAUSES )
    _disambiguate_sid_ksid( new_words_layer, text, scope=SENTENCES )
    _make_postfixes_2( new_words_layer )
    # 3) Attach the layer
    if layer_name != WORDS:
        #  Simply attach the new layer
        text[layer_name] = new_words_layer
    else:
        #  Perform word-by-word replacements
        # (because simple attaching won't work here)
        for wid, new_word in enumerate( new_words_layer ):
            text[WORDS][wid] = new_word
    return text



# =========================================================================================
#    Some other helpful methods
#    (not directly related to the converter,
#     but used for testing the converter)
# =========================================================================================

def get_analysis_dict( root, pos, form ):
    '''  Takes *root*, *pos* and *form* from Filosoft's mrf input and reformats as 
         EstNLTK's analysis dict:
          {
             "clitic":       string,
             "ending":       string,
             "form":         string,
             "partofspeech": string,
             "root":         string
          },
         Returns the dict;
    ''' 
    import sys
    result = { CLITIC:"", ENDING:"", FORM:form, POSTAG:pos, ROOT:"" }
    breakpoint = -1
    for i in range(len(root)-1, -1, -1):
        if root[i] == '+':
            breakpoint = i
            break
    if breakpoint == -1:
        result[ROOT]   = root
        result[ENDING] = "0"
        if not re.match("^\W+$", root):
            try:
                print( " No breakpoint found from: ", root, pos, form, file=sys.stderr )
            except UnicodeEncodeError:
                print( " No breakpoint found from input *root*!",  file=sys.stderr )
    else:
        result[ROOT]   = root[0:breakpoint]
        result[ENDING] = root[breakpoint+1:]
    if result[ENDING].endswith('ki') and len(result[ENDING]) > 2:
        result[CLITIC] = 'ki'
        result[ENDING] = re.sub('ki$', '', result[ENDING])
    if result[ENDING].endswith('gi') and len(result[ENDING]) > 2:
        result[CLITIC] = 'gi'
        result[ENDING] = re.sub('gi$', '', result[ENDING])
    return result



def read_text_from_idx_file( file_name, layer_name=WORDS, keep_init_lines=False ):
    ''' Reads IDX format morphological annotations from given file, and returns as a Text 
        object.
        
        The Text object will be tokenized for paragraphs, sentences, words, and it will
        contain morphological annotations in the layer *layer_name* (by default: WORDS);
        
        Parameters
        -----------
        file_name : str
            Name of the input file; Should contain IDX format text segmentation and 
            morphological annotation;
        
        keep_init_lines : bool
            Optional argument specifying whether the lines from the file should also be
            preserved on a special layer named 'init_lines';
            Default: False
        
        layer_name : str
            Name of the Text's layer in which morphological annotations from text are 
            stored; 
            Defaults to WORDS;
    
        Example: expected format of the input:
          129	1	1	"	"	"	Z	
          129	2	1	Mul	mina	mina+l	P	sg ad
          129	3	1	on	olema	ole+0	V	b
          129	3	1	on	olema	ole+0	V	vad
          129	4	1	palju	palju	palju+0	D	
          129	5	1	igasugust	igasugune	iga_sugune+t	P	sg p
          129	6	1	informatsiooni	informatsioon	informatsioon+0	S	sg p
          129	7	1	.	.	.	Z	
        
    '''
    from nltk.tokenize.simple import LineTokenizer
    from nltk.tokenize.regexp import RegexpTokenizer
    from estnltk import Text
    # 1) Collect the text along with morphological analyses from the input IDX file
    init_lines = []
    words      = []
    sentence   = []
    sentences  = []
    prev_sent_id = -1
    prev_word_id = -1
    in_f = codecs.open(file_name, mode='r', encoding='utf-8')
    for line in in_f:
        fields = line.split('\t')
        assert len(fields) == 8, '(!) Unexpected number of fields in the line: '+str(len(fields))
        sent_id   = fields[0]
        word_id   = fields[1]
        clause_id = fields[2]
        token     = fields[3]
        if prev_sent_id != sent_id:
            # Record the old sentence, start a new 
            if sentence:
               sentences.append( '  '.join(sentence) )
            sentence = []
        if prev_word_id != word_id:
            # Record a new token
            sentence.append( token )
            word = { TEXT:token, ANALYSIS:[] }
            words.append(word)
        # Augment the last word in the list with new analysis
        lemma  = fields[4]
        root   = fields[5]
        pos    = fields[6]
        form   = fields[7].rstrip()
        ending = ''
        clitic = ''
        analysis = get_analysis_dict( root, pos, form )
        analysis[LEMMA] = lemma
        words[-1][ANALYSIS].append( analysis )
        prev_sent_id = sent_id
        prev_word_id = word_id
        if keep_init_lines:
            init_lines.append( [sent_id+' '+word_id, line] )
    in_f.close()
    if sentence:
        # Record the last sentence
        sentences.append( '  '.join(sentence) )

    # 2) Construct the estnltk's Text
    kwargs4text = {
      # Use custom tokenization utils in order to preserve exactly the same 
      # tokenization as was in the input;
      "word_tokenizer":     RegexpTokenizer("  ", gaps=True),
      "sentence_tokenizer": LineTokenizer()
    }
    from estnltk.text import Text
    text = Text( '\n'.join(sentences), **kwargs4text )
    # Tokenize up to the words layer
    text.tokenize_words()

    # 3) Create a new layer with morphological analyses, or 
    #    populate the old layer with morphological analyses;
    assert len(text[WORDS]) == len(words), \
        '(!) Number of words from input does not match with the number of words in EstNLTK Text: '+\
             str(len(text[WORDS]) )+' != '+str(len(words))
    if layer_name != WORDS:
        # If necessary, create a new layer duplicating the WORDS layer
        text[layer_name] = []
        for word in text[WORDS]:
            text[layer_name].append({START:word[START], END:word[END], TEXT:word[TEXT]})
    # Copy morphological analyses to the new layer / populate the old layer
    for wid, word in enumerate( text[WORDS] ):
        text[layer_name][wid][ANALYSIS] = words[wid][ANALYSIS]
    if layer_name == WORDS:    
        assert text.is_tagged(ANALYSIS), '(!) The layer of analysis should exist by now!'
    
    if keep_init_lines:
        # Preserve the initial lines from file in a separate layer
        text['init_lines'] = []
        i = 0
        for wid, word in enumerate( text[layer_name] ):
            words_lines = []
            # collect lines associated with the word
            while i < len(init_lines):
                [lid, line] = init_lines[i]
                if not words_lines or words_lines[-1][0]==lid:
                    words_lines.append([lid, line])
                else:
                    break
                i += 1
            # record lines
            text['init_lines'].append( \
                {START:word[START], END:word[END], 'lines':[l[1] for l in words_lines]} )
        assert len(text['init_lines']) == len(text[layer_name]), \
            '(!) The number of initial lines should match the number of words in text!'
    return text



def get_original_vs_converted_diff( original ,converted ):
    '''  Compares the *original* text to *converted* text, and detects changes/differences in 
        morphological annotations. 

        The method constructs line-by-line comparison string, where lines are separated by 
        newline, and '***' at the beginning of the line indicates the difference.

        Returns a pair: results of the line-by-line comparison as a string, and boolean value
        indicating whether there were any differences.
    '''
    from estnltk.syntax.syntax_preprocessing import convert_Text_to_mrf
    old_layer_mrf = convert_Text_to_mrf( original )
    new_layer_mrf = convert_Text_to_mrf( converted )
    max_len_1 = max([len(l) for l in old_layer_mrf ])
    max_len_2 = max([len(l) for l in new_layer_mrf ])
    max_len   = max( max_len_1, max_len_2 )
    format_str = '{:<'+str(max_len+1)+'}'
    i = 0
    j = 0
    comp_lines = []
    diff_found = False
    while(i < len(old_layer_mrf) or j < len(new_layer_mrf)):
         l1 = old_layer_mrf[i]
         l2 = new_layer_mrf[j]
         # 1) Output line containing tokens
         if not l1.startswith(' ') and not l2.startswith(' '):
            diff = '*** ' if format_str.format(l1) != format_str.format(l2) else '    '
            comp_lines.append( diff+format_str.format(l1)+format_str.format(l2) )
            if diff == '*** ':
                 diff_found = True
            i += 1
            j += 1
         else:
            # 2) Output analysis line(s)
            while(i < len(old_layer_mrf) or j < len(new_layer_mrf)):
                 l1 = old_layer_mrf[i]
                 l2 = new_layer_mrf[j]
                 if l1.startswith(' ') and l2.startswith(' '):
                    diff = '*** ' if format_str.format(l1) != format_str.format(l2) else '    '
                    comp_lines.append( diff+format_str.format(l1)+format_str.format(l2) )
                    if diff == '*** ':
                       diff_found = True
                    i += 1
                    j += 1
                 elif l1.startswith(' ') and not l2.startswith(' '):
                    diff = '*** '
                    comp_lines.append( diff+format_str.format(l1)+format_str.format(' ') )
                    diff_found = True
                    i += 1
                 elif not l1.startswith(' ') and l2.startswith(' '):
                    diff = '*** '
                    comp_lines.append( diff+format_str.format(' ')+format_str.format(l2) )
                    diff_found = True
                    j += 1
                 else:
                    break
    return '\n'.join( comp_lines ), diff_found



