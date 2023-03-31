"""
 This module generates the pronominal coreference pairs based on the sentence context information.

 The source code is from Eduard Barbu's original "generate_pairs.py" 
 module in EstonianCoreferenceSystem (v1.0.0):
  https://github.com/SoimulPatriei/EstonianCoreferenceSystem/blob/7883ac24002fb715d43d9d149ee0340339aeda67/generate_pairs.py
 
 Minor modifications have been made by Siim Orasmaa.
"""

import re
import os
import collections
from estnltk_neural.taggers.coreference.v1 import coreference_features

def _get_corresponding_mentions (unit) :
    """Get the mention(s) corresponding to the pronoun in the coreference pair"""
    """Sometimes you have Coref=12.8,12.10 (two or more possible mentions)"""

    components=unit[-1].split("|")
    for component in components :
        if re.search("Coref=",component) :
            try :
                m=re.search("Coref=(.+)", component)
                matched = m.group(1)
            except AttributeError:
                matched = ""

    return matched


def _is_coreference (unit) :

    """Check if an unit contains a coreference relation"""
    if re.search("Coref=", unit[-1]):
        return True
    return False

def get_annotated_pairs(sentences_list, f_corpus_path) :

    """Get the signatures for all annotated  mention-pronoun pair in the corpus file."""

    signature_list=[]
    for index_sentence,sentence in enumerate(sentences_list) :
        for unit in sentence :
            if _is_coreference (unit) :
                mentions_reference=_get_corresponding_mentions (unit)
                components=mentions_reference.split(",")
                for component in components :
                    index_sentence_mention, index_mention =component.split(".")
                    unit_mention=sentences_list[int(index_sentence_mention)-1][int(index_mention)-1]
                    coreference_pair=([unit_mention[2],'MENTION',unit_mention[0]],[unit[2],'PRON',unit[0]],int(index_sentence_mention),index_sentence+1)
                    signature=os.path.split(f_corpus_path)[1]+"#"+coreference_features.get_signature (coreference_pair)
                    if not signature in signature_list :
                        signature_list.append(signature)
    return signature_list



def get_mentions (sentence,dict_configuration) :

    """Get the pronouns and mentions from a sentence"""

    mentionList=[]
    pronounsList=dict_configuration.keys()
    for unit in sentence :
        if unit[2] in pronounsList :
            mentionList.append (unit[2]+"\t"+"PRON\t"+unit[0])
        if re.search("Mention=Yes",unit[-1]) :
            mentionList.append(unit[2]+"\t"+"MENTION\t"+unit[0])
    return mentionList

def _is_pronoun (mention) :
    """Check if a mention is pronoun"""

    components=mention.split()
    if components[1]=="PRON" :
        return True
    return False

def _is_mention (mention) :
    """Check if an item is a mention"""

    components=mention.split()
    if components[1]=="MENTION" :
        return True
    return False

def _filter_pairs_in (pair_list,dict_context) :

    """Filter the pairs based on the fact that some pronouns allow pairs where the
    pronoun is the first and the mention appears after"""

    good_pair_list=[]
    for pair in pair_list :
        pron=pair[1][0]
        difference=int(pair[1][-1])-int(pair[0][-1])
        if dict_context[pron]["cataphora"]==0 and difference<0 :
            pass
        else :
            good_pair_list.append(pair)

    return good_pair_list

def _get_pairs_in (mention_list,index_sentence,dict_context) :
    """Get mention pronoun pairs in the same sentence """


    pair_list=[]
    for i in range(len(mention_list)):
        mention_i=mention_list[i]
        for j in range(i+1, len(mention_list)):
            mention_j = mention_list[j]
            components_i = mention_i.split("\t")
            components_j = mention_j.split("\t")
            if components_i[-1] != components_j[-1]:
                mention_j=mention_list[j]
                if _is_pronoun(mention_j) and _is_mention(mention_i) :
                    pair_list.append((components_i,components_j,index_sentence,index_sentence))
                elif _is_pronoun(mention_i) and _is_mention(mention_j) :
                    pair_list.append((components_j,components_i,index_sentence,index_sentence))

    return _filter_pairs_in (pair_list,dict_context)

def _filter_pairs_across (pair_list_across, dict_context) :

    """Filter the pairs accross sentences based on the context"""

    pair_list_aux=[]
    for my_tuple in pair_list_across:
        distance=my_tuple[3]-my_tuple[2]
        my_pron=my_tuple[1][0]
        if distance > 0 :
            if dict_context[my_pron]["sentences_before"] >=distance:
                pair_list_aux.append(my_tuple)
        else :
            if dict_context[my_pron]["sentences_after"] >= abs(distance):
                pair_list_aux.append(my_tuple)

    return pair_list_aux

def _get_pairs_across (start_mention_list, stop_mention_list, index_sentence_start, index_sentence_stop, dict_context) :

    """Get coreference pairs when the pronoun is in a sentence and the mention in other sentence"""

    pair_list=[]
    for i in range(len(start_mention_list)):
        mention_i =start_mention_list[i]
        for j in range(len(stop_mention_list)):
            mention_j = stop_mention_list[j]
            components_i = mention_i.split("\t")
            components_j = mention_j.split("\t")

            if _is_pronoun(mention_j) and not _is_pronoun(mention_i):
                pair_list.append((components_i, components_j,index_sentence_start,index_sentence_stop))

            elif _is_pronoun(mention_i) and not _is_pronoun(mention_j):
                pair_list.append((components_j, components_i, index_sentence_stop, index_sentence_start))
    return _filter_pairs_across(pair_list,dict_context)

def get_sentence_context (n_sentences,max_context_before, max_context_after) :

    """Generate the sentence pairs based on context parameters"""

    for index_sentence in range(n_sentences) :
        list_after=_look_ahead(index_sentence,max_context_after,n_sentences-1)
        list_before=_look_before(index_sentence,max_context_before)
        yield list_before+list_after

def _look_ahead (index_sentence,context, maximum) :
    """Generate the look ahead context starting with the sentence index and looking no more
    than max number of sentences"""

    context_pairs = []
    for i in range(1, context+1):
        s_index = index_sentence+i
        if s_index<=maximum:
            context_pairs.append((index_sentence, s_index))
    return context_pairs

def _look_before (index_sentence,context) :
    """Generate the look before context starting with the sentence index and looking no less than the first sentence"""

    context_pairs=[]
    for i in range(1,context+1) :
        s_index=index_sentence-i
        if  s_index>=0 :
            context_pairs.append(( s_index,index_sentence))
    return context_pairs

def get_maximum_contexts (dict_context) :
    """Get the number of sentences before and after to take"""

    max_before_context=0
    for pronoun in dict_context :
        if max_before_context <dict_context[pronoun]["sentences_before"] :
            max_before_context=dict_context[pronoun]["sentences_before"]

    max_after_context = 0
    for pronoun in dict_context:
        if max_after_context < dict_context[pronoun]["sentences_after"]:
            max_after_context = dict_context[pronoun]["sentences_after"]

    return max_before_context,max_after_context


def pronominal_coreference_candidate_pairs (dict_info,sentences_list,f_corpus_path):

    """Generate the pronominal coreference candidate pairs
    based on the context specified in the context dictionary"""

    dict_features = collections.OrderedDict()
    max_context_before, max_context_after = get_maximum_contexts(dict_info["context"])

    if max_context_before == 0 and max_context_after ==0 :
        max_context_before=1
        max_context_after=1

    #dictionary holding the single sentences processed
    dict_sentences={}

    #dictionary holding the pair of sentences
    dict_sentence_pairs={}


    for list_context in get_sentence_context(len(sentences_list),max_context_before,max_context_after) :
        for sentence_pair in list_context :

            index_sentence_start=sentence_pair[0]+1
            index_sentence_stop = sentence_pair[1]+1
            pair_sentences=str(index_sentence_start)+"-"+str(index_sentence_stop)

            start_mention_list=get_mentions (sentences_list[index_sentence_start-1],dict_info["context"])
            stop_mention_list=get_mentions(sentences_list[index_sentence_stop-1],dict_info["context"])

            #Get pairs inside the sentence start
            if index_sentence_start not in dict_sentences :
               pair_list_start=_get_pairs_in(start_mention_list,index_sentence_start,dict_info["context"])
               for pair in pair_list_start:
                   coreference_features.compute_pair_features(pair, sentences_list[index_sentence_start - 1], sentences_list[index_sentence_start - 1], dict_features, dict_info, f_corpus_path, sentences_list)
               dict_sentences[index_sentence_start] = 1

            #Get pairs inside the sentence stop
            if index_sentence_stop not in dict_sentences :
                pair_list_stop=_get_pairs_in(stop_mention_list, index_sentence_stop,dict_info["context"])
                for pair in pair_list_stop:
                    coreference_features.compute_pair_features(pair, sentences_list[index_sentence_stop - 1], sentences_list[index_sentence_stop - 1], dict_features, dict_info, f_corpus_path, sentences_list)
                dict_sentences[index_sentence_start] = 1

            #Get the pairs across sentences
            if not pair_sentences in dict_sentence_pairs :
                pair_list_across=_get_pairs_across(start_mention_list, stop_mention_list, index_sentence_start, index_sentence_stop, dict_info["context"])
                for pair in pair_list_across:
                    coreference_features.compute_pair_features(pair, sentences_list[pair[-2] - 1], sentences_list[pair[-1] - 1], dict_features, dict_info, f_corpus_path, sentences_list)
            dict_sentence_pairs.setdefault(pair_sentences, 0)

    return dict_features



def pronominal_coreference_candidate_pairs_with_locations(dict_info,sentences_list,f_corpus_path):

    """Generate the pronominal coreference candidate pairs 
    based on the context specified in the context dictionary. 
    Add span locations (from stanza output) to each pair."""

    dict_features = collections.OrderedDict()
    dict_locations = collections.OrderedDict()
    max_context_before, max_context_after = get_maximum_contexts(dict_info["context"])

    if max_context_before == 0 and max_context_after ==0 :
        max_context_before=1
        max_context_after=1

    #dictionary holding the single sentences processed
    dict_sentences={}

    #dictionary holding the pair of sentences
    dict_sentence_pairs={}

    if len(sentences_list) > 1:
        # If we have more than one sentence, extract pairs from pairs of sentences and from single sentences
        for list_context in get_sentence_context(len(sentences_list),max_context_before,max_context_after) :
            for sentence_pair in list_context :
                index_sentence_start=sentence_pair[0]+1
                index_sentence_stop = sentence_pair[1]+1
                pair_sentences=str(index_sentence_start)+"-"+str(index_sentence_stop)

                start_mention_list=get_mentions (sentences_list[index_sentence_start-1],dict_info["context"])
                stop_mention_list=get_mentions(sentences_list[index_sentence_stop-1],dict_info["context"])

                #Get pairs inside the sentence start
                if index_sentence_start not in dict_sentences :
                   pair_list_start=_get_pairs_in(start_mention_list,index_sentence_start,dict_info["context"])
                   for pair in pair_list_start:
                       # compute features
                       s_mention=sentences_list[index_sentence_start - 1]
                       s_pronoun=sentences_list[index_sentence_start - 1]
                       coreference_features.compute_pair_features(pair, s_mention, s_pronoun, dict_features, dict_info, f_corpus_path, sentences_list)
                       # get span location for the pair
                       get_pair_span_locations(pair,s_mention,s_pronoun,dict_locations,f_corpus_path)
                   dict_sentences[index_sentence_start] = 1

                #Get pairs inside the sentence stop
                if index_sentence_stop not in dict_sentences :
                    pair_list_stop=_get_pairs_in(stop_mention_list, index_sentence_stop,dict_info["context"])
                    for pair in pair_list_stop:
                        s_mention=sentences_list[index_sentence_stop - 1]
                        s_pronoun=sentences_list[index_sentence_stop - 1]
                        coreference_features.compute_pair_features(pair, s_mention, s_pronoun, dict_features, dict_info, f_corpus_path, sentences_list)
                        # get span location for the pair
                        get_pair_span_locations(pair,s_mention,s_pronoun,dict_locations,f_corpus_path)
                    dict_sentences[index_sentence_start] = 1

                #Get the pairs across sentences
                if not pair_sentences in dict_sentence_pairs :
                    pair_list_across=_get_pairs_across(start_mention_list, stop_mention_list, index_sentence_start, index_sentence_stop, dict_info["context"])
                    for pair in pair_list_across:
                        s_mention=sentences_list[pair[-2] - 1]
                        s_pronoun=sentences_list[pair[-1] - 1]
                        coreference_features.compute_pair_features(pair, s_mention, s_pronoun, dict_features, dict_info, f_corpus_path, sentences_list)
                        # get span location for the pair
                        get_pair_span_locations(pair,s_mention,s_pronoun,dict_locations,f_corpus_path)
                dict_sentence_pairs.setdefault(pair_sentences, 0)
    elif len(sentences_list) == 1:
        # If we have only one sentence, extract pairs from that sentence only
        index_sentence = 1
        pair_sentences=str(index_sentence)+"-"+str(index_sentence)
        mention_list=get_mentions(sentences_list[index_sentence-1],dict_info["context"])
        pair_list=_get_pairs_in(mention_list,index_sentence,dict_info["context"])
        for pair in pair_list:
            # compute features
            s_mention=sentences_list[index_sentence - 1]
            s_pronoun=sentences_list[index_sentence - 1]
            coreference_features.compute_pair_features(pair, s_mention, s_pronoun, dict_features, dict_info, f_corpus_path, sentences_list)
            # get span location for the pair
            get_pair_span_locations(pair,s_mention,s_pronoun,dict_locations,f_corpus_path)
        dict_sentences[index_sentence] = 1

    return dict_features, dict_locations



def get_pair_span_locations(pair,s_mention,s_pronoun,dict_locations,f_corpus_path):
    """
    Records span locations ('start_char=' & 'end_char=' from stanza output sentence) 
    of the pair.
    """
    assert pair[0][1] == 'MENTION'
    assert pair[1][1] == 'PRON'
    id_mention=pair[0][2]
    id_pronoun=pair[1][2]
    mention_token = [token for token in s_mention if token[0]==id_mention]
    pronoun_token = [token for token in s_pronoun if token[0]==id_pronoun]
    assert len(mention_token) == 1
    assert len(pronoun_token) == 1
    mention_span = mention_token[0][-1]
    pronoun_span = pronoun_token[0][-1]
    assert 'start_char=' in mention_span, f'Token {mention_token[0]!r} is missing "start_char="'
    assert 'end_char=' in mention_span, f'Token {mention_token[0]!r} is missing "end_char="'
    assert 'start_char=' in pronoun_span, f'Token {pronoun_token[0]!r} is missing "start_char="'
    assert 'end_char=' in pronoun_span, f'Token {pronoun_token[0]!r} is missing "end_char="'
    index_coreference_pair = os.path.split(f_corpus_path)[1] + "#" + coreference_features.get_signature(pair)
    dict_locations[index_coreference_pair] = {'MENTION':mention_span, 'PRON':pronoun_span}

