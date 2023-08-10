'''
   API for EstonianCoreferenceSystem (https://github.com/SoimulPatriei/EstonianCoreferenceSystem),
   based on https://github.com/SoimulPatriei/EstonianCoreferenceSystem/blob/7883ac24002fb715d43d9d149ee0340339aeda67/test.py 
   
   Provides:
   * Initialization of required resources, including stanza pipeline for preprocessing and 
     sklearn pipeline for making predictions;
   * Generation of coreference pair candidates and extraction of features for the pairs;
   * End-to-end processing: input raw text and output coreference pairs;
 
   Example usage:

        # Initialize required resources
         dict_background_res, stanza_nlp, model, model_features = \
             initialize_coreference_components(resource_catalog, stanza_models_dir, training_file, train_feature_names_file, 
                                               embedding_locations=embedding_locations)
        
        # Preprocessing: analyse sentences and generate features
        dict_locations, dict_features = generate_features(input_text, dict_background_res, stanza_nlp)
        
        # Predict coreference relations
        results = predict(dict_features, dict_locations, model, model_features)
'''

import os, os.path
import re
import logging
import collections

import stanza
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBClassifier

from estnltk_neural.taggers.coreference.v1 import utilities
from estnltk_neural.taggers.coreference.v1 import generate_pairs
from estnltk_neural.taggers.coreference.v1 import coreference_features

def init_stanza_pipeline(config=None):
    '''Initializes stanza Pipeline based on the given configuration.'''
    if config is None:
        config={'lang':'et'}
    nlp = stanza.Pipeline(**config)
    return nlp

def fit_model(f_feature_names, f_training_file):
    '''Fits coreference prediction model based on given feature_names and training_file.
       Returns (sklearn.pipeline.Pipeline, pipeline_features).
    '''
    dict_feature_type = utilities.get_feature_type(f_feature_names)
    categorical_features = [feature for feature in dict_feature_type if dict_feature_type[feature] == 'categorical']
    ct = ColumnTransformer([('one_hot_encoder', OneHotEncoder(categories='auto',handle_unknown='ignore'), categorical_features)],remainder = 'passthrough')
    pipeline = Pipeline(steps=[('t', ct), ('m', XGBClassifier())])
    X_train, y_train, features = utilities.getXy(f_training_file)
    pipeline.fit(X_train, y_train)
    return pipeline, features

def initialize_coreference_components(resources_root_dir, resource_catalog, stanza_models_dir, training_file, train_feature_names_file, 
                                      logger=None, embedding_locations=None, stanza_use_gpu=None):
    '''Initializes all resources/components required by Estonian Coreference System.'''
    if logger is None:
        # use the default logger
        logger = logging
    # Initialize required resources
    logger.info(f"""test::Initializing resources""")
    dict_catalog = utilities.read_resource_catalog( resource_catalog, f_root_dir=resources_root_dir )
    logger.info(f"""test::Read Resource Catalog from=>{resource_catalog}""")
    
    coreference_features.get_mention_global_scores(dict_catalog["global_mention_scores"])
    logger.info(f"""test::Read the global mention scores from=>{dict_catalog["global_mention_scores"]}""")
    coreference_features.get_eleri_abstractness(dict_catalog["eleri_abstractness"])
    logger.info(f"""test::Read Eleri Aedmaa abstractness scores from=> {dict_catalog["eleri_abstractness"]}""")
    if embedding_locations is None:
        # Load embeddings based on XML configuration file
        coreference_features.init_embedding_models(dict_catalog["embeddings_file"], logger, 
                                                   f_root_dir=resources_root_dir )
        logger.info(f"""test::Inited the embedding models from=> {dict_catalog["embeddings_file"]}""")
    else:
        # Load embeddings based on given dictionary
        assert 'tkachenko_embedding' in embedding_locations.keys(), \
            f'(!) Name "tkachenko_embedding" is missing from {embedding_locations.keys()!r}'
        coreference_features.init_embedding_models_based_on_dict(embedding_locations, logger)
        logger.info(f"""test::Inited the embedding models from=> {list(embedding_locations.keys())}""")
    # Fit model
    logger.info(f"""test::Fitting model based on=> {training_file}""")
    model, model_features = fit_model(train_feature_names_file, training_file)
    # Initialize background resources (required for feature extraction)
    dict_background_res = { 
        "context": utilities.read_context_file(dict_catalog["sentence_context_file"]),
        "tagset": utilities.read_configuration_file(dict_catalog["tagset_file"], "pos"),
        "cases": utilities.read_configuration_file(dict_catalog["cases_file"], "case"),
        "syntactic_functions": utilities.read_syntactic_file(dict_catalog["syntactic_function_file"], "syntactic_function"),
        "exclude_list" : utilities.read_exclude_words(dict_catalog["mention_info"]) }
    logger.info(f"""test::Initialized background resources""")
    # Initialize stanza pipeline
    if stanza_models_dir is not None:
        stanza_config = {'processors': 'tokenize,pos,lemma,depparse', 
                         'model_dir': stanza_models_dir, 
                         'download_method': None, 
                         'use_gpu': stanza_use_gpu,
                         'lang': 'et'}
    else:
        stanza_config = None
    stanza_nlp = init_stanza_pipeline(config=stanza_config)
    logger.info(f"""test::Initialized stanza nlp pipeline""")
    return dict_background_res, stanza_nlp, model, model_features

def compute_mentions(nlp,input_text,pronoun_list,exclude_list):
    '''Applies stanza nlp on input_text and returns resulting stanza Document.
       Marks pronouns and candidate mentions.'''
    assert isinstance(nlp, stanza.Pipeline)
    doc = nlp(input_text)
    for sentence in doc.sentences:
        for word in sentence.words:
            if utilities.is_pronoun(word,pronoun_list) :
                word.misc="Mention=Yes"
            elif utilities.is_candidate_mention(word,exclude_list) :
                word.misc="Mention=Yes"
    return doc

def add_mentions(pronoun_list,input_text,exlcude_list,stanza_nlp):
    '''Applies stanza nlp on input_text and returns list of resulting conllu sentences. 
       Each sentence is a list of tokens, and each token is a list of conllu field values 
       (parsing results of the token). 
       Marks pronouns and candidate mentions on tokens' 'misc' fields.'''
    tagged_corpus_list=[]
    doc=compute_mentions(stanza_nlp,input_text,pronoun_list,exlcude_list)
    #
    # The following code is replacement for deprecated "stanza.utils.conll.CoNLL.convert_dict( doc.to_dict() )"
    # https://github.com/stanfordnlp/stanza/blob/7bf81ea7a6802a73332e952590ad0558629c7bfc/stanza/utils/conll.py#L125-L128
    # https://github.com/stanfordnlp/stanza/blob/7bf81ea7a6802a73332e952590ad0558629c7bfc/stanza/utils/conll.py#L164-L171
    #
    doc_conll = []
    for sentence in doc.sentences:
        sent_conll = []
        for token in sentence.tokens:
            sent_conll.extend(token.to_conll_text().split("\n"))
        doc_conll.append(sent_conll)
    doc_conll = [[x.split("\t") for x in sentence] for sentence in doc_conll]
    return doc_conll

def generate_features(input_text, dict_background_res, stanza_nlp):
    '''Preprocesses input_text and generates all possible coreference pairs along with their features.
       Returns (dict_locations, dict_features):
       * dict_locations -- mapping from coreference pair index to dict of span locations (with keys 'MENTION' & 'PRON');
       * dict_features -- mapping from coreference pair index to corresponding sklearn model features;
    '''
    # Validate that all necessary background resources exist
    for res_key in ["context", "tagset", "cases", "syntactic_functions", "exclude_list"]:
        assert res_key in dict_background_res.keys(), \
            f'(!) Missing background resource {res_key!r} in {dict_background_res.keys()!r}'
    # Apply stanza nlp on text and extract potential mentions/pronouns
    sentences_list = add_mentions(dict_background_res["context"].keys(), input_text, dict_background_res["exclude_list"], stanza_nlp)
    # Generate features for mentions; also detect feature locations
    dict_features, dict_locations = generate_pairs.pronominal_coreference_candidate_pairs_with_locations(dict_background_res,sentences_list,'test_input.txt')
    # Validate
    assert list(dict_locations.keys()) == list(dict_features.keys())
    return dict_locations, dict_features

_start_char_pat = re.compile('start_char=(\d+)')
_end_char_pat = re.compile('end_char=(\d+)')

def extract_span_location(misc_value):
    '''Extracts start,end span locations from conllu 'misc' value.'''
    start, end = None, None
    start_m = _start_char_pat.search(misc_value)
    end_m = _end_char_pat.search(misc_value)
    if start_m:
        start = int(start_m.group(1))
    if end_m:
        end = int(end_m.group(1))
    return start, end

def predict(dict_features, dict_locations, model, model_features, verbose=False):
    '''Applies given model (with model_features) on coreference pair candidates 
       (dict_features) and predicts, which candidates should give a rise to actual 
       coreference relations.
       Returns list of coreference relations, where each relation is a dict 
       defining location of 'pronoun' and 'mention'.
    '''
    assert model_features[-1] == 'category'
    results = []
    # Reformat input features as a Dataframe
    X_test_dict = {}
    for i, coreference_pair in enumerate( dict_features.keys() ):
        values = []
        for feature in model_features[:-1]:
            if feature not in X_test_dict:
                X_test_dict[feature] = []
            feature_value = dict_features[coreference_pair][feature]
            if isinstance(feature_value, str):
                # !! Superimportant: numeric features need converting: str -> int, float !!
                if feature in ['eleri_abstractness_score', 'tkachenko_embedding']:
                    feature_value = float(feature_value)
                else:
                    assert re.match('^-?[0-9]+$', feature_value)
                    feature_value = int(feature_value)
            X_test_dict[feature].append( feature_value )
            values.append( feature_value )
    X_test = pd.DataFrame( X_test_dict, columns=model_features[:-1] )
    if len(X_test) > 0:
        # Apply model
        #y_pred = model.predict_proba(X_test)
        y_pred = model.predict(X_test)
        #print(y_pred)
        # Extract results
        for i, coreference_pair in enumerate( dict_features.keys() ):
            if y_pred[i]:
                mention_loc = extract_span_location(dict_locations[coreference_pair]['MENTION'])
                pronoun_loc = extract_span_location(dict_locations[coreference_pair]['PRON'])
                if verbose:
                    print(coreference_pair, f'mention: {mention_loc}', f'pronoun: {pronoun_loc}')
                results.append( {'pronoun': pronoun_loc, 'mention': mention_loc})
    return results


