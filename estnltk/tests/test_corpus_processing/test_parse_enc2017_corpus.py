import os, os.path
import tempfile

from estnltk import Text
from estnltk.core import PACKAGE_PATH

from estnltk.layer import AmbiguousAttributeList, AttributeList

from estnltk.corpus_processing.parse_enc2017 import parse_enc2017_file_content_iterator
from estnltk.corpus_processing.parse_enc2017 import parse_enc2017_file_iterator

from estnltk.layer_operations import split_by

inputfile_1 = 'test_enc2017_excerpt_1.prevert'
inputfile_2 = 'test_enc2017_excerpt_2.prevert'

# ===========================================================
#    Loading etTenTen corpus files
# ===========================================================

def test_parse_enc2017_file_iterator_w_original_tokenization_1():
    # Parse Texts from the ENC 2017 document (web17 subcorpus)
    texts = []
    inputfile_path = \
        os.path.join(PACKAGE_PATH, 'tests', 'test_corpus_processing', inputfile_1)
    for text_obj in parse_enc2017_file_iterator( inputfile_path, encoding='utf-8',\
                                                 tokenization='preserve'):
        texts.append( text_obj )
    # Make assertions
    assert len(texts) == 2
    # Document 1
    doc1 = texts[0]
    assert 'src' in doc1.meta and \
           doc1.meta['src'] == 'web17'
    assert 'id' in doc1.meta and \
           doc1.meta['id'] == '1071214'
    assert 'crawl_date' in doc1.meta and \
           doc1.meta['crawl_date'] == '2017-09-27 03:34'
    assert 'url' in doc1.meta and \
           doc1.meta['url'] == "http://teadus.usk.ee/kas-suurt-pauku-on-olnud"
    assert 'original_paragraphs' in doc1.layers 
    assert len( doc1.original_paragraphs ) == 1
    assert doc1.original_paragraphs[0].enclosing_text == '– Puuduv antiaine: Mõned suure paugu '+\
                                                         'teooriad eeldavad võrdselt aine ja '+\
                                                         'antiainete tekkimist. Sellegipoolest '+\
                                                         'leitakse ainult minimaalses koguses '+\
                                                         'antiaine-positrone ja antiprootoneid.'
    assert 'original_word_chunks' in doc1.layers
    assert doc1.original_word_chunks.text == ['–', 'Puuduv', 'antiaine:', 'Mõned', 'suure', 'paugu',\
          'teooriad', 'eeldavad', 'võrdselt', 'aine', 'ja', 'antiainete', 'tekkimist.', 'Sellegipoolest',\
          'leitakse', 'ainult', 'minimaalses', 'koguses', 'antiaine-positrone', 'ja', 'antiprootoneid.']
    
    # Document 2
    doc2 = texts[1]
    assert 'url' in doc2.meta and \
           doc2.meta['url'] == "http://evm.ee/est/meist/uudised?article_filters%5Btag%5D=%C3%BClest%C3%B5usmisp%C3%BChad"
    assert len(doc2.layers) == 6
    assert 'original_paragraphs' in doc2.layers 
    assert len( doc2.original_paragraphs ) == 3
    assert str( doc2.original_paragraphs.heading ) == "['yes', None, None]"
    assert str( doc2.original_paragraphs.langdiff ) == "['0.92', '0.58', '0.93']"



def test_parse_enc2017_file_iterator_w_original_tokenization_2():
    # Parse Texts from the ENC 2017 document (NC subcorpus)
    texts = []
    inputfile_path = \
        os.path.join(PACKAGE_PATH, 'tests', 'test_corpus_processing', inputfile_2)
    for text_obj in parse_enc2017_file_iterator( inputfile_path, encoding='utf-8',\
                                                 tokenization='preserve'):
        texts.append( text_obj )
    # Make assertions
    assert len(texts) == 2
    # Document 1
    doc1 = texts[0]
    assert 'src' in doc1.meta and \
           doc1.meta['src'] == 'NC'
    assert 'id' in doc1.meta and \
           doc1.meta['id'] == '10633'
    assert 'subdoc_id' in doc1.meta and \
           doc1.meta['subdoc_id'] == '650307'
    assert 'texttype' in doc1.meta and \
           doc1.meta['texttype'] == "periodicals"
    assert 'newspaperNumber' in doc1.meta and \
           doc1.meta['newspaperNumber'] == "Eesti Päevaleht 09.12.2004"
    assert 'original_sentences' in doc1.layers 
    assert len( doc1.original_sentences ) == 3
    assert doc1.original_sentences[1].enclosing_text == 'Selliste ümardamisreeglite järgimine jätab '+\
                                                        'inimestele üle 130 miljoni krooni rohkem '+\
                                                        'raha kätte.'
    
    doc2 = texts[1]
    assert 'src' in doc2.meta and \
           doc2.meta['src'] == 'NC'
    assert 'id' in doc2.meta and \
           doc2.meta['id'] == '10633'
    assert 'subdoc_id' in doc2.meta and \
           doc2.meta['subdoc_id'] == '650309'
    assert 'original_word_chunks' in doc2.layers 
    assert doc2.original_word_chunks[:11].text == \
           ['TALLINN,', '9.', 'detsember', '(EPLO)', '-', 'Neste', 'langetas', \
            'kell', '15.00', 'bensiinide', 'hindu']
    assert len( doc2.original_word_chunks ) == 41
    assert 'original_words' in doc2.layers 
    assert len( doc2.original_words ) == 48
    