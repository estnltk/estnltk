from typing import MutableMapping

import requests

from estnltk_core.layer_operations import join_layers_while_reusing_spans

from estnltk import Text
from estnltk import Layer
from estnltk.taggers import Tagger

from estnltk import logger

class GrammarCorrectorWebTagger( Tagger ):
    """Tags grammatical error correction suggestions in text via TartuNLP's webservice.
    IMPORTANT: Using this tagger means that the data will be processed by the public TartuNLP API. 
    This means that the text will be uploaded and can be read by a third party.
    """
    conf_param = ['url', 'batch_max_size']

    def __init__(self, output_layer='grammar_corrections', url="https://api.tartunlp.ai/grammar"):
        self.url = url
        self.output_layer = output_layer
        self.output_attributes = ('correction', )
        self.input_layers = []
        self.batch_max_size = 10000  # max size in characters

    def post_request(self, text: Text, layers: MutableMapping[str, Layer], parameters=None):
        if len( text.text ) > self.batch_max_size:
            # Note: normally, if batch processing works fine, this exception should never be thrown
            raise Exception('(!) The request Text object exceeds the web service '+\
                            'limit of maximum {} character size text.'.format(self.batch_max_size))
        request_body = { "language": "et", "text": text.text }
        response = requests.post(self.url, json=request_body)
        response.raise_for_status()
        response = response.json()
        # Create layer based on processing results
        layer = Layer(name=self.output_layer, attributes=self.output_attributes, ambiguous=True)
        layer.text_object = text
        for suggested_correction in response.get('corrections', []):
            # Webservice output example:
            # [{'replacements': [{'value': 'Grammatiliste vigade parandamine'}],
            #   'span': {'end': 31, 'start': 0, 'value': 'Gramatikliste veade parantamine'}},
            assert 'span' in suggested_correction
            assert 'replacements' in suggested_correction
            base_span = (suggested_correction['span']['start'], suggested_correction['span']['end'])
            text_snippet = suggested_correction['span']['value']
            assert text_snippet == text.text[base_span[0]:base_span[1]]
            for replacement in suggested_correction['replacements']:
                layer.add_annotation(base_span, {'correction': replacement['value']})
        return layer

    def batch_process(self, text: Text, layers: MutableMapping[str, Layer], parameters=None):
        assert self.batch_max_size is not None and \
                    isinstance(self.batch_max_size, int)
        # ================================================
        #  batch splitting guided by text size limit
        # ================================================
        if len( text.text ) > self.batch_max_size:
            # A) Text is too big: apply batched processing
            logger.debug('Text size exceeds limit {!r}. Applying batch processing ...'.format( \
                          self.batch_max_size ) )
            # Split large Text obj into smaller ones
            smaller_texts, separators = self._split_text_into_smaller_texts_via_string( text )
            # Process smaller Texts
            logger.debug( 'Batch processing {!r} chunks ...'.format(len(smaller_texts)) )
            resulting_layers = []
            for small_text in smaller_texts:
                new_layer = self.post_request(small_text, {}, parameters=parameters)
                resulting_layers.append( new_layer )
            logger.debug( 'Batch processing completed.'.format() )
            # Join/concatenate results
            new_layer = join_layers_while_reusing_spans( resulting_layers, separators )
            # Set Text object and return newly created layer
            new_layer.text_object = text
            return new_layer
        else:
            # B) Apply regular processing
            return self.post_request(text, {}, parameters=parameters)

    def _make_layer(self, text: Text, layers: MutableMapping[str, Layer], status: dict):
        layer = self.batch_process(text, layers)
        return layer

    # ================================================
    #  batch splitting guided by text size limit
    # ================================================

    def _split_text_into_smaller_texts_via_string( self, large_text: Text, seek_end_symbols: str='.!?' ):
        '''Splits given large_text into smaller texts following the text size limit. 
           Each smaller Text object's text string is allowed to have at most 
           `self.batch_max_size` characters.
           Returns smaller text objects and string separators between texts (for later joining).
        '''
        assert self.batch_layer is None
        assert self.batch_enveloping_layer is None
        assert self.batch_max_size > 0
        chunks = []
        chunk_separators = []
        last_chunk_end = 0
        while last_chunk_end < len(large_text.text):
            chunk_start = last_chunk_end
            chunk_end = chunk_start + self.batch_max_size
            if chunk_end >= len(large_text.text):
                chunk_end = len(large_text.text)
            if isinstance(seek_end_symbols, str):
                # Heuristic: Try to find the last position in the chunk that 
                # resembles sentence ending (matches one of the seek_end_symbols)
                i = chunk_end-1
                while i > chunk_start+1:
                    char = large_text.text[i]
                    if char in seek_end_symbols:
                        chunk_end = i+1
                        break
                    i -= 1
            chunks.append( Text(large_text.text[chunk_start:chunk_end]) )
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
        return ( chunks, chunk_separators )

    @property
    def about(self) -> str:
        raise NotImplementedError

    @property
    def status(self) -> str:
        status_resp = requests.get(self.url+'/health/liveness')
        status_resp.raise_for_status()
        return (status_resp.text).strip('"')

    @property
    def is_alive(self) -> bool:
        return self.status == 'OK'