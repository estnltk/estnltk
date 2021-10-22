#
#  BatchProcessingWebTagger -- a web tagger that processes input via small batches
#                              ( splits large requests into smaller ones )
#  Mandatory configuration parameters:
#   * batch_layer -- name of the layer which size is constrained while batching;
#   * batch_layer_max_size -- the maximum size for the batch layer: if this size is 
#                             exceeded, then Text object will be split into smaller 
#                             chunks and processed chunk by chunk;
#  Optional parameters:
#   * batch_enveloping_layer -- a layer enveloping the batch_layer. If set, then 
#                               tries to follow the boundaries of the enveloping 
#                               layer while splitting. 
#
from typing import MutableMapping

from estnltk import Text
from estnltk import Layer
from estnltk.web_taggers import WebTagger

from estnltk_core.layer_operations import join_layers_while_reusing_spans
from estnltk_core.layer_operations import extract_sections

from estnltk import logger

class BatchProcessingWebTagger( WebTagger ):
    conf_param = ['url', 'batch_layer', 'batch_layer_max_size', 'batch_enveloping_layer']

    def post_request(self, text: Text, layers: MutableMapping[str, Layer], parameters=None):
        assert self.batch_layer is not None and \
                    isinstance(self.batch_layer, str) and \
                    self.batch_layer in layers
        assert self.batch_layer_max_size is not None and \
                    isinstance(self.batch_layer_max_size, int)
        assert self.batch_enveloping_layer is None or \
                    isinstance(self.batch_enveloping_layer, str)
        if len( layers[self.batch_layer] ) > self.batch_layer_max_size:
            # Note: normally, if batch processing works fine, this exception should never be thrown
            raise Exception('(!) The request Text object exceeds the web service '+\
                            ('limit {} {!r} per text. '.format(self.batch_layer_max_size, self.batch_layer))+\
                            'Please use EstNLTK\'s methods extract_sections or split_by to split the Text object '+\
                            'into smaller Texts, and proceed by processing smaller Texts with the web service. '+\
                            'More information about Text splitting: '+\
                            'https://github.com/estnltk/estnltk/blob/version_1.6/tutorials/system/layer_operations.ipynb ')
        return super().post_request( text, layers, parameters=parameters )

    def batch_process(self, text: Text, layers: MutableMapping[str, Layer], parameters=None):
        assert self.batch_layer is not None and \
                    isinstance(self.batch_layer, str) and \
                    self.batch_layer in layers
        assert self.batch_layer_max_size is not None and \
                    isinstance(self.batch_layer_max_size, int)
        assert self.batch_enveloping_layer is None or \
                    isinstance(self.batch_enveloping_layer, str)
        if len( layers[ self.batch_layer ] ) > self.batch_layer_max_size:
            # A) Text/layer is too big: apply batched processing
            logger.debug('Input layer {!r} size exceeds limit {!r}. Applying batch processing ...'.format( \
                          self.batch_layer, self.batch_layer_max_size ) )
            # Check if all layers are attached
            target_text = text
            all_layers_attached = True
            for layer in layers.keys():
                if layer not in text.layers:
                    all_layers_attached = False
                    break
            if not all_layers_attached:
                # In case of detached layers, create a new surrogate Text obj 
                # with attached layers
                target_text = Text( text.text )
                for layer in Text.topological_sort(layers):
                    target_text.add_layer(layer)
            # Split large Text obj into smaller ones
            smaller_texts, separators = self._split_text_into_smaller_texts( target_text )
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

    def _make_layer(self, text: Text, layers: MutableMapping[str, Layer], status: dict):
        layer = self.batch_process(text, layers)
        return layer

    def _split_text_into_smaller_texts( self, large_text: Text ):
        '''Splits given large_text into smaller texts based on the batch_layer_max_size. 
           If batch_enveloping_layer is defined, then considers the boundaries of the enveloping 
           layer while splitting. 
           Returns smaller text objects and string separators between texts (for later joining).
        '''
        assert self.batch_layer in large_text.layers
        if self.batch_enveloping_layer is not None:
            assert self.batch_enveloping_layer in large_text.layers
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
                if cur_chunk_size + len(env_layer) >= self.batch_layer_max_size:
                    # Start a new chunk
                    chunks.append( [env_layer.start, -1] )
                    cur_chunk_size = 0
                # Complete the last chunk
                chunks[-1][-1] = env_layer.end
                cur_chunk_size += len(env_layer)
                # If the current sentence itself is bigger than the maximum size,
                # then attempt to split the sentence into subsentences considering
                # the maximum size
                if cur_chunk_size >= self.batch_layer_max_size:
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
                        if sub_words == self.batch_layer_max_size:
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
                if cur_chunk_size == self.batch_layer_max_size:
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