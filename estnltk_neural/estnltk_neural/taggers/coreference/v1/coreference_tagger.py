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
    missing, raises ModuleNotFoundError informing about missing packages.
    '''
    missing_libraries = []
    for tagger_dependency in ['stanza', 'sklearn', 'xgboost', 'gensim', 'pandas']:
        pkg_exists = pkgutil.find_loader(tagger_dependency) is not None
        if not pkg_exists:
            if tagger_dependency == 'sklearn':
                tagger_dependency = 'scikit-learn'
            missing_libraries.append( tagger_dependency )
    if missing_libraries:
        missing_libraries_str = ', '.join(missing_libraries)
        sg_plur_package = 'packages' if len(missing_libraries)>1 else 'package'
        sg_plur_is = 'are' if len(missing_libraries)>1 else 'is'
        raise ModuleNotFoundError(f'Missing {sg_plur_package} {missing_libraries_str} '+\
                f'that {sg_plur_is} required for using the tagger. Please install the '+\
                f'{sg_plur_package} module via conda or pip.')
    return

def check_configuration_dir(configuration_dir):
    '''
    Check that the configuration directory exists and contains required file(s).
    Raises FileNotFoundError in case of a missing file.
    '''
    if not os.path.exists(configuration_dir):
        raise FileNotFoundError(f'Configuration directory {configuration_dir!r} '+\
                                 'is missing or invalid.')
    catalog_file = \
        os.path.join(configuration_dir, 'estonian_catalog.xml')
    if not os.path.exists(catalog_file):
        raise FileNotFoundError('Configuration directory is missing '+\
                                'file "estonian_catalog.xml".')
    return

def check_resources_dir(resources_dir):
    '''
    Check that the resources directory exists and contains required file(s).
    Raises FileNotFoundError in case of a missing file.
    '''
    if not os.path.exists(resources_dir):
        raise FileNotFoundError(f'Resources directory {resources_dir!r} '+\
                                 'is missing or invalid.')
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
    Check that the stanza models directory exists and contains required file(s).
    Raises FileNotFoundError in case of a missing file.
    '''
    if not os.path.exists(stanza_models_dir):
        raise FileNotFoundError(f'Stanza models directory {stanza_models_dir!r} '+\
                                 'is missing or invalid.')
    resources_file = os.path.join(stanza_models_dir, 'resources.json')
    if not os.path.exists(resources_file):
        raise FileNotFoundError('Stanza models directory is missing '+\
                                f'file {resources_file!r}.')
    et_directory = os.path.join(stanza_models_dir, 'et')
    if not os.path.exists(et_directory) and os.path.isdir(et_directory):
        raise FileNotFoundError('Stanza models directory is missing '+\
                                f'sub directory {et_directory!r}.')
    return



class CoreferenceTagger(RelationTagger):
    '''Tags pronoun-mention coreference pairs in texts.
       
       Uses EstonianCoreferenceSystem v1.0.0 created by Eduard Barbu. 
       The system detects coreference of personal pronouns ("mina", "sina", 
       "tema"), relative pronouns "kes" and "mis", and the demonstrative 
       pronoun "see".
       
       Warning: the current version of the tagger is not thread safe.
       
       Uses stanza 'et' models for pre-processing of the input text.
    '''
    conf_param = ['add_chain_ids',
                  'stanza_nlp', 
                  'coref_model',
                  '_dict_background_res',
                  '_model_features',
                  '_generate_features',
                  '_predict']
    
    def __init__(self, output_layer='coreference', resources_dir=None, stanza_models_dir=None, 
                       ner_layer=None, add_chain_ids=True, logger=None):
        """Initializes pronominal coreference relation tagger.
        
        Parameters
        ----------
        output_layer: str (default: 'coreference')
            Name of the output layer.
        
        resources_dir: str (default: None)
            Root directory containing configuration files and resources required by 
            the tagger. Should contain sub directories 'estonian_configuration_files' 
            and 'estonian_resources'. If not provided, then attempts to download 
            resources automatically from EstNLTK's resources repository.
        
        stanza_models_dir: str (default: None)
            Root directory of stanza models to be used for preprocessing. Should 
            contain sub directory "et" and the index file "resources.json". If not 
            provided, then attempts to download resources automatically via stanza's 
            resource downloader.

        ner_layer: str (default: None)
            Name of the named entity layer. If provided, then expands proper noun 
            mentions detected by coreference system to full extend named entity 
            phrases. Otherwise (default), mentions of names are detected only as 
            1-word phrases.

        add_chain_ids: bool (default: True)
            If set (default), then detects chains among coreference pairs, and 
            assigns a "chain_id" (integer starting from 0) to each relation. 
        
        logger (default: None)
            
        """
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
        if resources_root_dir is None:
            # Attempt to download resources dir automagically
            resources_root_dir = \
                get_resource_paths("coreference_v1", only_latest=True, 
                                                     download_missing=True)
        # Check root directory
        if resources_root_dir is not None:
            if not os.path.exists(resources_root_dir):
                raise FileNotFoundError('Bad or missing coreference resources directory '+\
                                        f'{resources_root_dir!r}.')
        else:
            raise Exception(f'Models of {self.__class__.__name__} are missing. '+\
                             'Please use estnltk.download("coreference_v1") to download the models.')
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
        # Assumes embeddings file at location:
        #  'RESOURCES_ROOT_DIR/estonian_resources/estonian_embeddings/lemmas.cbow.s100.w2v.bin'
        embedding_locations = None
        # Make an internal import to avoid explicit dependencies
        from estnltk_neural.taggers.coreference.v1.coreference_api import initialize_coreference_components
        from estnltk_neural.taggers.coreference.v1.coreference_api import generate_features
        from estnltk_neural.taggers.coreference.v1.coreference_api import predict
        self._generate_features = generate_features
        self._predict = predict
        # Initialize required resources & components
        dict_background_res, stanza_nlp, model, model_features = \
            initialize_coreference_components(resources_root_dir,
                                              resource_catalog, 
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


