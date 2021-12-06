#
# Module for converting Koondkorpus XML TEI files to EstNLTK Text objects.
# Ported from the version 1.4.1.1:
#    https://github.com/estnltk/estnltk/blob/1.4.1.1/estnltk/teicorpus.py
#    ( with modifications )
# 
# The corpus (see http://www.cl.ut.ee/korpused/segakorpus/index.php?lang=et) contains 
# a variety of documents from different domains and can be used freely for non-commercial 
# purposes. EstNLTK is capable of reading XML formatted files of the corpus, and parsing 
# the documents, paragraphs, sentences and words with some additional metadata found in 
# XML files.
#
# The implementation is currently quite simplistic, though. But it should be sufficient 
# for simpler use cases. By default, the resulting documents have paragraphs separated by 
# two newlines and sentences by single newline. The original plain text is not known for 
# XML TEI files. Note that all punctuation has been separated from words in the TEI files. 
# 

from estnltk import Text
from estnltk import Layer
from estnltk_core.converters import json_to_text
from estnltk_core.converters import records_to_layer
from estnltk.taggers import TokensTagger, CompoundTokenTagger, WordTagger
from estnltk.taggers import SentenceTokenizer, ParagraphTokenizer

from estnltk.taggers import Tagger

from bs4 import BeautifulSoup
from copy import deepcopy

import os, os.path, re

from zipfile import ZipFile
import tarfile

# Tokenizer that splits text into words by spaces (created only if needed)
koond_whitespace_tokenizer   = None

# Whether the words layer should be made ambiguous
_MAKE_WORDS_AMBIGUOUS = True

def get_div_target( fnm ):
    """Based on the full name of the XML file (the name with full path), determines
       <div> type which is considered as a document in that XML file. 
       The <div> type usually needs to be manually looked up from the corpus 
       documentation. This function, therefore, uses hard-coded values.

    Parameters
    ----------
    fnm: str
        The full directory path to the XML TEI file along with the file name;
        
    Returns
    -------
    str
        <div> type corresponding to a document in the given XML file;
    """
    if 'drtood' in fnm:
        return 'dissertatsioon'
    if 'ilukirjandus' in fnm:
        return 'tervikteos'
    if 'seadused' in fnm:
        return 'seadus'
    if 'EestiArst' in fnm:
        return 'ajakirjanumber'
    if 'foorumid' in fnm:
        return 'teema'
    if 'kommentaarid' in fnm:
        return 'kommentaarid'
    if 'uudisgrupid' in fnm:
        return 'uudisgrupi_salvestus'
    if 'jututoad' in fnm:
        return 'jututoavestlus'
    if 'stenogrammid' in fnm:
        return 'stenogramm'
    return 'artikkel'


def get_text_subcorpus_name( corpus_dir, corpus_file, text_obj, \
                             expand_names = True ):
    """Based on the name of the text's file, and its directory or Text object, 
       determines to which subcorpus of the Reference Corpus the text belongs 
       to. Returns the name of the subcorpus, or None, if the subcorpus could 
       not be determined.
       
       Logic for determining the subcorpus is mostly based on checking the 
       name of the file. If the name is not helpful, then metadata inside 
       the Text object is also checked for additional cues. 
       The following logic is used for getting the Text object. If corpus_dir
       is provided, then the Text object is loaded from the json file
       located at corpus_dir + corpus_file. Otherwise, the Text object 
       should be given as the input argument text_obj.

    Parameters
    -----------
    corpus_dir: str
        The directory of the corpus_file; If metadata of the Text object
        needs to be checked, then the location corpus_dir + corpus_file
        should contain the Text object in json format;

    corpus_file: str
        Name of the file which corpus needs to be determined; In most 
        cases, the name of the subcorpus can be determined based on this 
        name. However, if not, then either corpus_dir or text_obj must 
        be provided;

    text_obj: Text
        Text object which is alternatively used for determining the 
        subcorpus name. For that purpose, metadata fields of the object will
        be checked;

    expand_names: boolean
        Whether subcorpus names should be expanded from short names to full 
        names, e.g. 'aja' -> 'ajakirjandus', 'sea' -> 'seadus' etc.
        (default: True)
    
    Returns
    -------
    str
       name of the subcorpus, or None, if the subcorpus could not be determined;
    """
    assert text_obj is not None or corpus_dir is not None, \
           '(!) At least one of the arguments corpus_dir and text_obj must be not None.'
    f_prefix  = re.sub(r'^([A-Za-z_\-]+)(\.|[0-9]+).*', '\\1', corpus_file)
    text_type = None
    if f_prefix.startswith('ilu_'):
        f_prefix  = 'ilu_'
        text_type = f_prefix
        if expand_names:
            text_type = text_type.replace('ilu', 'ilukirjandus')
    if f_prefix.startswith('tea_'):
        f_prefix = 'tea_'
        text_type = f_prefix
        if expand_names:
            text_type = text_type.replace('tea', 'teadus')
    if f_prefix.startswith('agraar_'):
        f_prefix = 'tea_'
        text_type = f_prefix
        if expand_names:
            text_type = text_type.replace('tea', 'teadus')
    if f_prefix.startswith('horisont_'):
        f_prefix = 'tea_'
        text_type = f_prefix
        if expand_names:
            text_type = text_type.replace('tea', 'teadus')
    if f_prefix.startswith('sea_'):
        f_prefix = 'sea_'
        text_type = f_prefix.replace('sea', 'seadus')
        if expand_names:
            text_type = text_type.replace('sea', 'seadus')
    if f_prefix.startswith('rkogu_'):
        f_prefix = 'rkogu_'
        text_type = f_prefix
        if expand_names:
            text_type = text_type.replace('rkogu', 'riigikogu_stenogramm')
    if f_prefix.startswith('aja_'):
        text_type = f_prefix
        if expand_names:
            text_type = text_type.replace('aja', 'ajakirjandus')
    if text_type and text_type.endswith('_'):
        text_type = text_type[:-1]
    # If text type cannot be determined from the name of the file, 
    # try to get it from metadata of the Text object
    if not text_type:
        if corpus_dir is not None:
            # A) Load Text object from the file
            fnm = os.path.join( corpus_dir, corpus_file )
            loaded_text_obj = json_to_text( file = fnm )
        elif text_obj is not None:
            # B) Take Text object that was provided as an argument
            loaded_text_obj = text_obj
        if 'alamfoorum' in loaded_text_obj.meta.keys():
            text_type = 'netifoorum'
        elif 'type' in loaded_text_obj.meta.keys():
            if loaded_text_obj.meta['type'] == 'jututoavestlus':
                text_type = loaded_text_obj.meta['type']
            elif loaded_text_obj.meta['type'] == 'uudisgrupi_salvestus':
                text_type = loaded_text_obj.meta['type']
            elif loaded_text_obj.meta['type'] == 'kommentaarid':
                text_type = 'neti'+loaded_text_obj.meta['type']
    return text_type


def parse_tei_corpora(root, prefix='', suffix='.xml', target=['artikkel'], \
                      encoding='utf-8', add_tokenization=False, \
                      preserve_tokenization=False, record_xml_filename=False, \
                      sentence_separator='\n', paragraph_separator='\n\n',\
                      orig_tokenization_layer_name_prefix='' ):
    """Parse documents from TEI style XML files.
    
    Gives each document FILE attribute that denotes the original filename.
    
    Parameters
    ----------
    root: str
        The directory path containing the TEI corpora XMl files.
    prefix: str
        The prefix of filenames to include (default: '')
    suffix: str
        The suffix of filenames to include (default: '.xml')
    target: list of str
        List of <div> types, that are considered documents in the XML files (default: ["artikkel"]).
    encoding: str
        Encoding to be used for decoding the content of the XML file. Defaults to 'utf-8'.
        If overwritten by None, then no separate decoding step is applied. 
    add_tokenization: boolean
        If True, then tokenization layers 'tokens', 'compound_tokens', 
        'words', 'sentences', 'paragraphs' will be added to all newly created 
        Text instances;
        If preserve_orig_tokenization is set, then original tokenization in 
        the document will be preserved; otherwise, the tokenization will be
        created with EstNLTK's default tokenization tools;
        (Default: False)
    preserve_tokenization: boolean
        If True, then the original segmentation from the XML file (sentences 
        between <s> and </s>, paragraphs between <p> and </p>, and words &
        tokens separated by spaces) is also preserved in the newly created Text 
        instances;
        Note: this only has effect if add_tokenization has been switched on;
        (Default: False)
    record_xml_filename: boolean
        If True, then the created documents will have the name of the original 
        XML file recorded in their metadata, under the key '_xml_file'. 
        (default: False)
    sentence_separator: str
        String to be used as a sentence separator during the reconstruction
        of the text. The parameter value should be provided, None is not 
        allowed.
        (Default: '\n')
    paragraph_separator: str
        String to be used as a paragraph separator during the reconstruction
        of the text. The parameter value should be provided, None is not 
        allowed.
        (Default: '\n\n')
    orig_tokenization_layer_name_prefix: str
        Prefix that will be added to names of layers of original tokenization, 
        if preserve_tokenization==True. 
        (Default: '')
    Returns
    -------
    list of estnltk.text.Text
        Corpus containing parsed documents from all files. The file path
        is stored in FILE attribute of the documents.
    """
    documents = []
    for fnm in get_filenames(root, prefix, suffix):
        path = os.path.join(root, fnm)
        docs = parse_tei_corpus(path, target, encoding, \
                                add_tokenization=add_tokenization, \
                                preserve_tokenization=preserve_tokenization, \
                                record_xml_filename=record_xml_filename, \
                                sentence_separator=sentence_separator, \
                                paragraph_separator=paragraph_separator, \
                                orig_tokenization_layer_name_prefix=orig_tokenization_layer_name_prefix )
        documents.extend(docs)
    return documents



def parse_tei_corpus(path, target=['artikkel'], encoding='utf-8', add_tokenization=False, \
                     preserve_tokenization=False, record_xml_filename=False, \
                     sentence_separator='\n', paragraph_separator='\n\n',\
                     orig_tokenization_layer_name_prefix='' ):
    """Load content of an XML TEI file, and parse documents from the content.
       Return a list of Text objects.
    
    Parameters
    ----------
    path: str
        The path of the XML file.
    target: list of str
        List of <div> types, that are considered documents in the XML files (default: ["artikkel"]).
    encoding: str
        Encoding to be used for decoding the content of the XML file. Defaults to 'utf-8'.
        If overwritten by None, then no separate decoding step is applied. 
    add_tokenization: boolean
        If True, then tokenization layers 'tokens', 'compound_tokens', 
        'words', 'sentences', 'paragraphs' will be added to all newly created 
        Text instances;
        If preserve_orig_tokenization is set, then original tokenization in 
        the document will be preserved; otherwise, the tokenization will be
        created with EstNLTK's default tokenization tools;
        (Default: False)
    preserve_tokenization: boolean
        If True, then the original segmentation from the XML file (sentences 
        between <s> and </s>, paragraphs between <p> and </p>, and words &
        tokens separated by spaces) is also preserved in the newly created Text 
        instances;
        Note: this only has effect if add_tokenization has been switched on;
        (Default: False)
    record_xml_filename: boolean
        If True, then the created documents will have the name of the original XML file recorded in 
        their metadata, under the key '_xml_file'. 
        (default: False)
    sentence_separator: str
        String to be used as a sentence separator during the reconstruction
        of the text. The parameter value should be provided, None is not 
        allowed.
        (Default: '\n')
    paragraph_separator: str
        String to be used as a paragraph separator during the reconstruction
        of the text. The parameter value should be provided, None is not 
        allowed.
        (Default: '\n\n')
    orig_tokenization_layer_name_prefix: str
        Prefix that will be added to names of layers of original tokenization, 
        if preserve_tokenization==True. 
        (Default: '')
    Returns
    -------
        list of esnltk.text.Text
    """
    with open(path, 'rb') as f:
        xml_doc_content = f.read()
    if encoding:
        xml_doc_content = xml_doc_content.decode( encoding )
    return parse_tei_corpus_file_content( xml_doc_content, path, target=target, \
                                          add_tokenization=add_tokenization, \
                                          preserve_tokenization = preserve_tokenization,\
                                          record_xml_filename = record_xml_filename,\
                                          sentence_separator=sentence_separator, \
                                          paragraph_separator=paragraph_separator, \
                                          orig_tokenization_layer_name_prefix=orig_tokenization_layer_name_prefix )



def parse_tei_corpus_file_content(content, file_path, target=['artikkel'], \
                                  add_tokenization=False, \
                                  preserve_tokenization=False, \
                                  record_xml_filename=False, \
                                  sentence_separator='\n', \
                                  paragraph_separator='\n\n',\
                                  orig_tokenization_layer_name_prefix='' ):
    """Parse documents from the (string) content of an XML TEI file. 
       Return a list of Text objects.
    
    Parameters
    ----------
    content: str
        Content of a single XML TEI file from Koondkorpus. Assumes that the content string 
        has already been decoded;
    file_path: str
        The path of the XML file. This is required for recording name of the original XML 
        file in metadata of a created Text object (see the argument record_xml_filename 
        for details); 
    target: list of str
        List of <div> types, that are considered documents in the XML files (default: ["artikkel"]).
    add_tokenization: boolean
        If True, then tokenization layers 'tokens', 'compound_tokens', 
        'words', 'sentences', 'paragraphs' will be added to all newly created 
        Text instances;
        If preserve_orig_tokenization is set, then original tokenization in 
        the document will be preserved; otherwise, the tokenization will be
        created with EstNLTK's default tokenization tools;
        (Default: False)
    preserve_tokenization: boolean
        If True, then the original segmentation from the XML file (sentences 
        between <s> and </s>, paragraphs between <p> and </p>, and words &
        tokens separated by spaces) is also preserved in the newly created Text 
        instances;
        Note: this only has effect if add_tokenization has been switched on;
        (Default: False)
    record_xml_filename: boolean
        If True, then the created documents will have the name of the original XML file recorded in 
        their metadata, under the key '_xml_file'. 
        (default: False)
    sentence_separator: str
        String to be used as a sentence separator during the reconstruction
        of the text. The parameter value should be provided, None is not 
        allowed.
        (Default: '\n')
    paragraph_separator: str
        String to be used as a paragraph separator during the reconstruction
        of the text. The parameter value should be provided, None is not 
        allowed.
        (Default: '\n\n')
    orig_tokenization_layer_name_prefix: str
        Prefix that will be added to names of layers of original tokenization, 
        if preserve_tokenization==True. 
        (Default: '')
    Returns
    -------
        list of esnltk.text.Text
    """
    soup = BeautifulSoup(content, 'html5lib')
    title = soup.find_all('title')[0].string
    
    documents = []
    for div1 in soup.find_all('div1'):
        documents.extend(parse_div(div1, dict(), target))
    if record_xml_filename:
        # Record name of the original XML file
        path_head, path_tail = os.path.split(file_path)
        for doc in documents:
            doc['_xml_file'] = path_tail
    return create_estnltk_texts( documents, \
                                 add_tokenization=add_tokenization, \
                                 sentence_separator=sentence_separator, \
                                 paragraph_separator=paragraph_separator, \
                                 preserve_orig_tokenization=preserve_tokenization, \
                                 orig_tokenization_layer_name_prefix=orig_tokenization_layer_name_prefix )



def parse_div(soup, metadata, target):
    """Parse a <div> tag from the file.
    
    The sections in XML files are given in <div1>, <div2> and <div3>
    tags. Each such tag has a type and name (plus possibly more extra attributes).
    
    If the div type is found in target variable, the div is parsed
    into structured paragraphs, sentences and words.
    
    Otherwise, the type and name are added as metadata to subdivs
    and stored in.
    
    Parameters
    ----------
    soup: bs4.BeautifulSoup
        The parsed XML data.
    metdata: dict
        The metadata for parent divs.
    target: list of str
        List of <div> types, that are considered documents in the XML files.
    
    """
    documents = []
    div_type = soup.get('type', None)
    div_title = list(soup.children)[0].string.strip()
    
    if div_type in target:
        div_authors = soup.find_all('author')
        document = {
            'type': div_type,
            'title': div_title
        }
        # add the textual content (paragraphs)
        if div_type.lower() == 'jututoavestlus':
            paragraphs_content = parse_chat_paragraphs( soup )
        else:
            paragraphs_content = parse_paragraphs( soup )
        document['paragraphs'] = paragraphs_content
        # add author, if it exists
        if len(div_authors) > 0:
            div_author = div_authors[0].text.strip()
            document['author'] = div_author
        # add collected metadata
        for k, v in metadata.items():
            document[k] = v
        documents.append(document)
    else:
        metadata[div_type] = div_title

        # recurse subdivs
        subdiv_name = get_subdiv(soup.name)
        subdivs = []
        if subdiv_name is not None:
            subdivs = soup.find_all(subdiv_name)
        if len(subdivs) > 0:
            for subdiv in subdivs:
                documents.extend(parse_div(subdiv, deepcopy(metadata), target))
    return documents


def parse_paragraphs(soup):
    """Parse sentences and paragraphs in the section.
    
    Parameters
    ----------
    soup: bs4.BeautifulSoup
        The parsed XML data.
        
    Returns
    -------
    list of (list of str)
        List of paragraphs given as list of sentences.
    """
    paragraphs = []
    for para in soup.find_all('p'):
        sentences = []
        for sent in para.find_all('s'):
            sentence = sent.text.strip()
            if len(sentence) > 0:
                sentences.append(sentence)
        if len(sentences) > 0:
            paragraphs.append({'sentences': sentences})
    return paragraphs


def parse_chat_paragraphs(soup):
    """Parse paragraphs from the chat subcorpus (jututubade korpus).
       The structure of XML is a little bit different in the chat 
       subcorpus than in the rest of the Estonian Reference Corpus, 
       so, a special approach is required for the parsing.
    
    Parameters
    ----------
    soup: bs4.BeautifulSoup
        The parsed XML data.
        
    Returns
    -------
    list of (list of str)
        List of paragraphs given as list of sentences.
    """
    paragraphs = []
    for para in soup.find_all('sp'):
        sentences = []
        p_tags       = para.find_all('p')
        speaker_tags = para.find_all('speaker')
        assert len(list(p_tags))==len(list(speaker_tags))
        for sid, p_tag in enumerate(p_tags):
            speaker  = speaker_tags[sid].text.strip()
            sentence = p_tag.text.strip()
            if len(sentence) > 0:
                # Normalize speaker name
                speaker = speaker.replace(':', '__colon__')
                sentences.append(speaker+': '+sentence)
        if len(sentences) > 0:
            paragraphs.append({'sentences': sentences})
    return paragraphs


def _reconstruct_enveloping_tokenization_layers( text_object, \
                                                 token_locations, \
                                                 sent_locations, \
                                                 para_locations, \
                                                 create_token_layers = False,
                                                 layer_name_prefix = ''):
    """Based on dictionary representations of tokens, 
       sentences, and paragraphs, reconstructs tokens, 
       compound_tokens, words, sentences, and paragraphs
       layers  along  with  the  EstNLTK's  enveloping 
       relations between the layers. Returns a list of 
       created layers.
       
       Following enveloping relations are used: 
        'compound_tokens' envelops 'tokens', 
        'sentences' envelops 'words', and 
        'paragraphs' envelops 'sentences'.
      
       Note that layers 'tokens', 'compound_tokens', 'words'
       are only created if create_token_layers == True.
       Otherwise, only layers 'sentences' and 'paragraphs'
       are created and returned.

       Parameters
       ----------
       text_object: Text
           Text object which will be associated with created
           layers;
       create_token_layers: boolean
           If set, then layers 'tokens', 'compound_tokens', 
           'words', 'sentences', and 'paragraphs' are created;
           otherwise, only layers 'sentences', and 'paragraphs' 
           are created;
           Default: False
       token_locations: list of dict
           List of token/word locations. Each location in the list 
           should be a dict, where key 'start' gives the start
           position and 'end' (exclusive) end position.
       sent_locations: list of dict
           List of sentence locations. Each location in the list 
           should be a dict, where key 'start' gives the start
           position and 'end' (exclusive) end position.
       para_locations: list of dict
           List of paragraph locations. Each location in the list 
           should be a dict, where key 'start' gives the start
           position and 'end' (exclusive) end position.
       layer_name_prefix: str
           Prefix that will be added to names of created layers
           in the reconstructed text;
           Default: ''
       
       Returns
       -------
       list of Layers
           a list of created layers along with the enveloping 
           relations;
    """
    assert isinstance(layer_name_prefix, str)
    created_layers       = []
    orig_tokens          = None
    orig_compound_tokens = None
    orig_words           = None
    orig_sentences       = None
    orig_paragraphs      = None
    if create_token_layers:
       # Create tokens layer from the token records
       orig_tokens = \
            records_to_layer( \
               Layer(name=layer_name_prefix+TokensTagger.output_layer, \
                     attributes=TokensTagger.output_attributes, \
                     text_object=text_object,\
                     ambiguous=False), token_locations)
       # Create compound tokens layer
       # Note: this layer will remain empty, as there is no information
       #       about compound tokens in the original text
       orig_compound_tokens = \
           Layer(name=layer_name_prefix+CompoundTokenTagger.output_layer, \
                 enveloping=orig_tokens.name, \
                 attributes=CompoundTokenTagger.output_attributes, \
                 text_object=text_object,\
                 ambiguous=False)
       # Create words layer from the token records
       if _MAKE_WORDS_AMBIGUOUS:
           token_locations = [ [tl] for tl in token_locations ]
       orig_words = \
            records_to_layer( \
               Layer(name=layer_name_prefix+WordTagger.output_layer, \
                     attributes=WordTagger.output_attributes, \
                     text_object=text_object,\
                     ambiguous=_MAKE_WORDS_AMBIGUOUS), token_locations )
       # Envelop sentences around words
       orig_sentences = Layer(name=layer_name_prefix+SentenceTokenizer.output_layer, \
                              enveloping=orig_words.name, \
                              attributes=SentenceTokenizer.output_attributes, \
                              text_object=text_object,\
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
              orig_sentences.add_annotation(orig_words[s_start:s_end+1])
              sid += 1; s_start = -1; s_end = -1
    else:
       # If the words layer was not provided, create a detached 
       # sentences layer
       orig_sentences = \
            records_to_layer( \
               Layer(name=layer_name_prefix+SentenceTokenizer.output_layer,\
                     text_object=text_object ), sent_locations )
    # Envelop paragraphs around sentences
    orig_paragraphs = Layer(name=layer_name_prefix+ParagraphTokenizer.output_layer, \
                            enveloping=orig_sentences.name, \
                            text_object=text_object, \
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
          orig_paragraphs.add_annotation(orig_sentences[p_start:p_end+1])
          pid += 1; p_start = -1; p_end = -1
    # Assemble created layers and return as a list
    if orig_words is not None:
       created_layers.append( orig_tokens )
       created_layers.append( orig_compound_tokens )
       created_layers.append( orig_words )
    created_layers.append( orig_sentences )
    created_layers.append( orig_paragraphs )
    return created_layers



def reconstruct_text( doc, \
                      sent_separator = '\n', \
                      para_separator = '\n\n',\
                      tokens_tagger  = None, \
                      layer_name_prefix = '',\
                      use_enveloping_layers = False ):
    """Based on the dictionary representation of a text, 
       reconstructs an EstNLTK Text object, creates layers
       preserving the original tokenization ( layers 
       'paragraphs'  and  'sentences'), and returns a tuple 
       containing the Text object and a list of created 
       layers.
       Note that created layers will not be attached to 
       the created Text object, but if use_enveloping_layers 
       is set, then they are suitable for attachment if 
       required.
       
       If tokens_tagger is provided, then the tokens_tagger 
       is used for segmenting sentences into word tokens and
       based on the segmentation, layers 'tokens', 'words',
       and 'compound_tokens' are also added to the returned 
       list of layers. Note that the layer 'compound_tokens'
       will always remain empty.

       Parameters
       ----------
       doc:  dict
           The dictionary representation of an imported XML 
           document. This dictionary is used as a basis for 
           reconstructing the text.
           The dictionary should be in the following format:
            { 'paragraphs' : [
               { 'sentences': [ ..., ... ] },
               { 'sentences': [ ..., ... ] },
               ...
             }

       sent_separator: str
           String that will be used for separating sentences in 
           the reconstructed text;
           Default: '\n'

       para_separator: str
           String that will be used for separating paragraphs in 
           the reconstructed text;
           Default: '\n\n'
       
       tokens_tagger: Tagger
           EstNLTK's Tagger that can be used for splitting 
           sentences into tokens. If specified, then tagger's 
           method tag() will be used for splitting each sentence 
           into words & tokens, and results will be stored in  
           layers named 'tokens', 'compound_tokens', and 'words'; 
           If tokens_tagger is None, then the returned list of 
           layers will not contain layers 'words', 'tokens',
           nor 'compound_tokens';
           Default: None

       layer_name_prefix: str
           Prefix that will be added to names of created layers
           in the reconstructed text;
           Default: ''
       
       use_enveloping_layers: boolean
           If True, then layer enveloping will be used: 'sentences'
           will envelop around 'words', and 'paragraphs' will envelop
           around 'sentences'. Otherwise, created layers will not be 
           connected with each other;
           Default: False
       
       Returns
       -------
       (Text, list of Layers)
           Reconstructed Text object,  and  a  list  of  layers 
           that preserve the original tokenization;
    """
    assert not tokens_tagger or isinstance(tokens_tagger, Tagger)
    assert isinstance(layer_name_prefix, str)
    # 1) Reconstruct text string
    #    Collect sentence and paragraph locations from the text
    #    Optionally, token locations can also be collected
    sent_locations  = []
    para_locations  = []
    token_locations = []
    cur_pos = 0
    paragraphs = []
    for pid, para in enumerate(doc['paragraphs']):
        sentences = []
        for sid, sentence in enumerate(para['sentences']):
            if tokens_tagger:
                records = []
                t_text = tokens_tagger.tag( Text(sentence) )
                for tok_span in t_text[tokens_tagger.output_layer]:
                    records.append( {'start': tok_span.start + cur_pos,\
                                     'end':   tok_span.end + cur_pos } )
                token_locations.extend( records )
            sent_location = {'start': cur_pos, \
                             'end':   cur_pos+len(sentence) }
            sentences.append(sentence)
            sent_locations.append(sent_location)
            cur_pos += len(sentence)
            if sid < len(para['sentences'])-1:
               sentences.append(sent_separator)
               cur_pos += len(sent_separator)
        paragraph_content = ''.join(sentences)
        para_location = {'start': cur_pos-len(paragraph_content), \
                         'end':   cur_pos }
        paragraphs.append( paragraph_content )
        para_locations.append( para_location )
        if pid < len(doc['paragraphs'])-1:
            paragraphs.append(para_separator)
            cur_pos += len(para_separator)
    text_str = ''.join(paragraphs)
    # 2) Reconstruct text 
    text = Text( text_str )
    # 3) Add metadata
    for key in doc.keys():
       if key not in ['paragraphs', 'sentences']:
            text.meta[key] = doc[key]
    # 4) Create tokenization layers
    if not use_enveloping_layers:
        # 4.1) Make detached layers
        orig_sentences  = \
            records_to_layer( \
               Layer(name=layer_name_prefix+'sentences',\
                     text_object=text), sent_locations)
        orig_paragraphs = \
            records_to_layer( \
               Layer(name=layer_name_prefix+'paragraphs',\
                     text_object=text), para_locations)
        created_layers = [orig_sentences, orig_paragraphs]
        if tokens_tagger:
           orig_compound_tokens = Layer(name='compound_tokens',\
                                        text_object=text)
           created_layers.insert(0, orig_compound_tokens)
           orig_tokens = \
                records_to_layer( \
                  Layer(name=layer_name_prefix+'tokens',\
                        text_object=text), token_locations)
           created_layers.insert(0, orig_tokens)
           if _MAKE_WORDS_AMBIGUOUS:
              token_locations = [ [tl] for tl in token_locations ]
           orig_words = \
                records_to_layer( \
                  Layer(name=layer_name_prefix+'words',\
                        text_object=text, 
                        ambiguous=_MAKE_WORDS_AMBIGUOUS), token_locations)
           created_layers.insert(0, orig_words)
    else:
        # 4.2) Make connected layers
        created_layers = _reconstruct_enveloping_tokenization_layers( 
                              text, \
                              token_locations, \
                              sent_locations, \
                              para_locations, \
                              create_token_layers = tokens_tagger is not None, \
                              layer_name_prefix = layer_name_prefix )
    return text, created_layers



def create_estnltk_texts( docs, 
                          add_tokenization=False,
                          preserve_orig_tokenization=False, \
                          sentence_separator='\n', \
                          paragraph_separator='\n\n', \
                          orig_tokenization_layer_name_prefix='',\
                          ):
    """Convert the imported documents to Text instances.

    Parameters
    ----------
    docs: list of (dict of dict)
        Documents parsed from an XML file that need to be converted
        to EstNLTK's Text objects;

    add_tokenization: boolean
        If True, then tokenization layers 'tokens', 'compound_tokens', 
        'words', 'sentences', 'paragraphs' will be added to all newly created 
        Text instances;
        If preserve_orig_tokenization is set, then original tokenization in 
        the document will be preserved; otherwise, the tokenization will be
        created with EstNLTK's default tokenization tools;
        (Default: False)
        
    preserve_orig_tokenization: boolean
        If True, then the original segmentation from the XML file (sentences 
        between <s> and </s>, paragraphs between <p> and </p>, and words &
        tokens separated by spaces) is also preserved in the newly created Text 
        instances;
        Note: this only has effect if add_tokenization has been switched on;
        (Default: False)
    
    sentence_separator: str
        String to be used as a sentence separator during the reconstruction
        of the text. The parameter value should be provided, None is not 
        allowed.
        (Default: '\n')
    
    orig_tokenization_layer_name_prefix: str
        Prefix that will be added to names of layers of original tokenization, 
        if preserve_orig_tokenization==True. 
        (Default: '')
    
    paragraph_separator: str
        String to be used as a paragraph separator during the reconstruction
        of the text. The parameter value should be provided, None is not 
        allowed.
        (Default: '\n\n')
    
    Returns
    -------
    list of Texts
        List of EstNLTK's Text objects.
    """
    global koond_whitespace_tokenizer
    assert isinstance(sentence_separator, str)
    assert isinstance(paragraph_separator, str)
    assert isinstance(orig_tokenization_layer_name_prefix, str)
    if add_tokenization and \
       preserve_orig_tokenization and \
       not koond_whitespace_tokenizer:
        # Create a word tokenizer that only splits into words by whitespaces
        from estnltk.taggers.standard.text_segmentation.whitespace_tokens_tagger \
             import WhiteSpaceTokensTagger
        koond_whitespace_tokenizer = \
           WhiteSpaceTokensTagger()
    texts = []
    for doc in docs:
        # 0) Reconstruct the text (and original layers)
        text, created_layers  = \
                  reconstruct_text( doc, sent_separator = sentence_separator, 
                                         para_separator = paragraph_separator, 
                                         tokens_tagger  = koond_whitespace_tokenizer, 
                                         use_enveloping_layers = preserve_orig_tokenization,
                                         layer_name_prefix=orig_tokenization_layer_name_prefix )
        # 1) Add metadata
        for key in doc.keys():
           if key not in ['paragraphs', 'sentences']:
                text.meta[key] = doc[key]
        # 2) Add tokenization (if required)
        if add_tokenization:
           if preserve_orig_tokenization:
                # Reconstruct tokenization layers based on the original ones
                prefix = orig_tokenization_layer_name_prefix
                tokens = \
                    [layer for layer in created_layers if layer.name==prefix+'tokens'][0]
                compound_tokens = \
                    [layer for layer in created_layers if layer.name==prefix+'compound_tokens'][0]
                words = \
                    [layer for layer in created_layers if layer.name==prefix+'words'][0]
                sentences = \
                    [layer for layer in created_layers if layer.name==prefix+'sentences'][0]
                paragraphs = \
                    [layer for layer in created_layers if layer.name==prefix+'paragraphs'][0]
                text.add_layer(tokens)
                text.add_layer(compound_tokens)
                text.add_layer(words)
                text.add_layer(sentences)
                text.add_layer(paragraphs)
           else:
                # Add tokenization with EstNLTK
                # ( overwrites the original tokenization )
                text.tag_layer(['tokens', 'compound_tokens'])
                text.tag_layer(['words', 'sentences', 'paragraphs'])
        texts.append( text )
    return texts


# =================================================
#   Helpful utils
# =================================================

def get_filenames(root, prefix='', suffix=''):
    """Function for listing filenames with given prefix and suffix in the root directory.
    
    Parameters
    ----------
    
    prefix: str
        The prefix of the required files.
    suffix: str
        The suffix of the required files
        
    Returns
    -------
    list of str
        List of filenames matching the prefix and suffix criteria.
    """
    return [fnm for fnm in os.listdir(root) if fnm.startswith(prefix) and fnm.endswith(suffix)]


def unpack_zipped_xml_files_iterator( path, encoding='utf-8', test_only=True ):
    """Unpacks given Koondkorpus .zip or .tar.gz archive, and yields XML TEI 
       files of the corpus. 
       Files that do not contain textual content (e.g. header XML files) will
       not be yielded.
    
    Parameters
    ----------
    path: str
        The path of the .zip or .tar.gz file;
    encoding: str
        Encoding to be used for decoding the content of the XML file. 
        Defaults to 'utf-8'.
    test_only: boolean
        If True, then only file names (strings) from the archive are returned.
        Otherwise, pairs (file path, decoded file content) will be returned.
        (default: False)
    Yields
    -------
        if test_only == True:
           path to XML TEI file : str
        else:
           a tuple : (path to XML TEI file : str, content of XML TEI file : str)
           
    """
    if path.endswith('.zip'):
        with ZipFile( path, mode='r' ) as opened_zip:
            for fnm_path in opened_zip.namelist():
                fnm_head, fnm_tail = os.path.split(fnm_path)
                if 'bin' in fnm_head:
                    # Skip files inside the 'bin' folder
                    continue
                if fnm_path.endswith('.xml'):
                    if test_only:
                       yield fnm_path
                    else:
                       with opened_zip.open(fnm_path, mode='r') as f:
                            content = f.read()
                       content = content.decode(encoding)
                       yield (fnm_path, content)
    elif path.endswith('.tar.gz'):
        opened_tar = tarfile.open(path, "r:gz")
        for tarinfo in opened_tar:
            if not tarinfo.isreg():
               # Skip directories
               continue
            fnm_head, fnm_tail = os.path.split(tarinfo.name)
            if 'bin' in fnm_head:
               # Skip files inside the 'bin' folder
               continue
            if tarinfo.name.endswith('.xml'):
               if test_only:
                  yield tarinfo.name
               else:
                  with opened_tar.extractfile(tarinfo) as f:
                       content = f.read()
                  content = content.decode(encoding)
                  yield (tarinfo.name, content)
        opened_tar.close()
    else:
        raise Exception('(!) Unexpected input file format: ',path)


def get_subdiv(div):
    n = div[3:]
    return 'div' + str(int(n) + 1)
