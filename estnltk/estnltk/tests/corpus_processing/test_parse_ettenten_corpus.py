import os
import tempfile

from estnltk import Text

from estnltk_core.layer import AmbiguousAttributeList, AttributeList

from estnltk.corpus_processing.parse_ettenten import parse_ettenten_corpus_file_content_iterator
from estnltk.corpus_processing.parse_ettenten import extract_doc_ids_from_corpus_file

from estnltk_core.layer_operations import split_by

# ===========================================================
#    Loading etTenTen corpus files
# ===========================================================

def _get_test_ettenten_content():
    return '''
<corpus>
<doc id="686275" length="10k-100k" crawl_date="2013-01-24" url="http://rahvahaal.delfi.ee/news/uudised/?id=64951806&com=1&s=7&no=340" web_domain="rahvahaal.delfi.ee" langdiff="0.18">
<gap/>
<p heading="1">
AP
</p>
<p heading="0">
Täienduseks ehk, et ka kuningatel juhtub vahel apsakaid ja kuningas teab, mis siis teha. Meie kuningad pole vist jootrahast kuulnudki midagi.
</p>
<p heading="0">
Ja-jaa
</p>
</doc>
<doc id="686281" length="0-1k" crawl_date="2013-01-24" url="http://www.epl.ee/news/majandus/?id=51174495" web_domain="www.epl.ee" langdiff="0.44">
<gap/>
<p heading="1">
Tuvastamata Kasutaja
</p>
<p heading="0">
30.07.2009 21:14
</p>
<p heading="0">
....alles see oli, kui põlevkivi ja elektrifirmad tegid seakisa ja isegi peaminister rääkis võimalikust katastroofist Ida-Virus....
</p>
</doc>
</corpus>
'''


def test_parse_ettenten_corpus_file_content_iterator_wo_tokenization():
    # Parse Texts from the XML content
    texts = []
    for text_obj in parse_ettenten_corpus_file_content_iterator( _get_test_ettenten_content() ):
        texts.append( text_obj )
    # Make assertions
    assert len(texts) == 2
    # Document 1
    doc1 = texts[0]
    assert 'id' in doc1.meta and \
           doc1.meta['id'] == '686275'
    assert 'crawl_date' in doc1.meta and \
           doc1.meta['crawl_date'] == '2013-01-24'
    assert 'url' in doc1.meta and \
           doc1.meta['url'] == "http://rahvahaal.delfi.ee/news/uudised/?id=64951806&com=1&s=7&no=340"
    assert 'original_paragraphs' in doc1.layers 
    assert len( doc1.original_paragraphs ) == 3
    assert doc1.original_paragraphs[1].text == 'Täienduseks ehk, et ka kuningatel juhtub vahel apsakaid '+\
                                               'ja kuningas teab, mis siis teha. Meie kuningad pole vist '+\
                                               'jootrahast kuulnudki midagi.'
    # Document 2
    doc2 = texts[1]
    assert 'url' in doc2.meta and \
           doc2.meta['url'] == "http://www.epl.ee/news/majandus/?id=51174495"
    assert len(doc2.layers) == 1
    assert 'original_paragraphs' in doc2.layers 
    assert len( doc2.original_paragraphs ) == 3
    assert str( doc2.original_paragraphs.heading ) == "[['1'], ['0'], ['0']]"



def test_parse_ettenten_corpus_file_content_iterator_w_tokenization():
    # Parse Texts from the XML content
    texts = []
    for text_obj in parse_ettenten_corpus_file_content_iterator( _get_test_ettenten_content(), \
                                                                 add_tokenization=True ):
        texts.append( text_obj )
    # Make assertions
    assert len(texts) == 2
    doc1 = texts[0]
    doc2 = texts[1]
    # Check for the existence of layers
    expected_layers = ['tokens', 'compound_tokens', 'words', 'sentences', 'paragraphs']
    for expected_layer in expected_layers:
        assert expected_layer in doc1.layers
        assert expected_layer in doc2.layers
    # Check that heading attributes have been loaded:
    assert str( doc1.paragraphs.heading ) == "['1', '0', '0']"
    assert str( doc2.paragraphs.heading ) == "['1', '0', '0']"



def test_parse_ettenten_corpus_file_content_iterator_and_split_by():
    # 1) Add tokenization and split by paragraphs
    texts = []
    for text_obj in parse_ettenten_corpus_file_content_iterator( _get_test_ettenten_content(), \
                                                                 add_tokenization=True ):
        # Split by paragraphs
        for paragraph_obj in split_by(text_obj, layer='paragraphs', \
                                      layers_to_keep=['tokens', 'compound_tokens', 'words', 'sentences']):
            texts.append( paragraph_obj )
    # Make assertions
    assert len(texts) == 6
    
    # 2) Do not add tokenization, but split by original_paragraphs (from XML mark-up)
    texts = []
    for text_obj in parse_ettenten_corpus_file_content_iterator( _get_test_ettenten_content(), \
                                                                 add_tokenization=False ):
        # Split by original_paragraphs
        for paragraph_obj in split_by(text_obj, layer='original_paragraphs', layers_to_keep=[] ):
            texts.append( paragraph_obj )
    # Make assertions
    assert len(texts) == 6
    
    # 3) Add tokenization and split by sentences
    texts = []
    for text_obj in parse_ettenten_corpus_file_content_iterator( _get_test_ettenten_content(), \
                                                                 add_tokenization=True ):
        # Split by sentences
        for paragraph_obj in split_by(text_obj, layer='sentences', \
                                      layers_to_keep=['tokens', 'compound_tokens', 'words']):
            texts.append( paragraph_obj )
    # Make assertions
    assert len(texts) == 7



def test_parse_ettenten_corpus_file_content_iterator_and_extract_specific_file():
    # Tests that files with specific id-s can be extracted
    # Parse Texts from the XML content
    texts = []
    for text_obj in parse_ettenten_corpus_file_content_iterator( _get_test_ettenten_content(), \
                                                                 focus_doc_ids=set(['686281']), \
                                                                 add_tokenization=True ):
        texts.append( text_obj )
    # Make assertions
    assert len(texts) == 1
    doc1 = texts[0]
    # Check metadata
    assert 'id' in doc1.meta and doc1.meta['id'] == '686281'
    assert 'url' in doc1.meta and \
           doc1.meta['url'] == "http://www.epl.ee/news/majandus/?id=51174495"
    # Check for the existence of layers
    expected_layers = ['tokens', 'compound_tokens', 'words', 'sentences', 'paragraphs']
    for expected_layer in expected_layers:
        assert expected_layer in doc1.layers



def test_parse_ettenten_extract_doc_ids_from_corpus_file():
    # Tests that document ids can be extracted from the ettenten corpus file
    # 1) Create a temporary file storing the test corpus
    fp = tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.vert', delete=False)
    fp.write( _get_test_ettenten_content() )
    fp.write( '\n' )
    fp.close()
    
    # 2) Extract ids from the corpus file;
    doc_ids = extract_doc_ids_from_corpus_file( fp.name )
    # Clean-up: remove temporary file
    os.remove(fp.name)
    
    # 3) Make assertion
    assert doc_ids == ["686275", "686281"]

