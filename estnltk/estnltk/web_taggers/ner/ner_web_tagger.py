from typing import MutableMapping, List, Tuple

import time
from difflib import Differ

import requests

from estnltk_core.taggers import MultiLayerTagger
from estnltk import Text, Layer


class NerWebTagger(MultiLayerTagger):
    '''
    NER tagger that uses TartuNLP's NER web service. 
    IMPORTANT: Using this tagger means that the data will be processed by the public TartuNLP API. 
    This means that the text will be uploaded and can be read by a third party.
    '''
    conf_param = ['custom_words_layer', 'url', 'batch_size', '_differ']

    def __init__(self, url='https://api.tartunlp.ai/bert/ner/v1', 
                       ner_output_layer='webner', tokens_output_layer ='nertokens', 
                       custom_words_layer='words', batch_size = 4500):
        '''
        Initializes NerWebTagger that uses TartuNLP's NER web service for tagging.
        
        Parameters
        ----------
        url: str
            URL of the web service. Defaults to the TartuNLP neural NER web service URL. 
        ner_output_layer: str
            Name of the output named entity annotations layer. 
            Default: 'webner'.
        tokens_output_layer: str
            Name of the auxiliary tokens layer, which is created during named entity recognition. 
            If custom_words_layer is None, then tokens_output_layer will be added to output 
            layers, and tokens of this layer will be enveloped by the output NE layer. 
            Otherwise, the output NE layer will be enveloping custom_words_layer, and 
            tokens_output_layer will not be added to output layers.
            Note that tokenization in this layer can diverge from EstNLTK's default 'words' 
            tokenization. 
            Default: 'nertokens'.
        custom_words_layer: str
            Name of a customized words layer that is taken as a basis on enveloping named 
            entity annotations instead of tokens_output_layer. 
            Default: 'words'. 
        batch_size: int
            Maximum batch size (in characters) that is processed as a whole by the webservice. 
            The input text is split into batches of the given size before processing. 
            Default: 4500
        '''
        output_layers = ['ner'] if ner_output_layer is None else [ner_output_layer]

        self.url = url
        self.output_layers = output_layers
        self.output_layers_to_attributes = {output_layers[0]: ["nertag"]}
        if custom_words_layer is None:
            self.output_layers.append(tokens_output_layer)
            self.output_layers_to_attributes[output_layers[1]] = []
            self.input_layers = []
        else:
            self.input_layers = [custom_words_layer]
            # use Differ for comparing custom words with the web-service words
            self._differ = Differ()
        self.custom_words_layer = custom_words_layer
        self.batch_size = batch_size

    def get_ner_word_spans(self, text, response):
        base_spans = []
        current_idx = 1
        for snt in response['result']:
            current_idx -= 1
            snt_idx = current_idx
            for word in snt:
                while text.text[current_idx:current_idx + len(word['word'])] != word['word']:
                    current_idx += 1
                    if current_idx >= len(text.text):
                        raise Exception(f"(!) Cannot find word {word['word']!r} from the sentence {text.text[snt_idx:snt_idx+500]!r}.")
                base_spans.append( (current_idx, current_idx + len(word['word'])) )
                current_idx += len(word['word'])
        return base_spans

    def _make_layers(self, text: Text, layers: MutableMapping[str, Layer], status: dict) -> Layer:
        nertag_attr = self.output_layers_to_attributes[self.output_layers[0]][0]
        # Apply batch processing: split input text into smaller batches and process batch by batch
        text_chunks, text_indexes = _split_text_into_smaller_texts(text, max_size=self.batch_size)
        chunk_count = 0
        all_ne_spans = []
        all_ner_word_spans = []
        all_ner_word_labels = []
        for text_chunk, (chunk_start, chunk_end) in zip(text_chunks, text_indexes):
            chunk_count += 1
            if chunk_count > 1:
                time.sleep(2) # pause before processing next chunk
            #logger.debug( f'Processing chunk {chunk_count} out of {len(text_chunks)} chunks.' )
            text_chunk_obj = Text(text_chunk)
            response = self.post_request(text_chunk_obj)
            cur_word_spans = self.get_ner_word_spans(text_chunk_obj, response)
            cur_labels = [word['ner'] for snt in response['result'] for word in snt]
            assert len(cur_word_spans) == len(cur_labels)
            entity_spans = []
            entity_type = None
            # Collect NE phrases & corresponding word spans
            for base_span, label in zip(cur_word_spans, cur_labels):
                corrected_base_span = (chunk_start+base_span[0], chunk_start+base_span[1])
                all_ner_word_spans.append( corrected_base_span )
                all_ner_word_labels.append( label )
                if entity_type is None:
                    entity_type = label[2:]
                if label == "O":
                    if entity_spans:
                        all_ne_spans.append( (entity_spans, {nertag_attr:entity_type}) )
                        entity_spans = []
                    continue
                if label[0] == "B" or entity_type != label[2:]:
                    if entity_spans:
                        all_ne_spans.append( (entity_spans, {nertag_attr:entity_type}) )
                        entity_spans = []
                entity_type = label[2:]
                entity_spans.append( corrected_base_span )
        assert len(all_ner_word_spans) == len(all_ner_word_labels)
        # Create layers
        nerlayer = Layer(name=self.output_layers[0], 
                         attributes=self.output_layers_to_attributes[self.output_layers[0]],
                         text_object=text)
        if self.custom_words_layer is None:
            # Use the original words tokanization as a basis for NER
            # (note, according to https://github.com/TartuNLP/bert-ner-service/tree/master ,
            #  this is stanza's "et" tokenization)
            wordslayer = Layer(name=self.output_layers[1], \
                               attributes=self.output_layers_to_attributes[self.output_layers[1]], \
                               text_object=text, enveloping=None, ambiguous=False)
            for (start, end) in all_ner_word_spans:
                wordslayer.add_annotation( (start, end) )
            nerlayer.enveloping = wordslayer.name
            for entity_spans, annotation_dict in all_ne_spans:
                nerlayer.add_annotation( entity_spans, annotation_dict )
        else:
            # Use the customized words layer as a basis for NER
            wordslayer = layers[self.input_layers[0]]
            nerlayer.enveloping = wordslayer.name
            # Fix and merge NE labels
            fixed_labels = \
                self._fix_and_merge_ne_labels(text, wordslayer, all_ner_word_spans, all_ner_word_labels)
            # Create NE annotations according to fixed labelling
            entity_spans = []
            entity_type = None
            for wid, word in enumerate(wordslayer):
                label = fixed_labels[wid]
                if entity_type is None:
                    entity_type = label[2:]
                if label == "O":
                    if entity_spans:
                        nerlayer.add_annotation( entity_spans, {nertag_attr:entity_type} )
                        entity_spans = []
                    continue
                if label[0] == "B" or entity_type != label[2:]:
                    if entity_spans:
                        nerlayer.add_annotation( entity_spans, {nertag_attr:entity_type} )
                        entity_spans = []
                entity_type = label[2:]
                entity_spans.append( word.base_span )
        # Return results
        nerlayer.name = self.output_layers[0]
        returnable_dict = { self.output_layers[0]: nerlayer }
        if self.custom_words_layer is None:
            wordslayer.name = self.output_layers[1]
            returnable_dict = { self.output_layers[1]: wordslayer, 
                                self.output_layers[0]: nerlayer }
        return returnable_dict

    def post_request(self, text: Text):
        data = {
            'text': text.text
        }
        resp = requests.post(self.url, json=data)
        resp.raise_for_status()
        return resp.json()

    def _map_custom_words_2_ws_words(self, text: Text, custom_words: Layer, ws_words: List[Tuple[int, int]]):
        '''
        Maps indexes of custom_words to indexes of corresponding ws_words. 
        Note that due to one-to-many and many-to-one (and also, possibly,
        many-to-many) correspondences, one custom_words index is mapped to 
        a list of ws_words indexes. 
        Returns a dict containing the mapping. 
        '''
        ws_words_texts = [text.text[s:e] for (s, e) in ws_words]
        custom_words_texts = [text.text[sp.start:sp.end] for sp in custom_words]
        difference = list(self._differ.compare(ws_words_texts, custom_words_texts))
        mapping = dict()
        i = 0; j = 0
        ws_diff = []; cw_diff = []
        for line in difference:
            line_clean = line.lstrip()
            if line_clean.startswith('- '):
                # only in ws_words
                word_str = line_clean[2:]
                assert ws_words_texts[i] == word_str
                # collect difference
                ws_diff.append( i )
                i += 1
            elif line_clean.startswith('+ '):
                # only in custom_words
                word_str = line_clean[2:]
                assert custom_words_texts[j] == word_str
                # collect difference
                cw_diff.append( j )
                j += 1
            elif not line_clean.startswith('? ') and len(line_clean) > 0:
                # in both
                assert ws_words_texts[i] == custom_words_texts[j]
                # record collected differences
                if ws_diff and cw_diff:
                    for item in cw_diff:
                        if item not in mapping:
                            mapping[item] = []
                        mapping[item].extend(ws_diff)
                    ws_diff = []; cw_diff = []
                # record mapping
                mapping[j] = [i]
                i += 1
                j += 1
        # record collected differences
        if ws_diff and cw_diff:
            for item in cw_diff:
                if item not in mapping:
                    mapping[item] = []
                mapping[item].extend(ws_diff)
        return mapping

    def _fix_and_merge_ne_labels(self, text, wordslayer, ner_word_spans, ner_word_labels):
        '''
        Creates a mapping from wordslayer to ner_word_spans and fixes/merges ner_word_labels 
        correspondingly. Returns a dict mapping from wordslayer indexes to corresponding NE 
        tags. 
        '''
        # Map indexes of words' layers
        custom_2_ws_map = \
            self._map_custom_words_2_ws_words(text, wordslayer, ner_word_spans)
        word2label = dict()
        last_ws_indexes = []
        last_entity_type = ''
        for wid, word in enumerate(wordslayer):
            ws_indexes = custom_2_ws_map[wid]
            ws_ner_labels = [ner_word_labels[i] for i in ws_indexes]
            for label in ws_ner_labels:
                cur_entity_type = label[2:]
                if label[0] == "B" or (label[0] == "I" and last_entity_type != cur_entity_type):
                    # Start of a new NE phrase
                    word2label[wid] = f'B-{cur_entity_type}'
                    last_entity_type = cur_entity_type
                    # Don't look further: consider the first 
                    # tag as a correct one
                    break
                elif label[0] == "I":
                    # Continue the old NE phrase
                    word2label[wid] = label
                last_entity_type = cur_entity_type
            if wid not in word2label:
                # If B/I were not encountered, then it is O instead
                word2label[wid] = 'O'
            if last_ws_indexes == ws_indexes:
                # This word maps to same ws_words as the previous word: 
                # consider it as a continuation of the last NE, if 
                # such exists
                assert wid-1 in word2label.keys()
                prev_label = word2label[wid-1]
                if prev_label[0] in ['B', 'I']:
                    # Continue the previous NE phrase
                    prev_label_type = prev_label[2:]
                    word2label[wid] = f'I-{prev_label_type}'
            last_ws_indexes = ws_indexes
        return word2label



def _split_text_into_smaller_texts(large_text: Text, max_size:int=1750, seek_end_symbols: str='.!?'):
    '''Splits given large_text into smaller texts following the text size limit. 
       Each smaller Text object's text string is allowed to have at most `max_size` characters.
       Returns smaller text strings and their (start, end) indexes in the original text.
    '''
    assert max_size > 0, f'(!) Invalid batch size: {max_size}'
    if len(large_text.text) < max_size:
        return [large_text.text], [(0, len(large_text.text))]
    chunks = []
    chunk_separators = []
    chunk_indexes = []
    last_chunk_end = 0
    while last_chunk_end < len(large_text.text):
        chunk_start = last_chunk_end
        chunk_end = chunk_start + max_size
        if chunk_end >= len(large_text.text):
            chunk_end = len(large_text.text)
        if isinstance(seek_end_symbols, str):
            # Heuristic: Try to find the last position in the chunk that 
            # resembles sentence ending (matches one of the seek_end_symbols)
            i = chunk_end - 1
            while i > chunk_start + 1:
                char = large_text.text[i]
                if char in seek_end_symbols:
                    chunk_end = i + 1
                    break
                i -= 1
        chunks.append( large_text.text[chunk_start:chunk_end] )
        chunk_indexes.append( (chunk_start, chunk_end) )
        # Find next chunk_start, skip space characters
        updated_chunk_end = chunk_end
        if chunk_end != len(large_text.text):
            i = chunk_end
            while i < len(large_text.text):
                char = large_text.text[i]
                if not char.isspace():
                    updated_chunk_end = i
                    break
                i += 1
            chunk_separators.append( large_text.text[chunk_end:updated_chunk_end] )
        last_chunk_end = updated_chunk_end
    assert len(chunk_separators) == len(chunks) - 1
    # Return extracted chunks
    return ( chunks, chunk_indexes )

