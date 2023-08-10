#
#  BatchProcessingWebTagger -- a web tagger that processes input via small batches
#                              ( splits large requests into smaller ones )
#
from typing import MutableMapping

from estnltk import Text
from estnltk import Layer
from estnltk.web_taggers import WebTagger

from estnltk_core.layer_operations import join_layers_while_reusing_spans
from estnltk_core.layer_operations import extract_sections

from estnltk import logger

class BatchProcessingWebTaggerError(Exception):
    pass


class BatchProcessingWebTagger( WebTagger ):
    '''A web tagger that processes large requests via small batches.
    
    There are two working modes:

    A) batch splitting guided by text size limits:

    *) `batch_max_size` -- the maximum size for the text string in Text object: 
       if this size is exceeded, then the text string will be split into smaller 
       chunks and processed chunk by chunk. However, no layer splitting is 
       performed. 
    *) `batch_layer` -- must be None;
    *) `batch_enveloping_layer` -- must be None;

    Note: this mode assumes that the tagger works on raw text -- no input_layers 
    can be defined in the web tagger.

    B) batch splitting guided by layer size limits:

    *) `batch_layer` -- name of the layer which size is constrained while batching;
       mandatory parameter.
    *) `batch_max_size` -- the maximum size for the batch layer: if this size is 
       exceeded, then Text object will be split into smaller chunks and processed 
       chunk by chunk; mandatory parameter.
    *) `batch_enveloping_layer` -- a layer enveloping the batch_layer. If set, then 
       tries to follow the boundaries of the enveloping layer while splitting. 
       An optional parameter, can be undefined.
    '''
    conf_param = ['url', 'batch_layer', 'batch_max_size', 'batch_enveloping_layer']

    def post_request(self, text: Text, layers: MutableMapping[str, Layer], parameters=None):
        assert self.batch_max_size is not None and \
                    isinstance(self.batch_max_size, int)
        if self.batch_layer is not None:
            # ================================================
            #  batch splitting guided by layer size limit
            # ================================================
            assert isinstance(self.batch_layer, str) and \
                   self.batch_layer in layers
            assert self.batch_enveloping_layer is None or \
                   isinstance(self.batch_enveloping_layer, str)
            if len( layers[self.batch_layer] ) > self.batch_max_size:
                # Note: normally, if batch processing works fine, this exception should never be thrown
                raise BatchProcessingWebTaggerError('(!) The request Text object exceeds the web service '+\
                               ('limit {} {!r} per text. '.format(self.batch_max_size, self.batch_layer))+\
                                'Please use EstNLTK\'s methods extract_sections or split_by to split the Text object '+\
                                'into smaller Texts, and proceed by processing smaller Texts with the web service. '+\
                                'More information about Text splitting: '+\
                                'https://github.com/estnltk/estnltk/blob/main/tutorials/system/layer_operations.ipynb ')
        else:
            # ================================================
            #  batch splitting guided by text size limit
            # ================================================
            if len(layers) > 0:
                raise BatchProcessingWebTaggerError('(!) The request Text object unexpectedly contains layers '+\
                                                    'in text size limited splitting mode.')
            if len( text.text ) > self.batch_max_size:
                # Note: normally, if batch processing works fine, this exception should never be thrown
                raise BatchProcessingWebTaggerError('(!) The request Text object exceeds the web service '+\
                                                    'limit of maximum {} character size text.'.format(self.batch_max_size))
        return super().post_request( text, layers, parameters=parameters )

    def batch_process(self, text: Text, layers: MutableMapping[str, Layer], parameters=None):
        assert self.batch_max_size is not None and \
                    isinstance(self.batch_max_size, int)
        if self.batch_layer is not None:
            # ================================================
            #  batch splitting guided by layer size limit
            # ================================================
            assert isinstance(self.batch_layer, str) and \
                   self.batch_layer in layers
            assert self.batch_enveloping_layer is None or \
                   isinstance(self.batch_enveloping_layer, str)
            if len( layers[ self.batch_layer ] ) > self.batch_max_size:
                # A) Text/layer is too big: apply batched processing
                logger.debug('Input layer {!r} size exceeds limit {!r}. Applying batch processing ...'.format( \
                              self.batch_layer, self.batch_max_size ) )
                # Check if all layers are attached
                target_text = text
                all_layers_attached = True
                for layer in layers.keys():
                    if layer not in text.layers:
                        all_layers_attached = False
                        break
                    if layer in text.relation_layers:
                        raise NotImplementedError('(!) Cannot use relation layer {!r} as an input layer for batch '+\
                                                  'processing web tagger. Functionality not implemented.'.format(layer))
                if not all_layers_attached:
                    # In case of detached layers, create a new surrogate Text obj 
                    # with attached layers
                    target_text = Text( text.text )
                    for layer in Text.topological_sort(layers):
                        target_text.add_layer(layer)
                # Split large Text obj into smaller ones
                smaller_texts, separators = self._split_text_into_smaller_texts_via_layer( target_text )
                # Process smaller Texts
                logger.debug( 'Batch processing {!r} chunks ...'.format(len(smaller_texts)) )
                resulting_layers = []
                for small_text in smaller_texts:
                    small_text_layers = {l: small_text[l] for l in small_text.layers}
                    new_layer = self.post_request(small_text, small_text_layers, parameters=parameters)
                    resulting_layers.append( new_layer )
                logger.debug( 'Batch processing completed.'.format() )
                # Join/concatenate results
                new_layer = join_layers_while_reusing_spans( resulting_layers, separators )
                # Set Text object and return newly created layer
                new_layer.text_object = text
                return new_layer
            else:
                # B) Apply regular processing
                return self.post_request(text, layers, parameters=parameters)
        else:
            # ================================================
            #  batch splitting guided by text size limit
            # ================================================
            if len(self.input_layers) > 0:
                raise BatchProcessingWebTaggerError('(!) BatchProcessingWebTagger cannot have input_layers '+\
                                                    'in text size limited splitting mode.')
            assert self.batch_enveloping_layer is None
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


    # ================================================
    #  batch splitting guided by layer size limit
    # ================================================

    def _split_text_into_smaller_texts_via_layer( self, large_text: Text ):
        '''Splits given large_text into smaller texts following the layer size limit. 
           Each smaller Text object is allowed to have at most `self.batch_max_size` 
           spans of the `self.batch_layer`. 
           If `self.batch_enveloping_layer` is defined, then considers the boundaries 
           of the enveloping layer while splitting. 
           Returns smaller text objects and string separators between texts (for later joining).
        '''
        assert isinstance(self.batch_layer, str) and \
               self.batch_layer in large_text.layers
        if self.batch_enveloping_layer is not None:
            assert self.batch_enveloping_layer in large_text.layers
        assert self.batch_max_size > 0
        chunks = []
        cur_chunk_size = 0
        trimming_required = False
        if self.batch_enveloping_layer is not None:
            # A) Chunk the layer into pieces considering the boundaries of the enveloping layer
            for env_layer in large_text[ self.batch_enveloping_layer  ]:
                # Initialize the first chunk
                if len(chunks) == 0:
                    chunks = [[0, -1]]
                # Check if the chunk exceeds the size limit
                if cur_chunk_size + len(env_layer) >= self.batch_max_size:
                    # Start a new chunk
                    chunks.append( [env_layer.start, -1] )
                    cur_chunk_size = 0
                # Complete the last chunk
                chunks[-1][-1] = env_layer.end
                cur_chunk_size += len(env_layer)
                # If the current sentence itself is bigger than the maximum size,
                # then attempt to split the sentence into subsentences considering
                # the maximum size
                if cur_chunk_size >= self.batch_max_size:
                    if chunks[-1][0] == env_layer.start:
                        # Remove mistakenly added new chunk
                        chunks.pop(-1)
                    if chunks[-1][0] == 0 and chunks[-1][1] == -1:
                        # Remove mistakenly added first chunk
                        chunks.pop(-1)
                    sub_words = 0
                    last_chunk_start = env_layer.start if chunks else 0
                    for wid, word in enumerate( env_layer ):
                        sub_words += 1
                        if sub_words == self.batch_max_size:
                            chunks.append( [last_chunk_start, word.end] )
                            if wid + 1 < len(env_layer):
                                last_chunk_start = env_layer[wid + 1].start
                            sub_words = 0
                        elif wid + 1 == len(env_layer):
                            assert last_chunk_start < word.end
                            chunks.append( [last_chunk_start, word.end] )
                    trimming_required = True
        else:
            # B) Chunk the layer into pieces only based on the target batch layer
            cur_chunk_size = 0
            last_chunk_start = None
            for wid, word in enumerate( large_text[ self.batch_layer ] ):
                if last_chunk_start is None:
                    last_chunk_start = 0
                cur_chunk_size += 1
                if cur_chunk_size == self.batch_max_size:
                    chunks.append( [last_chunk_start, word.end] )
                    if wid + 1 < len( large_text[ self.batch_layer ] ):
                        last_chunk_start = large_text[ self.batch_layer ][wid + 1].start
                    cur_chunk_size = 0
                elif wid + 1 == len( large_text[ self.batch_layer ] ):
                    assert last_chunk_start < word.end
                    chunks.append( [last_chunk_start, word.end] )
        # Find chunk separators
        chunk_separators = []
        last_chunk = None
        for [c_start, c_end] in chunks:
            if last_chunk is not None:
                chunk_separators.append( large_text.text[ last_chunk[-1]:c_start ] )
            last_chunk = [c_start, c_end]
        assert len(chunk_separators) == len(chunks) - 1
        # Exctract chunks
        return ( extract_sections(text=large_text, sections=chunks, layers_to_keep=large_text.layers, \
                                  trim_overlapping=trimming_required), chunk_separators )

    def _repr_html_(self):
        return self._repr_html('BatchProcessingWebTagger', self.about)