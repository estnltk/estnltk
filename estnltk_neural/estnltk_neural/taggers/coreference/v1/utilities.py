"""
 This module contains utility functions mostly related to the file processing.

 The source code is from Eduard Barbu's original "utilities.py" 
 module in EstonianCoreferenceSystem (v1.0.0):
  https://github.com/SoimulPatriei/EstonianCoreferenceSystem/blob/7883ac24002fb715d43d9d149ee0340339aeda67/utilities.py
 
 Minor modifications have been made by Siim Orasmaa.
"""

import fnmatch
import os
import xml.dom.minidom
import numpy as np
import pandas as pd
import stanza


def get_feature_type (f_feature_names) :
    """Get the type of features in a dict"""

    dict_feature_type ={}

    fi = open(f_feature_names, mode='r', encoding='utf-8')
    for line in fi :
        line = line.rstrip()
        f_name, f_type = line.split("\t")
        dict_feature_type[f_name]=f_type
    fi.close()

    return dict_feature_type


def getXy (f_model) :
  """Get X and y"""

  df = pd.read_csv(f_model)
  features = df.columns
  X = df[features[:-1]]
  y = np.array(df['category'])

  return X,y,features

def get_X (f_model,features) :

  df = pd.read_csv(f_model)
  X = df[features[:-1]]
  return X


def gen_find(filepat, directory):
    for path, dirlist, filelist in os.walk(directory):
        for name in fnmatch.filter(filelist, filepat):
            yield os.path.join(path, name)

def read_corpus (corpus_dir,extension) :
    """Read the corpus and return the name of the corpus files"""

    corpus_file_list=[]
    for file_path in gen_find(extension, corpus_dir):
        corpus_file_list.append(file_path)
    return corpus_file_list

def read_resource_catalog (f_catalog) :
    """Read the name of the files from the catalog"""

    doc = xml.dom.minidom.parse(f_catalog)
    dict_catalog = {
                    "tagset_file":doc.getElementsByTagName("tagset")[0].childNodes[0].data,
                    "syntactic_function_file":doc.getElementsByTagName("syntactic_function")[0].childNodes[0].data,
                    "cases_file":doc.getElementsByTagName("cases")[0].childNodes[0].data,
                    "embeddings_file":doc.getElementsByTagName("embeddings")[0].childNodes[0].data,
                    "sentence_context_file":doc.getElementsByTagName("sentence_context")[0].childNodes[0].data,
                    "global_mention_scores":doc.getElementsByTagName("global_mention_scores")[0].childNodes[0].data,
                    "eleri_abstractness": doc.getElementsByTagName("eleri_abstractness")[0].childNodes[0].data,
                    "mention_info": doc.getElementsByTagName("mention_info")[0].childNodes[0].data,
    }
    return dict_catalog

def read_context_file (f_context) :
    """Read the context file containing the context for each pronoun"""

    dict_context={}
    doc = xml.dom.minidom.parse(f_context)
    pronouns = doc.getElementsByTagName("pronoun")
    for pronoun in pronouns :
        literal= pronoun.getElementsByTagName("literal")[0].childNodes[0].data
        index= pronoun.getElementsByTagName("index")[0].childNodes[0].data
        context_before= pronoun.getElementsByTagName("sentences_before")[0].childNodes[0].data
        context_after = pronoun.getElementsByTagName("sentences_after")[0].childNodes[0].data
        before=pronoun.getElementsByTagName("cataphora")[0].childNodes[0].data

        dict_context[literal]={"index":index,
                               "sentences_before": int(context_before),
                               "sentences_after": int(context_after),
                               "cataphora": int(before)}

    return dict_context

def read_configuration_file (f_configuration,tag) :


    dict_configuration ={}
    doc = xml.dom.minidom.parse(f_configuration)
    elements = doc.getElementsByTagName(tag)
    for element in elements :
        name = element.getElementsByTagName("name")[0].childNodes[0].data
        number = element.getElementsByTagName("number")[0].childNodes[0].data
        dict_configuration[name]=number
    return dict_configuration



def read_syntactic_file (f_configuration,tag) :

    dict_configuration ={}
    doc = xml.dom.minidom.parse(f_configuration)
    elements = doc.getElementsByTagName(tag)
    for element in elements :
        name = element.getElementsByTagName("name")[0].childNodes[0].data
        number = element.getElementsByTagName("number")[0].childNodes[0].data
        keep = element.getElementsByTagName("keep")[0].childNodes[0].data
        dict_configuration[name]={}
        dict_configuration[name]["number"] =number
        dict_configuration[name]["keep"] = keep

    return dict_configuration


def read_exclude_words (f_words) :
    """Get the words to exclude from the computation of mentions"""

    exclude_list =[]
    fi = open(f_words, mode='r', encoding='utf-8')
    for line in fi:
        line = line.rstrip()
        exclude_list.append(line)
    fi.close()
    return exclude_list


def generate_scikit_learn_antet (dict_features_names,sklearn_file,training=0) :
    """Generate the header of the scikit-learn file"""

    fo = open(sklearn_file, mode='w', encoding='utf-8')
    features_string=""
    for feature in dict_features_names:
        features_string+=feature+","
    sir=features_string[:-1]
    if training :
        sir+=",category"
    fo.write(sir+"\n")
    fo.close()


def append_scikit_learn_file(dict_features,sklearn_file) :
    """Generate scikit-learn file"""

    fo = open(sklearn_file, mode='a', encoding='utf-8')
    for index in dict_features:
        values=""
        for feature, value in dict_features[index].items() :
            values+= str(value)+","
        fo.write(values[:-1]+"\n")

    fo.close()


def get_text (f_path) :

    line_file_list=[]
    fi = open(f_path, mode='r', encoding='utf-8')
    for line in fi :
        line_file_list.append(line)
    fi.close()

    return line_file_list


def deserialize_file (f_corpus):
    """Deserialize the file containing the annotated coreference"""

    conll, doc_comments = stanza.utils.conll.CoNLL.load_conll(get_text (f_corpus))
    return conll

def serialize_text (doc,f_output) :
    """Serialize the text to a file"""

    conll = stanza.utils.conll.CoNLL.convert_dict(doc.to_dict())
    fo = open(f_output, mode='w', encoding='utf-8')
    for my_sentence_list in conll :
        for my_word_unit in my_sentence_list:
            sir= "\t".join(my_word_unit)
            fo.write(sir+"\n")
        fo.write("\n")
    fo.close()


def is_pronoun (word, pronoun_list) :
    if word.lemma.lower() in pronoun_list :
        return True
    return False


def is_candidate_mention (word,exclude_list) :

    if word.pos in ['NOUN','PROPN', 'PRON'] and word.deprel!="flat" :
        if word.lemma.lower() in exclude_list :
            return False
        return True
    return False

def compute_mentions (nlp,f_path,pronoun_list,exclude_list) :

    f_text="".join(get_text (f_path))
    doc = nlp(f_text)
    for sentence in doc.sentences :
        for word in sentence.words :
            if is_pronoun(word,pronoun_list) :
                word.misc="Mention=Yes"
            elif is_candidate_mention(word,exclude_list) :
                word.misc = "Mention=Yes"
    return doc

def init_estonian_pipeline (config=None) :
    if config is None:
        config={'lang':'et'}
    nlp = stanza.Pipeline(**config)
    return nlp


def get_feature_type (f_feature_names) :
    """Get the type of features in a dict"""

    dict_feature_type ={}

    fi = open(f_feature_names, mode='r', encoding='utf-8')
    for line in fi :
        line = line.rstrip()
        f_name, f_type = line.split("\t")
        dict_feature_type[f_name]=f_type
    fi.close()

    return dict_feature_type
