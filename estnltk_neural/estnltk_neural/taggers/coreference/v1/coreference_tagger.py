import os, os.path
import networkx
import pkgutil

from estnltk_core import RelationLayer, Relation
from estnltk_core.taggers import RelationTagger

from estnltk.downloader import get_resource_paths

def check_tagger_dependencies():
    '''
    Checks if all required packages ('stanza', 'scikit-learn', 'xgboost', 
    'gensim', 'pandas') have been installed. If any of the packages is 
    missing, raises ModuleNotFoundError informing about the missing package.
    '''
    for tagger_dependency in ['stanza', 'sklearn', 'xgboost', 'gensim', 'pandas']:
        pkg_exists = pkgutil.find_loader(tagger_dependency) is not None
        if not pkg_exists:
            if tagger_dependency == 'sklearn':
                tagger_dependency = 'scikit-learn'
            raise ModuleNotFoundError(f'Missing {tagger_dependency} package '+\
              'that is required for using the tagger. Please install the '+\
              f'package module via conda or pip, e.g.\n pip install {tagger_dependency}')
    return

def check_configuration_dir(configuration_dir):
    '''
    Check that the configuration directory contains required file(s).
    Raises FileNotFoundError in case of a missing file.
    '''
    catalog_file = \
        os.path.join(configuration_dir, 'estonian_catalog.xml')
    if not os.path.exists(catalog_file):
        raise FileNotFoundError('Configuration directory is missing '+\
                                'file "estonian_catalog.xml".')
    return

def check_resources_dir(resources_dir):
    '''
    Check that the resources directory contains required file(s).
    Raises FileNotFoundError in case of a missing file.
    '''
    training_data_dir = \
        os.path.join(resources_dir, 'estonian_training_data_preprocessed')
    if not os.path.exists(training_data_dir):
        raise FileNotFoundError('Resources directory is missing '+\
                                'sub directory "estonian_training_data_preprocessed".')
    train_feature_names_file = \
        os.path.join(training_data_dir, 'estonian-computed-features.txt')
    if not os.path.exists(train_feature_names_file):
        raise FileNotFoundError('Resources directory is missing '+\
                                f'file {train_feature_names_file!r}.')
    train_data_file = \
        os.path.join(training_data_dir, 'estonian_training_corpus-sklearn.txt')
    if not os.path.exists(train_data_file):
        raise FileNotFoundError('Resources directory is missing '+\
                                f'file {train_data_file!r}.')
    return

def check_stanza_models_dir(stanza_models_dir):
    '''
    Check that the stanza models directory contains required file(s).
    Raises FileNotFoundError in case of a missing file.
    '''
    resources_file = os.path.join(stanza_models_dir, 'resources.json')
    if not os.path.exists(resources_file):
        raise FileNotFoundError('Stanza models directory is missing '+\
                                f'file {resources_file!r}.')
    et_directory = os.path.join(stanza_models_dir, 'et')
    if not os.path.exists(et_directory) and os.path.isdir(et_directory):
        raise FileNotFoundError('Stanza models directory is missing '+\
                                f'sub directory {et_directory!r}.')
    return



class CoreferenceRelationTagger(RelationTagger):
    '''Tags pronoun-mention coreference pairs in texts.
       Uses EstonianCoreferenceSystem v1.0.0 by Eduard Barbu.
       Relies on stanza based pre-processing of the input text.'''
    conf_param = ['add_chain_ids',
                  'stanza_nlp', 
                  'coref_model',
                  '_dict_background_res',
                  '_model_features',
                  '_generate_features',
                  '_predict']
    
    def __init__(self, resources_dir=None, stanza_models_dir=None, download_embeddings=False, 
                       output_layer='coreference', ner_layer=None, add_chain_ids=True, 
                       logger=None):
        self.output_layer = output_layer
        self.input_layers = ()
        if ner_layer is not None:
            self.input_layers += (ner_layer,)
        self.output_span_names = ('pronoun', 'mention')
        self.output_attributes = ()
        if add_chain_ids:
            self.output_attributes += ('chain_id',)
        self.add_chain_ids = add_chain_ids
        # Check that tagger dependency packages exist
        check_tagger_dependencies()
        resources_root_dir = resources_dir
        # TODO: download resources dir automagically (!)
        # Check root directory
        if resources_root_dir is not None:
            if not os.path.exists(resources_root_dir):
                raise FileNotFoundError('Bad or missing coreference resources directory '+\
                                        f'{resources_root_dir!r}.')
        else:
            raise Exception(f'Models of {self.__class__.__name__} are missing. '+\
                            'Please use estnltk.download("TODO") to download the models.')
        # Construct sub directories
        configuration_dir = \
            os.path.join(resources_root_dir, 'estonian_configuration_files')
        resources_dir = \
            os.path.join(resources_root_dir, 'estonian_resources')
        # Check configuration directory
        check_configuration_dir(configuration_dir)
        resource_catalog = os.path.join(configuration_dir, 'estonian_catalog.xml')
        # Check resources directory
        check_resources_dir(resources_dir)
        training_data_dir = \
            os.path.join(resources_dir, 'estonian_training_data_preprocessed')
        train_feature_names_file = \
            os.path.join(training_data_dir, 'estonian-computed-features.txt')
        training_file = \
            os.path.join(training_data_dir, 'estonian_training_corpus-sklearn.txt')
        # Check stanza models dir
        # (note: if not provided, stanza will attempt to download resources automagically)
        if stanza_models_dir is not None:
            check_stanza_models_dir(stanza_models_dir)
        # Download embeddings via estnltk (if required)
        # Otherwise, assumes embeddings file location:
        # 'RESOURCES_ROOT_DIR/estonian_resources/estonian_embeddings/lemmas.cbow.s100.w2v.bin'
        embedding_locations = None
        if download_embeddings:
            embeddings_path = \
                get_resource_paths("word2vec_lemmas_cbow_s100_2015-06-21", only_latest=True, download_missing=True)
            if embeddings_path is None:
                raise Exception('Word2Vec embeddings file required for preprocessing is missing. '+\
                                'Please use estnltk.download("word2vec_lemmas_cbow_s100_2015-06-21") '+\
                                'to download the models.')
            embedding_locations = {'tkachenko_embedding': embeddings_path}
        # Make an internal import to avoid explicit dependencies
        from estnltk_neural.taggers.coreference.v1.coreference_api import initialize_coreference_components
        from estnltk_neural.taggers.coreference.v1.coreference_api import generate_features
        from estnltk_neural.taggers.coreference.v1.coreference_api import predict
        self._generate_features = generate_features
        self._predict = predict
        # Initialize required resources & components
        dict_background_res, stanza_nlp, model, model_features = \
            initialize_coreference_components(resource_catalog, 
                                              stanza_models_dir, 
                                              training_file, 
                                              train_feature_names_file, 
                                              embedding_locations=embedding_locations,
                                              logger=logger)
        self.stanza_nlp = stanza_nlp
        self._dict_background_res = dict_background_res
        self.coref_model = model
        self._model_features = model_features

    def _make_layer_template(self) -> RelationLayer:
        return RelationLayer(self.output_layer, self.output_span_names, self.output_attributes)

    def _make_layer(self, text, layers, status=None) -> RelationLayer:
        layer = self._make_layer_template()
        layer.text_object = text
        # Preprocessing: analyse sentences with stanza and generate features
        dict_locations, dict_features = self._generate_features(text.text, 
                                                                self._dict_background_res, 
                                                                self.stanza_nlp)
        # Predict coreference relations
        results = self._predict(dict_features, dict_locations, 
                                self.coref_model, self._model_features)
        # Postprocess: add chain id-s
        if self.add_chain_ids:
            add_coreference_chain_ids(results)
        # Postprocess: expand mentions to named entity boundaries
        if len(self.input_layers) > 0:
            ner_layer = layers[self.input_layers[0]]
            expand_mentions_to_named_entities(results, ner_layer)
        # Format results as a layer
        for relation in results:
            layer.add_annotation( **relation )
        return layer


def expand_mentions_to_named_entities(relations, ner_layer):
    '''Expands mentions (in results) to full extend named entity phrases,
       using the phrases from given ner_layer.'''
    for relation in relations:
        mention_start = relation['mention'][0]
        mention_end   = relation['mention'][1]
        for ner_phrase in ner_layer:
            # Check that mention falls into NER phrase
            if ner_phrase.start <= mention_start and \
               mention_end <= ner_phrase.end:
                # Check that mention is shorter than the NER phrase
                if mention_end-mention_start<ner_phrase.end-ner_phrase.start:
                    # Update mention location from NER phrase
                    relation['mention'] = (ner_phrase.start, ner_phrase.end)
                    break
    return relations


def add_coreference_chain_ids(results):
    '''Expands coreference pairs (in results) to coreference chains.
       Adds corresponding chain_id-s to each relation in results.'''
    G = networkx.Graph()
    for relation_id, res in enumerate(results):
        mention = str(res['mention'])
        pronoun = str(res['pronoun'])
        G.add_edge(mention, pronoun, relation_id=relation_id)
    component_id = 0
    for node_set in networkx.connected_components(G):
        for node in node_set:
            for nbr, datadict in G.adj[node].items():
                relation_id = datadict['relation_id']
                results[relation_id]['chain_id'] = component_id
        component_id += 1
    return results


