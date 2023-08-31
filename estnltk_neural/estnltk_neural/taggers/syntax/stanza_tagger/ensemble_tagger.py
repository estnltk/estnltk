import os
from collections import defaultdict, Counter, OrderedDict
from decimal import Decimal, getcontext
from random import Random
from typing import Tuple
import warnings

from estnltk import Layer
from estnltk.taggers.standard.syntax.syntax_dependency_retagger import SyntaxDependencyRetagger
from estnltk.taggers.standard.syntax.ud_validation.deprel_agreement_retagger import DeprelAgreementRetagger
from estnltk.taggers.standard.syntax.ud_validation.ud_validation_retagger import UDValidationRetagger
from estnltk.taggers import Tagger
from estnltk.downloader import get_resource_paths

from estnltk.converters.serialisation_modules import syntax_v0

from estnltk_neural.taggers.syntax.stanza_tagger.common_utils import prepare_input_doc
from estnltk_neural.taggers.syntax.stanza_tagger.common_utils import feats_to_ordereddict

class StanzaSyntaxEnsembleTagger(Tagger):
    """
    Tags dependency syntactic analysis with Stanza.
    The tagger assumes that the segmentation to sentences and words is completed beforehand. When using default
    models, the tagger assumes that extended morph analysis is completed with VabaMorf module.

    The tagger creates a syntax layer that features Universal Dependencies dependency-tags in attribute 'deprel'.
    UPOS is the same as VabaMorf's part of speech tag and feats is based on VabaMorf's forms.

    Names of layers to use can be changed using parameters sentences_layer, words_layer and input_morph_layer,
    if needed. To use GPU for parsing, parameter use_gpu must be set to True.
    Parameter add_parents_and_children adds attributes that contain the parent and children of a word.

    When using models which are trained on some missing conllu fields (text, lemma, upos, xpos, feats), these
    fields can be omitted by assigning a list of field names to parameter `remove_fields`. Fields can also be
    replaced with a chosen string by assigning a tuple containing a list of field names as first element
    and string as a second to parameter `replace_fields`.

    The input morph analysis layer can be ambiguous. In that case, StanzaSyntaxEnsembleTagger picks randomly one 
    morph analysis for each ambiguous word, and predicts from "unambiguous" input. 
    Important: as a result, by default, the output will not be deterministic: for ambiguous words, you will 
    get different 'lemma', 'upostag', 'xpostag', 'feats' values on each run, and this also affects the results 
    of dependency parsing. 
    Ambiguity can also rise in dependency parsing: ensemble models can give multiple dependency parses with 
    maximum score and one parse needs to be chosen -- this is again done via a random choice (using a different 
    random generator).
    How to make the output deterministic: you can pass a seed value for picking one analysis from ambiguous 
    morph analyses via constructor parameter random_pick_seed (int, default value: None), and a seed value 
    for choosing one dependency result from results with maximum scores via constructor parameter 
    random_pick_max_score_seed (int, default value: None).
    Note that seed values are fixed once at creating a new instance of StanzaSyntaxEnsembleTagger, and you only 
    get deterministic / repeatable results if you tag texts in exactly the same order.
    Note: if you want to get the same deterministic output as in previous versions of the tagger, use 
    random_pick_seed=5 and random_pick_max_score_seed=3.
    
    Aggregation algorithm. For aggregating predictions from multiple models, there are currently 2 algorithms 
    available. The first / default method ('las_coherence') processes input sentence-wise and calculates LAS 
    scores between each model's sentence prediction and all other sentence predictions. The sentence prediction  
    with the highest average LAS will be chosen for the output. 
    The second method ('majority_voting') processes input token-wise and records predicted head & deprel frequencies 
    for each token in a sentence. After that, it applies Chu–Liu/Edmonds' algorithm to construct a valid syntactic 
    tree of the sentence over high frequency heads of each token. Any remaining ambiguities (e.g. choices between 
    multiple different deprels for a head) will be resolved via random choice. 
    You can set the aggregation algorithm via constructor parameter aggregation_algorithm. 
    
    Predictions' entropy. If `find_entropy` is switched on, then predictions' uncertainty (Shannon entropy) will 
    be calculated for each word, reflecting how much ensemble's models disagreed on choosing the deprel and the 
    head. 
    Zero entropy means no disagreement (full agreement between all models), while an entropy greater than zero 
    indicates disagreement: greater the value, larger the disagreement. 
    Calculated entropy will be stored in attribute `entropy`; another attribute `max_votes` will show the number 
    of votes that the top candidate obtained. 
    If `find_entropy` is switched on with `add_voting_results`, then explicit counts for f'{deprel}_{head}' 
    pairs will be recorded in the attribute `voting_results` for each word. 
    If `find_entropy` is switched on with `deprel_entropy`, then, in addition to deprel & head entropy, entropies 
    are also calculated separately for deprel values alone and the results will be stored in attributes:
    `deprel_max` (deprel that got maximal votes), `deprel_max_votes` (the number of votes top deprel obtained), 
    `deprel_entropy` (entropy encountered while choosing deprel value).
    If `find_entropy` is switched on with `head_entropy`, then, in addition to deprel & head entropy, entropies 
    are also calculated separately for head values alone and the results will be stored in attributes:
    `head_max` (head that got maximal votes), `head_max_votes` (the number of votes top head obtained), 
    `head_entropy` (entropy encountered while choosing head value).
    
    Tutorial:
    https://github.com/estnltk/estnltk/blob/main/tutorials/nlp_pipeline/C_syntax/03_syntactic_analysis_with_stanza.ipynb
    """

    conf_param = ['add_parent_and_children', 'aggregation_algorithm', 'syntax_dependency_retagger',
                  'mark_syntax_error', 'mark_agreement_error', 'agreement_error_retagger', 
                  'find_entropy', 'deprel_entropy', 'head_entropy', 'add_voting_results', 
                  'ud_validation_retagger', 'use_gpu', 'gpu_max_words_in_sentence', 'model_paths', 
                  'taggers', 'remove_fields', 'replace_fields', 'random_pick_seed', '_random1', 
                  'random_pick_max_score_seed', '_random2']

    def __init__(self,
                 output_layer: str = 'stanza_ensemble_syntax',
                 sentences_layer: str = 'sentences',
                 words_layer: str = 'words',
                 input_morph_layer: str = 'morph_extended',
                 aggregation_algorithm: str = 'las_coherence',
                 random_pick_seed: int = None,
                 random_pick_max_score_seed: int = None,
                 remove_fields: list = None,
                 replace_fields: Tuple[list, str] = None,
                 model_paths: list = None,
                 add_parent_and_children: bool = False,
                 mark_syntax_error: bool = False,
                 mark_agreement_error: bool = False,
                 find_entropy: bool = False,
                 deprel_entropy: bool = False,
                 head_entropy: bool = False,
                 add_voting_results: bool = False,
                 use_gpu: bool = False,
                 gpu_max_words_in_sentence: int = 1000
                 ):
        # Make an internal import to avoid explicit stanza dependency
        import stanza

        self.output_layer = output_layer
        self.remove_fields = remove_fields
        self.replace_fields = replace_fields
        self.model_paths = model_paths
        self.add_parent_and_children = add_parent_and_children
        self.mark_syntax_error = mark_syntax_error
        self.mark_agreement_error = mark_agreement_error
        self.output_attributes = ('id', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps', 'misc')
        if not isinstance(aggregation_algorithm, str) or \
           aggregation_algorithm.lower() not in ['las_coherence', 'majority_voting']:
            raise ValueError(('(!) Unexpected aggregation_algorithm value {!r}. '+\
                              'Must be a value from set {"las_coherence", "majority_voting"}').format(aggregation_algorithm))
        self.aggregation_algorithm = aggregation_algorithm.lower()
        self.use_gpu = use_gpu
        # We may run into "CUDA out of memory" error when processing very long sentences 
        # with GPU.
        # Set a reasonable default for max sentence length: if that gets exceeded, then a 
        # guarding exception will be thrown
        self.gpu_max_words_in_sentence = gpu_max_words_in_sentence
        
        # Random generator for picking one analysis from ambiguous morph analyses:
        self.random_pick_seed = random_pick_seed
        self._random1 = Random()
        if isinstance(self.random_pick_seed, int):
            self._random1.seed(self.random_pick_seed)
        # Random generator for choosing one dependency result from results with maximum scores:
        self.random_pick_max_score_seed = random_pick_max_score_seed
        self._random2 = Random()
        if isinstance(self.random_pick_max_score_seed, int):
            self._random2.seed(self.random_pick_max_score_seed)
        
        # Try to get the resources path for stanzasyntaxensembletagger. Attempt to download resources, if missing
        resources_path = get_resource_paths("stanzasyntaxensembletagger", only_latest=True, download_missing=True)
        if resources_path is None:
            raise Exception('Models of StanzaSyntaxEnsembleTagger are missing. '+\
                            'Please use estnltk.download("stanzasyntaxensembletagger") to download the models.')
        
        if not model_paths:
            self.model_paths = list()
            ensemble_path = os.path.join(resources_path, 'et', 'depparse', 'ensemble_models')
            if not os.path.isdir(ensemble_path):
                raise ValueError('Missing models under the subdirectory `stanza_resources/et/depparse/ensemble_models.')
            for model in os.listdir(ensemble_path):
                self.model_paths.append(os.path.join(ensemble_path, model))

        self.taggers = dict()  # Save taggers
        for i, model_path in enumerate(self.model_paths):
            if not os.path.isfile(model_path):
                raise ValueError('Invalid model path: {}'.format(model_path))

            nlp = stanza.Pipeline(lang='et', processors='depparse',
                                  dir=resources_path,
                                  depparse_pretagged=True,
                                  depparse_model_path=model_path,
                                  use_gpu=self.use_gpu,
                                  logging_level='WARN')
            self.taggers[str(i)] = nlp

        self.input_layers = [sentences_layer, input_morph_layer, words_layer]

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
        
        self.find_entropy = find_entropy
        if add_voting_results and not find_entropy:
            raise ValueError('Conflicting configuration: `find_entropy` must be True if `add_voting_results` is True.')
        self.add_voting_results = add_voting_results
        if deprel_entropy and not find_entropy:
            raise ValueError('Conflicting configuration: `find_entropy` must be True if `deprel_entropy` is True.')
        self.deprel_entropy = deprel_entropy
        if head_entropy and not find_entropy:
            raise ValueError('Conflicting configuration: `find_entropy` must be True if `head_entropy` is True.')
        self.head_entropy   = head_entropy
        if self.find_entropy:
            self.output_attributes += ('max_votes', 'entropy')
            if self.add_voting_results:
                self.output_attributes += ('voting_results',)
            if self.deprel_entropy:
                self.output_attributes += ('deprel_max', 'deprel_max_votes', 'deprel_entropy')
            if self.head_entropy:
                self.output_attributes += ('head_max', 'head_max_votes', 'head_entropy')

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

    def _make_layer(self, text, layers, status):
        # Make an internal import to avoid explicit stanza dependency
        import numpy as np
        from stanza import Document
        from stanza.models.common.chuliu_edmonds import chuliu_edmonds_one_root
        
        sentences_layer = self.input_layers[0]
        morph_layer = self.input_layers[1]

        sents_lases_table = defaultdict(dict)
        parsed_texts = defaultdict()

        text_data = prepare_input_doc(layers, sentences_layer, morph_layer, remove_fields=self.remove_fields,
                                      replace_fields=self.replace_fields, random_picker=self._random1)

        if self.use_gpu and self.gpu_max_words_in_sentence is not None:
            # Check that sentences are not too long (for CUDA memory)
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

        for model, nlp in self.taggers.items():
            doc = Document(text_data)
            nlp(doc)  # Parsing documents
            parsed_texts[model] = doc.to_dict()

        parent_layer = layers[self.input_layers[1]]

        # Find predictions' uncertainty/entropy & votes
        words_entropy = None
        if self.find_entropy:
            words_entropy = \
                find_prediction_entropy(parent_layer, parsed_texts, 
                                               add_model_votes=self.add_voting_results, 
                                               separate_deprel_entropy=self.deprel_entropy, 
                                               separate_head_entropy=self.head_entropy )
            assert len(words_entropy) == len(parent_layer)

        extracted_words = []
        if self.aggregation_algorithm == 'las_coherence':
            # 1) Compare predictions of each model against every other
            #    model, and find the prediction with the highest avg sentence 
            #    LAS score. This method ensures valid tree structure.
            extracted_data = []
            for model, parsed in parsed_texts.items():
                for model2, parsed2 in parsed_texts.items():
                    text_sentence_lases = text_sentence_LAS(parsed, parsed2)
                    sents_lases_table[model][model2] = text_sentence_lases

            final_table = defaultdict(dict)  # Scores by sentence indices.
            for idx in range(len(layers[sentences_layer])):
                for model, scores in sents_lases_table.items():
                    if model not in final_table:
                        final_table[idx][model] = {}
                    for model2, sentence_scores in scores.items():
                        score = sentence_scores[idx]
                        final_table[idx][model][model2] = score

            sent_scores = defaultdict(dict)
            getcontext().prec = 4
            for sent, score_dict in final_table.items():
                if sent not in sent_scores:
                    sent_scores[sent] = Counter()
                for base_model, score in score_dict.items():
                    decimals = list(map(Decimal, score.values()))
                    avg_score = sum(decimals) / Decimal(len(self.taggers))
                    sent_scores[sent][base_model] = avg_score

            chosen_sents = defaultdict(list)
            for sent, score in sent_scores.items():
                max_score = max(score.values())
                max_score_count = 0
                max_score_models = []
                for s in score:
                    if score[s] == max_score:
                        max_score_count += 1
                        max_score_models.append(s)
                self._random2.shuffle(max_score_models)
                chosen_sents[max_score_models[0]].append(sent)

            idxed_sents = {}
            for model, sent_no in chosen_sents.items():
                content = parsed_texts[model]
                sents_set = set(sent_no)
                for idx in sents_set:
                    idxed_sents[idx] = content[idx]

            for idx in range(0, len(idxed_sents)):
                extracted_data.append(idxed_sents[idx])

            extracted_words = [word for sentence in extracted_data for word in sentence]
        else:
            assert self.aggregation_algorithm == "majority_voting"
            # 2) Majority voting: pick the dependency relation with the 
            #    highest number of votes over all model predictions.
            #    This method can produce invalid tree structures.
            word_id = 0
            sentence_id = 0
            while sentence_id < len(layers[sentences_layer]):
                # 1) Collect words and votes for the current sentence
                sentence_word_id = 0
                sent_len = len(layers[sentences_layer][sentence_id])
                voting_table = defaultdict(lambda: defaultdict(int))
                label_token_map = defaultdict(lambda: defaultdict(list))
                sent_matrix = np.zeros((sent_len+1, sent_len+1))
                np.fill_diagonal(sent_matrix, -float('inf'))
                while sentence_word_id < sent_len:
                    # collect votes
                    for model, parsed_doc in parsed_texts.items():
                        assert len(parsed_doc) == len(layers[sentences_layer])
                        sentence = parsed_doc[sentence_id]
                        assert len(sentence) == sent_len
                        token = sentence[sentence_word_id]
                        label = '{}__{}'.format(token['deprel'], token['head'])
                        voting_table[sentence_word_id][label] += 1
                        label_token_map[sentence_word_id][label].append(token)
                        head_int = int(token['head'])
                        sent_matrix[sentence_word_id+1, head_int] += 1.0
                    sentence_word_id += 1
                    word_id += 1
                # 2) use Chu–Liu/Edmonds' algorithm to find head_seq of a valid tree 
                valid_tree_head_seq = chuliu_edmonds_one_root(sent_matrix)[1:]
                # 3) For each word, find maximum voting score and corresponding tokens
                for wid in sorted(voting_table.keys()):
                    valid_head = valid_tree_head_seq[wid]
                    max_votes_valid = []
                    for l, v in voting_table[wid].items():
                        if l.endswith('__{}'.format(valid_head)):
                            max_votes_valid.append((l, v))
                    if not max_votes_valid:
                        # If something went wrong, then fall back to unchecked tree.
                        word_str = layers[sentences_layer][sentence_id][wid]
                        sentence_str = layers[sentences_layer][sentence_id].enclosing_text
                        msg = ('(!) Unable to find a tree-bound head for '+\
                               'word {!r} in sentence {!r}. ').format(word_str, sentence_str)
                        msg += 'Falling back to unchecked tree construction, '
                        msg += 'which may result in an invalid syntax tree.'
                        warnings.warn(msg)
                        max_votes_valid = voting_table[wid].items()
                    max_votes = max([v for (l, v) in max_votes_valid])
                    max_votes_labels = [l for l, v in max_votes_valid if v==max_votes]
                    max_votes_tokens = []
                    for label, tokens in label_token_map[wid].items():
                        if label in max_votes_labels:
                            max_votes_tokens.extend(tokens)
                    # In case of a tie, pick a token randomly
                    self._random2.shuffle(max_votes_tokens)
                    extracted_words.append(max_votes_tokens[0])
                # Next sentence
                sentence_id += 1
            assert len(extracted_words) == len(parent_layer)

        layer = self._make_layer_template()
        layer.text_object=text

        global_word_id = 0
        for token, span in zip(extracted_words, parent_layer):
            assert span.text == token['text']
            word_id = token['id']
            lemma = token['lemma']
            upostag = token['upos']
            xpostag = token['xpos']
            feats = OrderedDict()
            if 'feats' in token.keys():
                feats = feats_to_ordereddict(token['feats'])
            head = token['head']
            deprel = token['deprel']

            attributes = {'id': word_id, 'lemma': lemma, 'upostag': upostag, 'xpostag': xpostag, 
                          'feats': feats, 'head': head, 'deprel': deprel, 'deps': '_', 'misc': '_'}
            
            # Record voting & entropy information
            if words_entropy is not None:
                entropy_info = words_entropy[global_word_id]
                attributes['entropy'] = entropy_info['entropy']
                attributes['max_votes'] = entropy_info['max_votes']
                if self.add_voting_results:
                    # Table that contains all head & deprel voting results
                    attributes['voting_results'] = entropy_info['all_votes']
                if self.deprel_entropy:
                    # Separate voting results covering only deprel-s
                    attributes['deprel_max'] = entropy_info['deprel_max']
                    attributes['deprel_max_votes'] = entropy_info['deprel_max_votes']
                    attributes['deprel_entropy'] = entropy_info['deprel_entropy']
                if self.head_entropy:
                    # Separate voting results covering only head-s
                    attributes['head_max'] = entropy_info['head_max']
                    attributes['head_max_votes'] = entropy_info['head_max_votes']
                    attributes['head_entropy'] = entropy_info['head_entropy']

            layer.add_annotation(span, **attributes)
            global_word_id += 1

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


def find_prediction_entropy(words_layer, parsed_texts, add_model_votes=True, 
                                         separate_deprel_entropy=False, 
                                         separate_head_entropy=False):
    '''
    Calculates uncertainty/Shannon entropy for ensemble predictions of each word. 
    If add_model_votes, then adds frequencies of model votes to results (for debugging).
    If separate_deprel_entropy, then calculates entropy separately for assigining 
    deprels and adds to the results.
    If separate_head_entropy, then calculates entropy separately for assigining 
    heads and adds to the results.
    '''
    from scipy.stats import entropy
    word_id = 0
    sentence_id = 0
    sentence_word_id = 0
    results = []
    nr_of_models = len(parsed_texts.items())
    while word_id < len( words_layer ):
        sentence = None
        # Get (deprel,head) votes for the word token
        votes = []
        votes_head = []
        votes_deprel = []
        for model, parsed_doc in parsed_texts.items():
            sentence = parsed_doc[sentence_id]
            token = sentence[sentence_word_id]
            label = '{}_{}'.format(token['deprel'], token['head'])
            votes.append(label)
            votes_head.append(token['head'])
            votes_deprel.append(token['deprel'])
        # A) Votes/entropy for both deprel & head
        voting_table = Counter(votes)
        normalized_voting_table = \
            [voting_table[k] / nr_of_models for k in voting_table.keys()]
        e = entropy(normalized_voting_table)
        r = {'entropy': e}
        r['max_votes'] = voting_table.most_common()[0][1]
        if add_model_votes:
            r['all_votes'] = voting_table.most_common()
        # B) Votes/entropy for deprel only
        if separate_deprel_entropy:
            deprel_table = Counter(votes_deprel)
            normalized_voting_table_deprel = \
                [deprel_table[k] / nr_of_models for k in deprel_table.keys()]
            r['deprel_entropy'] = entropy(normalized_voting_table_deprel)
            r['deprel_max'] = deprel_table.most_common()[0][0]
            r['deprel_max_votes'] = deprel_table.most_common()[0][1]
        # C) Votes/entropy for head only
        if separate_head_entropy:
            head_table = Counter(votes_head)
            normalized_voting_table_head = \
                [head_table[k] / nr_of_models for k in head_table.keys()]
            r['head_entropy'] = entropy(normalized_voting_table_head)
            r['head_max'] = head_table.most_common()[0][0]
            r['head_max_votes'] = head_table.most_common()[0][1]
        results.append(r)
        word_id += 1
        sentence_word_id += 1
        if sentence_word_id >= len(sentence):
            # Next sentence
            sentence_id += 1
            sentence_word_id = 0
    return results


def sentence_LAS(sent1, sent2):
    wrong = 0
    correct = 0
    for tok1, tok2 in zip(sent1, sent2):
        if tok1['xpos'] != 'Z':
            if tok1['head'] == tok2['head'] and tok1['deprel'] == tok2['deprel']:
                correct += 1
            else:
                wrong += 1

    if wrong == 0 and correct == 0:
        return 1
    else:
        return correct / (correct + wrong)


def text_sentence_LAS(sents1, sents2):
    file_sentence_lases = []
    for sent1, sent2 in zip(sents1, sents2):
        las = sentence_LAS(sent1, sent2)
        file_sentence_lases.append(las)
    return file_sentence_lases


