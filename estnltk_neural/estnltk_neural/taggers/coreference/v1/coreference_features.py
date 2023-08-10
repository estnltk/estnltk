"""
 The module computes features for the coreference pairs.

 The source code is from Eduard Barbu's original "coreference_features.py" 
 module in EstonianCoreferenceSystem (v1.0.0):
  https://github.com/SoimulPatriei/EstonianCoreferenceSystem/blob/7883ac24002fb715d43d9d149ee0340339aeda67/coreference_features.py
 
 Minor modifications have been made by Siim Orasmaa.
"""

import re
import os
import os.path
import xml
import collections
from gensim.models import KeyedVectors

# 
#  TODO: this is not thread safe and breaks consistency 
#  if multiple taggers with different configurations are 
#  used. For thread safety, these variables should be 
#  instance variables of the tagger
# 
mentions_score_dict={}
eleri_dict={}
dict_features_names=collections.OrderedDict()
dict_embeddings_fpaths={}
dict_embeddings_models={}

def get_feature_names () :
    return dict_features_names

def get_eleri_abstractness (f_eleri) :

    """Get the abstractness level as computed by Eleri Aedmaa"""

    fi = open(f_eleri, mode='r', encoding='utf-8')
    for line in fi :
        line=line.rstrip()
        mention,value=line.split()
        eleri_dict[mention]=value
    fi.close()

def get_mention_global_scores (f_mentions_score) :

    """Get the scores computed globally for mentions"""

    fi = open(f_mentions_score, mode='r', encoding='utf-8')
    for line in fi :
        line=line.rstrip()
        mention,value=line.split()
        mentions_score_dict[mention]=value
    fi.close()


def get_embeddings_path (f_embeddings, f_root_dir=None) :
    """Read the XML configuration file"""
    if f_root_dir is not None:
        f_embeddings = os.path.join(f_root_dir, f_embeddings)

    doc = xml.dom.minidom.parse(f_embeddings)
    embeddings= doc.getElementsByTagName("embeddings")
    for embedding in embeddings :

        name= embedding.getElementsByTagName("name")[0].childNodes[0].data
        path = embedding.getElementsByTagName("path")[0].childNodes[0].data
        dict_embeddings_fpaths[name]=path
        if f_root_dir is not None:
            dict_embeddings_fpaths[name] = os.path.join(f_root_dir, 
                                                        dict_embeddings_fpaths[name])


def init_embedding_models (f_embeddings,logging, f_root_dir=None) :
    """Init the embedding models globally based on given XML configuration."""
    assert f_root_dir is None or os.path.exists(f_root_dir), \
        f'Missing or invalid resources root directory {f_root_dir!r}'
    logger = logging.getLogger('coreference_features.init_embedding_models')
    get_embeddings_path(f_embeddings, f_root_dir=f_root_dir)
    for name in dict_embeddings_fpaths:
        model = KeyedVectors.load_word2vec_format(dict_embeddings_fpaths[name], binary=True)
        dict_embeddings_models[name] = model
        logger.info ("Inited "+name+ " embeddings")

def init_embedding_models_based_on_dict (embeddings_dict,logging) :
    """Init the embedding models globally based on given dict.
       Dictionary should provide mappings: (name, embeding_file_location)."""
    assert isinstance(embeddings_dict, dict)
    logger = logging.getLogger('coreference_features.init_embedding_models')
    for name, embeddings_fpath in embeddings_dict.items():
        assert os.path.exists(embeddings_fpath), \
            f'(!) Unable to find embeddings file from location {embeddings_fpath!r}'
        dict_embeddings_fpaths[name]=embeddings_fpath
        model = KeyedVectors.load_word2vec_format(embeddings_fpath, binary=True)
        dict_embeddings_models[name] = model
        logger.info ("Inited "+name+ " embeddings")

def distance_pronoun_antecedent (pair) :
    """Distance is 0 if the pronoun and antecedent are in the same sentence"""
    return pair[3]-pair[2]

def get_possible_mention_scores (s_pronoun_index,sentences_list,n_sentences_before, n_sentences_after) :
    """Compute a score for each mention in the neibourhood of a pronoun sentence"""

    dict_frequency={}
    n_sentences=len(sentences_list)

    index_start=s_pronoun_index-n_sentences_before
    index_end=s_pronoun_index+n_sentences_after

    if index_start<0 :
        index_start=0

    if index_end>n_sentences-1 :
        index_end=n_sentences-1


    for sentence in sentences_list[index_start:index_end+1] :
        for unit in sentence :
            if re.search("Mention=Yes", unit[-1]):
                dict_frequency.setdefault(unit[2], 0)
                dict_frequency[unit[2]] += 1

    return dict_frequency


def add_eleri_abstractness_level (mention) :
    """Add the level of abstractness according to Eleri Aedmaa file"""
    if mention in eleri_dict:
        return eleri_dict[mention]
    return 0


def add_mention_global_score (mention) :
    """Add the global score computed for mentions"""
    if mention in mentions_score_dict:
        return mentions_score_dict[mention]
    return 0



def _get_number_of_nouns_same_sentence(pair, sentence):
    """Get the number of nouns between the mention and pronoun
    when these two are in the same sentence"""

    noun_count = 0
    mention_index = int(pair[0][2])
    pronoun_index = int(pair[1][2])

    if pronoun_index > mention_index:
        start_index = mention_index
        end_index = pronoun_index
    else:
        start_index = pronoun_index
        end_index = mention_index

    for word in sentence[start_index:end_index - 1]:
        if word[3] == "NOUN" or word[3] == "PROPN":
            noun_count += 1

    return noun_count

def _get_number (my_unit) :
    """Get the number for the pronoun or antecedent"""

    components=my_unit[5].split("|")
    matched=""
    for component in components :
        m = re.search("Number=(.+)", component)
        if m :
            matched = m.group(1)
    return matched

def number_agreement (pair ,s_mention, s_pronoun) :
    """1 there is number agreement between antecedent and pronoun"""
    """0 otherwise """

    unit_mention=_get_unit(s_mention,pair[0][-1])
    unit_pronoun = _get_unit(s_pronoun, pair[1][-1])
    nb_mention=_get_number (unit_mention)
    nb_pronoun=_get_number (unit_pronoun)
    if nb_mention==nb_pronoun :
            return 1
    return 0

def is_specific_pos (pair,sentence,my_pos) :
    """1 if the antecedent is POS"""
    """0 otherwise"""

    unit_mention = _get_unit(sentence, pair[0][-1])
    if  unit_mention[3] == my_pos :
        return 1
    return 0

def _get_case (unit) :
    """Get the case for the pronoun or antecedent"""

    components=unit[5].split("|")
    matched=""
    for component in components :
        m = re.search("Case=(.+)", component)
        if m :
            matched = m.group(1)
    return matched

def get_case_value (my_case, dict_cases) :
    """Get the case value"""

    if my_case in dict_cases:
        return dict_cases[my_case]
    return 0


def get_case (my_index,my_sentence,dict_cases) :
    """Get the case of the pronoun or the antecedent"""

    my_unit=_get_unit(my_sentence,my_index)
    my_case=_get_case(my_unit)
    return get_case_value (my_case, dict_cases)

def _get_unit(sentence,index) :
    """Get the unit based on an index """

    for unit in sentence :
        if unit[0] == index :
            return unit
    return None


def get_syntactic_value (my_value,dict_syntactic_functions) :
    """Get the value of the syntactic function"""

    if my_value in dict_syntactic_functions :
        key=dict_syntactic_functions[my_value]['keep']
        return  dict_syntactic_functions[key]['number']
    return 0

def get_syntactic_function (my_sentence, my_index, dict_syntactic_functions) :
    """Get the syntactic function"""

    my_unit = _get_unit(my_sentence, my_index)
    return  get_syntactic_value (my_unit[7],dict_syntactic_functions)

def pos_head (my_index, s_mention,dict_tagset) :
    """Computes the POS of the head of the mention or
    the head of the pronoun"""

    unit_mention=_get_unit(s_mention,my_index)
    unit_head=_get_unit(s_mention, unit_mention[6])
    if unit_head :
        return get_pos_value (unit_head[3], dict_tagset)
    return len(dict_tagset)+1

def get_pos_value (my_pos, dict_tagset) :
    """Get the pos value"""

    if my_pos in dict_tagset:
        return dict_tagset[my_pos]
    return 0


def pos_word (my_sentence,my_index,dict_tagset) :
    """Get the POS of the word at the index"""

    my_unit = _get_unit(my_sentence,my_index)
    return get_pos_value (my_unit[3], dict_tagset)

def pos_after (my_index,s_mention, n_positions,dict_tagset) :
    """Get the POS n_positions after the pronoun or antecedent"""

    if int(my_index) + n_positions > len(s_mention) :
        return len(dict_tagset)+1
    unit=_get_unit(s_mention, str(int(my_index)+n_positions))
    return get_pos_value (unit[3], dict_tagset)

def pos_before (my_index,s_mention, n_positions,dict_tagset) :
    """Get the POS n_positions before the pronoun or antecedent"""

    if int(my_index) - n_positions <1 :
        return len(dict_tagset)+1
    unit=_get_unit(s_mention, str(int(my_index)-n_positions))
    return get_pos_value (unit[3], dict_tagset)

def get_position (pair, s_mention) :

    """Get the position of the antecedent : {beginning (0)  , middle(1), end (2)} of the sentence """

    antd_index=int(pair[0][-1])-1
    if antd_index == 0 :
        return 0
    if antd_index == len(s_mention) -1 :
        return 2
    return 1

def _get_lemmas (pair,s_mention,s_pronoun) :
    """Get the lemmas of the words from the pair"""


    for unit in s_mention :
        if pair[0][-1]==unit[0] :
            lemma_antd=unit[1]
            break

    for unit in s_pronoun:
        if pair[1][-1] == unit[0]:
            lemma_prn = unit[1]
            break

    return lemma_antd, lemma_prn



def check_exists (model, word) :
    """If the embedding vector exists in the model or not"""

    try :
        model.get_vector(word)
    except KeyError:
        return 0
    return 1

def compute_similarity (model, word, pronoun) :
    """Compute a similarity for a certain embedding"""

    if check_exists (model, word)  and check_exists (model, pronoun) :
        return round(model.similarity(word,pronoun),3)
    return -2

def _get_number_of_nouns_different_sentences (pair, sentenceBetweenList) :
    """""Get the number of nouns between the mention and pronoun
     when these two are in different sentences"""

    noun_count = 0
    if pair[-1]-pair[-2] >0 :
        start_index=int(pair[0][2])
        end_index=int(pair[1][2])
    else :
        start_index = int(pair[1][2])
        end_index = int(pair[0][2])

    for i,sentence in enumerate(sentenceBetweenList) :
        if i==0 :
            sentence=sentenceBetweenList[i][start_index:]
        elif i==len(sentenceBetweenList)-1 :
            sentence=sentenceBetweenList[i][0:end_index-1]
        for word in sentence :
            if word[3] == "NOUN" or word[3]=="PROPN":
                noun_count += 1
    return noun_count



def get_normalized_distance (pair,s_pronoun) :
    """Normalized distance: if the antecedent and the mention are the same sentence normalize, otherwise 0"""

    if pair[2] == pair[3] :
        distance = abs(int(pair[1][2]) - int(pair[0][2]))
        return round(distance / len(s_pronoun), 3)
    return 0


def get_in_between_number_of_nouns (pair, sentences_list) :

    if pair[-2] == pair[-1] :
        return _get_number_of_nouns_same_sentence (pair, sentences_list[pair[-1]-1])

    if pair[-1]-pair[-2] > 0:
           return _get_number_of_nouns_different_sentences(pair, sentences_list[pair[-2]-1:pair[-1]])

    return _get_number_of_nouns_different_sentences(pair, sentences_list[pair[-1]-1:pair[-2]])


def get_mention_local_score (pair,sentences_list) :

    dict_frequency = get_possible_mention_scores(pair[-1], sentences_list, 10, 10)
    return dict_frequency[pair[0][0]]

def check_exists (model, word) :
     """If the embedding vector exists in the model or not"""
     try :
         model.get_vector(word)
     except KeyError:
         return 0
     return 1


def compute_similarity (model, word, pronoun) :
    """Compute a similarity for a certain embedding"""
    if check_exists (model, word)  and check_exists (model, pronoun) :
         return round(model.similarity(word,pronoun),3)
    return -2

def compute_embeddings_similarity (word,pronoun,dict_features) :

     """Compute the feature embedding similarity for each model in the initialized model list"""
     for name in dict_embeddings_fpaths:
         similarity=compute_similarity(dict_embeddings_models[name],word,pronoun)
         if similarity==-2 :
            dict_features[name]=0
            dict_features_names[name]="numerical"

            dict_features["missing_"+name]=1
            dict_features_names["missing_"+name] = "categorical"

         else :
             dict_features[name]=similarity
             dict_features_names[name] = "numerical"

             dict_features["missing_" + name] = 0
             dict_features_names["missing_" + name] = "categorical"



def get_signature(my_pair):
    """Get the unique signature of a pair"""

    signature = ""
    for item in my_pair[0]:
        signature += item + "#"
    for item in my_pair[1]:
        signature += item + "#"
    signature = signature + str(my_pair[2]) + "#" + str(my_pair[3])
    return signature




def compute_pair_features(pair,s_mention,s_pronoun,dict_features,dict_info,f_corpus_path,sentences_list) :
    """Compute the features for generated mention pairs"""

    index_coreference_pair = os.path.split(f_corpus_path)[1] + "#" + get_signature(pair)
    dict_features[index_coreference_pair] = collections.OrderedDict()

    #Feature
    dict_features[index_coreference_pair]["distance_pronoun_antecedent"]= distance_pronoun_antecedent (pair)
    dict_features_names["distance_pronoun_antecedent"]="categorical"

    #Feature
    dict_features[index_coreference_pair]["number_agreement"]=number_agreement(pair,s_mention,s_pronoun)
    dict_features_names["number_agreement"]="categorical"

    #Feature
    dict_features[index_coreference_pair]["is_noun"]=is_specific_pos (pair,s_mention, "NOUN")
    dict_features_names["is_noun"]="categorical"

    dict_features[index_coreference_pair]["is_proper_noun"] = is_specific_pos(pair, s_mention, "PROPN")
    dict_features_names["is_proper_noun"]="categorical"

    #Feature
    dict_features[index_coreference_pair]["antecedent_position"] = get_position(pair, s_mention)
    dict_features_names["antecedent_position"]="categorical"

    #Feature
    dict_features[index_coreference_pair]["case_antecedent"]= get_case(pair[0][-1],s_mention, dict_info["cases"] )
    dict_features_names["case_antecedent"] = "categorical"

    dict_features[index_coreference_pair]["case_pronoun"] = get_case(pair[1][-1],s_pronoun, dict_info["cases"] )
    dict_features_names["case_pronoun"] = "categorical"

    #Feature
    dict_features[index_coreference_pair]["pos_mention"] = pos_word (s_mention,pair[0][-1],dict_info["tagset"])
    dict_features_names["pos_mention"] = "categorical"

    dict_features[index_coreference_pair]["pos_pronoun"] = pos_word (s_pronoun, pair[1][-1],dict_info["tagset"])
    dict_features_names["pos_pronoun"] = "categorical"

    #Feature
    dict_features[index_coreference_pair]["pos_before_mention_1"] = pos_before(pair[0][-1],s_mention,1,dict_info["tagset"])
    dict_features_names["pos_before_mention_1"] = "categorical"

    dict_features[index_coreference_pair]["pos_before_mention_2"] = pos_before(pair[0][-1], s_mention, 2,dict_info["tagset"])
    dict_features_names["pos_before_mention_2"] = "categorical"

    #Feature
    dict_features[index_coreference_pair]["pos_after_mention_1"] = pos_after(pair[0][-1],s_mention,1,dict_info["tagset"])
    dict_features_names["pos_after_mention_1"] = "categorical"

    dict_features[index_coreference_pair]["pos_after_mention_2"] = pos_after(pair[0][-1], s_mention, 2,dict_info["tagset"])
    dict_features_names["pos_after_mention_2"] = "categorical"

    #Feature
    dict_features[index_coreference_pair]["pos_before_pronoun_1"] = pos_before(pair[1][-1], s_pronoun, 1,dict_info["tagset"])
    dict_features_names["pos_before_pronoun_1"] = "categorical"

    dict_features[index_coreference_pair]["pos_before_pronoun_2"] = pos_before(pair[1][-1], s_pronoun, 2,dict_info["tagset"])
    dict_features_names["pos_before_pronoun_2"] = "categorical"

    #Feature
    dict_features[index_coreference_pair]["pos_after_pronoun_1"] = pos_after(pair[1][-1], s_pronoun, 1,dict_info["tagset"])
    dict_features_names["pos_after_pronoun_1"] = "categorical"

    dict_features[index_coreference_pair]["pos_after_pronoun_2"] = pos_after(pair[1][-1], s_pronoun, 2,dict_info["tagset"])
    dict_features_names["pos_after_pronoun_2"] = "categorical"

    # Feature
    dict_features[index_coreference_pair]["pos_head_mention"] = pos_head(pair[0][-1], s_mention,dict_info["tagset"])
    dict_features_names["pos_head_mention"] = "categorical"

    # Feature
    dict_features[index_coreference_pair]["pos_head_pronoun"] = pos_head(pair[1][-1], s_pronoun, dict_info["tagset"])
    dict_features_names["pos_head_pronoun"] = "categorical"

    #Feature
    dict_features[index_coreference_pair]["syntactic_function_mention"] = get_syntactic_function(s_mention, pair[0][-1], dict_info["syntactic_functions"])
    dict_features_names["syntactic_function_mention"] = "categorical"

    dict_features[index_coreference_pair]["syntactic_function_pronoun"] = get_syntactic_function(s_pronoun, pair[1][-1], dict_info["syntactic_functions"])
    dict_features_names["syntactic_function_pronoun"] = "categorical"

    # Feature
    dict_features[index_coreference_pair]["nouns_between_mentions"] = get_in_between_number_of_nouns(pair, sentences_list)
    dict_features_names["nouns_between_mentions"] = "categorical"

    #Feature
    dict_features[index_coreference_pair]["pronoun_value"] = dict_info["context"][pair[1][0]]['index']
    dict_features_names["pronoun_value"] = "categorical"

    # Feature
    dict_features[index_coreference_pair]["pronoun_sentence_length"] = len(s_pronoun)
    dict_features_names["pronoun_sentence_length"] = "numerical"

    #Feature
    dict_features[index_coreference_pair]["normalized_distance"]=get_normalized_distance(pair,s_pronoun)
    dict_features_names["normalized_distance"] = "numerical"


    #Feature
    dict_features[index_coreference_pair]["mention_local_score"]=get_mention_local_score(pair,sentences_list)
    dict_features_names["mention_local_score"]="numerical"

    #Feature
    compute_embeddings_similarity(pair[0][0], pair[1][0], dict_features[index_coreference_pair])

    #Feature
    dict_features[index_coreference_pair]["eleri_abstractness_score"]=add_eleri_abstractness_level(pair[0][0])
    dict_features_names["eleri_abstractness_score"] = "numerical"

    #Feature
    dict_features[index_coreference_pair]["mention_global_score"]=add_mention_global_score(pair[0][0])
    dict_features_names["mention_global_score"] = "numerical"





