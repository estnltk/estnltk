from typing import MutableMapping, Union

from transformers import AutoTokenizer
from transformers import AutoModelForTokenClassification
from transformers import pipeline

from estnltk_core.taggers import MultiLayerTagger

from estnltk.downloader import get_resource_paths

from estnltk import Text, Layer, EnvelopingBaseSpan, ElementaryBaseSpan
from estnltk import logger

from estnltk_neural.taggers.embeddings.bert.bert_tokens_to_words_rewriter import BertTokens2WordsRewriter


# Decorator for producing words_phrase's NE annotation based on BERT NE tokens
def ner_decorator(text_obj, words_phrase, corresponding_bert_tokens):
    nertags = [t.annotations[0]['nertag'] for t in corresponding_bert_tokens]
    return {"nertag": nertags[0]}


class EstBERTNERTagger(MultiLayerTagger):
    """EstNLTK wrapper for the huggingface EstBERTNER models."""
    conf_param = ('model_location', 'nlp', 'tokenizer', 'custom_words_layer', 'batch_size', 
                  'postfix_expand_suffixes', 'postfix_concat_same_type_entities', 'postfix_remove_infix_matches',
                  '_bert_tokens_rewriter')

    def __init__(self, model_location: str = None, output_layer: str = 'estbertner', 
                       tokens_output_layer:str ='nertokens', custom_words_layer:str = 'words', 
                       batch_size:int=1750, 
                       postfix_expand_suffixes:bool=False, 
                       postfix_concat_same_type_entities:bool=False, 
                       postfix_remove_infix_matches:bool=False, 
                       device: Union[int, "torch.device"] = None 
                       ):
        """
        Initializes EstBERTNERTagger.
        
        Parameters
        ----------
        model_location: str
            Full path to the EstBERTNER model files directory. If not provided (default), then 
            attempts to use estbertner v1 model from estnltk_resources. If that fails (model is 
            missing and downloading fails), then throws an exception.
        output_layer: str
            Name of the output named entity annotations layer. 
            Default: 'estbertner'.
        tokens_output_layer: str
            Name of the BERT tokens layer, which is created during named entity recognition. 
            If custom_words_layer is None, then tokens_output_layer will be added to output 
            layers, and tokens of this layer will be enveloped by the output NE layer. 
            Otherwise, the output NE layer will be enveloping custom_words_layer, and 
            tokens_output_layer will not be added to output layers.
            Note that BERT's tokenization in this layer does not correspond to EstNLTK's 
            tokenization. 
            Default: 'nertokens'.
        custom_words_layer: str
            Name of a customized words layer that is taken as a basis on enveloping named 
            entity annotations instead of tokens_output_layer. This means that all BERT NE 
            tokens that hit word spans will be marked as covering corresponding spans, and 
            BERT NE tokens covering multiple words will result in multi-word NE phrases. 
            If multiple BERT NE tokens cover a word phrase, then label of the first BERT NE 
            token will be chosen as the label of the whole words phrase. 
            Default: 'words'. 
        batch_size: int
            Maximum batch size (in characters) that is processed as a whole by the BERT model. 
            The input text is split into batches of the given size before processing. 
            Default: 1750
        postfix_expand_suffixes: bool
            If set (default), then postcorrects NER annotations by adding missing suffixes to 
            phrases, for instance: "[Pärnu]ga" -> "[Pärnuga]", "[Brüsseli]sse" -> "[Brüsselisse]". 
            These postcorrections are only required if custom_words_layer == None. 
            Default: False.
        postfix_concat_same_type_entities: bool
            If set (default), then postcorrects NER annotations by joining consecutive named 
            entity snippets that are not separated by whitespace, and that have same type of 
            named entities. For instance: "[Ken][yast]" -> "[Kenyast]", '[Kure][ssaare]' -> 
            '[Kuressaare]', "[Domini][ca Ühendus]" -> "[Dominica Ühendus]", .
            These postcorrections are only required if custom_words_layer == None. 
            Default: False.
        postfix_remove_infix_matches: bool
            If set (default), then postcorrects NER annotations by removing entity snippets 
            that are shorter than / equal to 3 characters, and that are surrounded by alphanumeric 
            characters, either at the start or at the end of the entity. Examples:
            "Te[ma]" -> "Tema", "[L]A[P]S[E]P[Õ]LVEKODU" -> "LAPSEPÕLVEKODU". 
            These postcorrections are only required if custom_words_layer == None. 
            Default: False.
        device: int
            The device argument to be passed to transformers.pipeline. Optional, defaults to -1. 
            According to transformers' documentation: "Device ordinal for CPU/GPU supports. Setting 
            this to -1 will leverage CPU, a positive will run the model on the associated CUDA 
            device id. You can pass native `torch.device` or a `str` too."
        """
        if model_location is None:
            # Try to get the resources path for berttagger. Attempt to download, if missing
            resources_path = get_resource_paths("estbertner", only_latest=True, download_missing=True)
            if resources_path is None:
                raise Exception( "EstBERTNER's resources have not been downloaded. "+\
                                 "Use estnltk.download('estbertner') to get the missing resources. "+\
                                 "Alternatively, you can specify the directory containing the model "+\
                                 "via parameter model_location at creating the tagger." )
            self.model_location = resources_path

        else:
            self.model_location = model_location

        tokenizer = AutoTokenizer.from_pretrained(self.model_location, model_max_length=512)
        bertner = AutoModelForTokenClassification.from_pretrained(self.model_location)

        self.nlp = pipeline("ner", model=bertner, tokenizer=tokenizer, device=device)
        self.tokenizer = tokenizer
        self.batch_size = batch_size
        
        self.input_layers = []
        self.output_layers = [output_layer]

        self.output_layers_to_attributes = {self.output_layers[0]: ["nertag"]}

        if custom_words_layer is None:
            self.output_layers.append(tokens_output_layer)
            self.output_layers_to_attributes[self.output_layers[1]] = []
            self._bert_tokens_rewriter = None
        else:
            self.input_layers = [custom_words_layer]
            self._bert_tokens_rewriter = \
                BertTokens2WordsRewriter('temp_bertner', 
                                         input_words_layer = custom_words_layer, 
                                         output_attributes = ("nertag",), 
                                         output_layer = self.output_layers[0],
                                         decorator = ner_decorator)

        self.custom_words_layer = custom_words_layer
        self.postfix_expand_suffixes = postfix_expand_suffixes
        self.postfix_concat_same_type_entities = postfix_concat_same_type_entities
        self.postfix_remove_infix_matches = postfix_remove_infix_matches

    def tokenize_with_bert(self, text, include_spanless=True):
        '''Tokenizes input Text object with Bert's tokenizer and returns a list of token spans.
           Each token span is a triple (start, end, token). 
           If include_spanless==True (default), then Bert's special "spanless" tokens 
           (e.g. [CLS], [SEP]) will also be included with their respective start/end indexes 
           set to None.
        '''
        tokens = []
        batch_encoding = self.tokenizer(text.text)
        for token_id, token in enumerate(batch_encoding.tokens()):
            char_span = batch_encoding.token_to_chars(token_id)
            if char_span is not None:
                tokens.append( (char_span.start, char_span.end, token) )
            elif include_spanless:
                tokens.append( (None, None, token) )
        return tokens

    def _make_layers(self, text: Text, layers: MutableMapping[str, Layer], status: dict) -> Layer:
        # Create layers (and layer templates)
        nerlayer = Layer(name='temp_bertner', 
                         attributes=self.output_layers_to_attributes[self.output_layers[0]],
                         text_object=text,
                         enveloping=self.input_layers[0] if len(self.input_layers) > 0 else self.output_layers[1])
        nertag_attr = self.output_layers_to_attributes[self.output_layers[0]][0]
        tokenslayer = Layer(name='temp_bert_tokens', attributes=(), text_object=text)
        # Apply batch processing: split input text into smaller batches and process batch by batch
        text_chunks, text_indexes = _split_text_into_smaller_texts(text, max_size=self.batch_size)
        chunk_count = 0
        for text_chunk, (chunk_start, chunk_end) in zip(text_chunks, text_indexes):
            chunk_count += 1
            #logger.debug( f'Processing chunk {chunk_count} out of {len(text_chunks)} chunks.' )
            # A) Create (possibly temporary) Bert tokens layer
            bert_tokens = self.tokenize_with_bert(Text(text_chunk), include_spanless=True)
            for (start_span, end_span, token) in bert_tokens:
                if (start_span, end_span) == (None, None):
                    # Skip special tokens (e.g. [CLS], [SEP])
                    continue
                tokenslayer.add_annotation( ElementaryBaseSpan(chunk_start+start_span, chunk_start+end_span) )
            labels = ['O'] * len(bert_tokens)
            # B) Annotate NE labels
            response = self.nlp( text_chunk )
            for detected_entity in response:
                labels[detected_entity['index']] = detected_entity['entity']
            # C) Combine NE labels with Bert tokens to get full NE annotations
            entity_spans = []
            entity_type = None
            for span, label in zip(bert_tokens, labels):
                if span[0] is None and span[1] is None:
                    # Skip special tokens (e.g. [CLS], [SEP])
                    continue
                if entity_type is None:
                    entity_type = label[2:]
                if label == "O":
                    if entity_spans:
                        nerlayer.add_annotation(EnvelopingBaseSpan(entity_spans),
                                                **{nertag_attr: entity_type})
                        entity_spans = []
                    continue
                if label[0] == "B" or entity_type != label[2:]:
                    if entity_spans:
                        nerlayer.add_annotation(EnvelopingBaseSpan(entity_spans),
                                                **{nertag_attr: entity_type})
                        entity_spans = []
                entity_type = label[2:]
                # Apply corrections to entity positions
                corrected_start = chunk_start + span[0]
                corrected_end   = chunk_start + span[1]
                entity_spans.append( ElementaryBaseSpan(corrected_start, corrected_end) )
        # Apply postfixes to raw BERT output
        # (Note: if you use custom_words_layer, then no need for postfixes)
        if self.postfix_expand_suffixes:
            self._postfix_expand_suffixes(text, nerlayer, tokenslayer)
        if self.postfix_concat_same_type_entities:
            self._postfix_concatenate_same_type_entities(text, nerlayer)
        if self.postfix_remove_infix_matches:
            self._postfix_remove_infix_matches(text, nerlayer)
        # Rewrite bert tokens to EstNLTK's words (or any other customized words)
        if self.custom_words_layer is not None:
            layers_copy = layers.copy()
            assert self.custom_words_layer in layers_copy.keys()
            layers_copy[nerlayer.name] = nerlayer
            layers_copy[tokenslayer.name] = tokenslayer
            nerlayer = self._bert_tokens_rewriter.make_layer(text, layers_copy, {})
        # Return results
        nerlayer.name = self.output_layers[0]
        returnable_dict = { self.output_layers[0]: nerlayer }
        if self.custom_words_layer is None:
            tokenslayer.name = self.output_layers[1]
            returnable_dict = { self.output_layers[1]: tokenslayer, 
                                self.output_layers[0]: nerlayer }
        return returnable_dict

    def _postfix_expand_suffixes(self, text:Text, nerlayer:Layer, tokenslayer:Layer):
        '''Applies post-fixing on NER layer: finds entity snippets that are followed by 
           alphanumeric characters, and expands them in text until a punctuation or a 
           whitespace character, whichever appears first. 
           The goal is to fix suffixes of NE phrases, for instance:
           "[Pärnu]ga" -> "[Pärnuga]", 
           "[Brüsseli]sse" -> "[Brüsselisse]", 
           "[Transatlantilise Kesk]use" -> "[Transatlantilise Keskuse]".
        '''
        # Collect start and end indexes of entities
        start_indexes = set([ne_span.start for ne_span in nerlayer])
        end_indexes   = set([ne_span.end for ne_span in nerlayer])
        nertag_attr   = self.output_layers_to_attributes[self.output_layers[0]][0]
        # Find NE snippets that can be further expanded 
        to_replace = []
        for ne_span in nerlayer:
            ne_start, ne_end = ne_span.start, ne_span.end
            ne_end_alphanum = ne_end < len(text.text) and text.text[ne_end].isalnum()
            if ne_end_alphanum and not ne_end in start_indexes:
                # Find potential NE ending (next whitespace)
                i = ne_end
                while i < len(text.text):
                    if (text.text[i]).isspace() or text.text[i] in '"\',.:;?!':
                        break
                    i += 1
                # Collect missing tokens 
                missing_tokens = \
                    [sp for sp in tokenslayer if ne_end <= sp.start and sp.end <= i]
                # Check that missing tokens do not cover existing NE-s.  
                # Otherwise, we'll have a conflict
                if all([(t.start not in start_indexes and t.end not in end_indexes) for t in missing_tokens]) and \
                   len(missing_tokens) > 0:
                    nertag = ne_span.annotations[0][nertag_attr]
                    new_entity_spans = [base_span for base_span in ne_span.base_span]
                    for token in missing_tokens:
                        new_entity_spans.append( ElementaryBaseSpan(token.start, token.end) )
                    current_span = f'{ne_span.enclosing_text}'
                    expansion    = f'{_text_snippet(text,ne_end,i)}'
                    context = f'...{_text_snippet(text,ne_start-10,ne_start)}[{current_span}][{expansion}]{_text_snippet(text,i,i+10)}...'
                    logger.debug( f'NER postfix expanded entity in: {context!r}' )
                    to_replace.append( (ne_span, EnvelopingBaseSpan(new_entity_spans), nertag) )
        for (old_span, new_entity_spans, ner_tag) in to_replace:
            nerlayer.remove_span(old_span)
            nerlayer.add_annotation(new_entity_spans, **{nertag_attr: ner_tag})

    def _postfix_concatenate_same_type_entities(self, text:Text, nerlayer:Layer):
        '''Applies post-fixing on NER layer: finds consecutive named entity snippets 
           that are not separated by whitespace, and that have same type of named entities 
           and concatenates these entities into a single NE phrase.
           The goal is to join NE phrases mistakenly broken into multiple annotations, 
           for instance:
           "[Ken][yast]" -> "[Kenyast]", "[Domini][ca Ühendus]" -> "[Dominica Ühendus]", 
           "[Me][ck][lenburg]" -> "[Mecklenburg]", "[MacA][rthurit]" -> "[MacArthurit]".
        '''
        # Collect start and end indexes of entities + corresponding tags
        nertag_attr   = self.output_layers_to_attributes[self.output_layers[0]][0]
        start_indexes = {}
        end_indexes   = {}
        for ne_span in nerlayer:
            ne_start, ne_end = ne_span.start, ne_span.end
            nertag = ne_span.annotations[0][nertag_attr]
            start_indexes[ne_start] = nertag
            end_indexes[ne_end] = nertag
        to_concatenate = []
        i = 0
        while i < len(nerlayer):
            ne_span = nerlayer[i]
            nertag = ne_span.annotations[0][nertag_attr]
            # Find following entities that can be appended to this entity
            cur_concat_spans = [ne_span]
            j = i + 1
            while j < len(nerlayer):
                ne_span2 = nerlayer[j]
                nertag2 = ne_span2.annotations[0][nertag_attr]
                if cur_concat_spans[-1].end == ne_span2.start and \
                   text.text[ne_span2.start-1].isalnum() and \
                   text.text[ne_span2.start].isalnum() and \
                   nertag == nertag2:
                    cur_concat_spans.append( ne_span2 )
                else:
                    # Not possible to expand any further
                    break
                j += 1
            if len(cur_concat_spans) > 1:
                # Concatenation possible: record spans that should be added together
                new_entity_spans = []
                for cur_span in cur_concat_spans:
                    for base_span in cur_span.base_span:
                        new_entity_spans.append( base_span )
                current_span = f'{ne_span.enclosing_text}'
                expansion    = f'{_text_snippet(text,ne_end,i)}'
                ne_start = new_entity_spans[0].start
                ne_end   = new_entity_spans[-1].end
                conc_strs = [f'[{cur_span.enclosing_text}]' for cur_span in cur_concat_spans]
                context = f'...{_text_snippet(text,ne_start-10,ne_start)}{"".join(conc_strs)}{_text_snippet(text,ne_end,ne_end+10)}...'
                logger.debug( f'NER postfix concatenated entities in: {context!r}' )
                to_concatenate.append( (cur_concat_spans, EnvelopingBaseSpan(new_entity_spans), nertag) )
                i = j - 1
            i += 1
        for (old_spans, new_entity_spans, ner_tag) in to_concatenate:
            # Remove old spans
            for old_span in old_spans:
                nerlayer.remove_span(old_span)
            # Add new concatenated spans
            nerlayer.add_annotation(new_entity_spans, **{nertag_attr: ner_tag})

    def _postfix_remove_infix_matches(self, text:Text, nerlayer:Layer, max_length:int=3):
        '''Applies post-fixing on NER layer: removes entity snippets that are shorter than /
           equal to max_length, and that are surrounded by alphanumeric characters, either 
           at the start or at the end of the entity, but these alphanumeric characters do 
           not belong to any other named entity.
           Surrounding alphanumeric characters (that are not inside other named entities) 
           indicate that the entity annotation is likely broken, e.g. "...MA[R]T VÕRKLAEV...", 
           "...RA[IN]ER SAKS...".'''
        # Collect start and end indexes of entities
        start_indexes = set([ne_span.start for ne_span in nerlayer])
        end_indexes   = set([ne_span.end for ne_span in nerlayer])
        # Find removable NE snippets
        to_remove = []
        for ne_span in nerlayer:
            if isinstance(max_length, int):
                if len(ne_span.enclosing_text) > max_length:
                    continue
            ne_start, ne_end = ne_span.start, ne_span.end
            # Check whether before NE start or after NE end is an alphanumeric character, 
            # but it is not an end or a start of another named entity
            ne_start_alphanum = ne_start-1 >= 0 and text.text[ne_start-1].isalnum()
            ne_end_alphanum   = ne_end < len(text.text) and text.text[ne_end].isalnum()
            if (ne_start_alphanum and not ne_start in end_indexes) or \
               (ne_end_alphanum and not ne_end in start_indexes):
                context = f'...{_text_snippet(text,ne_start-10,ne_start)}[{ne_span.enclosing_text}]{_text_snippet(text,ne_end,ne_end+10)}...'
                logger.debug( f'NER postfix removed tag from context: {context!r}' )
                to_remove.append(ne_span)
        for span_to_remove in to_remove:
            nerlayer.remove_span(span_to_remove)



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


def _text_snippet( text_obj:Text, start:int, end:int ) -> str:
    '''
    Takes a snippet out of the text while assuring that text boundaries are not exceeded.
    For debugging purposes.
    '''
    start = 0 if start < 0 else start
    start = len(text_obj.text) if start > len(text_obj.text) else start
    end   = len(text_obj.text) if end > len(text_obj.text)   else end
    end   = 0 if end < 0 else end
    snippet = text_obj.text[start:end]
    snippet = snippet.replace('\n', '\\n')
    return snippet