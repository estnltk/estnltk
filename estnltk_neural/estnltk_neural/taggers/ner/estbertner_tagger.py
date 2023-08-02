from typing import MutableMapping

from transformers import BertTokenizer, BertForTokenClassification
from transformers import pipeline

from estnltk_core.taggers import MultiLayerTagger

from estnltk.downloader import get_resource_paths

from estnltk import Text, Layer, EnvelopingBaseSpan, ElementaryBaseSpan

from estnltk import logger


class EstBERTNERTagger(MultiLayerTagger):
    """EstNLTK wrapper for the huggingface EstBERTNER models."""
    conf_param = ('model_location', 'nlp', 'tokenizer','input_layers','output_layers', 
                  'output_layers_to_attributes', 'custom_tokens_layer', 'batch_size', 
                  'postfix_expand_suffixes', 'postfix_remove_infix_matches')

    def __init__(self, model_location: str = None, output_layer: str = 'estbertner', custom_tokens_layer:str=None,
                       batch_size:int=1750, tokens_output_layer:str ='nertokens', postfix_expand_suffixes:bool=True, 
                       postfix_remove_infix_matches:bool=True):
        """
        Initializes EstBERTNERTagger.
        
        Note #1: if a custom tokens layer is chosen, then it is not checked whether the tokens segmentation in that 
        layer matches the segmentation done by the NER tagger. If the segmentations do not match, it will lead to 
        wrong tags in the output.
        
        Note #2: if flag postfix_expand_suffixes is set (default), then adds missing suffixes to NE phrases, for 
        instance: "[Pärnu]ga" -> "[Pärnuga]", "[Brüsseli]sse" -> "[Brüsselisse]".
        
        Note #3: if flag postfix_remove_infix_matches is set (default), then applies post-fixing on NER layer: 
        removes entity snippets that are shorter than / equal to 3 characters, and that are surrounded by 
        alphanumeric characters, either at the start or at the end of the entity.
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

        tokenizer = BertTokenizer.from_pretrained(self.model_location, model_max_length=512)
        bertner = BertForTokenClassification.from_pretrained(self.model_location)

        self.nlp = pipeline("ner", model=bertner, tokenizer=tokenizer)
        self.tokenizer = tokenizer
        self.batch_size = batch_size
        
        self.input_layers = []
        self.output_layers = [output_layer]

        self.output_layers_to_attributes = {self.output_layers[0]: ["nertag"]}

        if custom_tokens_layer is None:
            self.output_layers.append(tokens_output_layer)
            self.output_layers_to_attributes[self.output_layers[1]] = []
        else:
            self.input_layers = [custom_tokens_layer]

        self.custom_tokens_layer = custom_tokens_layer
        self.postfix_expand_suffixes = postfix_expand_suffixes
        self.postfix_remove_infix_matches = postfix_remove_infix_matches

    def tokenize_with_bert(self, text):
        '''Tokenizes input Text object with bert's tokenizer and returns list of start-end indexes of tokens.
           Note: [UNK] tokens will obtain indexes (-1, -1).
        '''
        token_indexes = []
        current_idx = 0
        bert_tokens = list( self.tokenizer.tokenize(text.text) )
        for token_id, token in enumerate(bert_tokens):
            if token.startswith('##'):
                token = token[2:]
            if token != "[UNK]":
                last_idx = current_idx
                while lowercase_no_diacritics(slice_wo_soft_hyphen(text.text, current_idx, current_idx + len(token))) != \
                      lowercase_no_diacritics(token):
                    current_idx += 1
                    if current_idx == len(text.text):
                        raise Exception(f"(!) Cannot find bert_token's {token!r} text location at {text.text[last_idx:]!r}.")
                token_indexes.append( (current_idx, current_idx + len(token)) )
                current_idx += len(token)
            else:
                # Mark UNK token with (-1, -1). It will be skipped later
                token_indexes.append( (-1, -1) )
                # Find the next matching token
                next_idx = self._next_matching_token(text.text, current_idx, bert_tokens, token_id)
                if next_idx is not None:
                    current_idx = next_idx
        return token_indexes

    def _next_matching_token(self, text_str, text_pos, bert_tokens, token_id):
        '''Finds next matching token text_pos after given text_pos/token_id that is not [UNK] token.'''
        token = bert_tokens[token_id]
        while token == "[UNK]" and token_id < len(bert_tokens):
            token = bert_tokens[token_id]
            token_id += 1
        while text_pos < len(text_str):
            if lowercase_no_diacritics(slice_wo_soft_hyphen(text_str, text_pos, text_pos+len(token))) == \
               lowercase_no_diacritics(token):
                return text_pos
            text_pos += 1
        return None

    def _make_layers(self, text: Text, layers: MutableMapping[str, Layer], status: dict) -> Layer:
        nerlayer = Layer(name=self.output_layers[0], 
                         attributes=self.output_layers_to_attributes[self.output_layers[0]],
                         text_object=text,
                         enveloping=self.input_layers[0] if len(self.input_layers) > 0 else self.output_layers[1])
        nertag_attr = self.output_layers_to_attributes[self.output_layers[0]][0]
        tokenslayer = None
        if self.custom_tokens_layer is None:
            tokenslayer = Layer(name=self.output_layers[1], 
                                attributes=self.output_layers_to_attributes[self.output_layers[1]], 
                                text_object=text)
        # Apply batch processing: split input text into smaller batches and process batch by batch
        text_chunks, text_indexes = _split_text_into_smaller_texts(text, max_size=self.batch_size)
        chunk_count = 0
        for text_chunk, (chunk_start, chunk_end) in zip(text_chunks, text_indexes):
            chunk_count += 1
            #logger.debug( f'Processing chunk {chunk_count} out of {len(text_chunks)} chunks.' )
            response = self.nlp( text_chunk )
            entity_spans = []
            entity_type = None
            if self.custom_tokens_layer is None:
                #
                # A) Create NE tokens layer on the fly
                #
                bert_token_indexes = self.tokenize_with_bert( Text(text_chunk) )
                for (start_span, end_span) in bert_token_indexes:
                    if (start_span, end_span) == (-1, -1):
                        # Skip [UNK] tokens
                        continue
                    tokenslayer.add_annotation( ElementaryBaseSpan(chunk_start+start_span, chunk_start+end_span) )
                labels = ['O'] * len(bert_token_indexes)
                for word in response:
                    labels[word['index'] - 1] = word['entity']
                for span, label in zip(bert_token_indexes, labels):
                    if span == (-1, -1):
                        # Skip [UNK] tokens
                        if label != 'O':
                            logger.error( f'Skipping [UNK] token with tag {label!r} from annotations.' )
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
            else:
                #
                # B) Rely on existing NE tokens layer
                #
                words = self.input_layers[0] if len(self.input_layers) > 0 else self.output_layers[1]
                existing_words_layer = getattr(text, words)
                words_subset = [sp for sp in existing_words_layer if chunk_start <= sp.start and \
                                                                     sp.end <= chunk_end]
                labels = ['O'] * len( words_subset )
                for word in response:
                    labels[word['index'] - 1] = word['entity']
                for span, label in zip(words_subset, labels):
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
                    entity_spans.append( span.base_span )
        # Apply postfixes
        if self.postfix_expand_suffixes:
            if tokenslayer is None:
                words = self.input_layers[0] if len(self.input_layers) > 0 else self.output_layers[1]
                tokenslayer = getattr(text, words)
            self._postfix_expand_suffixes(text, nerlayer, tokenslayer)
        if self.postfix_remove_infix_matches:
            self._postfix_remove_infix_matches(text, nerlayer)
        # Return results
        returnable_dict = { self.output_layers[0]: nerlayer }
        if self.custom_tokens_layer is None:
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

def lowercase_no_diacritics(word_str: str) -> str:
    '''
    Converts given word string to lowercase and removes 
    common diacritics/accents from letters.
    '''
    word_str = word_str.lower()
    # common letters w diacritics/accents:
    word_str = word_str.replace('ö', 'o')
    word_str = word_str.replace('õ', 'o')
    word_str = word_str.replace('ä', 'a')
    word_str = word_str.replace('ü', 'u')
    word_str = word_str.replace('š', 's')
    word_str = word_str.replace('ž', 'z')
    # and some less common letters:
    word_str = word_str.replace('è', 'e')
    word_str = word_str.replace('é', 'e')
    word_str = word_str.replace('à', 'a')
    word_str = word_str.replace('á', 'a')
    word_str = word_str.replace('â', 'a')
    word_str = word_str.replace('å', 'a')
    word_str = word_str.replace('ū', 'u')
    word_str = word_str.replace('ú', 'u')
    word_str = word_str.replace('ł', 'l')
    # TODO: generalize this to all unicode letters with diacritics
    return word_str

def slice_wo_soft_hyphen(text_str:str, start:int, end:int) -> str:
    '''
    Takes a slice [start:end] from text_str, but leaves out soft hyphen.
    Reason: soft hyphen '\xad' is invisible to bert tokenizer, and thus 
    needs to be removed or otherwise matching with the original text 
    fails.
    '''
    i = start
    text_slice = []
    while i < len(text_str):
        c = text_str[i]
        if c != '\xad':
            text_slice.append(c)
        else:
            # Skip soft hyphen, advance the ending position
            end += 1
        i += 1
        if i == end:
            break
    return ''.join(text_slice)

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