#
#  Module for converting etTenTen 2013 documents to EstNLTK Text objects.
#
#  The etTenTen 2013 corpus contains documents crawled from the web. 
#  Documents are in the XML format and they have metadata (e.g 
#  document URL and crawling date). Document content has been 
#  split into paragraphs, and cleaned from HTML annotation (although 
#  some tags remain).
#
#

import re

from estnltk_core.converters import records_to_layer

from estnltk import Text, Layer
from estnltk.taggers import ParagraphTokenizer

# =================================================
#   Helpful utils
# =================================================

# Pattern for capturing names & values of attributes
ettenten_tag_attrib_pat = re.compile('([^= ]+)="([^"]+?)"')


def parse_tag_attributes( tag_str ):
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
    attribs = {}
    for attr_match in ettenten_tag_attrib_pat.finditer(tag_str):
        key   = attr_match.group(1)
        value = attr_match.group(2)
        if key in attribs:
           raise Exception(' (!) Unexpected: attribute "'+key+'" appears more than once in: '+tag_str)
        attribs[key] = value
    return attribs


def extract_doc_ids_from_corpus_file( in_file, encoding='utf-8' ):
    '''Opens an etTenTen corpus file, reads its content, and 
       extracts all document id-s. 
       Returns a list of document id-s (list of strings).
       
       Parameters
       ----------
       in_file: str
           Full name of etTenTen corpus file (name with path);
           
       encoding: str
           Encoding of in_file. Defaults to 'utf-8';
       
       Returns
       -------
       list of str
           a list of extracted document id-s;
    '''
    ettenten_doc_tag_start = re.compile("<doc[^<>]+>")
    doc_ids = []
    with open( in_file, mode='r', encoding=encoding ) as f:
        for line in f:
            stripped_line = line.strip()
            m_doc_start = ettenten_doc_tag_start.search(stripped_line)
            if m_doc_start: 
                attribs = parse_tag_attributes( stripped_line )
                assert 'id' in attribs.keys()
                doc_ids.append( attribs['id'] )
    return doc_ids


# =================================================
#   Parsing and reconstruction of a document
# =================================================

def reconstruct_ettenten_text( document, \
                               add_tokenization=False, \
                               paragraph_separator='\n\n', \
                               para_internal_separator=' ' ):
    """Based on the dictionary representation of an etTenTen
       document, reconstructs an EstNLTK Text object, adds 
       tokenization to it ( if add_tokenization==True ),
       preserves the original paragraphs layer, and 
       returns the created Text object.
       
       If add_tokenization==True, then layers 'tokens', 
       'compound_tokens', 'words', 'sentences' will be 
       added to the Text object with EstNLTK, and the 
       original paragraphs layer will be added as an
       enveloping layer around 'sentences' (if enveloping
       fails, an exception will be thrown).
       If add_tokenization==False, then the original 
       paragraphs layer will be added as a stand-alone
       layer, and it will bear name 'original_paragraphs';
      
       Parameters
       ----------
       document: dict
           dictionary representation of the document;
           The dictionary should be in the following 
           format:
            { '_paragraphs' : [
                 { 'texts': [ ..., ... ] },
                 { 'texts': [ ..., ... ] },
               ...
             }

       add_tokenization:
           Adds 'tokens', 'compound_tokens', 'words', 'sentences'
           annotations with EstNLTK's default tools.
           If add_tokenization==False, then the layer 'original_paragraphs' 
           will be collected from XML annotations and added as a stand-
           alone annotation layer of Text object.
           If add_tokenization==True, then the layer 'paragraphs' 
           will be collected from XML annotations and enveloped around
           EstNLTK's 'sentences' layer.

       paragraph_separator: str
           String that will be used for separating paragraphs in 
           the reconstructed text;
           Default: '\n\n'

       para_internal_separator: str
           String that will be used for separating text snippets 
           inside paragraphs. Normally, there should be only one 
           "text snippet" inside a paragraph in the XML. But if 
           the XML contains more snippets, separated by newlines, 
           then this string will be used to join these snippets
           together into a single string.
           Default: ' '

       Returns
       -------
       Text
           reconstructed text as an EstNLTK Text object
    """
    assert '_paragraphs' in document
    assert isinstance(paragraph_separator, str)
    assert isinstance(para_internal_separator, str)
    # 0) Collect attribute names of all paragraphs
    paragraph_attrib_names = set()
    for pid, paragraph in enumerate(document['_paragraphs']):
        for attrib in paragraph.keys():
            if attrib not in ['texts']:
                paragraph_attrib_names.add( attrib )
    # 1) Reconstruct text string
    #    Collect paragraph locations from the text
    cur_pos = 0
    paragraphs     = []
    para_locations = []
    for pid, paragraph in enumerate(document['_paragraphs']):
        paragraph_content = \
            para_internal_separator.join(paragraph['texts'])
        para_location = {'start': cur_pos, \
                         'end':   cur_pos+len(paragraph_content) }
        for attrib in paragraph_attrib_names:
            para_location[attrib] = \
                 paragraph[attrib] if attrib in paragraph else None
        paragraphs.append( paragraph_content )
        para_locations.append( [para_location] )
        if pid < len(document['_paragraphs'])-1:
            paragraphs.append(paragraph_separator)
            cur_pos += len(paragraph_content)
            cur_pos += len(paragraph_separator)
    text_str = ''.join(paragraphs)
    # 2) Reconstruct text 
    text = Text( text_str )
    # 3) Add metadata
    for key in document.keys():
       if key not in ['_paragraphs']:
            text.meta[key] = document[key]
    # 4) Add EstNLTK's annotations up to sentences (optional)
    if add_tokenization:
       text.tag_layer(['tokens', 'compound_tokens'])
       text.tag_layer(['words', 'sentences'])
    # 5) Add paragraphs layer:
    if add_tokenization:
        # 5.1) Add an enveloping layer, if other annotations exist
        orig_paragraphs = Layer(name=ParagraphTokenizer.output_layer, \
                                attributes = tuple(list(paragraph_attrib_names)), \
                                enveloping='sentences', \
                                text_object=text, \
                                ambiguous=False)
        pid = 0; p_start = -1; p_end = -1
        for sid, sentence in enumerate(text['sentences']):
            if pid > len(para_locations):
               break
            paragraph = para_locations[pid][0]
            if sentence.start == paragraph['start']:
               p_start = sid
            if sentence.end == paragraph['end']:
               p_end = sid
            if p_start != -1 and p_end != -1:
               current_paragraph_attribs = {}
               for attrib in paragraph_attrib_names:
                   current_paragraph_attribs[attrib] = \
                       paragraph[attrib] if attrib in paragraph else None
               orig_paragraphs.add_annotation(text['sentences'][p_start:p_end+1], **current_paragraph_attribs)
               pid += 1; p_start = -1; p_end = -1
        if pid < len(para_locations):
           raise Exception('(!) Unable to align all paragraphs with sentences.\n'+\
                           'Unaligned paragraphs: '+str(para_locations[pid:]))
        text.add_layer(orig_paragraphs)
    else:
        # 5.2) If there are no other annotations, then add stand-alone 
        #      layer 'original_paragraphs'
        orig_paragraphs = \
            records_to_layer( \
               Layer(name = 'original_paragraphs',
                     text_object=text,
                     attributes = tuple(list(paragraph_attrib_names)),
                     ambiguous=True ), para_locations )
        text.add_layer(orig_paragraphs)
    return text



class EtTenTenXMLParser:
    """ A very simple XMLParser that allows line by line parsing of etTenTen's 
        XML files. The parser maintains the state and reconstructs a Text object 
        whenever a single document from XML has been completely parsed.
        
        This parser takes advantage of the simple structure of the input XML 
        files: all XML tags are on separate lines, so the line by line parsing 
        is actually the most straightforward approach.
    """

    def __init__(self, focus_doc_ids=None,\
                       add_tokenization=False, \
                       discard_empty_paragraphs=True, \
                       store_paragraph_attributes=True, \
                       paragraph_separator='\n\n' ):
        '''Initializes the parser.
        
           Parameters
           ----------
           focus_doc_ids: set of str
               Set of document id-s corresponding to the documents which 
               need to be extracted from the XML content.
               If provided, then only documents with given id-s will be 
               parsed, and all other documents will be skipped.
               If None or empty, then all documents in the content will 
               be parsed.
            
           add_tokenization: boolean
               Specifies if tokenization will be added to the reconstructed 
               text;
               If add_tokenization==False, then the layer 'original_paragraphs' 
               will be collected from XML annotations and added as a stand-
               alone annotation layer of Text object.
               If add_tokenization==True, then the layer 'paragraphs' 
               will be collected from XML annotations and enveloped around
               EstNLTK's 'sentences' layer, and other EstNLTK's tokenization
               layers will also be added;
               (default: False)
           
           discard_empty_paragraphs: boolean
               If set, then empty paragraphs will be discarded.
               (default: True)

           store_paragraph_attributes: boolean
               If set, then attributes in the paragraph's XML tag will be 
               collected and added as attributes of the corresponding layer
               in Text object.
               (default: True)

           paragraph_separator: str
               String that will be used for separating paragraphs in 
               the reconstructed text;
               Default: '\n\n'
        '''
        # Initialize the state of parsing
        self.lines            = 0
        self.inside_p         = False
        self.inside_focus_doc = False
        self.paragraphs = []
        self.document   = {}
        if focus_doc_ids is not None:
            assert isinstance(focus_doc_ids, set)
            if len(focus_doc_ids) == 0:
                focus_doc_ids = None
        self.focus_doc_ids              = focus_doc_ids
        self.add_tokenization           = add_tokenization
        self.store_paragraph_attributes = store_paragraph_attributes
        self.discard_empty_paragraphs   = discard_empty_paragraphs
        self.paragraph_separator        = paragraph_separator
        # Patterns for detecting tags
        self.ettenten_corpus_tag_start = re.compile("<corpus[^<>]*>")
        self.ettenten_doc_tag_start    = re.compile("<doc[^<>]+>")
        self.ettenten_doc_tag_end      = re.compile("</doc>")
        self.ettenten_p_tag_start      = re.compile("<p( [^<>]+)>")
        self.ettenten_p_tag_end        = re.compile("</p>")


    def parse_next_line( self, line: str ):
        '''Parses a next line from the XML content of etTenTen corpus.
        
           If an end of document is reached, reconstructs and returns 
           Text object based on the seen document. Otherwise, returns 
           None. 
           
           If focus_doc_ids was provided, then only documents which
           id-s are in the set focus_doc_ids will be extracted.
        '''
        stripped_line = line.strip()
        m_doc_start  = self.ettenten_doc_tag_start.search(stripped_line)
        m_doc_end    = self.ettenten_doc_tag_end.search(stripped_line)
        m_par_start  = self.ettenten_p_tag_start.search(stripped_line)
        m_par_end    = self.ettenten_p_tag_end.search(stripped_line)
        m_corp_start = self.ettenten_corpus_tag_start.search(stripped_line)
        # *** Start of a new document
        if m_doc_start: 
            self.document   = {}
            self.paragraphs = []
            attribs = parse_tag_attributes( stripped_line )
            for key, value in attribs.items():
                if key == '_paragraphs':
                   raise Exception("(!) Improper key name "+key+" in tag <doc>.")
                self.document[key] = value
            self.inside_p = False
            if self.focus_doc_ids is not None:
                self.inside_focus_doc = self.document['id'] in self.focus_doc_ids
            else:
                self.inside_focus_doc = True
        # *** End of a document
        if m_doc_end and self.inside_focus_doc:
           self.document['_paragraphs'] = self.paragraphs
           return reconstruct_ettenten_text( 
                              self.document, \
                              add_tokenization = self.add_tokenization,\
                              paragraph_separator = self.paragraph_separator )
        # Skip document if it is not one of the focus documents
        if not self.inside_focus_doc:
           self.lines += 1
           return None
        # *** New paragraph
        if m_par_start and not self.inside_p:
            self.inside_p = True
            new_paragraph = { 'texts':[] }
            if self.store_paragraph_attributes:
               attribs = parse_tag_attributes( stripped_line )
               for key, value in attribs.items():
                   if key in new_paragraph.keys():
                      raise Exception("(!) Unexpected repeating attribute name in <p>: "+str(key))
                   new_paragraph[key] = value
            self.paragraphs.append( new_paragraph )
        # *** Paragraph's end
        if m_par_end:
            if self.discard_empty_paragraphs and self.paragraphs:
               # Check if the last paragraph was empty
               last_par = self.paragraphs[-1]
               last_par_text = ''.join(last_par['texts'])
               if len(last_par_text) == 0 or re.match(r'^\s+$', last_par_text):
                   # If it was empty, remove the empty paragraph
                   self.paragraphs.pop()
            self.inside_p = False
        # *** Text content inside paragraph
        if self.inside_p and not m_par_start and len( stripped_line ) > 0:
            line = re.sub('\n{2,}','\n', line)
            last_par = self.paragraphs[-1]
            last_par['texts'].append( line.rstrip() )
        self.lines += 1
        return None


# =================================================
#   Corpus iterators
# =================================================

def parse_ettenten_corpus_file_iterator( in_file, 
                                encoding='utf-8', \
                                focus_doc_ids=None, \
                                add_tokenization=False, \
                                discard_empty_paragraphs=True, \
                                store_paragraph_attributes=False, \
                                paragraph_separator='\n\n' ):
    '''Opens an etTenTen corpus file, reads its content document 
       by document, reconstructs Text objects from the documents, 
       and yields created Text objects one by one.
       
       Created Text objects will always have a layer preserving
       original paragraph annotations (from <p> tags in XML),
       and optionally may have 'tokens', 'compound_tokens',
       'words', and 'sentences' layers created with EstNLTK's 
       default tokenization tools (if add_tokenization==True).
       If EstNLTK's tokenization is not used, the name of 
       paragraphs layer is 'original_paragraphs', otherwise
       it's name is 'paragraphs'.
       
       Parameters
       ----------
       in_file: str
           Full name of etTenTen corpus file (name with path);
           
       encoding: str
           Encoding of in_file. Defaults to 'utf-8';
       
       focus_doc_ids: set of str
            Set of document id-s corresponding to the documents which 
            need to be extracted from the in_file.
            If provided, then only documents with given id-s will be 
            processed, and all other documents will be skipped.
            If None or empty, then all documents in the file will be 
            processed.
       
       add_tokenization: boolean
           Specifies if tokenization will be added to reconstructed 
           texts;
           If add_tokenization==False, then the layer 'original_paragraphs' 
           will be collected from XML annotations and added as a stand-
           alone annotation layer of a Text object.
           If add_tokenization==True, then the layer 'paragraphs' 
           will be collected from XML annotations and enveloped around
           EstNLTK's 'sentences' layer, and other EstNLTK's tokenization
           layers will also be added;
           (default: False)
       
       discard_empty_paragraphs: boolean
           If set, then empty paragraphs will be discarded.
           (default: True)

       store_paragraph_attributes: boolean
           If set, then attributes in the paragraph's XML tag will be 
           collected and added as attributes of the corresponding layer
           in a Text object.
           (default: True)

       paragraph_separator: str
           String that will be used for separating paragraphs in 
           the reconstructed text;
           Default: '\n\n'
    '''
    xmlParser = EtTenTenXMLParser(
                   focus_doc_ids=focus_doc_ids, \
                   add_tokenization=add_tokenization, \
                   discard_empty_paragraphs=discard_empty_paragraphs, \
                   store_paragraph_attributes=store_paragraph_attributes, \
                   paragraph_separator=paragraph_separator )
    with open( in_file, mode='r', encoding=encoding ) as f:
        for line in f:
            result = xmlParser.parse_next_line( line )
            if result:
                # If the parser completed a document and created a 
                # Text object, yield it gracefully
                yield result



def parse_ettenten_corpus_file_content_iterator( content, \
                                                 focus_doc_ids=None, \
                                                 add_tokenization=False, \
                                                 discard_empty_paragraphs=True, \
                                                 store_paragraph_attributes=True, \
                                                 paragraph_separator='\n\n' ):
    '''Reads etTenTen corpus file's content, extracts documents 
       based on the XML annotations, reconstructs Text objects from 
       the documents, and yields created Text objects one by one.
       
       Created Text objects will always have a layer preserving
       original paragraph annotations (from <p> tags in XML),
       and optionally may have 'tokens', 'compound_tokens',
       'words', and 'sentences' layers created with EstNLTK's 
       default tokenization tools (if add_tokenization==True).
       If EstNLTK's tokenization is not used, the name of 
       paragraphs layer is 'original_paragraphs', otherwise
       it's name is 'paragraphs'.
       
       Parameters
       ----------
       content: str
           etTenTen corpus file's content (or a subset of the content) 
           as a string.
       
       focus_doc_ids: set of str
            Set of document id-s corresponding to the documents which 
            need to be extracted from the content.
            If provided, then only documents with given id-s will be 
            processed, and all other documents will be skipped.
            If None or empty, then all documents in the content will 
            be processed.
       
       add_tokenization: boolean
           Specifies if tokenization will be added to reconstructed 
           texts;
           If add_tokenization==False, then the layer 'original_paragraphs' 
           will be collected from XML annotations and added as a stand-
           alone annotation layer of a Text object.
           If add_tokenization==True, then the layer 'paragraphs' 
           will be collected from XML annotations and enveloped around
           EstNLTK's 'sentences' layer, and other EstNLTK's tokenization
           layers will also be added;
           (default: False)
       
       discard_empty_paragraphs: boolean
           If set, then empty paragraphs will be discarded.
           (default: True)

       store_paragraph_attributes: boolean
           If set, then attributes in the paragraph's XML tag will be 
           collected and added as attributes of the corresponding layer
           in a Text object.
           (default: True)

       paragraph_separator: str
           String that will be used for separating paragraphs in 
           the reconstructed text;
           Default: '\n\n'
    '''
    assert isinstance(content, str)
    xmlParser = EtTenTenXMLParser(
                   focus_doc_ids=focus_doc_ids, \
                   add_tokenization=add_tokenization, \
                   discard_empty_paragraphs=discard_empty_paragraphs, \
                   store_paragraph_attributes=store_paragraph_attributes, \
                   paragraph_separator=paragraph_separator )
    # Process the content line by line
    for line in content.splitlines( keepends=True ):
        result = xmlParser.parse_next_line( line )
        if result:
            # If the parser completed a document and created a 
            # Text object, yield it gracefully
            yield result

