# Module for converting Koondkorpus XML TEI files to EstNLTK Text objects.
# Ported from the version 1.4.1.1:
#    https://github.com/estnltk/estnltk/blob/1.4.1.1/estnltk/teicorpus.py
#    ( with slight modifications )
# 
# The corpus (see http://www.cl.ut.ee/korpused/segakorpus/index.php?lang=et) contains 
# a variety of documents from different domains and can be used freely for non-commercial 
# purposes. EstNLTK is capable of reading XML formatted files of the corpus and parse the 
# documents, paragraphs, sentences and words with some additional metadata found in XML 
# files.
#
# The implementation is currently quite simplistic, though. But it should be sufficient for 
# simpler use cases. The resulting documents have paragraphs separated by two newlines and 
# sentences by single newline. The original plain text is not known for XML TEI files.
# Note that all punctuation has been separated from words in the TEI files. 
# 

from estnltk.text import Text
from estnltk.taggers import SentenceTokenizer

from bs4 import BeautifulSoup
from copy import deepcopy

import os


def get_div_target(fnm):
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
    if 'foorum' in fnm:
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


def parse_tei_corpora(root, prefix='', suffix='.xml', target=['artikkel'], \
                      encoding=None, preserve_tokenization=False):
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
        Encoding to be used for decoding the content of the XML file. If not specified (default), 
        then no separate decoding step is applied.
    preserve_tokenization: boolean
        If True, then the created documents will have layers 'words', 'sentences', 'paragraphs', 
        which follow the original segmentation in the XML file. 
        (In the XML, sentences are between <s> and </s> and paragraphs are between <p> and </p>);
        Otherwise, the documents are created without adding layers 'words', 'sentences', 'paragraphs';
        (default: False)

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
                                preserve_tokenization=preserve_tokenization)
        for doc in docs:
            doc['file'] = fnm
        documents.extend(docs)
    return documents


def parse_tei_corpus(path, target=['artikkel'], encoding=None, preserve_tokenization=False):
    """Parse documents from a TEI style XML file. Return a list of Text objects.
    
    Parameters
    ----------
    path: str
        The path of the XML file.
    target: list of str
        List of <div> types, that are considered documents in the XML files (default: ["artikkel"]).
    encoding: str
        Encoding to be used for decoding the content of the XML file. If not specified (default), 
        then no separate decoding step is applied.
    preserve_tokenization: boolean
        If True, then the created documents will have layers 'words', 'sentences', 'paragraphs', 
        which follow the original segmentation in the XML file. 
        (In the XML, sentences are between <s> and </s> and paragraphs are between <p> and </p>);
        Otherwise, the documents are created without adding layers 'words', 'sentences', 'paragraphs';
        (default: False)
    Returns
    -------
    list of esnltk.text.Text
    """
    with open(path, 'rb') as f:
        html_doc = f.read()
    if encoding:
        html_doc = html_doc.decode( encoding )
    soup = BeautifulSoup(html_doc, 'html5lib')
    title = soup.find_all('title')[0].string
    
    documents = []
    for div1 in soup.find_all('div1'):
        documents.extend(parse_div(div1, dict(), target))
    # By default, no tokenization will be added
    add_tokenization        = False
    preserve_tokenization_x = False
    if preserve_tokenization:
        # If required, preserve the original tokenization
        add_tokenization      = True
        preserve_tokenization_x = True
    return create_estnltk_texts(documents, \
                                add_tokenization=add_tokenization, \
                                preserve_tokenization=preserve_tokenization_x )


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
            'title': div_title,
            'paragraphs': parse_paragraphs(soup)
        }
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


def create_estnltk_texts( docs, 
                          add_tokenization=False,
                          preserve_tokenization=False):
    """Convert the imported documents to Text instances.

    Parameters
    ----------
    docs: list of (dict of dict)
        Documents parsed from an XML file that need to be converted
        to EstNLTK's Text objects;

    add_tokenization: boolean
        If True, then tokenization layers 'words', 'sentences', 'paragraphs'
        will be added to all newly created Text instances;
        (Default: False)
        
    preserve_tokenization: boolean
        If True, then the original segmentation from the XML file (sentences 
        between <s> and </s>, and paragraphs between <p> and </p>) is also 
        preserved in the newly created Text instances;
        Note: this only has effect if add_tokenization has been switched on;
        (Default: False)
        
    Returns
    -------
    list of (list of str)
        List of paragraphs given as list of sentences.
    """
    texts = []
    for doc in docs:
        text_str = '\n\n'.join(['\n'.join(para['sentences']) for para in doc['paragraphs']])
        text = Text( text_str )
        # 1) Add metadata
        for key in doc.keys():
           if key not in ['paragraphs', 'sentences']:
                text.meta[key] = doc[key]
        # 2) Add tokenization (if required)
        if add_tokenization:
           if preserve_tokenization:
                text.tag_layer(['words'])
                # Create a sentence tokenizer that only splits sentences in places of new lines
                from nltk.tokenize.simple import LineTokenizer
                newline_sentence_tokenizer = \
                   SentenceTokenizer( base_sentence_tokenizer=LineTokenizer() )
                newline_sentence_tokenizer.tag(text)
                text.tag_layer(['paragraphs'])
           else:
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


def get_subdiv(div):
    n = div[3:]
    return 'div' + str(int(n) + 1)
