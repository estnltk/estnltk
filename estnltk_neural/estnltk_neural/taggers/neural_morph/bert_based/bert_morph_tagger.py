# EstNLTK's BERT-based morphological tagger. Uses Vabamorf's tagset (partofspeech and form tags). 

# Works with next module versions:
# estnltk == 1.7.3
# torch == 2.4.0
# sentencepiece == 0.2.0

# Code references:
# * https://github.com/estnltk/estnltk-model-training/tree/main/morph_tagging
# * https://github.com/estnltk/estnltk/blob/main/estnltk_neural/estnltk_neural/taggers/ner/estbertner_tagger.py
# * https://bitbucket.org/utDigiHum/public/src/8635582194ef1f2dcec53c40abdfa3f29299a067/skriptid/nimeuksuste_m2rgendamine/bert_morph_tagging_tagger.py

import os
import torch
import collections
import warnings

from typing import MutableMapping, List, Optional

from transformers import AutoConfig, AutoTokenizer, AutoModelForTokenClassification

from estnltk import Text, Layer, Retagger
from estnltk.downloader import get_resource_paths

from estnltk_neural.taggers.embeddings.bert.bert_tokens_to_words_rewriter import BertTokens2WordsRewriter

class BertMorphTagger(Retagger):
    """Applies BERT-based tagging of morphological features (partofspeech and form tags). 
       Uses partofspeech and form tags from Vabamorf's tagset. 
       
       This tagger works either as a tagger (A) or as a retagger (B), depending on 
       whether the flag <code>disambiguate</code> is disabled or enabled. As a Tagger, 
       it creates a new morphological analysis layer, while as a Retagger, it disambiguates 
       an existing morphological analysis layer that has annotations in Vabamorf's tagset. 
       
       A) If <code>disambiguate</code> is False, then the tagger works as a tagger and 
       a new morph layer (<code>output_layer</code>) can be created by calling tagger's 
       tag(...) or make_layer(...) methods. 
       
       B) If <code>disambiguate</code> is True, then <code>output_layer</code> must be set 
       to a morphological analysis (which will become an input layer) and which then can 
       be disambiguated by calling tagger's retag(...) or change_layer(...) methods. 
    """

    def __init__(
        self,
        model_location: Optional[str] = None,
        get_top_n_predictions: int = 1,
        output_layer: str = 'bert_morph_tagging',
        sentences_layer: str = 'sentences',
        words_layer: str = 'words',
        token_level: bool = False,
        split_pos_form: bool = True,
        disambiguate: bool = False,
        **kwargs
    ):
        """
        Initializes BertMorphTagger

        Args:
            model_location (str, Optional): 
                Full path to the BertMorphTagger's model files directory. If not provided (default), then 
                attempts to use bert_morph_tagging model from estnltk_resources. If that fails (model is 
                missing and downloading fails), then throws an exception.
            get_top_n_predictions (int): Number of labeles predicted for each word.
            output_layer (str): 
                Name of the output morphological annotations layer. Defaults to 'bert_morph_tagging'. 
                Note: if <code>disambiguate==True</code>, then this must be name a Vabamorf-based morph 
                analysis layer which will be disambiguated by calling tagger's <code>retag</code> method. 
            sentences_layer (str): Name of the layer containing sentences.
            words_layer (str): Name of the layer containing words.
            token_level (bool): Whether to tag the text BERT token-level or EstNLTK's word-level. Defaults to False. 
            split_pos_form (bool): Whether to split the predicted labels into two separate features. Defaults to True. 
                <i>Predicted BERT label is a concatenation of Vabamorf's <code>form</code> and <code>partofspeech</code>
                joined with <code>_</code>, for example <code>sg n_S</code></i>.
            disambiguate (bool): Whether the tagger is to be used as an disambiguator of an input morph analyis layer. 
                Defaults to False. If set, then BertMorphTagger can be used to disambiguate an existing Vabamorf-based 
                morph analysis layer by calling <code>BertMorphTagger.retag(text_obj)</code>. Note that the input 
                <code>text_obj</code> must already have <code>output_layer<code> which will be disambiguated. 

        Raises:
            Exception: Raises when BertMorphTagger's resources have not been downloaded.
        """

        # Configuration parameters
        self.conf_param = ('model_location', 'get_top_n_predictions', 'bert_tokenizer', 'bert_morph_tagging', 'id2label', \
                           'token_level', 'split_pos_form', 'disambiguate', 'sentences_layer', 'words_layer', 'output_layer', \
                           'input_layers', 'output_attributes', '_bert_tokens_rewriter')

        if model_location is None:
            # Try to get the resources path for bert_morph_tagger. Attempt to download, if missing
            resources_path = get_resource_paths("bert_morph_tagging", only_latest=True, download_missing=True)
            if resources_path is None:
                raise Exception( "BertMorphTagger's resources have not been downloaded. "+\
                                 "Use estnltk.download('bert_morph_tagging') to get the missing resources. "+\
                                 "Alternatively, you can specify the directory containing the model "+\
                                 "via parameter model_location at creating the tagger." )
            self.model_location = resources_path

        else:
            self.model_location = model_location

        tokenizer_kwargs = { k:v for (k,v) in kwargs.items() if k in ['do_lower_case', 'use_fast'] }
        self.get_top_n_predictions = get_top_n_predictions
        self.bert_tokenizer = AutoTokenizer.from_pretrained(self.model_location, **tokenizer_kwargs )
        self.bert_morph_tagging = AutoModelForTokenClassification.from_pretrained(self.model_location,
                                                                        output_attentions = False,
                                                                        output_hidden_states = False)

        # Fetch id2label mapping from configuration
        config_dict = AutoConfig.from_pretrained(self.model_location).to_dict()
        self.id2label, _ = config_dict["id2label"], config_dict["label2id"]

        # Set input and output layers
        self.split_pos_form = split_pos_form
        self.disambiguate = disambiguate
        self.token_level = token_level
        self.sentences_layer = sentences_layer
        self.words_layer = words_layer
        self.output_layer = output_layer
        self.input_layers = [sentences_layer, words_layer]
        if self.disambiguate:
            # Check other parameters
            if not self.split_pos_form:
                raise Exception( ('(!) Cannot use BertMorphTagger as a disambiguator (disambiguate==True) if '+\
                                  'split_pos_form==False.').format(attr, morph_layer.name) )
            if self.get_top_n_predictions > 1:
                warnings.warn( f'(!) Parameter get_top_n_predictions=={self.get_top_n_predictions} has no effect '+\
                                'during retagging/disambiguation (disambiguate==True). Only the label with the '+\
                                'highest probability is used in the disambiguation.' )
            # Add output_layer as an expected input layer that needs to be disambiguated
            self.input_layers.append( self.output_layer )
        self.output_attributes = ['bert_tokens', 'form', 'partofspeech', 'probability'] if self.split_pos_form else ['bert_tokens', 'morph_label', 'probability']
        if self.token_level:
            self._bert_tokens_rewriter = None
        else:
            # Create BertTokens2WordsRewriter for rewriting bert tokens to Estnltk's words
            if self.split_pos_form:
                self._bert_tokens_rewriter = BertTokens2WordsRewriter(
                    bert_tokens_layer=self.output_layer, 
                    input_words_layer=self.words_layer, 
                    output_attributes=self.output_attributes, 
                    output_layer=self.output_layer, 
                    enveloping=False, 
                    decorator=rewriter_decorator_Vabamorf)
            else:
                self._bert_tokens_rewriter = BertTokens2WordsRewriter(
                    bert_tokens_layer=self.output_layer, 
                    input_words_layer=self.words_layer, 
                    output_attributes=self.output_attributes, 
                    output_layer=self.output_layer, 
                    enveloping=False, 
                    decorator=rewriter_decorator_BERT)

    def _get_bert_morph_tagging_label_predictions(self, 
                                                  input_str:str, 
                                                  get_top_n_predictions:int = 1):
        """
        Applies Bert on the given input string and returns Bert's tokens,
        token indexes, and top N predicted labels for each token. \n
        Labels will be converted to Vabamorf's annotations type if <code>self.split_pos_form</code> is True.

        Args:
            input_str (str): The input string to be processed.
            top_n (int): Number of top predictions to return for each token.

        Returns:
            List[dict]: Each token's top N predictions with their probabilities.
        """
        # Tokenize the input string
        tokens, batch_encoding = self._tokenize_with_bert(input_str)
        token_indexes = torch.tensor([batch_encoding['input_ids']])

        # Check if the length exceeds the model's maximum sequence length
        max_seq_length = self.bert_tokenizer.model_max_length
        if token_indexes.size(1) > max_seq_length:
            raise ValueError(f"Input length exceeds the model's max_seq_length of {max_seq_length} tokens")

        # Get predictions
        with torch.no_grad():
            output = self.bert_morph_tagging(token_indexes)

        # Get top N predictions
        top_n_predictions = []
        logits = output.logits.squeeze()  # Shape: [sequence_length, num_labels]
        probs = torch.softmax(logits, dim=-1)  # Convert logits to probabilities

        for i, token_data in enumerate(tokens):
            token_probs = probs[i]  # Probabilities for the current token
            top_n_indices = torch.topk(token_probs, get_top_n_predictions).indices  # Top N label indices
            top_n_labels = [self.id2label[idx.item()] for idx in top_n_indices]  # Convert indices to labels
            top_n_probs = [round(token_probs[idx].item(), 5) for idx in top_n_indices]  # Get probabilities for top N labels

            top_n_predictions.append({
                'token': token_data,
                'predictions': [{'label': label, 'probability': prob} for label, prob in zip(top_n_labels, top_n_probs)]
            })

        # Convert BERT labels to Vabamorf's form and POS
        if self.split_pos_form:
            top_n_predictions = convert_bert_labels_to_vabamorf(top_n_predictions)

        return top_n_predictions

    def _tokenize_with_bert(self, 
                            text:str, 
                            include_spanless:bool=True):

        """
        Tokenizes input string with Bert's tokenizer and returns a list of token spans.
        Each token span is a triple (start, end, token).
        If include_spanless==True (default), then Bert's special "spanless" tokens
        (e.g. [CLS], [SEP]) will also be included with their respective start/end indexes
        set to None.

        Args:
            text(str): The input string to be processed.
            include_spanless(bool): Whether to include Bert's special "spanless" tokens. Defaults to True
        Returns:
            tuple: A tuple containing
            <ul>
                <li>tokens (list): A list of tuples where each tuple contains (start, end, token).</li>
                <li>batch_encoding: The batch encoding object from the BERT tokenizer.</li>
            </ul>
        """
        tokens = []
        batch_encoding = self.bert_tokenizer(text)
        for token_id, token in enumerate(batch_encoding.tokens()):
            char_span = batch_encoding.token_to_chars(token_id)
            if char_span is not None:
                tokens.append( (char_span.start, char_span.end, token) )
            elif include_spanless:
                tokens.append( (None, None, token) )
        return tokens, batch_encoding

    def _make_layer(self, text: Text, layers: MutableMapping[str, Layer], status: dict) -> Layer:
        """
        Processes the input text to generate a morphological layer by using BERT predictions.

        This method processes each sentence, tokenizes it using BERT, and then assigns morphological
        annotations (i.e., part of speech, form, and probability) to each token. It optionally splits 
        morphological tags into <code>form</code> and <code>partofspeech</code>.

        Args:
            text (Text): The input text object to be processed.
            layers (MutableMapping[str, Layer]): A mapping of layer names to their corresponding layers
                                                in the text object (e.g., sentences, words, etc.).
            status (dict): ... (unused in this function).

        Returns:
            Layer: The morphological layer containing annotations for each token.
        """
        sentences_layer = layers[ self.sentences_layer ]
        words_layer = layers[ self.words_layer ]
        morph_layer = Layer(name=self.output_layer, 
                        attributes=self.output_attributes, 
                        text_object=text, 
                        parent=self.words_layer, 
                        ambiguous=True)

        for k, sentence in enumerate( sentences_layer ):
            sent_start = sentence.start
            sent_text  = sentence.enclosing_text
            # Apply batch processing: split larger input sentence into smaller chunks and process chunk by chunk
            sent_chunks, sent_chunk_indexes = _split_sentence_into_smaller_chunks(sent_text)
            for sent_chunk, (chunk_start, chunk_end) in zip(sent_chunks, sent_chunk_indexes):
                # Get predictions for the sentence
                top_n_predictions = self._get_bert_morph_tagging_label_predictions(sent_chunk, self.get_top_n_predictions)

                # Collect token level annotations (a label for each token)
                for token_data in top_n_predictions:
                    start, end  = token_data['token'][0], token_data['token'][1]
                    bert_tokens = token_data['token'][2]
                    if start is None or end is None:
                        continue  # Ignore sentence start and end tokens (<s>, </s>)
                    all_labels = [pred['label'] for pred in token_data['predictions']]
                    all_probabilities = [pred['probability'] for pred in token_data['predictions']]
                    token_span = (sent_start + chunk_start + start, sent_start + chunk_start + end)
                    for label, prob in zip(all_labels, all_probabilities):
                        if self.split_pos_form:
                            annotation = {
                                'bert_tokens': bert_tokens,
                                'form': label[0],
                                'partofspeech': label[1],
                                'probability': prob
                            }
                        else:
                            annotation = {
                                'bert_tokens': bert_tokens,
                                'morph_label': label,
                                'probability': prob
                            }
                        morph_layer.add_annotation(token_span, **annotation)

        # Add annotations
        if self.token_level:
            # Return token level annotations
            return morph_layer

        else:
            # Aggregate tokens back into words/phrases
            # Use BertTokens2WordsRewriter to convert BERT tokens to words
            # Rewrite to align BERT tokens with words
            morph_layer = self._bert_tokens_rewriter.make_layer(text, layers={morph_layer.name: morph_layer})

        assert len(morph_layer) == len(words_layer), \
        f"Failed to rewrite '{morph_layer.name}' layer tokens to '{words_layer.name}' layer words: {len(morph_layer)} != {len(words_layer)}"

        return morph_layer


    def _change_layer(self, text, layers, status=None):
        # Validate configuration
        if not self.split_pos_form:
            raise Exception( ('(!) Cannot use BertMorphTagger as a disambiguator if '+\
                              'split_pos_form is set False.').format(attr, morph_layer.name) )
        # Validate inputs
        morph_layer = layers[self.output_layer]
        for attr in ['partofspeech', 'form']:
            if attr not in morph_layer.attributes:
                raise Exception( ('(!) Missing attribute {!r} in output_layer {!r}.'+\
                                  '').format(attr, morph_layer.name) )
        # Create disambiguation layer
        disamb_layer = self._make_layer(text, layers, status)
        # Disambiguate input_morph_analysis_layer
        assert len(morph_layer) == len(disamb_layer)
        for original_word, disamb_word in zip(morph_layer, disamb_layer):
            disamb_pos  = disamb_word.annotations[0]['partofspeech']
            disamb_form = disamb_word.annotations[0]['form']
            # Filter annotations of the original morph layer: keep only those
            # annotations that are matching with the disambiguated annotation
            # (note: there can be multiple suitable annotations due to lemma 
            #  ambiguities)
            keep_annotations = []
            for annotation in original_word.annotations:
                if annotation['partofspeech'] == disamb_pos and annotation['form'] == disamb_form:
                    keep_annotations.append(annotation)
            if len(keep_annotations) > 0:
                # Only disambiguate if there is at least one annotation left
                # (can't leave a word without any annotations)
                original_word.clear_annotations()
                for annotation in keep_annotations:
                    original_word.add_annotation( annotation )


def convert_bert_labels_to_vabamorf(predictions:List[dict]):
    '''Converts BERT labels into Vabamorf's annotations (<code>partofspeech</code> and <code>form</code>)

    Args:
        predictions (List[dict]): Each token's top N predictions with their probabilities.

    Returns:
        List[dict]: Each token's top N predictions (converted labels) with their probabilities.
    '''
    for prediction in predictions:
        # Update labels by converting to (form, pos)
        for label in prediction['predictions']:
            label_text = label['label']

            if '_' in label_text: # Has both form and pos
                label_split = label_text.split('_')
                form = label_split[0]
                pos = label_split[1]
            else: # Has only form or pos
                if label_text.isupper(): # POS is uppercased
                    form = ''
                    pos = label_text
                else:
                    form = label_text
                    pos = ''

            label['label'] = (form, pos)
    return predictions


def rewriter_decorator_BERT(text_obj, word_index, span):
    """
    Decorator function for <code>BertTokens2WordsRewriter</code>. \n
    Aggregates the <code>morph_labels</code> and <code>probabilities</code> from <code>shared_bert_tokens</code>, finds the most
    common top-1 label, and retrieves the top N labels and their probabilities from the
    first token that contains this top-1 label.

    Args:
        text_obj: EstNLTK Text object.
        words_index: Index of the word in <code>words</code> layer.
        span: EstNLTK's Span object.

    Returns:
        dict: Annotations with the top N labels and probabilities for the word/phrase.
    """

    # Step 1: Find the most frequent top-1 label across all tokens
    top_1_label_counts = collections.Counter()

    for sp in span:
        top_1_label = sp['morph_label'][0] # Get top-1 label
        top_1_label_counts[top_1_label] += 1  # Count occurrences of each top-1 label

    # Identify the most frequent top-1 label
    most_frequent_label = top_1_label_counts.most_common(1)[0][0]
    annotations = list()

    # Step 2: Find the first token that has this most frequent top-1 label
    for sp in span:
        if most_frequent_label in sp['morph_label']:

            # Extract the top N labels and their probabilities starting from this label
            labels = sp['morph_label']
            probabilities = sp['probability']

            assert len(labels) == len(probabilities)

            for (label, prob) in zip(labels, probabilities):
                annotation = {
                'bert_tokens': [sp['bert_tokens'][0] for sp in span],
                'morph_label': label,
                'probability': prob
                }
                annotations.append(annotation)

            # Return the final annotation
            return annotations

    # Fallback if no label found (shouldn't happen)
    raise RuntimeError(f'Could not find a token with this label: {most_frequent_label}')

def rewriter_decorator_Vabamorf(text_obj, word_index, span):
    """
    Decorator function for <code>BertTokens2WordsRewriter</code>. \n
    Aggregates the <code>form</code>, <code>partofspeech</code> and <code>probabilities</code> from <code>shared_bert_tokens</code>, finds the most
    common top-1 label, and retrieves the top N labels and their probabilities from the
    first token that contains this top-1 label.

    Args:
        text_obj: EstNLTK Text object.
        words_index: Index of the word in <code>words</code> layer.
        span: EstNLTK's Span object.

    Returns:
        dict: Annotations with the top N labels and probabilities for the word/phrase.
    """

    # Step 1: Find the most frequent top-1 label across all tokens
    top_1_label_counts = collections.Counter()
    for sp in span:
        forms = sp['form']
        poses = sp['partofspeech']
        for form, pos in zip(forms, poses):
            top_1_label = form + '_' + pos # Get top-1 label
            top_1_label_counts[top_1_label] += 1  # Count occurrences of each top-1 label

    # Identify the most frequent top-1 label
    most_frequent_label = top_1_label_counts.most_common(1)[0][0]
    annotations = list()

    # Step 2: Find the first token that has this most frequent top-1 label
    for sp in span:
        form = most_frequent_label.split('_')[0]
        pos = most_frequent_label.split('_')[1]
        if form in sp['form'] and pos in sp['partofspeech']:

            # Extract the top N labels and their probabilities starting from this label
            tokens = [sp['bert_tokens'][0] for sp in span]
            forms = sp['form']
            poses = sp['partofspeech']
            probabilities = sp['probability']
            for form, pos, probability in zip(forms, poses, probabilities):
                annotation = {
                                'bert_tokens': tokens,
                                'form': form,
                                'partofspeech': pos,
                                'probability': probability
                            }
                annotations.append(annotation)

            # Return the final annotation
            return annotations

    # Fallback if no label found (shouldn't happen)
    raise RuntimeError(f'Could not find a token with this label: {most_frequent_label}')


def _split_sentence_into_smaller_chunks(large_sent: str, max_size:int=1000, seek_end_symbols: str='.!?'):
    """
    Splits given large_sent into smaller texts following the text size limit.
    Each smaller text string is allowed to have at most `max_size` characters.
    Returns smaller text strings and their (start, end) indexes in the large_sent.
    """
    assert max_size > 0, f'(!) Invalid batch size: {max_size}'
    if len(large_sent) < max_size:
        return [large_sent], [(0, len(large_sent))]
    chunks = []
    chunk_separators = []
    chunk_indexes = []
    last_chunk_end = 0
    while last_chunk_end < len(large_sent):
        chunk_start = last_chunk_end
        chunk_end = chunk_start + max_size
        if chunk_end >= len(large_sent):
            chunk_end = len(large_sent)
        if isinstance(seek_end_symbols, str):
            # Heuristic: Try to find the last position in the chunk that
            # resembles sentence ending (matches one of the seek_end_symbols)
            i = chunk_end - 1
            while i > chunk_start + 1:
                char = large_sent[i]
                if char in seek_end_symbols:
                    chunk_end = i + 1
                    break
                i -= 1
        chunks.append( large_sent[chunk_start:chunk_end] )
        chunk_indexes.append( (chunk_start, chunk_end) )
        # Find next chunk_start, skip space characters
        updated_chunk_end = chunk_end
        if chunk_end != len(large_sent):
            i = chunk_end
            while i < len(large_sent):
                char = large_sent[i]
                if not char.isspace():
                    updated_chunk_end = i
                    break
                i += 1
            chunk_separators.append( large_sent[chunk_end:updated_chunk_end] )
        last_chunk_end = updated_chunk_end
    assert len(chunk_separators) == len(chunks) - 1
    # Return extracted chunks
    return ( chunks, chunk_indexes )