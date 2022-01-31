#
#  Module for converting Estonian National Corpus (ENC) 2017 and 2019 
#  documents to EstNLTK Text objects.
#
#  The Estonian National Corpus (ENC) 2017 & 2019 contain variety of corpora,
#  including documents crawled from web (etTenTen 2013 and etTenTen 2017),
#  documents from the National Corpus (e.g. Estonian Reference Corpus), 
#  and articles from Estonian Wikipedia.
#
#  Documents are in an XML-like format, contain metadata (e.g  document 
#  source and title), and have been split into subdocuments and sentences, 
#  or into paragraphs and sentences.
#  etTenTen 2017 web documents have been crawled with the tool SpiderLing, 
#  see http://corpus.tools/wiki/SpiderLing for details. Most of the textual 
#  content should be clean from HTML annotations, but some annotations may 
#  have remained.
#

import re
from io import TextIOWrapper
from typing import Iterable

from logging import Logger
from logging import getLevelName
from sys import stderr

from tqdm import tqdm
from tqdm.notebook import tqdm as notebook_tqdm

from estnltk_core.converters import records_to_layer

from estnltk import Text, Layer

from estnltk.taggers.standard.morph_analysis.morf_common import ESTNLTK_MORPH_ATTRIBUTES

from estnltk.taggers import TokensTagger, CompoundTokenTagger, WordTagger
from estnltk.taggers import SentenceTokenizer, ParagraphTokenizer

# =================================================
#   Helpful utils
# =================================================

# Whether the words layer should be made ambiguous
_MAKE_WORDS_AMBIGUOUS = True

# Pattern for capturing names & values of attributes
enc_tag_attrib_pat = re.compile('([^= ]+)="([^"]+?)"')

def parse_tag_attributes( tag_str, logger:Logger=None ):
    """Extracts names & values of attributes from an XML tag string,
       and returns as a dictionary.
       Throws an Exception if attribute key appears more than once.
       Parameters
       ----------
       tag_str: str
           string representation of an XML tag;
        
       Returns
       -------
       dict
           a dictionary with attribute-value pairs;
    """
    assert tag_str.count('"') % 2 == 0, \
        '(!) Uneven number of quotation marks in: '+str(tag_str)
    attribs = {}
    seen_duplicates = set()
    for attr_match in enc_tag_attrib_pat.finditer(tag_str):
        key   = attr_match.group(1)
        value = attr_match.group(2)
        if key in attribs and key not in seen_duplicates:
            if logger != None:
                logger.log(getLevelName('WARNING'), '(!) Unexpected: attribute "'+key+'" appears more than once in: '+tag_str)
            else:
                stderr.write('(!) Unexpected: attribute "'+key+'" appears more than once in: '+tag_str+'\n')
            seen_duplicates.add(key)
        attribs[key] = value
    return attribs


def extract_doc_ids_from_corpus_file( in_file:str, encoding:str='utf-8' ):
    '''Opens a vert / prevert corpus file, reads its content, and 
       extracts all document id-s. 
       Returns a list of document id-s (list of strings).
       
       Parameters
       ----------
       in_file: str
           Full name of the corpus file (name with path);
           
       encoding: str
           Encoding of in_file. Defaults to 'utf-8';
       
       Returns
       -------
       list of str
           a list of extracted document id-s;
    '''
    enc_doc_tag_start = re.compile("<doc[^<>]+>")
    doc_ids = []
    with open( in_file, mode='r', encoding=encoding ) as f:
        for line in f:
            stripped_line = line.strip()
            if stripped_line.startswith('<doc'):
                # Problem:  sometimes <doc>-tag contains more than one 
                #           < or >, and thus escapes from detection
                # Solution: replace < and > with &lt; and &gt; inside 
                #           the tag
                if stripped_line.count('<') > 1:
                    stripped_line = '<'+(stripped_line[1:]).replace('<', '&lt;')
                if stripped_line.count('>') > 1:
                    stripped_line = (stripped_line[:-1]).replace('>', '&gt;')+'>'
            m_doc_start = enc_doc_tag_start.search(stripped_line)
            if m_doc_start and stripped_line.startswith('<doc '):
                attribs = parse_tag_attributes( stripped_line )
                assert 'id' in attribs.keys()
                doc_ids.append( attribs['id'] )
    return doc_ids


# =================================================
#   Reconstructing EstNLTK Text objects
# =================================================

class ENCTextReconstructor:
    """ ENCTextReconstructor builds Estnltk Text objects 
        based on document contents extracted by VertXMLFileParser.
    """
    NOT_METADATA_KEYS = ['_paragraphs','_sentences','_words',\
                         '_original_words','_morph']

    def __init__(self, tokenization:str='preserve',
                       paragraph_separator:str='\n\n', \
                       sentence_separator:str=' ', \
                       word_separator:str=' ', \
                       layer_name_prefix:str='',\
                       restore_morph_analysis:bool=False,\
                       replace_broken_morph_with_none:bool=True,\
                       logger:Logger=None ):
        '''Initializes the parser.
        
           Parameters
           ----------
           tokenization: ['none', 'preserve', 'estnltk']
                Specifies if tokenization will be added to created Texts, 
                and if so, then how it will be added. 
                Four options:
                * 'none'     -- text   will   be   created  without  any 
                                tokenization layers;
                * 'preserve' -- original tokenization from XML files will 
                                be preserved in layers of the text; 
                                This option creates layers 'tokens',
                                'compound_tokens', 'words', 'word_chunks',
                                'sentences', and 'paragraphs' (only if 
                                paragraphs were recorded in the original
                                text);
                * 'preserve_partially' -- original tokenization from XML 
                                          files will be preserved in layers 
                                          of the text, but only partially;
                                          This option creates layers 'words',
                                          'sentences', and 'paragraphs' (only 
                                          if paragraphs were recorded in the 
                                          original text);
                                          Note: using this option can help 
                                          to speed up the process, because 
                                          creating layers 'tokens' and 
                                          'word_chunks' takes some time.
                * 'estnltk'  -- text's original tokenization will be 
                                overwritten by estnltk's tokenization;
               (default: 'preserve')
           paragraph_separator: str
               String that will be used for separating paragraphs in 
               the reconstructed text;
               Default: '\n\n'
           sentence_separator: str
               String that will be used for separating sentences in 
               the reconstructed text;
               Default: ' '
           word_separator: str
               String that will be used for separating words in the 
               reconstructed text;
               Default: ' '
           layer_name_prefix: str
               Prefix that will be added to names of created layers
               in the reconstructed text if original tokenization is
               preserved (tokenization == 'preserve');
               Default: ''
           restore_morph_analysis: boolean
               If set, then morphological analysis layer is also created 
               based on the morphological annotations in the input dict
               representation of the document.
               Note that this only succeeds if VertXMLFileParser was also 
               configured to preserve morphological analyses.
               If not set, then morphological analyses will be discarded 
               and only tokenization layers will be created.
               (default: False)
           replace_broken_morph_with_none: boolean
               If set, then malformed/broken morphological annotations
               will have all their attribute values set to None.
               Otherwise, the processing will halted with raising an 
               expection if a malformed morphological annotation is 
               encountered.
               Note: this only has effect if restore_morph_analysis
               has been set.
               (default: True)
           logger: logging.Logger
               Logger to be used for warning and debug messages.
        '''
        assert isinstance(paragraph_separator, str)
        assert isinstance(sentence_separator, str)
        assert isinstance(word_separator, str)
        assert isinstance(layer_name_prefix, str)
        assert not logger or isinstance(logger, Logger)
        assert tokenization in [None, 'none', 'preserve', 'preserve_partially', 'estnltk'], \
            '(!) Unknown tokenization option: {!r}'.format(tokenization)
        if not tokenization:
            tokenization = 'none'
        self.tokenization           = tokenization
        self.paragraph_separator    = paragraph_separator
        self.sentence_separator     = sentence_separator
        self.word_separator         = word_separator
        self.layer_name_prefix      = layer_name_prefix
        self.logger                 = logger
        # Sanity checks
        if restore_morph_analysis:
            if tokenization == 'none':
                raise Exception('(!) Conflicting configuration: cannot restore morphological '+\
                                'analysis without restoring tokenization.' )
            elif tokenization == 'estnltk':
                raise Exception('(!) Conflicting configuration: cannot restore original '+\
                                "morphological analysis with estnltk's tokenization. Please "+\
                                "use original tokenization instead.")
        self.restore_original_morph = restore_morph_analysis
        self.replace_broken_morph_with_none = replace_broken_morph_with_none



    def reconstruct_text( self, doc_dict:dict ):
        '''Reconstructs Text object based on dictionary representation
           of the document (doc_dict).
        '''
        # 0. Collect attribute names 
        par_attribs = self._collect_attribute_names( doc_dict, '_paragraphs' )
        s_attribs   = self._collect_attribute_names( doc_dict, '_sentences' )
        # 1. Reconstruct text string
        #    Collect locations of paragraphs, sentences, words
        sent_locations       = []
        para_locations       = []
        word_locations       = []
        word_chunk_locations = [] # only contains tokens glued together in the original text
        morph_analyses       = []
        cur_pos = 0
        all_text_tokens = []
        if '_paragraphs' in doc_dict:
            # --------------------------------------------------------
            paragraphs = doc_dict['_paragraphs']
            for pid, paragraph in enumerate(paragraphs):
                p_start = cur_pos
                if '_sentences' in paragraph:
                    # Collect sentences and words
                    cur_pos, sent_locations, word_locations, \
                    word_chunk_locations, morph_analyses, \
                    all_text_tokens = \
                        self._collect_sentences_and_words( paragraph,
                                                           cur_pos,
                                                           sent_locations,
                                                           word_locations,
                                                           word_chunk_locations,
                                                           morph_analyses, 
                                                           all_text_tokens,
                                                           s_attribs )
                p_end = cur_pos
                # Record paragraph
                # 1) Create record
                record = {'start':p_start, 'end':p_end}
                # 2) Collect paragraph's attributes
                if par_attribs:
                    for attrib in par_attribs:
                        record[attrib] = \
                            paragraph[attrib] if attrib in paragraph else None
                # 3) Store record
                para_locations.append( record )
                if pid+1 < len(paragraphs):
                    all_text_tokens.append(self.paragraph_separator)
                    cur_pos += len(self.paragraph_separator)
            # --------------------
            if '_sentences' in doc_dict:
                # Note: if input document's annotations are malformed, like 
                #       in case of the document with id=1175371, then there 
                #       will be both '_paragraphs' and '_sentences' in the 
                #       doc_dict.  Currently,  only  '_paragraphs'  will be 
                #       extracted in such situations ...
                self._log('WARNING', ('Malformed annotations in doc with id={}: '+\
                          'sentence tags <s> and </s> outside the paragraph tags '+\
                          '<p> and </p>. Only content inside paragraphs will be '+\
                          'extracted.').format( doc_dict['id'] ))
        elif '_sentences' in doc_dict:
            # --------------------------------------------------------
            cur_pos, sent_locations, word_locations, \
            word_chunk_locations, morph_analyses, \
            all_text_tokens = \
                self._collect_sentences_and_words( doc_dict,
                                                   cur_pos,
                                                   sent_locations,
                                                   word_locations,
                                                   word_chunk_locations,
                                                   morph_analyses,
                                                   all_text_tokens,
                                                   s_attribs )
        # 2) Reconstruct text 
        text = Text( ''.join(all_text_tokens) )
        # 3) Add metadata
        for key in doc_dict.keys():
            if key not in self.NOT_METADATA_KEYS:
                text.meta[key] = doc_dict[key]
        # 4) Create tokenization layers (if required)
        if self.tokenization in ['preserve', 'preserve_partially']:
            # Preserve original tokenization layers
            # Attach layers to the Text obj
            self._create_original_layers( text, para_locations, sent_locations, \
                                          word_locations, word_chunk_locations, \
                                          morph_analyses, s_attribs, par_attribs )
        elif self.tokenization == 'estnltk':
            # Create tokenization with estnltk's default tools
            # ( overwrites the original tokenization )
            text.tag_layer(['tokens', 'compound_tokens'])
            text.tag_layer(['words', 'sentences', 'paragraphs'])
        return text



    def _collect_attribute_names( self, doc_dict:dict, segmentation:str ):
        '''Collects  all  legal  attribute  names  used  in  doc_dict
           for given segmentation (either '_paragraphs' or '_sentences').
        '''
        assert segmentation in ['_paragraphs', '_sentences']
        attribs = set()
        parent = None
        # 1) '_paragraphs' or '_sentences' inside doc_dict
        if segmentation in doc_dict:
            for segment in doc_dict[segmentation]:
                for key in segment.keys():
                    attribs.add(key)
        # 2) '_sentences' inside '_paragraphs'
        elif segmentation == '_sentences' and \
           '_paragraphs' in doc_dict:
            for paragraph in doc_dict['_paragraphs']:
                if segmentation in paragraph:
                    for segment in paragraph[segmentation]:
                        for key in segment.keys():
                            attribs.add(key)
        # Remove redundant keys:
        for rkey in self.NOT_METADATA_KEYS:
            if rkey in attribs:
                attribs.remove(rkey)
        return attribs



    def _collect_sentences_and_words( self, content_dict:dict,
                                            cur_pos:int,
                                            sent_locations:list,
                                            word_locations:list,
                                            word_chunk_locations:list,
                                            morph_analyses:list,
                                            all_text_tokens:list,
                                            sent_attribs:set ):
        '''Collects content of '_sentences', '_original_words' and 
           '_words' from given content_dict. If restore_original_morph
           is set, also collects content of morph analysis from 
           '_morph' of given content_dict.
           
           Records token locations into sent_locations, word_locations
           and word_chunk_locations, and updates the pointer cur_pos.
           
           Adds tokens that should go into reconstructable text string
           into list all_text_tokens.
        '''
        assert '_sentences' in content_dict
        sentences = content_dict['_sentences']
        for sid, sentence in enumerate(sentences):
            s_start = cur_pos
            local_word_chunk_locations = []
            if '_original_words' in sentence:
                # Collect all word chunks from sentence
                words = sentence['_original_words']
                for wid, word in enumerate(words):
                    w_start = cur_pos
                    w_end   = cur_pos+len(word)
                    cur_pos += len(word)
                    local_word_chunk_locations.append( \
                        {'start':w_start, 'end':w_end} )
                    all_text_tokens.append( word )
                    if wid+1 < len(words):
                        all_text_tokens.append(self.word_separator)
                        cur_pos += len(self.word_separator)
            if '_words' in sentence:
                last_cur_pos = cur_pos
                cur_pos = s_start
                # Collect subwords/tokens from sentence
                words = sentence['_words']
                for wid, word in enumerate(words):
                    w_start = cur_pos
                    w_end   = cur_pos+len(word)
                    cur_pos += len(word)
                    word_locations.append( \
                        {'start':w_start, 'end':w_end} )
                    # Check if given word is inside a bigger word chunk
                    inside_chunk = False
                    for chunk in local_word_chunk_locations:
                        if chunk['start'] <= w_start and \
                           chunk['end'] > w_end:
                            inside_chunk = True
                            # Remember that this chunk covers 
                            # multiple tokens
                            chunk['multitoken'] = True
                            break
                    if wid+1 < len(words) and not inside_chunk:
                        cur_pos += len(self.word_separator)
                cur_pos = last_cur_pos
            # Keep only those word chunks that cover multiple 
            # tokens, forget all other (redundant information)
            for chunk in local_word_chunk_locations:
                if 'multitoken' in chunk and chunk['multitoken']:
                    del chunk['multitoken']
                    word_chunk_locations.append( chunk )
            # Collect original morph analyses
            if self.restore_original_morph:
                assert '_morph' in sentence, \
                    "(!) Key '_morph' missing from dict: {!r}".format(sentence)
                assert len(sentence['_morph']) == len(sentence['_words']), \
                    ("(!) Mismatching number of elements in "+\
                    "{!r} and {!r}").format(sentence['_morph'],sentence['_words'])
                morph_analyses.extend( sentence['_morph'] )
            s_end = cur_pos
            # Create sentence record
            record = {'start':s_start, 'end':s_end}
            # Collect attributes
            if sent_attribs:
                for attrib in sent_attribs:
                    record[attrib] = \
                        sentence[attrib] if attrib in sentence else None
            # Record sentence
            sent_locations.append( record )
            if sid+1 < len(sentences):
                all_text_tokens.append(self.sentence_separator)
                cur_pos += len(self.sentence_separator)
        return cur_pos, sent_locations, word_locations, \
               word_chunk_locations, morph_analyses, \
               all_text_tokens



    def _create_original_layers( self, text_obj:Text,
                                 para_locations:list,
                                 sent_locations:list,
                                 word_locations:list,
                                 word_chunk_locations:list,
                                 morph_analyses:list,
                                 sent_extra_attribs:set, 
                                 para_extra_attribs:set,
                                 attach_layers:bool=True ):
        '''Creates Text object layers based on given locations 
           of original paragraphs, sentences, words, and 
           word chunks.
           
           If attach_layers=True, attaches created layer to the 
           text_obj (default), otherwise, returns the list of 
           created layers.
           
           Note: if the input document is empty (has no words,
           sentences nor paragraphs), no layers will be created.
        '''
        assert isinstance(text_obj, Text)
        orig_word_chunks     = None
        orig_tokens          = None
        orig_compound_tokens = None
        orig_words           = None
        orig_sentences       = None
        orig_paragraphs      = None
        orig_morph_analysis  = None
        # Create word chunks layer
        if word_chunk_locations is not None and len(word_chunk_locations) > 0:
            if self.tokenization == 'preserve':
                orig_word_chunks = \
                    records_to_layer( \
                        Layer(name=self.layer_name_prefix+'word_chunks', \
                              attributes=(), \
                              text_object=text_obj,\
                              ambiguous=False), word_chunk_locations )
        # Create words layer from the token records
        if word_locations is not None and len(word_locations) > 0:
            if self.tokenization == 'preserve':
                # Create tokens layer
                orig_tokens = \
                    records_to_layer( \
                        Layer(name=self.layer_name_prefix+TokensTagger.output_layer, \
                              attributes=(), \
                              text_object=text_obj,\
                              ambiguous=False), word_locations )
                # Create compound tokens layer
                # Note: this layer will remain empty, as there is no information
                #       about compound tokens in the original text
                orig_compound_tokens = \
                    Layer(name=self.layer_name_prefix+CompoundTokenTagger.output_layer, \
                          enveloping=orig_tokens.name, \
                          attributes=CompoundTokenTagger.output_attributes, \
                          text_object=text_obj,\
                          ambiguous=False)
            # Create words layer
            if _MAKE_WORDS_AMBIGUOUS:
                word_locations = [ [wl] for wl in word_locations ]
            orig_words = \
                records_to_layer( \
                    Layer(name=self.layer_name_prefix+WordTagger.output_layer, \
                          attributes=WordTagger.output_attributes, \
                          text_object=text_obj,\
                          ambiguous=_MAKE_WORDS_AMBIGUOUS), word_locations )
        # Create sentences layer enveloping around words
        if sent_locations is not None and len(sent_locations) > 0 and \
           orig_words is not None: 
            s_attributes = SentenceTokenizer.output_attributes
            if sent_extra_attribs:
                for attrib in sent_extra_attribs:
                    s_attributes += (attrib,)
            orig_sentences = Layer(name=self.layer_name_prefix+SentenceTokenizer.output_layer, \
                                   enveloping=orig_words.name, \
                                   attributes=s_attributes, \
                                   text_object=text_obj,\
                                   ambiguous=False)
            sid = 0; s_start = -1; s_end = -1
            for wid, word in enumerate(orig_words):
                if sid > len(sent_locations):
                    break
                sentence = sent_locations[sid]
                if word.start == sentence['start']:
                    s_start = wid
                if word.end == sentence['end']:
                    s_end = wid
                if s_start != -1 and s_end != -1:
                    current_sent_attribs={}
                    if sent_extra_attribs:
                          for attrib in sent_extra_attribs:
                              current_sent_attribs[attrib] = \
                                  sentence[attrib] if attrib in sentence else None
                    orig_sentences.add_annotation(orig_words[s_start:s_end+1], **current_sent_attribs)
                    sid += 1; s_start = -1; s_end = -1
            error_msg = orig_sentences.check_span_consistency()
            if error_msg is not None:
                raise AssertionError( 'Error on parsing sentences: {}'.format(error_msg) )
            assert sid == len(sent_locations)
        # Create paragraphs layer enveloping around sentences
        if para_locations is not None and len(para_locations) > 0 and \
           orig_sentences is not None:
            p_attributes = ParagraphTokenizer.output_attributes
            if para_extra_attribs:
                for attrib in para_extra_attribs:
                    p_attributes += (attrib,)
            orig_paragraphs = Layer(name=self.layer_name_prefix+ParagraphTokenizer.output_layer, \
                                    enveloping=orig_sentences.name, \
                                    attributes=p_attributes, \
                                    text_object=text_obj, \
                                    ambiguous=False)
            pid = 0; p_start = -1; p_end = -1
            for sid, sentence in enumerate(orig_sentences):
               if pid > len(para_locations):
                  break
               paragraph = para_locations[pid]
               if sentence.start == paragraph['start']:
                  p_start = sid
               if sentence.end == paragraph['end']:
                  p_end = sid
               if p_start != -1 and p_end != -1:
                  current_paragraph_attribs={}
                  if para_extra_attribs:
                      for attrib in para_extra_attribs: 
                          current_paragraph_attribs[attrib] = \
                              paragraph[attrib] if attrib in paragraph else None
                  orig_paragraphs.add_annotation(orig_sentences[p_start:p_end+1], **current_paragraph_attribs)
                  pid += 1; p_start = -1; p_end = -1
            error_msg = orig_paragraphs.check_span_consistency()
            if error_msg is not None:
                raise AssertionError( 'Error on parsing paragraphs: {}'.format(error_msg) )
            if pid == 0 and len(orig_paragraphs) == 0:
                # The situation where only starting <p> tags exists
                # ( occurs in 'etnc19_doaj.vert' document 6024414 )
                if len(para_locations) > 0:
                    self._log('WARNING', ('Malformed annotations in doc with id={}: '+\
                              'only starting paragraph tags <p> exist, unable to create paragraph '+\
                              'annotations. ').format( text_obj.meta['id'] ))
            elif pid > 0:
                assert pid == len(para_locations)
        # Create morph_analyses enveloping around words
        if self.restore_original_morph and morph_analyses is not None and \
           len(morph_analyses) > 0 and orig_words is not None:
            orig_morph_analysis = \
              self._create_original_morph_analysis_layer( text_obj, word_locations,
                                                          orig_words, morph_analyses )
        # Collect results
        created_layers = [orig_word_chunks, orig_tokens, orig_compound_tokens, 
                          orig_words, orig_sentences, orig_paragraphs, 
                          orig_morph_analysis]
        if attach_layers:
            for layer in created_layers:
                if layer is not None:
                    text_obj.add_layer(layer)
        else:
            return created_layers

    def _create_original_morph_analysis_layer(self, text_obj: Text,
                                              word_locations: list,
                                              orig_words_layer: Layer,
                                              raw_morph_analyses: list):
        """Creates a morph_analysis layer based on raw_morph_analyses
        extracted from the vert / prevert content.

        """
        assert len(raw_morph_analyses) == len(orig_words_layer)
        assert len(raw_morph_analyses) == len(word_locations)

        layer_attributes = ESTNLTK_MORPH_ATTRIBUTES
        morph_layer = Layer(name=self.layer_name_prefix+'morph_analysis',
                            parent=orig_words_layer.name,
                            ambiguous=True,
                            text_object=text_obj,
                            attributes=layer_attributes)

        for word, raw_analysis in zip(orig_words_layer, raw_morph_analyses):
            # A) Parse morph analysis from the raw analysis
            analysis_dict = self._create_morph_analysis_dict(raw_analysis)
            # B) Normalize and set attributes
            attributes = {attr: analysis_dict.get(attr) for attr in layer_attributes}
            if 'root_tokens' in attributes:
                if attributes['root_tokens'] is not None:
                    attributes['root_tokens'] = tuple(attributes['root_tokens'])
            # C) Record span to the layer
            morph_layer.add_annotation(word.base_span, **attributes)
        return morph_layer

    def _create_morph_analysis_dict(self, raw_morph_analysis:str):
        '''Creates a morph analysis dict from the raw_morph_analysis line 
           extracted from the vert / prevert input file.'''
        analysis_dict = {}
        if '\t' in raw_morph_analysis:
            items = raw_morph_analysis.split("\t")
            if len(items) == 8:
                #
                # Full scale morph analysis, for instance:
                #   ministrite	S.pl.g	minister-s	pl_g	minister	minister	te	
                #   nõukogule	S.sg.all	nõukogu-s	sg_all	nõu kogu	nõu_kogu	le	
                #   selles	P.sg.in	see-p	sg_in	see	see	s	
                #   küsimuses	S.sg.in	küsimus-s	sg_in	küsimus	küsimus	s	
                #   esitatud	V.tud	esitama-v	tud	esita	esita	tud	
                #   EKAK	Y.?	EKAK-y	?	EKAK	EKAK	0	
                #   sissejuhatavat	A.sg.p	sissejuhatav-a	sg_p	sisse juhatav	sisse_juhatav	t	
                #
                analysis_dict['root'] = items[5]
                analysis_dict['form'] = items[3].replace('_', ' ')
                analysis_dict['ending'] = items[6].replace('_', ' ')
                analysis_dict['partofspeech'] = items[1][0]
                assert analysis_dict['partofspeech'].isupper(), \
                   "(!) Unexpected lowercase 'partofspeech' in {!r} at line {!r}".format(items[1], raw_morph_analysis)
                pos_ending = '-'+analysis_dict['partofspeech'].lower()
                assert items[2].endswith(pos_ending), \
                   "(!) Unexpected pos-ending in {!r} at line {!r}".format(items[2], raw_morph_analysis)
                analysis_dict['lemma'] = items[2].replace(pos_ending, '')
                analysis_dict['root_tokens'] = items[4].split()
                analysis_dict['clitic'] = items[7]
            else:
                # Unexpected format for morph analysis
                status_str = 'critical'
                status_action = ''
                if self.replace_broken_morph_with_none:
                    # Add an empty annotation
                    analysis_dict['root'] = None
                    analysis_dict['form'] = None
                    analysis_dict['ending'] = None
                    analysis_dict['partofspeech'] = None
                    analysis_dict['lemma'] = None
                    analysis_dict['root_tokens'] = None
                    analysis_dict['clitic'] = None
                    status_str    = 'WARNING'
                    status_action = ' Adding an empty annotation.'
                self._log(status_str, \
                   '(!) Broken raw_morph_analysis in line {!r}.{}'.format(raw_morph_analysis,status_action))
                if not self.replace_broken_morph_with_none:
                    raise Exception('(!) Unexpected malformed raw_morph_analysis: {!r}'.format(raw_morph_analysis))
        else:
            # This should be a tag: format it as a 'Z'
            if raw_morph_analysis.startswith('<') and \
               raw_morph_analysis.endswith('>'):
               analysis_dict['partofspeech'] = 'Z'
               for attr in ESTNLTK_MORPH_ATTRIBUTES:
                   if attr in ['lemma', 'root']:
                       analysis_dict[attr] = raw_morph_analysis
                   elif attr == 'root_tokens':
                       analysis_dict[attr] = [raw_morph_analysis]
                   else:
                       analysis_dict[attr] = ''
            else:
               # If it is not tag, then something unexpected happened
               status_str = 'critical'
               status_action = ''
               if self.replace_broken_morph_with_none:
                   # Add an empty annotation
                   analysis_dict['root'] = None
                   analysis_dict['form'] = None
                   analysis_dict['ending'] = None
                   analysis_dict['partofspeech'] = None
                   analysis_dict['lemma'] = None
                   analysis_dict['root_tokens'] = None
                   analysis_dict['clitic'] = None
                   status_str    = 'WARNING'
                   status_action = ' Adding an empty annotation.'
               self._log(status_str, \
                   '(!) Broken raw_morph_analysis in line {!r}.{}'.format(raw_morph_analysis,status_action))
               if not self.replace_broken_morph_with_none:
                   raise Exception('(!) Unexpected malformed raw_morph_analysis: {!r}'.format(raw_morph_analysis))
        return analysis_dict



    def _log( self, level:str, msg:str ):
        '''Writes a logging message if logging facility is available.'''
        if self.logger is not None:
            assert isinstance(level, str)
            level = getLevelName( level.upper() )
            self.logger.log(level, msg)



# =================================================
#   Parsing ENC 2017 & 2019 corpus files
# =================================================

class VertXMLFileParser:
    """ A very simple XMLParser that allows line by line parsing of vert type 
        (or prevert type) XML files. 
        The parser maintains the state and reconstructs a Text object 
        whenever a single document from XML has been completely parsed.
        
        This parser takes advantage of the simple structure of the input XML 
        files: all XML tags are on separate lines, so the line by line parsing 
        is actually the most straightforward approach.
        
        * VertXMLFileParser is made for parsing vert files of ENC 2017 & 2019; 
          the implementation is loosely based on earlier EtTenTenXMLParser;
        * vert / prevert is an output file type used by the SpiderLing web 
          crawler, see http://corpus.tools/wiki/SpiderLing for details; 
    """
    CORPUS_ANNOTATION_TAGS = ['g', 's', 'p', 'info', 'doc', 'gap']
    HTML_ANNOTATION_TAGS   = ['div', 'span', 'i', 'b', 'br', 'ul', 'ol', 'li', 'img',
                              'table', 'caption', 'pre', 'tr', 'td', 'th', 'thead',
                              'tfoot', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a', 'em',
                              'iframe', 'body', 'head', 'header']

    def __init__(self, focus_ids:set=None,\
                       focus_srcs:set=None,\
                       focus_lang:set=None,\
                       discard_empty_fragments:bool=True, \
                       store_fragment_attributes:bool=True, \
                       add_unexpected_tags_to_words:bool=False, \
                       record_morph_analysis:bool=False,\
                       textReconstructor:ENCTextReconstructor=None,\
                       logger:Logger=None ):
        '''Initializes the parser.
        
           Parameters
           ----------
           focus_ids: set of str
               Set of document id-s corresponding to the documents which 
               need to be extracted from the XML content.
               If provided, then only documents with given id-s will be 
               parsed, and all other documents will be skipped.
               If None or empty, then all documents in the content will 
               be parsed.
               Important note: ids must be given as strings, not as 
               integers.
           focus_srcs: set of str
               Set of document src-s corresponding to subcorpora from 
               which documents need to be extracted from the XML content.
               If provided, then only documents that have a src value from
               the set will be extracted, and all other documents will 
               be skipped.
               If None or empty, then all documents in the content will 
               be parsed.
           focus_lang: set of str
               Set of allowed document languages.
               If provided, then only documents that have a lang value from
               the set will be extracted, and all other documents will 
               be skipped. Note that if focus_lang is set, but the document
               does not have lang attribute, the document will also be 
               skipped;
               If None or empty, then all documents in the content will 
               be parsed.
           discard_empty_fragments: boolean
               If set, then empty text fragments -- documents, paragraphs and 
               sentences -- will be discarded.
               (default: True)
           store_fragment_attributes: boolean
               If set, then attributes in the XML tag of a paragraph or sentence 
               will be collected and added as attributes of the corresponding 
               layer in Text object.
               (default: True)
           add_unexpected_tags_to_words: boolean
               If set, then tags at unexpected locations will be added to the 
               reconstructed text as words. 
               Otherwise, all unexpected tags will be discarded.
               (default: False)
           record_morph_analysis: boolean
               If set, then morphological analyses will also be extracted from 
               the input content, and recorded in dict representation of the 
               document.
               Otherwise, morphological analyses will be discarded and only 
               segmentation annotations will be recorded.
               (default: False)
           textReconstructor: ENCTextReconstructor
               ENCTextReconstructor instance that can be used for reconstructing
               the Text object based on extracted document content;
               Default: None
           logger: logging.Logger
               Logger to be used for warning and debug messages.
        '''
        assert not logger or isinstance(logger, Logger)
        assert not textReconstructor or isinstance(textReconstructor, ENCTextReconstructor)
        # Initialize the state of parsing
        self.lines            = 0
        self.inside_focus_doc = False
        self.document         = {} # metadata of the document
        self.content          = {} # content of the document or subdocument
        self.last_was_glue    = False
        self.last_was_doc_end = False
        if focus_ids is not None:
            assert isinstance(focus_ids, set)
            if len(focus_ids) == 0:
                focus_ids = None
            else:
                # Validate that all id-s are strings
                for fid in focus_ids:
                    if not isinstance(fid, str):
                        raise ValueError('(!) focus_doc_id should be str: unexpected id value {!r}'.format(fid))
        self.focus_doc_ids = focus_ids
        if focus_srcs is not None:
            assert isinstance(focus_srcs, set)
            if len(focus_srcs) == 0:
                focus_srcs = None
        self.focus_srcs = focus_srcs
        if focus_lang is not None:
            assert isinstance(focus_lang, set)
            if len(focus_lang) == 0:
                focus_lang = None
        self.focus_lang                = focus_lang
        self.store_fragment_attributes = store_fragment_attributes
        self.discard_empty_fragments   = discard_empty_fragments
        self.add_unexpected_tags_to_words = add_unexpected_tags_to_words
        self.record_original_morph        = record_morph_analysis
        self.logger                       = logger
        self.textreconstructor            = textReconstructor
        if self.textreconstructor:
            # Validate that configurations regarding restoring morph analysis are matching
            if self.textreconstructor.restore_original_morph != self.record_original_morph:
                conf1 = '{}.record_original_morph={}'.format( \
                      self.__class__.__name__,self.record_original_morph)
                conf2 = '{}.restore_original_morph={}'.format( \
                      self.textreconstructor.__class__.__name__,self.textreconstructor.restore_original_morph)
                raise Exception('(!) Conflicting configurations: {} and {}'.format(conf1, conf2) )
        # Hack: remember the number of Wiki 2017 docs with broken tags encountered (to avoid an abundance of warnings)
        self.broken_tag_docs_with_wiki_2017_src = 0
        # ... and in similar vein: remember the number of Web 2017 docs with broken tags encountered
        self.broken_tag_docs_with_web_2017_src  = 0
        # Patterns for detecting tags
        self.enc_doc_tag_start  = re.compile(r"^<doc[^<>]+>\s*$")
        self.enc_doc_tag_end    = re.compile(r"^</doc>\s*$")
        # Info tags: used for marking subdocuments inside documents
        self.enc_info_tag_start = re.compile(r"^<info[^<>]+>\s*$")
        self.enc_info_tag_end   = re.compile(r"^</info>\s*$")
        self.enc_p_tag_start    = re.compile(r"^<p( [^<>]+)?>\s*$")
        self.enc_p_tag_end      = re.compile(r"^</p>\s*$")
        self.enc_s_tag_start    = re.compile(r"^<s( [^<>]+)?>\s*$")
        self.enc_s_tag_end      = re.compile(r"^</s>\s*$")
        self.enc_glue_tag       = re.compile("^<g/>$")
        self.enc_unknown_tag    = re.compile("^<([^<>]+)>$")



    def parse_next_line( self, line: str ):
        '''Parses a next line from the XML content of ENC corpus.
        
           If an end of document is reached with the line, there a two 
           possibilities.
           First, if textreconstructor is set, reconstructs and returns 
           Text object based on the seen document. Second, if 
           textreconstructor is not set, returns dict representation
           of the the seen document. 
           And if the line is not definitive, but just continues 
           the document content, returns None.
           
           If any of the filters (focus_doc_ids, focus_srcs, focus_lang)
           are provided, then only documents passing all the filters will
           be returned. If a document does not pass the filters, then None 
           is returned instead of the document.
        '''
        stripped_line = line.strip()
        lt_escaped = False
        gt_escaped = False
        if stripped_line.startswith('<doc'):
            # Problem:  sometimes <doc>-tag contains more than one 
            #           < or >, and thus escapes from detection
            # Solution: replace < and > with &lt; and &gt; inside 
            #           the tag
            if stripped_line.count('<') > 1:
                stripped_line = '<'+(stripped_line[1:]).replace('<', '&lt;')
                lt_escaped = True
            if stripped_line.count('>') > 1:
                stripped_line = (stripped_line[:-1]).replace('>', '&gt;')+'>'
                gt_escaped = True
        m_doc_start = self.enc_doc_tag_start.match(stripped_line)
        m_doc_end   = self.enc_doc_tag_end.match(stripped_line)
        # *** Start of a new document
        if m_doc_start and stripped_line.startswith('<doc '): 
            # Replace back &lt; and &gt;
            if lt_escaped:
                stripped_line = stripped_line.replace('&lt;', '<')
            if gt_escaped:
                stripped_line = stripped_line.replace('&gt;', '>')
            # Clear old doc content
            self.document.clear()
            self.content.clear()
            if 'src="Wikipedia 2017"' in stripped_line and \
               stripped_line.count('lang_scores=') > 1:
                #
                #  Note: There is a systemic error in 'etnc19_wikipedia_2017.vert':
                #        each and every <doc> contains two "lang_scores" attributes.
                #        As a result, we would have an abundance of warnings about
                #        repeated attribute names. In order to avoid that, we remove
                #        the first "lang_scores" attribute from the <doc> tag after 
                #        we have recorded five of these warnings.
                #
                self.broken_tag_docs_with_wiki_2017_src += 1
                if self.broken_tag_docs_with_wiki_2017_src > 5:
                   stripped_line = re.sub('lang_scores="[^"]+"',' ',stripped_line,count=1)
            #
            #  Note: the file 'etnc19_web_2017.vert' also has systematic duplicates in tag 
            #        attributes, so apply the same strategy as previously:  warn  for  the 
            #        first 5 malformed doc tags, and then remove the duplicates to suppress 
            #        the abundance of warnings.
            #
            if 'src="Web 2017"' in stripped_line and \
               (stripped_line.count('lang_old=') > 1 or \
                stripped_line.count('lang_scores=') > 1 ):
                self.broken_tag_docs_with_web_2017_src += 1
                if self.broken_tag_docs_with_web_2017_src > 5:
                    if stripped_line.count('lang_old=') > 1:
                        stripped_line = re.sub('lang_old="[^"]+"',' ',stripped_line,count=1)
                    if stripped_line.count('lang_scores=') > 1:
                        stripped_line = re.sub('lang_scores="[^"]+"',' ',stripped_line,count=1)
            # Carry over attributes
            attribs = parse_tag_attributes( stripped_line, logger=self.logger )
            for key, value in attribs.items():
                if key in ['_paragraphs','_sentences','_words','_original_words']:
                   raise Exception("(!) Improper key name "+key+" in tag <doc>.")
                self.document[key] = value
            if 'id' not in self.document:
                self._log( 'CRITICAL', '(!) doc-tag misses id attribute: {!r}'.format(stripped_line))
            if 'src' not in self.document and 'id' in self.document:
                self._log( 'WARNING', 'Document with id={} misses src attribute'.format(self.document['id']))
            # Check if the document passes filters: id, src, lang
            doc_filters_passed = []
            if self.focus_doc_ids is not None:
                doc_filters_passed.append( self.document['id'] in self.focus_doc_ids )
            if self.focus_srcs is not None:
                doc_filters_passed.append( 'src' in self.document and \
                                           self.document['src'] in self.focus_srcs )
            if self.focus_lang is not None:
                doc_filters_passed.append( 'lang' in self.document and \
                                           self.document['lang'] in self.focus_lang )
            # Include document to processing only if there were no filters or
            # if all filters were successfully passed 
            if not doc_filters_passed or all( doc_filters_passed ):
                self.inside_focus_doc = True
            self.last_was_doc_end = False
        # *** End of a document
        if m_doc_end:
            self.last_was_doc_end = True
        if m_doc_end and self.inside_focus_doc:
            self.inside_focus_doc = False
            if 'subdoc' in self.content:
                # If document consisted of subdocuments, then we are finished
                self.lines += 1
                return None
            else:
                if self.discard_empty_fragments:
                    # Check that the document is not empty
                    if '_sentences' not in self.content and \
                       '_paragraphs' not in self.content:
                        # if the document had no content, discard it ...
                        self._log( 'WARNING', 'Discarding empty document with id={}'.format(self.document['id']) )
                        self.lines += 1
                        return None
                # Carry over metadata attributes
                for key, value in self.document.items():
                    assert key not in self.content, \
                        ('(!) Key {!r} already in {!r}.').format( key, self.content.keys() )
                    self.content[key] = value
                self.lines += 1
                if self.textreconstructor:
                    # create Text object
                    text_obj = self.textreconstructor.reconstruct_text( self.content )
                    return text_obj
                else:
                    return self.content
        # Sanity check : is there an unexpected continuation after document ending?
        if self.last_was_doc_end:
            if not m_doc_end and not m_doc_start:
                # Note: this problem is frequent to 'etnc19_doaj.vert'
                self._log( 'WARNING', ('Unexpected content line {}:{!r} after document '+\
                                       'ending tag. Content outside documents will be skipped.').format(self.lines, stripped_line))
            self.last_was_doc_end = False
        # Skip document if it is not one of the focus documents
        if not self.inside_focus_doc:
            self.lines += 1
            return None
        # Next patterns to be checked
        m_info_start  = self.enc_info_tag_start.match(stripped_line)
        m_info_end    = self.enc_info_tag_end.match(stripped_line)
        m_par_start   = self.enc_p_tag_start.match(stripped_line)
        m_par_end     = self.enc_p_tag_end.match(stripped_line)
        m_s_start     = self.enc_s_tag_start.match(stripped_line)
        m_s_end       = self.enc_s_tag_end.match(stripped_line)
        m_glue        = self.enc_glue_tag.match(stripped_line)
        m_unk_tag     = self.enc_unknown_tag.match(stripped_line)
        # *** New subdocument (info)
        if m_info_start:
            # Assert that some content from the doc tag has already been read
            assert 'id' in self.document
            info_attribs = parse_tag_attributes( stripped_line, logger=self.logger )
            # Create a new subdocument
            if 'subdoc' in self.content:
                self.content['subdoc'].clear()
            else:
                self.content['subdoc'] = {}
            # 1) Carry over subdocument attributes
            for key, value in info_attribs.items():
                if key == 'id':
                    # Rename 'id' -> 'subdoc_id'
                    key = 'subdoc_id'
                if key in ['_paragraphs','_sentences','_words','_original_words']:
                    raise Exception("(!) Improper key name "+key+" in tag <doc>.")
                self.content['subdoc'][key] = value
            # 2) Carry over parent document's attributes
            for key, value in self.document.items():
                assert key not in self.content['subdoc']
                self.content['subdoc'][key] = value
        # *** End of a subdocument (info)
        if m_info_end:
            if 'subdoc' in self.content:
                parent = self.content['subdoc']
            else:
                # --------------------------------------------
                # Note: If the first <info> tag is broken and 
                # 'subdoc' is missing, like in document with 
                # id==12446, then we will discard reconstruction
                # of the document at this point.
                # If the next line is </doc>, the document 
                # would still be successfully reconstructed, 
                # and if the next line is <info ...>, then
                # this document will be discarded altogether
                # --------------------------------------------
                self._log( 'WARNING', 'Malformed tag in doc with id={}: tag </info> without <info>'.format(self.document['id']) )
                self.lines += 1
                return None
            if self.discard_empty_fragments:
                # Check that the document is not empty
                if '_sentences' not in parent and \
                   '_paragraphs' not in parent:
                    # if the document had no content, discard it ...
                    self._log( 'WARNING', 'Discarding empty subdocument: doc id={} subdoc id={}'.format(self.document['id'], document['subdoc_id']) )
                    self.lines += 1
                    return None
            self.lines += 1
            if self.textreconstructor:
                # create Text object
                text_obj = self.textreconstructor.reconstruct_text( parent )
                return text_obj
            else:
                return self.content
        # *** New paragraph
        if m_par_start:
            # Create new paragraph
            new_paragraph = {}
            if self.store_fragment_attributes:
                attribs = parse_tag_attributes( stripped_line, logger=self.logger )
                for key, value in attribs.items():
                    if key in new_paragraph.keys():
                       raise Exception("(!) Unexpected repeating attribute name in <p>: "+str(key))
                    if '-' in key:
                       self._log( 'WARNING', 'Fixing attribute name {!r} -> {!r}'.format(key, key.replace('-', '_')) )
                       key = key.replace('-', '_')
                    if not key.isidentifier():
                       self._log( 'CRITICAL', 'Invalid attribute name {} in {!r}'.format(key, stripped_line) )
                    new_paragraph[key] = value
            # Attach the paragraph
            parent = None
            if 'subdoc' in self.content:
                parent = self.content['subdoc']
            else:
                parent = self.content
            if '_paragraphs' not in parent:
                parent['_paragraphs'] = []
            parent['_paragraphs'].append( new_paragraph )
        # *** Paragraph's end
        if m_par_end:
            if self.discard_empty_fragments:
                # Check if the last paragraph was empty
                parent = None
                if 'subdoc' in self.content:
                    parent = self.content['subdoc']
                else:
                    parent = self.content
                if '_paragraphs' in parent:
                    assert len(parent['_paragraphs']) > 0
                    parent = parent['_paragraphs']
                    if parent:
                        # If there are no words nor sentences, remove 
                        # the empty paragraph
                        if ('_sentences' not in parent[-1] or \
                            len(parent[-1]['_sentences']) == 0) \
                            and \
                           ('_words' not in parent[-1] or \
                            len(parent[-1]['_words']) == 0):
                            parent.pop()
        # *** New sentence
        if m_s_start:
            # Create new sentence
            new_sentence = {}
            if self.store_fragment_attributes:
                attribs = parse_tag_attributes( stripped_line, logger=self.logger )
                for key, value in attribs.items():
                    if key in new_sentence.keys():
                       raise Exception("(!) Unexpected repeating attribute name in <p>: "+str(key))
                    if '-' in key:
                       self._log( 'WARNING', 'Fixing attribute name {!r} -> {!r}'.format(key, key.replace('-', '_')) )
                       key = key.replace('-', '_')
                    if not key.isidentifier():
                       self._log( 'CRITICAL', 'Invalid attribute name {} in {!r}'.format(key, stripped_line) )
                    new_sentence[key] = value
            # Attach the sentence
            parent = None
            if 'subdoc' in self.content:
                parent = self.content['subdoc']
            else:
                parent = self.content
            if '_paragraphs' in parent:
                assert len(parent['_paragraphs']) > 0
                parent = parent['_paragraphs'][-1]
            if '_sentences' not in parent:
                parent['_sentences'] = []
            parent['_sentences'].append( new_sentence )
        # *** Sentence end
        if m_s_end:
            if self.discard_empty_fragments:
                # Check if the last sentence was empty
                parent = None
                if 'subdoc' in self.content:
                    parent = self.content['subdoc']
                else:
                    parent = self.content
                if '_paragraphs' in parent:
                    assert len(parent['_paragraphs']) > 0
                    parent = parent['_paragraphs'][-1]
                if '_sentences' in parent:
                    assert len(parent['_sentences']) > 0
                    parent = parent['_sentences']
                    if parent:
                        # If there are no words, remove the empty sentence
                        if '_words' not in parent[-1] or \
                           len(parent[-1]['_words']) == 0:
                            parent.pop()
        # *** The glue tag: tokens from both side should be joined 
        if m_glue:
            self.last_was_glue = True
        # *** Text content + morph analysis inside sentence or paragraph
        elif len( stripped_line ) > 0 and '\t' in stripped_line:
            if not stripped_line.count('\t') >= 2:
                # Inform that morph analysis is likely broken at this point
                warn_msg = 'Malformed line {!r} : unexpected number of tabs ({}) in line.'
                self._log( 'WARNING', warn_msg.format( stripped_line, 
                                                       stripped_line.count('\t') ) )
            # Add word
            items = stripped_line.split('\t')
            token = items[0]
            self._add_new_word_token( token, line.rstrip('\n') )
        elif m_unk_tag:
            # Handle an unexpected tag
            self._handle_unexpected_tag( stripped_line, m_unk_tag.group(1) )
        self.lines += 1
        return None



    def _add_new_word_token( self, word_str: str, whole_line: str ):
        '''Inserts given word_str into the document under reconstruction.
        
           Finds appropriate substructure (e.g. last paragraph or last 
           sentence) which is incomplete and adds word to the structure.
           Takes account of any glue markings added between the words.
           
           If record_original_morph_analysis is set, then records
           whole_line as the morphological analysis of the input word.
        '''
        # Get the parent
        parent = None
        if 'subdoc' in self.content:
            parent = self.content['subdoc']
        else:
            parent = self.content
        if '_paragraphs' in parent:
            assert len(parent['_paragraphs']) > 0
            parent = parent['_paragraphs'][-1]
        if '_sentences' in parent:
            assert len(parent['_sentences']) > 0
            parent = parent['_sentences'][-1]
        if '_words' not in parent:
            # _original_words == words separated by 
            #                    whitespace
            parent['_original_words'] = []
            # _words == words morphologically analysed;
            #           these words can be tokens inside 
            #           _original_words
            parent['_words'] = []
            if self.record_original_morph:
                # _morph == raw lines of morphological
                #           analysis
                parent['_morph'] = []
        prev_words = parent['_words']
        prev_original_words = parent['_original_words']
        # Add given word
        prev_words.append( word_str )
        if self.last_was_glue:
            if len(prev_original_words) > 0:
                # Merge word to the previous one
                prev_original_words[-1] = prev_original_words[-1] + word_str
            else:
                # Broken annotation: <g/> is not between 
                # two tokens, but at the start of the 
                # sentence instead 
                self._log( 'WARNING', 'Unexpectedly <g/> is not between two tokens at line {}'.format(self.lines-1) )
                # Add a new word to the list 
                prev_original_words.append( word_str )
        else:
            # Add a new word to the list 
            prev_original_words.append( word_str )
        # Record original morphological analysis
        if self.record_original_morph:
            assert whole_line is not None and len(whole_line)>0
            parent['_morph'].append( whole_line )
        self.last_was_glue = False
        



    def _handle_unexpected_tag( self, line_with_tag: str, tag_content: str ):
        '''Logic for handling an unexpected tag.'''
        tagname = tag_content.strip('/')
        tagname = tagname.split()[0]
        if tagname not in self.CORPUS_ANNOTATION_TAGS:
            msg_end = 'Discarding.'
            if self.add_unexpected_tags_to_words:
                # Add tag as word
                self._add_new_word_token( line_with_tag, line_with_tag )
                msg_end = 'Including as a word.'
            doc_id = self.document['id']
            if tagname.lower() in self.HTML_ANNOTATION_TAGS:
                #self._log('DEBUG', 'Unexpected HTML tag {!r} at line {} in doc id={}. {}'.format(line_with_tag,self.lines,doc_id,msg_end) )
                pass  # to not report HTML tags
            else:
                self._log('DEBUG', 'Unexpected tag {!r} at line {} in doc id={}. {}'.format(line_with_tag,self.lines,doc_id,msg_end) )



    def _log( self, level:str, msg:str ):
        '''Writes a logging message if logging facility is available.'''
        if self.logger is not None:
            assert isinstance(level, str)
            level = getLevelName( level.upper() )
            self.logger.log(level, msg)


# =================================================
#   Corpus iterators
# =================================================

def _get_iterable_content_w_tqdm( iterable_content:Iterable,
                                  line_progressbar:str=None ):
    ''' Wraps tqdm progressbar around iterable_content. 
        Type  of  the  progressbar  is  given  in  argument
        line_progressbar, and it should be one of the following: 
            ['ascii', 'unicode', 'notebook']
        If line_progressbar == None, simply returns the 
        iterable_content, without any wrapping.
    '''
    progressbar_options = [None, 'ascii', 'unicode', 'notebook']
    assert line_progressbar in progressbar_options, \
       '(!) line_progressbar should be one of the following: {!r}'.format(progressbar_options)
    assert isinstance(iterable_content, (list, TextIOWrapper))
    if line_progressbar is not None:
        # If progressbar is required, then
        # 1) Find out total count
        total = 0
        if isinstance(iterable_content, list):
            # Input is list: simply get its length as total
            total = len(iterable_content)
        else:
            assert isinstance(iterable_content, TextIOWrapper)
            # Get file length in lines
            for line in iterable_content:
                total += 1
            # Restart file reading from the beginning
            iterable_content.seek(0)
        # 2) Get corresponding line_progressbar
        if line_progressbar == 'notebook':
            return notebook_tqdm(iterable_content,
                                 total=total,
                                 unit='line',
                                 smoothing=0)
        else:
            return tqdm(iterable_content,
                        total=total,
                        unit='line',
                        ascii=(line_progressbar == 'ascii'),
                        smoothing=0)
    # Otherwise (line_progressbar was not required), simply 
    # return given iterable_content
    return iterable_content



def parse_enc_file_iterator( in_file:str, 
                             encoding:str='utf-8', \
                             focus_doc_ids:set=None, \
                             focus_srcs:set=None, \
                             focus_lang:set=None, \
                             tokenization:str='preserve', \
                             original_layer_prefix:str='original_',\
                             restore_morph_analysis:bool=False, \
                             vertParser:VertXMLFileParser=None, \
                             textReconstructor:ENCTextReconstructor=None, \
                             line_progressbar:str=None, \
                             logger:Logger=None  ):
    '''Opens ENC 2017 or ENC 2019 corpus file (a vert type file), 
       reads its content document by document, reconstructs Text 
       objects from the documents, and yields created Text objects 
       one by one.
       
       If tokenization=='preserve' (default), then created Text 
       objects will have layers preserving original segmentation:
       '_original_paragraphs', '_original_sentences', '_original_words'
       and '_original_word_chunks'.
       The layer '_original_word_chunks' contains words glued together
       with punctuation.
       If tokenization=='estnltk', then the created Text objects 
       will be tokenized with estnltk's default tools, and the original
       tokenization will be discarded.
       And if tokenization=='none', no tokenization will be added 
       to texts.
       
       Parameters
       ----------
       in_file: str
           Full name of ENC corpus file (name with path);
           
       encoding: str
           Encoding of in_file. Defaults to 'utf-8';
       
       focus_doc_ids: set of str
           Set of document id-s corresponding to the documents which 
           need to be extracted from the XML content of the file.
           If provided, then only documents with given id-s will be 
           parsed, and all other documents will be skipped.
           If None or empty, then all documents in the content will 
           be parsed.
           Important note: ids must be given as strings, not as 
           integers.
       
       focus_srcs: set of str
           Set of document src-s corresponding to subcorpora which 
           documents need to be extracted from the file.
           If provided, then only documents that have a src value from
           the set will be extracted, and all other documents will 
           be skipped.
           If None or empty, then all documents in the content will 
           be parsed.
       
       focus_lang: set of str
           Set of allowed document languages.
           If provided, then only documents that have a lang value from
           the set will be extracted, and all other documents will 
           be skipped. Note that if focus_lang is set, but the document
           does not have lang attribute, then the document will also be 
           skipped;
           If None or empty, then all documents in the content will 
           be parsed.
       
       tokenization: ['none', 'preserve', 'estnltk']
            Specifies if tokenization will be added to created Texts, 
            and if so, then how it will be added. 
            Four options:
            * 'none'     -- text   will   be   created  without  any 
                            tokenization layers;
            * 'preserve' -- original tokenization from XML files will 
                            be preserved in layers of the text; 
                            This option creates layers 'tokens',
                            'compound_tokens', 'words', 'word_chunks',
                            'sentences', and 'paragraphs' (only if 
                            paragraphs were recorded in the original
                            text);
            * 'preserve_partially' -- original tokenization from XML 
                                      files will be preserved in layers 
                                      of the text, but only partially;
                                      This option creates layers 'words',
                                      'sentences', and 'paragraphs' (only 
                                      if paragraphs were recorded in the 
                                      original text);
                                      Note: using this option can help 
                                      to speed up the process, because 
                                      creating layers 'tokens' and 
                                      'word_chunks' takes some time.
            * 'estnltk'  -- text's original tokenization will be 
                            overwritten by estnltk's tokenization;
           (default: 'preserve')
      
       original_layer_prefix: str
           Prefix to be added to names of layers of original annotations
           when  tokenization=='preserve' 
                 or 
                 tokenization=='preserve_partially';
           (default: 'original_')
       
       restore_morph_analysis: boolean
           If set, then morphological analysis layer is also created 
           based on the morphological annotations available in the 
           vert file content.
           If not set, then morphological annotations will be discarded 
           and only tokenization layers will be created.
           (default: False)
       
       vertParser: VertXMLFileParser
           If set, then overrides the default VertXMLFileParser with the 
           given vertParser.
       
       textReconstructor: ENCTextReconstructor
           If set, then overrides the default ENCTextReconstructor with 
           the given textReconstructor.
       
       line_progressbar:str
           Initiates a line-counting progressbar that shows the progress on
           reading the file. Possible values: 
               ['ascii', 'unicode', 'notebook', None]
           If line_progressbar == None, then progressbar is not shown.
           Default: None
       
       logger: logging.Logger
           Logger to be used for warning and debug messages.
    '''
    assert isinstance(original_layer_prefix, str)
    assert not vertParser or isinstance(vertParser, VertXMLFileParser)
    assert not textReconstructor or isinstance(textReconstructor, ENCTextReconstructor)
    if textReconstructor:
        reconstructor = textReconstructor
    else:
        reconstructor = ENCTextReconstructor(tokenization=tokenization,\
                                             layer_name_prefix=original_layer_prefix,\
                                             restore_morph_analysis=restore_morph_analysis,\
                                             logger=logger)
    if vertParser:
        xmlParser = vertParser
    else:
        xmlParser = VertXMLFileParser(
                   focus_ids=focus_doc_ids, \
                   focus_srcs=focus_srcs, \
                   focus_lang=focus_lang, \
                   textReconstructor=reconstructor,\
                   record_morph_analysis=restore_morph_analysis,\
                   logger=logger )
    with open( in_file, mode='r', encoding=encoding ) as f:
        for line in _get_iterable_content_w_tqdm( f, line_progressbar ):
            result = xmlParser.parse_next_line( line )
            if result:
                # If the parser completed a document and created a 
                # Text object, yield it gracefully
                yield result



def parse_enc_file_content_iterator( content, 
                                     focus_doc_ids:set=None, \
                                     focus_srcs:set=None, \
                                     focus_lang:set=None, \
                                     tokenization:str='preserve', \
                                     original_layer_prefix:str='original_',\
                                     restore_morph_analysis:bool=False, \
                                     vertParser:VertXMLFileParser=None, \
                                     textReconstructor:ENCTextReconstructor=None, \
                                     line_progressbar:str=None, \
                                     logger:Logger=None  ):
    '''Reads ENC 2017 or ENC 2019 corpus file's content, extracts 
       documents based on the XML annotations, reconstructs Text 
       objects from the documents, and yields created Text objects 
       one by one.
       
       If tokenization=='preserve' (default), then created Text 
       objects will have layers preserving original segmentation:
       '_original_paragraphs', '_original_sentences', '_original_words'
       and '_original_word_chunks'.
       The layer '_original_word_chunks' contains words glued together
       with punctuation.
       If tokenization=='estnltk', then the created Text objects 
       will be tokenized with estnltk's default tools, and the original
       tokenization will be discarded.
       And if tokenization=='none', no tokenization will be added 
       to texts.
       
       Parameters
       ----------
       content: str
           ENC 2017 or 2019 corpus file's content (or a subset of the 
           content) as a string.
       
       focus_doc_ids: set of str
           Set of document id-s corresponding to the documents which 
           need to be extracted from the XML content of the file.
           If provided, then only documents with given id-s will be 
           parsed, and all other documents will be skipped.
           If None or empty, then all documents in the content will 
           be parsed.
           Important note: ids must be given as strings, not as 
           integers.
       
       focus_srcs: set of str
           Set of document src-s corresponding to subcorpora which 
           documents need to be extracted from the file.
           If provided, then only documents that have a src value from
           the set will be extracted, and all other documents will 
           be skipped.
           If None or empty, then all documents in the content will 
           be parsed.
       
       focus_lang: set of str
           Set of allowed document languages.
           If provided, then only documents that have a lang value from
           the set will be extracted, and all other documents will 
           be skipped. Note that if focus_lang is set, but the document
           does not have lang attribute, then the document will also be 
           skipped;
           If None or empty, then all documents in the content will 
           be parsed.
       
       tokenization: ['none', 'preserve', 'estnltk']
            Specifies if tokenization will be added to created Texts, 
            and if so, then how it will be added. 
            Four options:
            * 'none'     -- text   will   be   created  without  any 
                            tokenization layers;
            * 'preserve' -- original tokenization from XML files will 
                            be preserved in layers of the text; 
                            This option creates layers 'tokens',
                            'compound_tokens', 'words', 'word_chunks',
                            'sentences', and 'paragraphs' (only if 
                            paragraphs were recorded in the original
                            text);
            * 'preserve_partially' -- original tokenization from XML 
                                      files will be preserved in layers 
                                      of the text, but only partially;
                                      This option creates layers 'words',
                                      'sentences', and 'paragraphs' (only 
                                      if paragraphs were recorded in the 
                                      original text);
                                      Note: using this option can help 
                                      to speed up the process, because 
                                      creating layers 'tokens' and 
                                      'word_chunks' takes some time.
            * 'estnltk'  -- text's original tokenization will be 
                            overwritten by estnltk's tokenization;
           (default: 'preserve')
       
       original_layer_prefix: str
           Prefix to be added to names of layers of original annotations
           when  tokenization=='preserve' 
                 or 
                 tokenization=='preserve_partially';
           (default: 'original_')
       
       restore_morph_analysis: boolean
           If set, then morphological analysis layer is also created 
           based on the morphological annotations available in the 
           vert file content.
           If not set, then morphological annotations will be discarded 
           and only tokenization layers will be created.
           (default: False)
       
       vertParser: VertXMLFileParser
           If set, then overrides the default VertXMLFileParser with the 
           given vertParser.
       
       textReconstructor: ENCTextReconstructor
           If set, then overrides the default ENCTextReconstructor with the 
           given textReconstructor.
       
       line_progressbar:str
           Initiates a line-counting progressbar that shows the progress on
           reading the file. Possible values: 
               ['ascii', 'unicode', 'notebook', None]
           If line_progressbar == None, then progressbar is not shown.
           Default: None
       
       logger: logging.Logger
           Logger to be used for warning and debug messages.
    '''
    assert isinstance(content, str)
    assert isinstance(original_layer_prefix, str)
    assert not vertParser or isinstance(vertParser, VertXMLFileParser)
    assert not textReconstructor or isinstance(textReconstructor, ENCTextReconstructor)
    if textReconstructor:
        reconstructor = textReconstructor
    else:
        reconstructor = ENCTextReconstructor(tokenization=tokenization,\
                                             layer_name_prefix=original_layer_prefix,\
                                             restore_morph_analysis=restore_morph_analysis,\
                                             logger=logger)
    if vertParser:
        xmlParser = vertParser
    else:
        xmlParser = VertXMLFileParser(
                       focus_ids=focus_doc_ids, \
                       focus_srcs=focus_srcs, \
                       focus_lang=focus_lang, \
                       textReconstructor=reconstructor,\
                       record_morph_analysis=restore_morph_analysis,\
                       logger=logger)
    # Process the content line by line
    for line in _get_iterable_content_w_tqdm( content.splitlines( keepends=True ), \
                                              line_progressbar ):
        result = xmlParser.parse_next_line( line )
        if result:
            # If the parser completed a document and created a 
            # Text object, yield it gracefully
            yield result

