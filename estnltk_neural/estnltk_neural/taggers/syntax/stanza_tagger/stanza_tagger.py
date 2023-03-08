import os
from collections import OrderedDict
from random import Random

from estnltk import Layer
from estnltk.taggers.standard.syntax.syntax_dependency_retagger import SyntaxDependencyRetagger
from estnltk.taggers.standard.syntax.ud_validation.deprel_agreement_retagger import DeprelAgreementRetagger
from estnltk.taggers.standard.syntax.ud_validation.ud_validation_retagger import UDValidationRetagger
from estnltk.taggers import Tagger
from estnltk.converters.serialisation_modules import syntax_v0
from estnltk.downloader import get_resource_paths


class StanzaSyntaxTagger(Tagger):
    """
    Tags dependency syntactic analysis with Stanza.
    The tagger assumes that the segmentation to sentences and words is completed before. Morphological analysis
    can be used, too.

    The tagger assumes that morph analysis is completed with VabaMorf module and follows EstMorph tagset.
    For using extended analysis, basic morph analysis layer must first exist.

    The tagger creates a syntax layer that features Universal Dependencies dependency-tags in attribute 'deprel'.
    When using only sentences for prediction, features and UPOS-tags from UD-tagset are used and displayed.
    Otherwise UPOS is the same as VabaMorf's part of speech tag and feats is based on VabaMorf's forms.

    An optional input_type flag allows choosing layer type to use as the base of prediction. Default is 'morph_analysis',
    which expects 'morph_analysis' as input. Values 'morph_extended' and 'sentences' can also be chosen. When using
    one of the morphological layers, the name of the morphological layer to use must be declared in input_morph_layer
    parameter (default 'morph_analysis'). Possible configurations (with default layer names):
        1) input_type='sentences', input_morph_layer=None;
           uses only 'sentences' from estnltk, and the lingustic processing is done with stanza's models;
           (value of input_morph_layer is irrelevant)
        
        2) input_type='morph_analysis', input_morph_layer='morph_analysis';
           uses a model trained on Vabamorf's layer ('morph_analysis'); input_morph_layer 
           must point to the name of the Vabamorf's layer;
           
        3) input_type='morph_extended', input_morph_layer='morph_extended';
           uses a model trained on the extended Vabamorf's layer ('morph_extended'); input_morph_layer 
           must point to the name of the layer;

    Names of layers to use can be changed using parameters sentences_layer, words_layer and input_morph_layer,
    if needed. To use GPU for parsing, parameter use_gpu must be set to True. 
    Parameter add_parents_and_children adds attributes that contain the parent and children of a word. 
    
    The input morph analysis layer can be ambiguous. In that case, StanzaSyntaxTagger picks randomly one 
    morph analysis for each ambiguous word, and predicts from "unambiguous" input. 
    Important: as a result, by default, the output will not be deterministic: for ambiguous words, you will 
    get different 'lemma', 'upostag', 'xpostag', 'feats' values on each run, and this also affects the results 
    of dependency parsing. 
    How to make the output deterministic: you can pass a seed value for the random generator via constructor 
    parameter random_pick_seed (int, default value: None). Note that the seed value is fixed once at creating 
    a new instance of StanzaSyntaxTagger, and you only get deterministic / repeatable results if you tag texts 
    in exactly the same order.
    Note: if you want to get the same deterministic output as in previous versions of the tagger, use 
    random_pick_seed=4.
    
    Tutorial:
    https://github.com/estnltk/estnltk/blob/main/tutorials/nlp_pipeline/C_syntax/03_syntactic_analysis_with_stanza.ipynb
    """

    conf_param = ['model_path', 'add_parent_and_children', 'syntax_dependency_retagger',
                  'input_type', 'dir', 'mark_syntax_error', 'mark_agreement_error', 'agreement_error_retagger',
                  'ud_validation_retagger', 'nlp', 'use_gpu', 'gpu_max_words_in_sentence', 'random_pick_seed', 
                  '_random']

    def __init__(self,
                 output_layer='stanza_syntax',
                 sentences_layer='sentences',
                 words_layer='words',
                 input_morph_layer='morph_analysis',
                 input_type='morph_analysis',  # or 'morph_extended', 'sentences'
                 random_pick_seed=None,
                 add_parent_and_children=False,
                 depparse_path=None,
                 resources_path=None,
                 mark_syntax_error=False,
                 mark_agreement_error=False,
                 use_gpu=False,
                 gpu_max_words_in_sentence=1000
                 ):
        # Make an internal import to avoid explicit stanza dependency
        import stanza

        self.add_parent_and_children = add_parent_and_children
        self.mark_syntax_error = mark_syntax_error
        self.mark_agreement_error = mark_agreement_error
        self.output_layer = output_layer
        self.output_attributes = ('id', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps', 'misc')
        self.input_type = input_type
        self.use_gpu = use_gpu
        self.random_pick_seed = random_pick_seed
        self._random = Random()
        if isinstance(self.random_pick_seed, int):
            self._random.seed(self.random_pick_seed)

        # We may run into "CUDA out of memory" error when processing very long sentences 
        # with GPU.
        # Set a reasonable default for max sentence length: if that gets exceeded, then a 
        # guarding exception will be thrown
        self.gpu_max_words_in_sentence = gpu_max_words_in_sentence

        if not resources_path:
            # Try to get the resources path for stanzasyntaxtagger. Attempt to download resources, if missing
            self.dir = get_resource_paths("stanzasyntaxtagger", only_latest=True, download_missing=True)
        else:
            self.dir = resources_path
        # Check that resources path has been set
        if self.dir is None:
            raise Exception('Models of StanzaSyntaxTagger are missing. '+\
                            'Please use estnltk.download("stanzasyntaxtagger") to download the models.')

        self.syntax_dependency_retagger = None
        if add_parent_and_children:
            self.syntax_dependency_retagger = SyntaxDependencyRetagger(conll_syntax_layer=output_layer)
            self.output_attributes += ('parent_span', 'children')

        self.ud_validation_retagger = None
        if mark_syntax_error:
            self.ud_validation_retagger = UDValidationRetagger(output_layer=output_layer)
            self.output_attributes += ('syntax_error', 'error_message')

        self.agreement_error_retagger = None
        if mark_agreement_error:
            if not add_parent_and_children:
                raise ValueError('`add_parent_and_children` must be True for marking agreement errors.')
            else:
                self.agreement_error_retagger = DeprelAgreementRetagger(output_layer=output_layer)
                self.output_attributes += ('agreement_deprel',)

        if self.input_type not in ['sentences', 'morph_analysis', 'morph_extended']:
            raise ValueError('Invalid input type {}'.format(input_type))

        # Check for illegal parameter combinations (mismatching input type and layer):
        if input_type=='morph_analysis' and input_morph_layer=='morph_extended':
            raise ValueError( ('Invalid parameter combination: input_type={!r} and input_morph_layer={!r}. '+\
                              'Mismatching input type and layer.').format(input_type, input_morph_layer))
        elif input_type=='morph_extended' and input_morph_layer=='morph_analysis':
            raise ValueError( ('Invalid parameter combination: input_type={!r} and input_morph_layer={!r}. '+\
                              'Mismatching input type and layer.').format(input_type, input_morph_layer))

        if depparse_path and not os.path.isfile(depparse_path):
            raise ValueError('Invalid path: {}'.format(depparse_path))
        elif depparse_path and os.path.isfile(depparse_path):
            self.model_path = depparse_path
        else:
            if input_type == 'morph_analysis':
                self.model_path = os.path.join(self.dir, 'et', 'depparse', 'morph_analysis.pt')
            if input_type == 'morph_extended':
                self.model_path = os.path.join(self.dir, 'et', 'depparse', 'morph_extended.pt')
            if input_type == 'sentences':
                self.model_path = os.path.join(self.dir, 'et', 'depparse', 'stanza_depparse.pt')

        if not os.path.isfile(self.model_path):
            raise FileNotFoundError('Necessary models missing, download from https://entu.keeleressursid.ee/public-document/entity-9791 '
                             'and extract folders `depparse` and `pretrain` to root directory defining '
                             'StanzaSyntaxTagger under the subdirectory `stanza_resources/et (or set )`')

        if input_type == 'sentences':
            if not os.path.isfile(os.path.join(self.dir, 'et', 'pretrain', 'edt.pt')):
                raise FileNotFoundError(
                    'Necessary pretrain model missing, download from https://entu.keeleressursid.ee/public-document/entity-9791 '
                    'and extract folder `pretrain` to root directory defining '
                    'StanzaSyntaxTagger under the subdirectory `stanza_resources/et`')

        if self.input_type == 'sentences':
            # Stanza default pipeline on EstNLTK's pretagged tokens/sentences
            self.input_layers = [sentences_layer, words_layer]
            self.nlp = stanza.Pipeline(lang='et', processors='tokenize,pos,lemma,depparse',
                                       dir=self.dir,
                                       tokenize_pretokenized=True,
                                       depparse_model_path=self.model_path,
                                       use_gpu=self.use_gpu,
                                       logging_level='WARN')  # Logging level chosen so it does not display
            # information about downloading model

        elif self.input_type in ['morph_analysis', 'morph_extended']:
            self.input_layers = [sentences_layer, input_morph_layer, words_layer]
            self.nlp = stanza.Pipeline(lang='et', processors='depparse',
                                       dir=self.dir,
                                       depparse_pretagged=True,
                                       depparse_model_path=self.model_path,
                                       use_gpu=self.use_gpu,
                                       logging_level='WARN')

    def _make_layer_template(self):
        """Creates and returns a template of the layer."""
        layer = Layer(name=self.output_layer,
                      text_object=None,
                      attributes=self.output_attributes,
                      parent=self.input_layers[1],
                      ambiguous=False )
        if self.add_parent_and_children:
            layer.serialisation_module = syntax_v0.__version__
        return layer

    def _make_layer(self, text, layers, status=None):
        # Make an internal import to avoid explicit stanza dependency
        from stanza.models.common.doc import Document

        if self.input_type in ['morph_analysis', 'morph_extended']:
            # Input: EstNLTK's tokenization and morphological features
            sentences = self.input_layers[0]
            morph_analysis = self.input_layers[1]
            text_data = prepare_input_doc(layers, sentences, morph_analysis, 
                                          random_picker=self._random)
            if self.use_gpu and self.gpu_max_words_in_sentence is not None:
                # Using GPU: Check that sentences are not too long (for CUDA memory)
                for sentence in text_data:
                    if len(sentence) > self.gpu_max_words_in_sentence:
                        raise Exception( ('(!) Encountered a sentence which length ({}) exceeds '+\
                                          'gpu_max_words_in_sentence ({}). Are you sure GPU '+\
                                          'has enough memory for processing this long sentence? '+\
                                          'Either process this document with CPU or, if GPU '+\
                                          'memory is ensured, pass parameter '+\
                                          'gpu_max_words_in_sentence=None to this tagger '+\
                                          'to disable this exception.').format(len(sentence), \
                                          self.gpu_max_words_in_sentence) )
            document = Document(text_data)
        else:
            # Input: EstNLTK's tokenization only
            sentences = self.input_layers[0]
            document = prepare_input_doc(layers, sentences, None, only_tokenization=True)

        parent_layer = layers[self.input_layers[1]]

        layer = self._make_layer_template()
        layer.text_object=text

        doc = self.nlp(document)

        extracted_data = [analysis for sentence in doc.to_dict() for analysis in sentence]

        for line, span in zip(extracted_data, parent_layer):
            id = line['id']
            lemma = line['lemma']
            upostag = line['upos']
            xpostag = line['xpos']
            feats = OrderedDict()  # Stays this way if word has no features.
            if 'feats' in line.keys():
                feats = feats_to_ordereddict(line['feats'])
            head = line['head']
            deprel = line['deprel']

            attributes = {'id': id, 'lemma': lemma, 'upostag': upostag, 'xpostag': xpostag, 'feats': feats,
                          'head': head, 'deprel': deprel, 'deps': '_', 'misc': '_'}

            layer.add_annotation(span, **attributes)

        if self.add_parent_and_children:
            # Add 'parent_span' & 'children' to the syntax layer.
            self.syntax_dependency_retagger.change_layer(text, {self.output_layer: layer})

        if self.mark_syntax_error:
            # Add 'syntax_error' & 'error_message' to the layer.
            self.ud_validation_retagger.change_layer(text, {self.output_layer: layer})

        if self.mark_agreement_error:
            # Add 'agreement_deprel' to the layer.
            self.agreement_error_retagger.change_layer(text, {self.output_layer: layer})

        return layer


def prepare_input_doc(layers, sentences, morph_analysis, only_tokenization=False, 
                      random_picker=None):
    '''
    Prepares input document for StanzaSyntaxTagger. Based on given sentences and 
    morph_analysis layers, constructs a list of sentences, where each sentence 
    consists of list of word dictionaries, each of which defines conllu fields
    {'id', 'lemma', 'upostag', ..., 'deps'} for a word.
    
    (By default) Returns list of lists of dicts, which can be given as an input 
    to stanza.models.common.doc.Document.
    
    If only_tokenization==True, then collects only sentence/word tokenization 
    and discards words' morphological features (conllu dictionaries). In that 
    case, returns list of lists of strings, which can be given as an input to 
    stanza.models.common.doc.Document.
    '''
    if random_picker is None and not only_tokenization:
        random_picker = Random()
    assert isinstance(layers, dict)
    assert sentences in layers.keys(), '(!) Missing {!r} layer'.format(sentences)
    assert only_tokenization or \
        morph_analysis in layers.keys(), '(!) Missing {!r} layer'.format(morph_analysis)
    data = []
    global_word_id = 0
    for sentence in layers[sentences]:
        sentence_analyses = []
        if only_tokenization:
            # Collect only sentence tokenization
            sentence_analyses = sentence.text
        else:
            # Collect sentence tokenization & morph features
            for wid, word_base_span in enumerate(sentence.base_span):
                # Get morph analysis of the word
                morph_word = layers[morph_analysis][global_word_id]
                assert word_base_span == morph_word.base_span
                # Pick an annotation randomly
                annotation = random_picker.choice(morph_word.annotations)
                feats = ''
                if annotation['form']:
                    feats = annotation['form']
                if not feats:
                    feats = '_'
                else:
                    # Make and join keyed features.
                    feats = '|'.join([a + '=' + a for a in feats.strip().split(' ') if a])
                # Construct conllu fields for the word
                word_conllu = {
                    'id': wid+1,
                    'text': morph_word.text,
                    'lemma': annotation['lemma'],
                    'upos': annotation['partofspeech'],
                    'xpos': annotation['partofspeech'],
                    'feats': feats,
                    'misc': '_',
                    'deps': '_',
                }
                sentence_analyses.append( word_conllu )
                global_word_id += 1
        data.append(sentence_analyses)
    return data


def feats_to_ordereddict(feats_str):
    """
    Converts feats string to OrderedDict (as in MaltParserTagger and UDPipeTagger)
    """
    feats = OrderedDict()
    if feats_str == '_':
        return feats
    feature_pairs = feats_str.split('|')
    for feature_pair in feature_pairs:
        key, value = feature_pair.split('=')
        feats[key] = value
    return feats
