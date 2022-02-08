import os, os.path

from estnltk.common import PACKAGE_PATH

from estnltk.corpus_processing.parse_enc import VertXMLFileParser
from estnltk.corpus_processing.parse_enc import ENCTextReconstructor

from estnltk.corpus_processing.parse_enc import parse_enc_file_iterator

from estnltk_core.converters import layer_to_records
from estnltk_core.layer_operations import split_by

inputfile_1 = 'test_enc2017_excerpt_1.vert'
inputfile_2 = 'test_enc2017_excerpt_2.vert'
inputfile_3 = 'test_enc2017_excerpt_3.vert'

# ===========================================================
#    Loading ENC 2017 corpus files
# ===========================================================

def test_parse_enc2017_file_iterator_w_original_tokenization_1():
    # Parse Texts from the ENC 2017 file (web17 subcorpus)
    texts = []
    inputfile_path = \
        os.path.join(PACKAGE_PATH, 'tests', 'corpus_processing', inputfile_1)
    for text_obj in parse_enc_file_iterator( inputfile_path, encoding='utf-8',\
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
    assert doc1.original_word_chunks.text == ['antiaine:', 'tekkimist.', 'antiprootoneid.']
    
    # Document 2
    doc2 = texts[1]
    assert 'url' in doc2.meta and \
           doc2.meta['url'] == "http://evm.ee/est/meist/uudised?article_filters%5Btag%5D=%C3%BClest%C3%B5usmisp%C3%BChad"
    assert len(doc2.layers) == 6
    assert 'original_paragraphs' in doc2.layers 
    assert 'original_word_chunks' in doc2.layers 
    assert doc2.original_word_chunks.text == ['pühapäeval,', 'kevadlaadale,', 'ülestõusmispühi.',\
                                              'pühadekommetest,', 'toidukraami.', 'kontserdid.']
    assert len( doc2.original_paragraphs ) == 3
    assert str( doc2.original_paragraphs.heading ) == "['yes', None, None]"
    assert str( doc2.original_paragraphs.langdiff ) == "['0.92', '0.58', '0.93']"



def test_parse_enc2017_file_iterator_w_original_tokenization_2():
    # Parse Texts from the ENC 2017 file (NC subcorpus)
    texts = []
    inputfile_path = \
        os.path.join(PACKAGE_PATH, 'tests', 'corpus_processing', inputfile_2)
    for text_obj in parse_enc_file_iterator( inputfile_path, encoding='utf-8',\
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
    assert doc2.original_word_chunks.text == \
           ['TALLINN,', '(EPLO)', 'kohta,', 'kütuseturul.', '11,80,', 'Online.']
    assert 'original_words' in doc2.layers 
    assert len( doc2.original_words ) == 48



def test_parse_enc2017_file_iterator_extract_specific_docs():
    # Parse only specific Texts from the ENC 2017 file
    # 1) Extract documents with specific id-s
    focus_doc_ids=set()
    focus_doc_ids.add('1071215')
    focus_doc_ids.add('12446')
    texts = []
    for inputfile in [ inputfile_1, inputfile_2, inputfile_3 ]:
        inputfile_path = \
            os.path.join(PACKAGE_PATH, 'tests', 'corpus_processing', inputfile)
        for text_obj in parse_enc_file_iterator( inputfile_path, encoding='utf-8',\
                                                     focus_doc_ids=focus_doc_ids ):
            texts.append( text_obj )
    # Make assertions
    assert len(focus_doc_ids) == len(texts)
    doc1 = texts[0]
    assert doc1.meta['id'] == '1071215'
    assert len(doc1.original_words) == 46
    assert len(doc1.original_sentences) == 5
    doc2 = texts[1]
    assert doc2.meta['id'] == '12446'
    assert len(doc2.original_words) == 17
    assert len(doc2.original_sentences) == 2

    
    # 2) Extract documents with specific src-s
    focus_srcs=set()
    focus_srcs.add('web17')
    texts = []
    for inputfile in [ inputfile_1, inputfile_2, inputfile_3 ]:
        inputfile_path = \
            os.path.join(PACKAGE_PATH, 'tests', 'corpus_processing', inputfile)
        for text_obj in parse_enc_file_iterator( inputfile_path, encoding='utf-8',\
                                                     focus_srcs=focus_srcs ):
            texts.append( text_obj )
    # Make assertions
    assert len(texts) == 3
    doc1 = texts[0]
    assert doc1.meta['id'] == '1071214'
    assert len(doc1.original_words) == 24 
    assert len(doc1.original_sentences) == 2
    doc2 = texts[2]
    assert doc2.meta['id'] == '2990189'
    assert len(doc2.original_words) == 31
    assert len(doc2.original_sentences) == 3



def test_parse_enc2017_file_iterator_with_empty_docs():
    # Parse Texts from the ENC 2017 file, and do not fail on empty documents

    # 1) Discard empty fragments, including empty documents (default option)
    texts = []
    inputfile_path = \
        os.path.join(PACKAGE_PATH, 'tests', 'corpus_processing', inputfile_3)
    for text_obj in parse_enc_file_iterator( inputfile_path, encoding='utf-8',\
                                                 tokenization='preserve'):
        texts.append( text_obj )
    # One document should be missing
    assert len(texts) == 3
    # 2) Allow empty documents, and create empty Text objects
    original_word_layers  = ['original_words', 'original_tokens', 'original_compound_tokens']
    original_upper_layers = ['original_sentences', 'original_paragraphs']
    texts = []
    inputfile_path = \
        os.path.join(PACKAGE_PATH, 'tests', 'corpus_processing', inputfile_3)
    # Create VertXMLFileParser that does not discard empty fragments
    reconstructor = ENCTextReconstructor(layer_name_prefix='original_')
    vertParser = VertXMLFileParser(discard_empty_fragments=False,\
                                   textReconstructor=reconstructor)
    for text_obj in parse_enc_file_iterator( inputfile_path, encoding='utf-8',\
                                                 tokenization='preserve',
                                                 vertParser=vertParser):
        # Assert that:
        if text_obj.text is None or len(text_obj.text) == 0:
            # 1) an empty document has no layers
            for layer in original_word_layers:
                assert layer not in text_obj.layers
            for layer in original_upper_layers:
                assert layer not in text_obj.layers
        else:
            # 2) a document with content has:
            #    2.1) all word layers
            for layer in original_word_layers:
                assert layer in text_obj.layers
            #    2.2) either layers paragraphs/sentences or 
            #         only sentences (depending on available)
            #         annotations
            assert any([l in text_obj.layers for l in original_upper_layers])
        texts.append( text_obj )
    # There should be one additional document (the empty one)
    assert len(texts) == 4



def test_parse_enc2017_with_original_tokens_use_split_by():
    # Parse Texts from the ENC 2017 file, preserve original segmentation, 
    # and apply split_by on extracted Text objects
    # 1) Collect texts
    texts = []
    inputfile_path = \
            os.path.join(PACKAGE_PATH, 'tests', 'corpus_processing', inputfile_1)
    for text_obj in parse_enc_file_iterator( inputfile_path, encoding='utf-8',\
                                                 tokenization='preserve',\
                                                 restore_morph_analysis=True ):
        texts.append( text_obj )
    assert len(texts) == 2
    # 2) Test splitting texts and make assertions
    for doc in texts:
        # Split by paragraphs
        paragraph_count = 0
        for paragraph in split_by(doc, layer='original_paragraphs', 
                                        layers_to_keep=['original_sentences', 
                                                        'original_tokens', 
                                                        'original_compound_tokens', 
                                                        'original_words', 
                                                        'original_morph_analysis', 
                                                        'original_word_chunks']):
            paragraph_count += 1
        assert paragraph_count == len(doc.original_paragraphs)
        # Split by sentences
        sent_count = 0
        for sentence in split_by(doc, layer='original_sentences', 
                                        layers_to_keep=['original_tokens', 'original_compound_tokens', 
                                                        'original_morph_analysis', 'original_words', 
                                                        'original_word_chunks']):
            sent_count += 1
        assert sent_count == len(doc.original_sentences)
        # Split by word chunks
        wchk_count = 0
        for word_chunk in split_by(doc, layer='original_word_chunks', 
                                        layers_to_keep=['original_tokens', 'original_compound_tokens', 
                                                        'original_morph_analysis', 'original_words']):
            assert len(word_chunk['original_tokens']) > 0
            assert len(word_chunk['original_words']) > 0
            assert len(word_chunk['original_morph_analysis']) > 0
            wchk_count += 1
        assert wchk_count == len(doc.original_word_chunks)



def test_parse_enc2017_with_original_tokens_and_restore_morph_analysis():
    # Parse Texts from the ENC 2017 file, preserve original segmentation, 
    # and restore original morph analysis (from the XML file)
    # 1) Configure restoring morph analysis "manually":
    #    Create TextReconstructor that preserves original tokenization,
    #    and restores original morph analysis; 
    #    Create also VertXMLFileParser with matching configuration;
    reconstructor = ENCTextReconstructor(restore_morph_analysis=True,\
                                             tokenization='preserve',\
                                             layer_name_prefix='original_')
    parser = VertXMLFileParser(textReconstructor=reconstructor, \
                               record_morph_analysis=True)
    # Collect morph analysed texts from all input files
    texts = []
    for inputfile in [ inputfile_1, inputfile_2, inputfile_3 ]:
        inputfile_path = \
            os.path.join(PACKAGE_PATH, 'tests', 'corpus_processing', inputfile)
        for text_obj in parse_enc_file_iterator( inputfile_path, encoding='utf-8',\
                                                     textReconstructor=reconstructor,\
                                                     vertParser=parser):
            # Assert that required layers exist
            assert 'original_sentences' in text_obj.layers
            assert 'original_words' in text_obj.layers
            assert 'original_morph_analysis' in text_obj.layers
            # and there is a morph analysis for each word
            assert len(text_obj["original_morph_analysis"]) == len(text_obj['original_words'])
            texts.append( text_obj )
    # Assert / Check some details
    doc1 = texts[1]
    assert layer_to_records( doc1.original_morph_analysis, with_text=True )[0:6] == \
           [[{'text': 'Uudised', 'end': 7, 'form': 'pl n', 'start': 0, 'ending': 'd', 'partofspeech': 'S', 'root': 'uudis', 'root_tokens': ('uudis',), 'lemma': 'uudis', 'clitic': ''}], \
            [{'text': 'Sel', 'end': 12, 'form': 'sg ad', 'start': 9, 'ending': 'l', 'partofspeech': 'P', 'root': 'see', 'root_tokens': ('see',), 'lemma': 'see', 'clitic': ''}], 
            [{'text': 'pühapäeval', 'end': 23, 'form': 'sg ad', 'start': 13, 'ending': 'l', 'partofspeech': 'S', 'root': 'püha_päev', 'root_tokens': ('püha', 'päev'), 'lemma': 'pühapäev', 'clitic': ''}], \
            [{'text': ',', 'end': 24, 'form': '', 'start': 23, 'ending': '', 'partofspeech': 'Z', 'root': ',', 'root_tokens': (',',), 'lemma': ',', 'clitic': ''}], \
            [{'text': '1.', 'end': 27, 'form': '?', 'start': 25, 'ending': '0', 'partofspeech': 'O', 'root': '1.', 'root_tokens': ('1.',), 'lemma': '1.', 'clitic': ''}], \
            [{'text': 'mail', 'ending': 'il', 'root_tokens': ('maa',), 'form': 'pl ad', 'partofspeech': 'S', 'root': 'maa', 'start': 28, 'end': 32, 'clitic': '', 'lemma': 'maa'}] ]
    doc2 = texts[3]
    assert layer_to_records( doc2.original_morph_analysis, with_text=True )[0:7] == \
           [[{'text': 'TALLINN', 'root_tokens': ('Tallinn',), 'start': 0, 'ending': '0', 'partofspeech': 'H', 'form': 'sg n', 'root': 'Tallinn', 'lemma': 'Tallinn', 'clitic': '', 'end': 7}], \
            [{'text': ',', 'root_tokens': (',',), 'start': 7, 'ending': '', 'partofspeech': 'Z', 'form': '', 'root': ',', 'lemma': ',', 'clitic': '', 'end': 8}], \
            [{'text': '9.', 'root_tokens': ('9.',), 'start': 9, 'ending': '0', 'partofspeech': 'O', 'form': '?', 'root': '9.', 'lemma': '9.', 'clitic': '', 'end': 11}], \
            [{'text': 'detsember', 'root_tokens': ('detsember',), 'start': 12, 'ending': '0', 'partofspeech': 'S', 'form': 'sg n', 'root': 'detsember', 'lemma': 'detsember', 'clitic': '', 'end': 21}], \
            [{'text': '(', 'root_tokens': ('(',), 'start': 22, 'ending': '', 'partofspeech': 'Z', 'form': '', 'root': '(', 'lemma': '(', 'clitic': '', 'end': 23}], \
            [{'text': 'EPLO', 'root_tokens': ('EPLO',), 'start': 23, 'ending': '0', 'partofspeech': 'Y', 'form': '?', 'root': 'EPLO', 'lemma': 'EPLO', 'clitic': '', 'end': 27}], \
            [{'text': ')', 'root_tokens': (')',), 'start': 27, 'ending': '', 'partofspeech': 'Z', 'form': '', 'root': ')', 'lemma': ')', 'clitic': '', 'end': 28}]]

    # 2) Configure restoring morph analysis via parse_enc_file_iterator's
    #    argument
    texts = []
    inputfile_path = \
            os.path.join(PACKAGE_PATH, 'tests', 'corpus_processing', inputfile_3)
    for text_obj in parse_enc_file_iterator( inputfile_path, encoding='utf-8',\
                                                 tokenization='preserve',\
                                                 restore_morph_analysis=True ):
        assert len(text_obj["original_morph_analysis"]) == len(text_obj['original_words'])
        texts.append( text_obj )
    # Assert / Check some details
    doc1 = texts[0]
    assert layer_to_records( doc1.original_morph_analysis, with_text=True )[0:4] == \
           [[{'text': 'Kuidas', 'root_tokens': ('kuidas',), 'lemma': 'kuidas', 'start': 0, 'form': '', 'end': 6, 'ending': '0', 'root': 'kuidas', 'clitic': '', 'partofspeech': 'D'}], \
            [{'text': 'õunu', 'root_tokens': ('õun',), 'lemma': 'õun', 'start': 7, 'form': 'pl p', 'end': 11, 'ending': 'u', 'root': 'õun', 'clitic': '', 'partofspeech': 'S'}], \
            [{'text': 'paremini', 'root_tokens': ('paremini',), 'lemma': 'paremini', 'start': 12, 'form': '', 'end': 20, 'ending': '0', 'root': 'paremini', 'clitic': '', 'partofspeech': 'D'}], \
            [{'text': 'säilitada', 'root_tokens': ('säilita',), 'lemma': 'säilitama', 'start': 21, 'form': 'da', 'end': 30, 'ending': 'da', 'root': 'säilita', 'clitic': '', 'partofspeech': 'V'}]]



def test_parse_enc2017_with_original_tokens_and_add_morph_analysis():
    # Parse Texts from the ENC 2017 file, preserve original
    # segmentation, and add estnltk's morph analysis
    
    # 1) Create TextReconstructor that preserves original tokenization,
    #     but does not add prefix 'original_' to layer names
    #   (so, layer names will be identical to estnltk's layer names)
    textReconstructor = ENCTextReconstructor(tokenization='preserve',\
                                                 layer_name_prefix='')
    texts = []
    for inputfile in [ inputfile_1, inputfile_2, inputfile_3 ]:
        inputfile_path = \
            os.path.join(PACKAGE_PATH, 'tests', 'corpus_processing', inputfile)
        for text_obj in parse_enc_file_iterator( inputfile_path, encoding='utf-8',\
                                                     textReconstructor=textReconstructor ):
            # Assert that required layers exist (and have correct names)
            assert 'sentences' in text_obj.layers
            assert 'words' in text_obj.layers
            assert 'compound_tokens' in text_obj.layers
            texts.append( text_obj )
    # 2) Tag morph analyses
    for text_obj in texts:
        text_obj.tag_layer(['morph_analysis'])
        # Make assertions
        assert 'morph_analysis' in text_obj.layers
        assert len(text_obj['morph_analysis']) == len(text_obj['words'])
    
    