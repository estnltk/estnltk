#
#  Rules for checking consistency between clause and syntactic annotations
#

import os, os.path, sys, re
import warnings

from collections import defaultdict

from estnltk import Text, Layer

from estnltk_core.layer_operations import extract_section, extract_sections

# =========================================================================
#   (Optimized) Iterators
# =========================================================================

def yield_clauses_and_syntax_words(text, clauses_layer='clauses', 
                                         syntax_layer='syntax', 
                                         sentences_layer='sentences'):
    '''Yields clauses with sentence id-s and words inside the clause from the syntax layer.
       More specifically, yields triples: (sentence_id, clause, list_of_syntax_words_of_clause) 
    '''
    assert clauses_layer   in text.layers
    assert syntax_layer    in text.layers
    assert sentences_layer in text.layers
    discarded_anns_encountered = 0
    sentence_id = 0
    # optimization: maintain list of fall back syntax word ids, so 
    # that we do not have to start matching from the beginning for 
    # every clause
    fall_back_syntax_ids = [0]
    for clause in text[clauses_layer]:
        cl_start = clause.start
        cl_end   = clause.end
        # collect syntax words inside the clause
        cl_syntax_words = []
        while True:
            for syntax_id_start in fall_back_syntax_ids[:][::-1]:
                syntax_id = syntax_id_start
                while syntax_id < len( text[syntax_layer] ):
                    syntax_w = text[syntax_layer][syntax_id]
                    if clause.start == syntax_w.start:
                        if syntax_id not in fall_back_syntax_ids:
                            # Update the list of fallback start indexes
                            fall_back_syntax_ids.append( syntax_id )
                    if syntax_w.start >= cl_start and syntax_w.end <= cl_end:
                        # Note: because of embedded clauses, we must 
                        # check that the word is exactly inside the 
                        # clause, not part of an embedded sub clause
                        is_clause_word = False
                        for cl_word in clause:
                            if cl_word.base_span == syntax_w.base_span:
                                is_clause_word = True
                                break
                        if is_clause_word:
                            cl_syntax_words.append( syntax_w )
                    elif syntax_w.start >= cl_end:
                        break
                    syntax_id += 1
                if len(cl_syntax_words) > 0:
                    break
            if len(cl_syntax_words) > 0:
                break
        if len(cl_syntax_words) != len(clause):
            # Check for discarded annotations (specific to UD-EWT corpus)
            if 'discarded_annotations' in text[syntax_layer].meta and \
               text[syntax_layer].meta['discarded_annotations'] > 0:
                discarded_anns_encountered += len(clause) - len(cl_syntax_words)
            else:
                raise Exception( ('(!) Unable to fetch all clause words from the '+\
                                  'syntax layer {!r}; clause words: {!r} vs syntax '+\
                                  'words: {!r}.').format( syntax_layer, \
                                        [ w.text for w in cl_syntax_words ], \
                                        [ w.text for w in clause ] ) )
        if discarded_anns_encountered > 0:
            assert discarded_anns_encountered <= text[syntax_layer].meta['discarded_annotations']
        # Fetch & update sentence ids
        while sentence_id < len(text[sentences_layer]):
            sentence = text[sentences_layer][sentence_id]
            if sentence.start <= cl_start and sentence.end >= cl_end:
                # clause is inside the sentence: stop
                break
            # Fetch the next sentence
            sentence_id += 1
        yield sentence_id, clause, cl_syntax_words


def yield_clauses_and_syntax_words_sentence_wise(text, clauses_layer='clauses', 
                                                 syntax_layer='syntax', 
                                                 sentences_layer='sentences'):
    '''Yields clauses along with syntax words inside clauses grouped by sentences.
       More specifically, yields triples: 
         (sentence_id, list_of_clauses_inside_sentence, list_of_syntax_words_of_clauses) 
    '''
    last_sent_id = -1
    sentence_clauses = []
    sentence_syntax_words = []
    for sent_id, clause, cl_syntax_words in yield_clauses_and_syntax_words( \
                                                  text, \
                                                  clauses_layer=clauses_layer, \
                                                  syntax_layer=syntax_layer, \
                                                  sentences_layer=sentences_layer ):
        if last_sent_id != sent_id:
            # Yield collected sentence
            if len(sentence_clauses) > 0:
                yield last_sent_id, sentence_clauses, sentence_syntax_words
            # Start a new sentence
            sentence_clauses = []
            sentence_syntax_words = []
        sentence_clauses.append( clause )
        sentence_syntax_words.append( cl_syntax_words )
        last_sent_id = sent_id
    # Yield collected sentence
    if len(sentence_clauses) > 0:
        yield last_sent_id, sentence_clauses, sentence_syntax_words

# =========================================================================
#   Helpful utilities
# =========================================================================

def _first_index(element, lst):
    '''Returns first index of the element in the list.
       If the element is missing, returns -1.'''
    idx = 0
    while idx < len(lst):
        if lst[idx] == element:
            return idx
        idx += 1
    return -1


def _last_index(element, lst):
    '''Returns last index of the element in the list.
       If the element is missing, returns -1.'''
    idx = len(lst)-1
    while idx > -1:
        if lst[idx] == element:
            return idx
        idx -= 1
    return -1


def _get_prev_clause(cur_clause, all_clauses, can_be_embedded=False):
    '''Returns the clause preceding the cur_clause in all_clauses.
       If there is no preceding clause, returns None.
       If can_be_embedded==False (default) then preceding clause is 
       returned only if it is non-embedded.
    '''
    for clause in all_clauses:
        if cur_clause.start-2 <= -1:
            continue
        clause_type = clause.annotations[0]['clause_type']
        if cur_clause.start-2 <= clause.end:
            if not can_be_embedded and clause_type == 'embedded':
                continue
            return clause
    return None


def _get_prev_clause_syntax_words(cur_clause, all_clauses, sent_cl_syntax_words, can_be_embedded=False):
    '''Returns syntax_words of the clause preceding the cur_clause in all_clauses.
       If there is no preceding clause, returns None.
       If can_be_embedded==False (default) then preceding clause's words are 
       returned only if the clause is non-embedded.
    '''
    for clause, cl_syntax_words in zip(all_clauses, sent_cl_syntax_words):
        if cur_clause.start-2 <= -1:
            continue
        clause_type = clause.annotations[0]['clause_type']
        if cur_clause.start-2 <= clause.end:
            if not can_be_embedded and clause_type == 'embedded':
                continue
            return cl_syntax_words
    return None


def get_phrase_conjunctions( cl_syntax_words, remove_overlaps=True ):
    '''Finds all conjunction phrases from the syntax words of the clause.
       In other words, finds words connected with 'conj' relations and 
       all their syntactic children. Note that 'conj' relations pointing 
       outside the clause will be discarded. 
       
       Returns a list of lists of indexes, where each sub list contains
       indexes of (clause) words belonging to a conjunction phrase.
       Indexes are sorted numerically.
       
       Examples:
       1) clause: ['paneme', 'rannasoleku', 'ajad', 'ja', 'mõõtmisandmed', 'kokku', ',']
          conjunction phrase: ['rannasoleku', 'ajad', 'ja', 'mõõtmisandmed']
          conjunction phrase syntax: [(12, 13, 'nmod'), (13, 11, 'obj'), (14, 15, 'cc'), (15, 13, 'conj')]
       
       2) clause: ['Vabatahtlikud', 'proovivad', 'tervise', 'ja', 'naha', 'vastupidavust']
          conjunction phrase: ['tervise', 'ja', 'naha']
          conjunction phrase syntax: [(3, 6, 'nmod'), (4, 5, 'cc'), (5, 3, 'conj')]
       
       3) clause: ['Kuus', 'läheb', 'võla', 'ja', 'lasteaia', 'peale', '1500', 'krooni', '.']
          conjunction phrase: ['võla', 'ja', 'lasteaia', 'peale']
          conjunction phrase syntax: [(3, 2, 'obl'), (4, 5, 'cc'), (5, 3, 'conj'), (6, 3, 'case')]
    '''
    inside_clause_indexes = [w.annotations[0]['id'] for w in cl_syntax_words]
    inside_clause_id_map  = {ind:i for i, ind in enumerate(inside_clause_indexes)}
    conj_heads = {}
    for i, word in enumerate(cl_syntax_words):
        ind = word.annotations[0]['id']
        head = word.annotations[0]['head']
        deprel = word.annotations[0]['deprel']
        if deprel == 'conj' and head in inside_clause_id_map:
            head_word = cl_syntax_words[inside_clause_id_map[head]]
            if head not in conj_heads:
                conj_heads[head] = [head]
            # Find all children of the (head) node
            nodes = [head]
            while len( nodes ) > 0:
                node = nodes.pop(0)
                if node not in conj_heads[head]:
                    conj_heads[head].append(node)
                for i2, word2 in enumerate(cl_syntax_words):
                    ind2 = word2.annotations[0]['id']
                    head2 = word2.annotations[0]['head']
                    if head2 == node:
                        nodes.append(ind2)
    # Find clause indexes corresponding to the syntax nodes 
    # Take out conjunction phrases
    conjunctions = []
    for c_head in conj_heads:
        sorted_indexes = sorted( \
            [inside_clause_id_map[i] for i in conj_heads[c_head]] )
        conjunctions.append( sorted_indexes )
    # Remove overlapped phrases 
    if remove_overlaps:
        to_remove = []
        for p1 in conjunctions:
            for p2 in conjunctions:
                if p1 != p2:
                    # p1 is inside p2
                    if p2[0] <= p1[0] and \
                       p1[-1] <= p2[-1] and \
                       p1 not in to_remove:
                        to_remove.append(p1)
        for p in to_remove:
            conjunctions.remove(p)
    return conjunctions

def _get_parent_features_in_clause(cl_syntax_words, features):
    '''Returns a list of dictionaries of parent features of words. 
       Only features of parents that are inside the clause will 
       be extracted; however, each dictionary will always contain 
       full set of keys, but words with missing parents have all 
       of their feature values set to None.'''
    assert isinstance(features, (set, list))
    cl_ids = [ w.annotations[0]['id'] for w in cl_syntax_words ]
    cl_id_map = {ind:i for i, ind in enumerate(cl_ids)}
    parent_features = []
    for i, word in enumerate(cl_syntax_words):
        ind = word.annotations[0]['id']
        head = word.annotations[0]['head']
        if head in cl_id_map.keys():
            head_word = cl_syntax_words[cl_id_map[head]]
            head_annotations = word.annotations[0]
            collected_features = {}
            for feat in features:
                collected_features[feat]=head_annotations[feat]
            parent_features.append(collected_features)
        else:
            collected_features = {feat : None for feat in features}
            parent_features.append(collected_features)
    return parent_features

# =========================================================================
#   Detection of clause errors
# =========================================================================

def detect_clause_errors( text, output_layer='clause_errors', 
                                clauses_layer='clauses', syntax_layer='syntax', sentences_layer='sentences', 
                                debug_output=False, status=None ):
    '''
    Detects potential errors in clauses layer using information from the syntax layer.
    Returns a layer with annotations of error positions along with descriptions of corrections.
    
    Currently, this is just a diagnostic function, no actual corrections are made.
    
    Parameters
    ----------
    text: Text
        Analysable Text object.
    output_layer: str
        Name of the output layer. Default: 'clause_errors'
    clauses_layer: str
        Name of the clauses layer attached to the Text object.
        Default: 'clauses'
    syntax_layer: str
        Name of the syntax layer attached to the Text object.
        Default: 'syntax'
    sentences_layer: str
        Name of the sentences layer attached to the Text object.
        Default: 'sentences'
    debug_output: bool
        If True, returns tuple: (errors_layer, debug_output)
        Otherwise (default), returns only errors_layer.
    status: dict
        Used to keep track of total errors found while analysing
        multiple texts in a row.
    
    Returns
    -------
    Layer
        A layer with markings of error positions.
    '''
    status = defaultdict(int) if status is None else status
    errors_layer = Layer(output_layer, attributes=('err_type', 'sent_id', 'correction_description'), text_object=text)
    attributive_clause_start_lemmas = \
        ['mis', 'kes', 'millal', 'kus', 'kust', 'kuhu', 'kuna', 'kuidas', 'kas']
    output_str = []
    for sent_id, sent_clauses, sent_cl_syntax_words in yield_clauses_and_syntax_words_sentence_wise( text, \
                                                                                clauses_layer=clauses_layer, \
                                                                                syntax_layer=syntax_layer, \
                                                                                sentences_layer=sentences_layer ):
        sentence = text[sentences_layer][sent_id]
        # Check for consistencey and possible errors
        for clause, cl_syntax_words in zip(sent_clauses, sent_cl_syntax_words):
            is_sentence_start = clause.start == sentence.start
            clause_lemmas  = [ w.annotations[0]['lemma'] for w in cl_syntax_words ]
            clause_postags = [ w.annotations[0]['xpostag'] for w in cl_syntax_words ]
            clause_deprels = [ w.annotations[0]['deprel'] for w in cl_syntax_words ]
            first_verb_idx = _first_index('V', clause_postags)
            last_comma_idx = _last_index(',',  clause_lemmas)
            last_root_idx  = _last_index('root', clause_deprels)
            if clause_lemmas[0] in attributive_clause_start_lemmas and \
               last_root_idx > -1 and last_comma_idx > -1 and last_comma_idx < last_root_idx and \
               first_verb_idx < last_comma_idx and first_verb_idx > -1:
                # ==========================================
                # Detect errors related to attributive clauses starting with mis/kes/millal/kus/kust/kuhu/kuna/kuidas/kas 
                # ==========================================
                exceptions_passed = True
                #
                # Pattern: [...] [ mis/kes ... verb ... , ... root ] --> [... [ mis/kes ... verb ...  , ] ... root ]
                #          ( create an embedded clause )
                #
                # Example: [Kahtlemata on iga keel,] [mida inimene valdab, topeltrikkus (root) .] --> 
                #          [Kahtlemata on iga keel [, mida inimene valdab,] topeltrikkus (root) .]
                #
                # Example: [Seega mingeid hirme,] [kuidas osaga hakkama saada, pole mul absoluutselt (root) .] --> 
                #          [Seega mingeid hirme [, kuidas osaga hakkama saada,] pole mul absoluutselt (root) .]
                #
                # check previous clause. we are assuming that previous clause ends with comma
                prev_cl_syntax_words = \
                    _get_prev_clause_syntax_words( clause, sent_clauses, 
                                                   sent_cl_syntax_words, can_be_embedded=False )
                if prev_cl_syntax_words is not None and prev_cl_syntax_words[-1].text != ',':
                    exceptions_passed = False
                if 'conj' in clause_deprels:
                    # 
                    #  Exception: [ mis/kes/kus jne ... (conj) verb ... (conj) , ... (conj) root ] --> DON'T CHANGE
                    #             ( tricky, but if the comma is in the middle of a conjunction phrase, 
                    #               then it likely belongs to the conjunction, and is not a clause break )
                    #
                    #  Example:   [ Mindi presidendilossi , kuhu üles rivistatud orkestrile , auvahtkonnale ja 
                    #               ministritele lisaks oli kutsutud (root) ka 30 soomepoissi . ]
                    #
                    conj_phrases = get_phrase_conjunctions(cl_syntax_words)
                    for conj_phrase in conj_phrases:
                        if last_comma_idx in conj_phrase:
                            idx = conj_phrase.index(last_comma_idx)
                            # Check if comma is in the middle of a phrase
                            if 0 < idx and idx < len(conj_phrase):
                                exceptions_passed = False
                                break
                pat_name = 'attributive_embedded_clause_wrong_end'
                if is_sentence_start:
                    # 
                    #  Exception: [ Mis/Kes ... verb ... , ... root ] --> DON'T CHANGE
                    #             ( too tricky )
                    #
                    #  Example:   [ Mis aga alkoholi puutub siis shampanja on ikka väga hea , samuti hea vein (root) .]
                    #
                    exceptions_passed = False
                if last_comma_idx + 2 < len(clause_lemmas):
                    if clause_lemmas[last_comma_idx + 1] == 'välja' and \
                       clause_lemmas[last_comma_idx + 2] in ['arvama', 'arvatud']:
                        # 
                        #  Exception: [ mis/kes ... verb ... , välja arvatud (root) ... ] --> 
                        #             [ mis/kes ... verb ...  , ] [ välja arvatud (root) ... ]
                        #             ( create regular clause )
                        #
                        #  Example:  [ teenused ,] 
                        #            [ mis on seotud liiklusõiguste kasutamisega, välja arvatud (root) käesoleva lisa 
                        #              punktis 3 sätestatu .] 
                        #             -->
                        #            [ teenused ,] 
                        #            [ mis on seotud liiklusõiguste kasutamisega, ] 
                        #            [ välja arvatud (root) käesoleva lisa punktis 3 sätestatu . ]
                        #
                        pat_name = 'attributive_clause_wrong_end'
                if prev_cl_syntax_words is not None and len(prev_cl_syntax_words) > 1:
                    prev_clause_lemmas = [ w.annotations[0]['lemma'] for w in prev_cl_syntax_words ]
                    if prev_clause_lemmas[0] in ['kui', 'et'] or prev_clause_lemmas[1] in ['kui', 'et']:
                        # 
                        #  Exception: [kui/et ...] [ mis/kes ... verb ... , ... root ] --> 
                        #             [kui/et ...] [ mis/kes ... verb ...  , ] [ ... root ]
                        #             ( create regular clause )
                        #
                        #  Example:   [kui on huvilisi] 
                        #             [kes sooviks saada küsitlustöö kogemust ... , andku (root) endast mulle märku] 
                        #              --> 
                        #             [kui on huvilisi] 
                        #             [kes sooviks saada küsitlustöö kogemust ... ,] 
                        #             [andku (root) endast mulle märku]
                        #
                        #  Example:   [sellest,] 
                        #             [et kolme aasta jooksul pole parlament suutnud otsusele jõuda ,] 
                        #             [kelle kasuks otsus langetada , võib ka aru saada (root) ]
                        #               --> 
                        #             [sellest,] 
                        #             [et kolme aasta jooksul pole parlament suutnud otsusele jõuda ,] 
                        #             [kelle kasuks otsus langetada ,] 
                        #             [võib ka aru saada (root) ]
                        #
                        pat_name = 'attributive_clause_wrong_end'
                    prev_clause_deprels = [ w.annotations[0]['deprel'] for w in prev_cl_syntax_words ]
                    if prev_clause_deprels[-1] == 'punct' and prev_clause_deprels[-2] == 'discourse':
                        # 
                        #  Exception: [<discourse> ,] [ mis/kes ... , ... root ] -->
                        #             [<discourse> ,] [ mis/kes ... ,] [... root ]
                        #             ( create regular clause )
                        #
                        #
                        #  Example:   [Ah,] [mis neist peensustest ikka rääkida , lööb Kaie käega .]
                        #              -->
                        #             [Ah,] 
                        #             [mis neist peensustest ikka rääkida ,] 
                        #             [lööb Kaie käega .] 
                        #
                        pat_name = 'attributive_clause_wrong_end'
                    if prev_clause_lemmas[0] in attributive_clause_start_lemmas:
                        # 
                        #  Exception: [kus/kes/mis ...] [ mis/kes ... , ... root ] --> DON'T CHANGE
                        #             ( tricky )
                        #
                        #  Example:   [Ivanovi sõnul on olukord,] 
                        #             [kus õnnitletakse veterane,] 
                        #             [keda enam elavate kirjas pole , kestnud (root) juba aastaid.] 
                        #
                        #  Example:   [Toodete suhtes,] 
                        #             [mille puhul ekspordiga seotud formaalsused on täidetud või] 
                        #             [mille suhtes kohaldati ... mõnda määruse osutatud korda , pikendatakse (root) määruse 
                        #              ... lõike] 
                        #
                        #
                        exceptions_passed = False
                    prev_clause_postags = [ w.annotations[0]['xpostag'] for w in prev_cl_syntax_words ]
                    if 'V' not in prev_clause_postags and _last_index('V', clause_postags) < last_comma_idx:
                        # 
                        #  Exception: [...no_verb ...] [ mis/kes ... , ... no_verb ] --> DON'T CHANGE
                        #
                        #
                        #  Example:   [Lisaks veel kroonilaenud,] [ mille tagasimakse on eurodes , veel 33%.]
                        #
                        exceptions_passed = False
                if exceptions_passed:
                    # Create error description
                    correction_desc = ''
                    split_at_word = cl_syntax_words[last_comma_idx]
                    if pat_name == 'attributive_embedded_clause_wrong_end':
                        embed_positions  = f'{prev_cl_syntax_words[-1].start}:{split_at_word.end}'
                        parent_positions = f'{prev_cl_syntax_words[0].start}:{clause.end}'
                        correction_desc = f'Split clause after position {split_at_word.end} '+\
                                          f'and then embed the clause {embed_positions} '+\
                                          f'into clause {parent_positions}.'
                        # Make pattern name more specific
                        pat_name = f'attributive_{clause_lemmas[0]}_embedded_clause_wrong_end'
                    if pat_name == 'attributive_clause_wrong_end':
                        correction_desc = f'Split clause after position {split_at_word.end}.'
                        # Make pattern name more specific
                        pat_name = f'attributive_{clause_lemmas[0]}_clause_wrong_end'
                    # Add error marker to the output layer
                    if pat_name not in errors_layer.meta:
                        errors_layer.meta[pat_name] = 0
                    errors_layer.meta[pat_name] += 1
                    status[pat_name] += 1
                    errors_layer.add_annotation( split_at_word.base_span, 
                                                 err_type=pat_name, 
                                                 sent_id=sent_id, 
                                                 correction_description=correction_desc )
                    # Construct debug output
                    if debug_output:
                        output_str.append( '\n' )
                        output_str.append( '='*50 )
                        output_str.append( '\n' )
                        output_str.append( f'{pat_name}::{status[pat_name]}' )
                        output_str.append( '\n' )
                        output_str.append( '\n' )
                        inside_clause_indexes = [w.annotations[0]['id'] for w in cl_syntax_words]
                        for clause2, cl_syntax_words2 in zip(sent_clauses, sent_cl_syntax_words):
                            cl_word_idx = 0
                            for w in cl_syntax_words2:
                                marking = ''
                                if w.annotations[0]['id'] in inside_clause_indexes and cl_word_idx == last_comma_idx:
                                    marking = '<--- NEW CLAUSE END / EMBEDDING'
                                    if not pat_name.endswith('_embedded_clause_wrong_end'):
                                        marking = '<--- NEW CLAUSE END'
                                output_str.append( f"{w.text} {w.annotations[0]['id']} {w.annotations[0]['head']} {w.annotations[0]['deprel']} {marking}" )
                                output_str.append( '\n' )
                                cl_word_idx += 1
                            output_str.append( '' )
                            output_str.append( '\n' )
                        output_str.append( '' )
                        output_str.append( '\n' )
            elif first_verb_idx == -1 and clause_lemmas[-1] == ',' and 'root' not in clause_deprels:
                # ==========================================
                # Detect errors related to disconnected root clauses 
                # (an embedding should be cut out in order to connect the root clause)
                # ==========================================
                #
                # Pattern: [ A ... no_verb/no_root/headed_by_root     , ] [ B ... , ] [ C root ... ] --> 
                #          [ A ... no_verb/no_root/headed_by_root [ B , ... , ]           root ... ]
                #          ( create an embedded clause )
                #
                # Example: [Juulis,] [kui karupojad ise toitu otsima hakkavad,] [tuuakse nad tagasi.] --> 
                #          [Juulis   [,kui karupojad ise toitu otsima hakkavad,] tuuakse nad tagasi.]
                #
                # Example: [Varakevadel,] [kui talvevarudest napib,] [käime Naissaarel hülgeid küttimas.] --> 
                #          [Varakevadel   [,kui talvevarudest napib,] käime Naissaarel hülgeid küttimas.]
                #
                # Example: [Sest selleks,] [et saada relvaluba,] [on vaja täita palju formaalsusi.] --> 
                #          [Sest selleks [, et saada relvaluba ,] on vaja täita palju formaalsusi.]
                #
                # Example: [Mõnikord,] [kui eriti vaja pole,] [tuleb BIOS upgradesid ette igasuguseid.] --> 
                #          [Mõnikord   [,kui eriti vaja pole,] tuleb BIOS upgradesid ette igasuguseid.]
                #
                w_ids = [ w.annotations[0]['id'] for w in cl_syntax_words ]
                w_heads = [ w.annotations[0]['head'] for w in cl_syntax_words ]
                # Find depenency relations pointing out of the clause
                out_of_clause_heads = []
                for w_id, w_head, w_lemma in zip(w_ids, w_heads, clause_lemmas):
                    if w_head not in w_ids and w_lemma != ',':
                        out_of_clause_heads.append( w_head )
                root_clause = None
                clauses_in_between = []
                if out_of_clause_heads:
                    # Find if any out_of_clause_heads leads to a (verbal) root 
                    # in other/following clauses
                    following_clause = 0
                    for clause2, cl_syntax_words2 in zip(sent_clauses, sent_cl_syntax_words):
                        if clause2.end < clause.start:
                            # Skip preceding clauses
                            continue
                        last_clause = clause if not clauses_in_between else clauses_in_between[-1]
                        if last_clause != clause2 and clause2.start-2 <= last_clause.end:
                            # This is a regular clause following the initial clause 
                            # or one of its followers
                            if clause2.annotations[0]['clause_type'] == 'regular':
                                clauses_in_between.append(clause2)
                        if len(clauses_in_between) == 2:
                            # Look only 2nd following clause
                            clauses_in_between.pop(-1)
                            clause2_deprels = [w.annotations[0]['deprel'] for w in cl_syntax_words2]
                            if 'root' in clause2_deprels:
                                parent_feats = \
                                    _get_parent_features_in_clause(cl_syntax_words2, {'xpostag', 'deprel'})
                                for wid, w in enumerate( cl_syntax_words2 ):
                                    # Verbal root or its parent should be at beginning of the clause
                                    if wid == 0 and \
                                       w.annotations[0]['id'] in out_of_clause_heads and \
                                       w.annotations[0]['xpostag'] == 'V':
                                        if w.annotations[0]['deprel'] == 'root' or \
                                           (parent_feats[wid]['deprel'] == 'root' and \
                                            parent_feats[wid]['xpostag'] == 'V'):
                                            root_clause = clause2
                                            break
                        if root_clause is not None:
                            break
                #
                # (!) Skip problematic cases:
                #
                #  Exception: [Tõsi,] [et mitte jääda narriks,] [esitab fond Moskvale jätkuvalt nõudmisi.]
                #              --> DON'T CHANGE
                #             (tricky case)
                #
                #  Exception: [Alati,] [kui hakkan viina võtma,] [otsin ma taskust Mart Laari pildi.] 
                #              --> DON'T CHANGE
                #             (embedding changes the meaning of the main clause)
                #
                #  Exception: [Ent ükskõik,] [mis summa hüvitatakse,] [kasutatakse seekord /---/ omavastutust.]
                #              --> DON'T CHANGE
                #             (tricky case)
                #
                #  Exception: [Juhul,] [kui komisjon peab vajalikuks,] [tuleb eelarves teha muudatusi.]
                #              --> DON'T CHANGE
                #             (tricky case)
                #
                #  Exception: [Lugupeetud kolleegid,] [nagu komisjon ütles,] [vajab eelnõu /---/]
                #              --> DON'T CHANGE
                #             (tricky case)
                #
                problematic = any( [lemma in ['lugupeetud', 'austatud', 'tõepoolest', 'tõsi', \
                                              'muide', 'muuseas', 'võimalik', 'alati', 'ükskõik', \
                                                                'niipea', 'iseasi', 'iseküsimus'] \
                                                                  for lemma in clause_lemmas] )
                clause_word_texts = [ w.text.lower() for w in cl_syntax_words ]
                problematic = problematic or any( [word in ['kallid', 'juhul', 'juhtudel'] \
                                                            for word in clause_word_texts] )
                #
                #  Exception: If the clause in between ends with quotes, then 
                #             it is likely a part of the direct speech --> DON'T CHANGE
                #
                problematic = problematic or \
                              (len(clauses_in_between) > 0 and 
                               clauses_in_between[-1][-1].text in ['"', "'", '»', '“', '”'])
                if root_clause is not None and not problematic:
                    pat_name = 'disconnected_root_clause'
                    # Add error marker to the output layer
                    if pat_name not in errors_layer.meta:
                        errors_layer.meta[pat_name] = 0
                    errors_layer.meta[pat_name] += 1
                    status[pat_name] += 1
                    embed_positions  = f'{cl_syntax_words[-1].start}:{last_clause.end}'
                    parent_positions = f'{clause.start}:{root_clause.end}'
                    correction_desc = f'Embed the adjusted clause {embed_positions} '+\
                                      f'into clause {parent_positions}.'
                    errors_layer.add_annotation( root_clause[0].base_span, 
                                                 err_type=pat_name, 
                                                 sent_id=sent_id, 
                                                 correction_description=correction_desc )
                    # Construct debug output
                    if debug_output:
                        output_str.append( '\n' )
                        output_str.append( '='*50 )
                        output_str.append( '\n' )
                        output_str.append( f'{pat_name}::{status[pat_name]}' )
                        output_str.append( '\n' )
                        output_str.append( '\n' )
                        for clause2, cl_syntax_words2 in zip(sent_clauses, sent_cl_syntax_words):
                            cl_word_idx = 0
                            cl_type = clause2.annotations[0]['clause_type']
                            if cl_type == 'embedded':
                                output_str.append( '<EMBEDDED_CLAUSE>' )
                                output_str.append( '\n' )
                            for w in cl_syntax_words2:
                                marking = ''
                                if w.base_span == root_clause[0].base_span:
                                    marking = '<--- NEW EMBEDDING FROM PREV CLAUSE'
                                output_str.append( f"{w.text} {w.annotations[0]['id']} {w.annotations[0]['head']} {w.annotations[0]['deprel']} {marking}" )
                                output_str.append( '\n' )
                            output_str.append( '' )
                            output_str.append( '\n' )
                        output_str.append( '' )
                        output_str.append( '\n' )
                
    return errors_layer if not debug_output else (errors_layer, ''.join(output_str))


# =========================================================================
#   Extraction of potential erroneous sentences
# =========================================================================

def _extract_sentences_with_clause_errors( text, clauses_layer='clauses', syntax_layer='syntax', sentences_layer='sentences',
                                                 copy_metadata=True ):
    '''
    Extracts sentences with potential clause errors with the method detect_clause_errors().
    Yields extracted sentences as Text objects that have the same set of layers as the 
    input text.
    
    Parameters
    ----------
    text: Text
        Analysable Text object.
    clauses_layer: str
        Name of the clauses layer attached to the Text object. 
        Default: 'clauses'
    syntax_layer: str
        Name of the syntax layer attached to the Text object. 
        Default: 'syntax'
    sentences_layer: str
        Name of the sentences layer attached to the Text object. 
        Default: 'sentences'
    copy_metadata: bool
        If True, then metadata of the input Text object is also 
        carried to the yielded Text object.
    
    Yields
    -------
    Text
        A Text object corresponding to a potentially erroneous sentence.
    '''
    errors_layer = detect_clause_errors( text, output_layer='clause_errors', clauses_layer=clauses_layer, 
                                               syntax_layer=syntax_layer, sentences_layer=sentences_layer )
    words_layer_name = text[sentences_layer].enveloping
    assert words_layer_name in text.layers
    if len(errors_layer) > 0:
        for err_span in errors_layer:
            err_sentence = text[sentences_layer][err_span.sent_id]
            err_sentence_start = err_sentence.start
            extracted_text = extract_section( text = text, 
                start = err_sentence.start,
                end = err_sentence.end,
                layers_to_keep = text.layers,
                trim_overlapping=False
            )
            # Carry over metadata
            if copy_metadata:
                for key in text.meta.keys():
                    extracted_text.meta[key] = text.meta[key]
            extracted_text.meta['_original_sentence_start'] = err_sentence.start
            extracted_text.meta['_original_sentence_end'] = err_sentence.end
            yield extracted_text

# =========================================================================
#   Repair clause errors
# =========================================================================

_pattern_simple_split = \
    re.compile(r'Split clause after position (\d+)\.')
_pattern_split_and_embed = \
    re.compile(r'Split clause after position (\d+) and then embed the clause (\d+):(\d+) into clause (\d+):(\d+)\.')
_pattern_embed = \
    re.compile(r'Embed the adjusted clause (\d+):(\d+) into clause (\d+):(\d+)\.')

def fix_clause_errors_with_syntax( text, clauses_layer='clauses', syntax_layer='syntax', 
                                         sentences_layer='sentences', output_layer='clauses' ):
    '''
    Detects potential clause errors with the method detect_clause_errors(), and applies 
    described corrections to the clauses layer. 
    Returns a new fixed clauses layer, which is not attached to the Text object.
    
    Parameters
    ----------
    text: Text
        Analysable Text object.
    clauses_layer: str
        Name of the clauses layer attached to the Text object. 
        Default: 'clauses'
    syntax_layer: str
        Name of the syntax layer attached to the Text object. 
        Default: 'syntax'
    sentences_layer: str
        Name of the sentences layer attached to the Text object. 
        Default: 'sentences'
    output_layer: str
        Name of the output fixed clauses layer. The layer will 
        not be attached to the Text object by default.
        Default: 'clauses'
    
    Yields
    -------
    Layer
        A fixed clauses layer.
    '''
    errors_layer = detect_clause_errors( text, output_layer='clause_errors', clauses_layer=clauses_layer, 
                                               syntax_layer=syntax_layer, sentences_layer=sentences_layer )
    old_clauses_layer = text[clauses_layer]
    assert old_clauses_layer.enveloping is not None 
    assert old_clauses_layer.enveloping in text.layers
    # Find erroneous sentences
    sent_to_clause_errors_map = {}
    for error in errors_layer:
        sent_id = error.annotations[0]['sent_id']
        if sent_id not in sent_to_clause_errors_map:
            sent_to_clause_errors_map[sent_id] = []
        sent_to_clause_errors_map[sent_id].append(error)
    # Iterate sentences and apply fixes
    fixed_layer = Layer(output_layer, attributes=old_clauses_layer.attributes, 
                                      enveloping=old_clauses_layer.enveloping, text_object=text)
    for sent_id, sent_clauses, sent_cl_syntax_words in yield_clauses_and_syntax_words_sentence_wise( text, \
                                                                                clauses_layer=clauses_layer, \
                                                                                syntax_layer=syntax_layer, \
                                                                                sentences_layer=sentences_layer ):
        if sent_id not in sent_to_clause_errors_map.keys():
            # Nothing to fix here, just carry over the clauses
            for clause in sent_clauses:
                annotation = {attr: clause.annotations[0][attr] for attr in fixed_layer.attributes}
                fixed_layer.add_annotation( clause.base_span, annotation )
        else:
            # Apply fixes
            for error_id, error in enumerate(sent_to_clause_errors_map[sent_id]):
                correction_description = error.annotations[0]['correction_description']
                if error_id > 0:
                    warnings.warn( ('Applying multiple fixes on a sentence has not been implemented. '+\
                                    'Discarding the fix {!r}.').format(correction_description) )
                    continue
                m1 = _pattern_simple_split.match(correction_description)
                m2 = _pattern_split_and_embed.match(correction_description)
                m3 = _pattern_embed.match(correction_description)
                if m1:
                    # Instruction:  Split clause after position (\d+).
                    split_after = int(m1.group(1))
                    old_clause = None
                    old_clause_id = None
                    first_subclause = []
                    second_subclause = []
                    for cid, clause in enumerate(sent_clauses):
                        split_clause_at_word = -1
                        for wid, word in enumerate(clause):
                            if word.end == split_after:
                                old_clause = clause
                                old_clause_id = cid
                                first_subclause  = \
                                    [clause[i].base_span for i in range(0, wid+1)]
                                second_subclause = \
                                    [clause[i].base_span for i in range(wid+1, len(clause))]
                                break
                        if first_subclause and second_subclause:
                            break
                    if first_subclause and second_subclause:
                        # Apply fixes
                        # TODO: make it work in a way that multiple fixes can also be applied on a sentence
                        for cid, clause in enumerate(sent_clauses):
                            if cid != old_clause_id:
                                # Simply copy the old clause
                                annotation = {attr: clause.annotations[0][attr] for attr in fixed_layer.attributes}
                                fixed_layer.add_annotation( clause.base_span, annotation )
                            else:
                                # Make two subclauses
                                annotation = {attr: old_clause.annotations[0][attr] for attr in fixed_layer.attributes}
                                fixed_layer.add_annotation( first_subclause, annotation )
                                fixed_layer.add_annotation( second_subclause, annotation )
                    else:
                        raise Exception( ('(!) Unable to find clause meeting '+\
                                          'correction_description {!r}.').format(correction_description) )
                elif m2:
                    # Instruction: Split clause after position (\d+) and then embed the clause (\d+):(\d+) into clause (\d+):(\d+)
                    split_after  = int(m2.group(1))
                    embed_start  = int(m2.group(2))
                    embed_end    = int(m2.group(3))
                    parent_start = int(m2.group(4))
                    parent_end   = int(m2.group(5))
                    old_clause = None
                    old_clause_id = None
                    old_parent_clause = None
                    old_parent_clause_id = None
                    conj_span = None
                    embedded_clause = []
                    parent_clause_start = []
                    parent_clause_end = []
                    for cid, clause in enumerate(sent_clauses):
                        split_clause_at_word = -1
                        for wid, word in enumerate(clause):
                            if word.start == parent_start:
                                # First half of the parent clause
                                assert wid == 0
                                old_parent_clause = clause
                                old_parent_clause_id = cid
                                parent_clause_start = []
                                while wid < len(clause):
                                    word = clause[wid]
                                    if word.start < embed_start:
                                        parent_clause_start.append(word.base_span)
                                    elif word.start == embed_start:
                                        conj_span = word.base_span
                                        break
                                    else:
                                        break
                                    wid += 1
                                break
                            if word.end == split_after:
                                # Embedded clause and second half of the parent clause
                                old_clause = clause
                                old_clause_id = cid
                                embedded_clause = \
                                    [clause[i].base_span for i in range(0, wid+1)]
                                parent_clause_end = \
                                    [clause[i].base_span for i in range(wid+1, len(clause))]
                                assert embedded_clause[-1].end == embed_end
                                assert parent_clause_end[-1].end == parent_end
                                break
                        if embedded_clause and parent_clause_start and parent_clause_end:
                            break
                    if embedded_clause and parent_clause_start and parent_clause_end and conj_span:
                        # Apply fixes
                        # TODO: make it work in a way that multiple fixes can also be applied on a sentence
                        for cid, clause in enumerate(sent_clauses):
                            if cid == old_parent_clause_id:
                                # Make a parent clause
                                annotation = {attr: old_parent_clause.annotations[0][attr] for attr in fixed_layer.attributes}
                                fixed_layer.add_annotation( parent_clause_start + parent_clause_end, annotation )
                            elif cid == old_clause_id:
                                # Make an embedded clause
                                annotation = {attr: old_clause.annotations[0][attr] for attr in fixed_layer.attributes}
                                annotation['clause_type'] = 'embedded'
                                fixed_layer.add_annotation( [conj_span]+embedded_clause, annotation )
                            else:
                                # Simply copy the old clause
                                annotation = {attr: clause.annotations[0][attr] for attr in fixed_layer.attributes}
                                fixed_layer.add_annotation( clause.base_span, annotation )
                    else:
                        raise Exception( ('(!) Unable to find clauses meeting '+\
                                          'correction_description {!r}.').format(correction_description) )
                elif m3:
                    # Instruction: Embed the adjusted clause (\d+):(\d+) into clause (\d+):(\d+)
                    embed_start  = int(m3.group(1))
                    embed_end    = int(m3.group(2))
                    parent_start = int(m3.group(3))
                    parent_end   = int(m3.group(4))
                    old_clause = None
                    old_clause_id = None
                    old_parent_clause_start = None
                    old_parent_clause_start_id = None
                    old_parent_clause_end = None
                    old_parent_clause_end_id = None
                    conj_span = None
                    embedded_clause = []
                    parent_clause_start = []
                    parent_clause_end = []
                    for cid, clause in enumerate(sent_clauses):
                        split_clause_at_word = -1
                        for wid, word in enumerate(clause):
                            if word.start == parent_start:
                                # First half of the parent clause
                                assert wid == 0
                                old_parent_clause_start = clause
                                old_parent_clause_start_id = cid
                                parent_clause_start = []
                                while wid < len(clause):
                                    word = clause[wid]
                                    if word.start < embed_start:
                                        parent_clause_start.append(word.base_span)
                                    elif word.start == embed_start:
                                        conj_span = word.base_span
                                        break
                                    else:
                                        break
                                    wid += 1
                                break
                            if word.end == embed_end:
                                # Embedded clause
                                old_clause = clause
                                old_clause_id = cid
                                embedded_clause = \
                                    [clause[i].base_span for i in range(0, wid+1)]
                                assert embedded_clause[-1].end == embed_end
                                break
                            if word.end == parent_end:
                                # End of the parent clause
                                old_parent_clause_end = clause
                                old_parent_clause_end_id = cid
                                parent_clause_end = \
                                    [clause[i].base_span for i in range(0, wid+1)]
                                assert parent_clause_end[-1].end == parent_end
                        if embedded_clause and parent_clause_start and parent_clause_end:
                            break
                    if embedded_clause and parent_clause_start and parent_clause_end and conj_span:
                        # Apply fixes
                        for cid, clause in enumerate(sent_clauses):
                            if cid == old_parent_clause_start_id:
                                # Make a parent clause
                                annotation = {attr: old_parent_clause_start.annotations[0][attr] for attr in fixed_layer.attributes}
                                fixed_layer.add_annotation( parent_clause_start + parent_clause_end, annotation )
                            elif cid == old_parent_clause_end_id:
                                # Leave out old parent clause ending
                                pass
                            elif cid == old_clause_id:
                                # Make an embedded clause
                                annotation = {attr: old_clause.annotations[0][attr] for attr in fixed_layer.attributes}
                                annotation['clause_type'] = 'embedded'
                                fixed_layer.add_annotation( [conj_span]+embedded_clause, annotation )
                            else:
                                # Simply copy the old clause
                                annotation = {attr: clause.annotations[0][attr] for attr in fixed_layer.attributes}
                                fixed_layer.add_annotation( clause.base_span, annotation )
                    else:
                        raise Exception( ('(!) Unable to find clauses meeting '+\
                                          'correction_description {!r}.').format(correction_description) )
                else:
                    raise NotImplementedError( ('(!) Unexpected correction_description {!r}. '+\
                                                'No fix implemented for such correction.').format(correction_description) )
            
    return fixed_layer