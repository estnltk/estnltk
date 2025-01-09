#
# GliLemTagger: Vabamorf's analysis/lemmatization enhanced with a GLiNER model
# Building upon adorkin's GliLem demo: 
# https://huggingface.co/spaces/adorkin/GliLem/tree/fc03dac178c5c0e8b5206f07e47a60ba372da995
# This tagger works either as a tagger or as a retagger/disambiguator.
# 

import os
import warnings

from typing import MutableMapping, List, Optional

from estnltk import Text, Layer, Retagger
from estnltk.downloader import get_resource_paths

from estnltk_neural.taggers.embeddings.bert.bert_tokens_to_words_rewriter import BertTokens2WordsRewriter

from estnltk_neural.taggers.neural_morph.glilem.rule_processor import RuleProcessor
from estnltk_neural.taggers.neural_morph.glilem.vabamorf_glilem_lemmatizer import Lemmatizer
from estnltk_neural.taggers.neural_morph.glilem.vabamorf_glilem_lemmatizer import create_glilem_layer


def gilem_decorator(text, word_id, gilem_tokens):
    if len(gilem_tokens) > 0:
        if len(gilem_tokens) > 1:
            warnings.warn(f'(!) word {text["words"][word_id].text!r} mapped to multiple gilem tokens: {gilem_tokens!r}')
        return {'lemma': gilem_tokens[0].annotations[0]['lemma'],
                'score': gilem_tokens[0].annotations[0]['score'],
                'label': gilem_tokens[0].annotations[0]['label'],
                'vabamorf_overwritten': gilem_tokens[0].annotations[0]['vabamorf_overwritten'],
                'is_input_token': gilem_tokens[0].annotations[0]['is_input_token']}


class GliLemTagger(Retagger):
    """Applies GliLem lemmatization or disambiguates Vabamorf's morph_analysis layer with GliLem. 
       
       This tagger works either as a tagger (A) or as a retagger (B), depending on 
       whether the flag <code>disambiguate</code> is disabled or enabled. As a Tagger, 
       it creates a new layer with glilem annotations, while as a Retagger, it disambiguates 
       an existing morphological analysis layer that has annotations in Vabamorf's tagset. 
       
       A) If <code>disambiguate</code> is False, then the tagger works as a tagger and 
       a new morph layer (<code>output_layer</code>) can be created by calling tagger's 
       tag(...) or make_layer(...) methods. 
       
       B) If <code>disambiguate</code> is True, then <code>output_layer</code> must be set 
       to a morphological analysis layer (which will become an input layer) and which then 
       can be disambiguated by calling tagger's retag(...) or change_layer(...) methods. 
       
       Building upon the GliLem demo:
       https://huggingface.co/spaces/adorkin/GliLem/tree/fc03dac178c5c0e8b5206f07e47a60ba372da995
    """

    def __init__(
        self,
        model_location: Optional[str] = None,
        output_layer: str = 'glilem', 
        missing_lemmas_strategy: str = "DISCARD", 
        disambiguate: bool = False
    ):
        """
        Initializes GliLemTagger

        Args:
            model_location (str, Optional): 
                Path to the GliLemTagger's model files directory. If not provided (default), then 
                attempts to use glilem model from estnltk_resources. If that fails (model is missing 
                and downloading fails), then throws an exception.
            output_layer (str): 
                Name of the output layer. Defaults to 'glilem'. If <code>disambiguate==True</code>, then 
                this must be name a Vabamorf-based morph analysis layer which will be disambiguated by 
                calling tagger's <code>retag</code> method. 
            missing_lemmas_strategy (str):
                What to do if GliLem does not produce any lemma for a word? Options:
                * "DISCARD" (default) -- do no produce any spans for such words;
                * "NONE_VALUES" -- add missing spans with None values;
                * "VABAMORF_LEMMAS" -- add missing spans from underlying Vabamorf's lemmatizer;
                  Note: the underlying Vabamorf's lemmatizer uses settings compound=False,
                  disambiguate=False, guess=False, slang_lex=False, propername=True by default;
                Whether the tagger is to be used as an disambiguator of an input morph analyis layer. 
                Defaults to False. If set, then GliLemTagger can be used to disambiguate an existing 
                Vabamorf-based morph analysis layer by calling <code>GliLemTagger.retag(text_obj)</code>. 
                Note that the input <code>text_obj</code> must already have <code>output_layer<code> 
                which will be disambiguated. 
        """
        from gliner import GLiNER
        self.conf_param = ('model', 'missing_lemmas_strategy', 'disambiguate', '_lemmatizer', 
                           '_rule_processor', '_bert_tokens_rewriter')
        if missing_lemmas_strategy is None:
            missing_lemmas_strategy = "DISCARD"
        assert missing_lemmas_strategy.lower() in ['discard', 'none_values', 'vabamorf_lemmas'], \
            f'(!) Unexpected value {missing_lemmas_strategy!r} for parameter missing_lemmas_strategy. '+\
            ' Allowed values are: "discard", "none_values", "vabamorf_lemmas".'
        self.missing_lemmas_strategy = missing_lemmas_strategy.lower()
        if model_location is None:
            # Try to get the resources path for glilem_vabamorf_disambiguator. Attempt to download, if missing
            resources_path = get_resource_paths("glilem_vabamorf_disambiguator", only_latest=True, download_missing=True)
            if resources_path is None:
                raise Exception( "GliLemTagger's resources have not been downloaded. "+\
                                 "Use estnltk.download('glilem') to get the missing resources. "+\
                                 "Alternatively, you can specify the directory containing the model "+\
                                 "via parameter model_location at creating the tagger." )
            model_location = resources_path
        else:
            model_location = model_location
        #model_location = "tartuNLP/glilem-vabamorf-disambiguator"
        self.model = GLiNER.from_pretrained(model_location, model_max_length=512)
        self.output_layer = output_layer
        self.input_layers = ['words', 'compound_tokens', 'sentences']
        self._rule_processor = RuleProcessor()
        self._lemmatizer = Lemmatizer(
            disambiguate=False, use_context=False, proper_name=True, separate_punctuation=True
        )
        self.output_attributes = ('lemma', 'score', 'label', 'vabamorf_overwritten', 'is_input_token')
        self._bert_tokens_rewriter = BertTokens2WordsRewriter(
            bert_tokens_layer='_glilem_tokens', 
            input_words_layer=self.input_layers[0], 
            output_attributes=self.output_attributes, 
            output_layer=self.output_layer, 
            enveloping=False, 
            ambiguous=True, 
            decorator=gilem_decorator)
        self.disambiguate = disambiguate
        if self.disambiguate:
            self.input_layers = list(self.input_layers) + [self.output_layer]

    def _make_layer_template(self):
        """Creates and returns a template of the layer."""
        layer = Layer(name=self.output_layer,
                      text_object=None,
                      attributes=self.output_attributes,
                      parent=self.input_layers[0], 
                      ambiguous=False )
        return layer

    def _make_layer(self, text: Text, layers: MutableMapping[str, Layer], status: dict) -> Layer:
        """
        Processes the input text to generate a GliLem layer. 
        """
        words_layer = layers[ self.input_layers[0] ]
        sentences_layer = layers[ self.input_layers[-1] ]
        glilem_layer = Layer(name='_glilem_tokens', text_object=text, ambiguous=True, 
                             attributes=('lemma', 'score', 'label', 'vabamorf_overwritten', 'is_input_token'))
        for k, sentence in enumerate( sentences_layer ):
            sent_start = sentence.start
            sent_text  = sentence.enclosing_text
            # Apply batch processing: split larger input sentence into smaller chunks and process chunk by chunk
            sent_chunks, sent_chunk_indexes = _split_sentence_into_smaller_chunks(sent_text)
            for sent_chunk, (chunk_start, chunk_end) in zip(sent_chunks, sent_chunk_indexes):
                # Get predictions for the sentence
                chunk_glilem_layer = create_glilem_layer( sent_chunk, self.model, output_layer='_glilem_tokens',
                                     add_missing_lemmas_from_vabamorf=(self.missing_lemmas_strategy=='vabamorf_lemmas'))
                for chunk_span in chunk_glilem_layer:
                    start = chunk_span.start
                    end = chunk_span.end
                    new_span = (sent_start + chunk_start + start, sent_start + chunk_start + end)
                    chunk_annotation = chunk_span.annotations[0]
                    annotation = { 'lemma': chunk_annotation['lemma'],
                                   'score': chunk_annotation['score'],
                                   'label': chunk_annotation['label'],
                                   'vabamorf_overwritten': chunk_annotation['vabamorf_overwritten'],
                                   'is_input_token': chunk_annotation['is_input_token'] }
                    glilem_layer.add_annotation(new_span, **annotation)
        # Aggregate tokens back into words in the original input tokenization
        # Use BertTokens2WordsRewriter to convert BERT tokens to words
        mapped_layer = self._bert_tokens_rewriter.make_layer(text, layers={'_glilem_tokens': glilem_layer,
                                                                          'words': layers['words']})
        # Note: there is no guarantee that there is a glilem analysis for every word
        # If required, then add spans missing from glilem output with None values
        if self.missing_lemmas_strategy == 'none_values':
            for word_span in words_layer:
                if word_span.base_span not in mapped_layer._span_list: # An efficient way to check for span existence
                    new_span = word_span.base_span
                    annotation = { 'lemma': None,
                                   'score': None,
                                   'label': None,
                                   'vabamorf_overwritten': None,
                                   'is_input_token': True }
                    mapped_layer.add_annotation(new_span, **annotation)
        return mapped_layer

    def _change_layer(self, text, layers, status=None):
        # Validate configuration
        if not self.disambiguate:
            raise Exception( ('(!) Cannot use GliLemTagger as a disambiguator if '+\
                              'disambiguate is set False.') )
        # Validate inputs
        morph_layer = layers[self.output_layer]
        if 'lemma' not in morph_layer.attributes:
            raise Exception( ('(!) Missing attribute {!r} in output_layer {!r}.'+\
                              '').format('lemma', morph_layer.name) )
        # Create disambiguation layer
        disamb_layer = self._make_layer(text, layers, status)
        disamb_idx = 0
        for original_word in morph_layer:
            if disamb_idx < len(disamb_layer):
                disamb_word = disamb_layer[disamb_idx]
                if disamb_word.base_span == original_word.base_span:
                    # Matching spans
                    disamb_lemma = disamb_word.annotations[0]['lemma']
                    # Filter annotations of the original morph layer: keep only those
                    # annotations that are matching with the disambiguated annotation
                    keep_annotations = []
                    for annotation in original_word.annotations:
                        if annotation['lemma'] == disamb_lemma:
                            keep_annotations.append(annotation)
                    if len(keep_annotations) > 0:
                        # Only disambiguate if there is at least one annotation left
                        # (can't leave a word without any annotations)
                        original_word.clear_annotations()
                        for annotation in keep_annotations:
                            original_word.add_annotation( annotation )
                    disamb_idx += 1


def _split_sentence_into_smaller_chunks(large_sent: str, max_size:int=1000, seek_end_symbols: str='.!?'):
    """
    Splits given large_sent into smaller texts following the text size limit.
    Each smaller text string is allowed to have at most `max_size` characters.
    Returns smaller text strings and their (start, end) indexes in the large_sent.
    
    Original source:
    https://bitbucket.org/utDigiHum/public/src/master/skriptid/nimeuksuste_m2rgendamine/bert_ner_tagger.py
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

