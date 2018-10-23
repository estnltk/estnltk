from estnltk import Text

from estnltk.layer import AmbiguousAttributeList

from estnltk.corpus_processing.parse_koondkorpus import reconstruct_text
from estnltk.corpus_processing.parse_ettenten import reconstruct_ettenten_text
from estnltk.corpus_processing.parse_ettenten import parse_ettenten_corpus_file_content_iterator

from estnltk.taggers.text_segmentation.whitespace_tokens_tagger import WhiteSpaceTokensTagger
from estnltk.layer_operations import split_by

# ===========================================================
#    Koondkorpus processing 
# ===========================================================


def test_reconstruct_text_detached_layers():
    # Tests that the text and its layers can be reconstructed based on a dictionary representation
    # Test the situation when reconstructed layers are detached from each other
    # ( this kind of reconstruction is used in importing texts from koondkorpus XML files )
    tokenizer = WhiteSpaceTokensTagger()
    # dict representation of the text
    test_text_dict = { 'paragraphs': [ {'sentences':['Millist hinda oleme nõus maksma enese täiustamise eest?']}, \
                                       {'sentences':['Inimestel on palju eetilisi muresid, mis seostuvad vaimset '+\
                                        'võimekust parandavate ravimite või seadmetega, kuid tõenäoliselt haihtuvad '+\
                                        'need hetkel, mil turule ilmub esimene selline läbimurdeline vahend, tõdeb '+\
                                        'Oxfordi Ülikooli filosoof Anders Sandberg intervjuus Arko Oleskile.']}, \
                                       {'sentences':['REKLAAM']},\
                                       {'sentences':['Kas olete näinud filmi «Kõrvalnähud» («Limitless»), kus peategelane '+\
                                        'hakkab kasutama ravimit, mis tema vaimseid võimeid tohutult parandab, kuid jääb '+\
                                        'sellest sõltuvusse...']},\
                                       {'sentences':['Oo, jaa.', 'Mulle meeldis see väga.']},\
                                       {'sentences':['Tõesti?']},\
                                     ] }
    # Reconstruct the text
    wstokenizer = WhiteSpaceTokensTagger()
    text, tokenization_layers = reconstruct_text(test_text_dict, \
                                                 tokens_tagger=wstokenizer, \
                                                 use_enveloping_layers=False )
    
    # Make assertions #1.1
    expected_text = 'Millist hinda oleme nõus maksma enese täiustamise eest?\n\n'+\
                    'Inimestel on palju eetilisi muresid, mis seostuvad vaimset võimekust parandavate ravimite või seadmetega, kuid tõenäoliselt haihtuvad need hetkel, mil turule ilmub esimene selline läbimurdeline vahend, tõdeb Oxfordi Ülikooli filosoof Anders Sandberg intervjuus Arko Oleskile.\n\n'+\
                    'REKLAAM\n\n'+\
                    'Kas olete näinud filmi «Kõrvalnähud» («Limitless»), kus peategelane hakkab kasutama ravimit, mis tema vaimseid võimeid tohutult parandab, kuid jääb sellest sõltuvusse...\n\n'+\
                    'Oo, jaa.\n'+'Mulle meeldis see väga.\n\n'+\
                    'Tõesti?'
    assert text.text == expected_text
    assert any([layer.name=='tokens' for layer in tokenization_layers])
    assert any([layer.name=='compound_tokens' for layer in tokenization_layers])
    assert any([layer.name=='words' for layer in tokenization_layers])
    assert any([layer.name=='sentences' for layer in tokenization_layers])
    assert any([layer.name=='paragraphs' for layer in tokenization_layers])
    
    # Attach layers
    for layer in tokenization_layers:
        text[layer.name] = layer
    tokens     = [layer for layer in tokenization_layers if layer.name=='tokens'][0]
    words      = [layer for layer in tokenization_layers if layer.name=='words'][0]
    sentences  = [layer for layer in tokenization_layers if layer.name=='sentences'][0]
    paragraphs = [layer for layer in tokenization_layers if layer.name=='paragraphs'][0]
    
    # Make assertions #1.2
    assert words.text == tokens.text
    
    # Make assertions #2
    expected_words = ['Millist', 'hinda', 'oleme', 'nõus', 'maksma', 'enese', 'täiustamise', 'eest?', \
                       'Inimestel', 'on', 'palju', 'eetilisi', 'muresid,', 'mis', 'seostuvad', 'vaimset', \
                       'võimekust', 'parandavate', 'ravimite', 'või', 'seadmetega,', 'kuid', 'tõenäoliselt', \
                       'haihtuvad', 'need', 'hetkel,', 'mil', 'turule', 'ilmub', 'esimene', 'selline', \
                       'läbimurdeline', 'vahend,', 'tõdeb', 'Oxfordi', 'Ülikooli', 'filosoof', 'Anders', \
                       'Sandberg', 'intervjuus', 'Arko', 'Oleskile.', 'REKLAAM', 'Kas', 'olete', 'näinud', \
                       'filmi', '«Kõrvalnähud»', '(«Limitless»),', 'kus', 'peategelane', 'hakkab', 'kasutama',\
                       'ravimit,', 'mis', 'tema', 'vaimseid', 'võimeid', 'tohutult', 'parandab,', 'kuid', 'jääb',\
                       'sellest', 'sõltuvusse...', 'Oo,', 'jaa.', 'Mulle', 'meeldis', 'see', 'väga.', 'Tõesti?']
    assert words.text == expected_words
    expected_sentences = ['Millist hinda oleme nõus maksma enese täiustamise eest?', \
                          'Inimestel on palju eetilisi muresid, mis seostuvad vaimset võimekust parandavate '+\
                          'ravimite või seadmetega, kuid tõenäoliselt haihtuvad need hetkel, mil turule ilmub '+\
                          'esimene selline läbimurdeline vahend, tõdeb Oxfordi Ülikooli filosoof Anders Sandberg '+\
                          'intervjuus Arko Oleskile.', 'REKLAAM', 'Kas olete näinud filmi «Kõrvalnähud» («Limitless»), '+\
                          'kus peategelane hakkab kasutama ravimit, mis tema vaimseid võimeid tohutult parandab, '+\
                          'kuid jääb sellest sõltuvusse...', 'Oo, jaa.', 'Mulle meeldis see väga.', 'Tõesti?']
    assert sentences.text == expected_sentences
    expected_paragraphs = ['Millist hinda oleme nõus maksma enese täiustamise eest?', \
                           'Inimestel on palju eetilisi muresid, mis seostuvad vaimset võimekust parandavate '+\
                          'ravimite või seadmetega, kuid tõenäoliselt haihtuvad need hetkel, mil turule ilmub '+\
                          'esimene selline läbimurdeline vahend, tõdeb Oxfordi Ülikooli filosoof Anders Sandberg '+\
                          'intervjuus Arko Oleskile.', 'REKLAAM', \
                          'Kas olete näinud filmi «Kõrvalnähud» («Limitless»), '+\
                          'kus peategelane hakkab kasutama ravimit, mis tema vaimseid võimeid tohutult parandab, '+\
                          'kuid jääb sellest sõltuvusse...', 'Oo, jaa.\nMulle meeldis see väga.', 'Tõesti?']
    assert paragraphs.text == expected_paragraphs



def test_reconstruct_text_enveloping_layers():
    # Tests that the text and its layers can be reconstructed based on a dictionary representation
    # Test the situation when reconstructed layers are connected via enveloping
    # ( this kind of reconstruction is used in importing texts from koondkorpus XML files )
    tokenizer = WhiteSpaceTokensTagger()
    # dict representation of the text
    test_text_dict = { 'paragraphs': [ {'sentences':['Millist hinda oleme nõus maksma enese täiustamise eest?']}, \
                                       {'sentences':['Inimestel on palju eetilisi muresid, mis seostuvad vaimset '+\
                                        'võimekust parandavate ravimite või seadmetega, kuid tõenäoliselt haihtuvad '+\
                                        'need hetkel, mil turule ilmub esimene selline läbimurdeline vahend, tõdeb '+\
                                        'Oxfordi Ülikooli filosoof Anders Sandberg intervjuus Arko Oleskile.']}, \
                                       {'sentences':['REKLAAM']},\
                                       {'sentences':['Kas olete näinud filmi «Kõrvalnähud» («Limitless»), kus peategelane '+\
                                        'hakkab kasutama ravimit, mis tema vaimseid võimeid tohutult parandab, kuid jääb '+\
                                        'sellest sõltuvusse...']},\
                                       {'sentences':['Oo, jaa.', 'Mulle meeldis see väga.']},\
                                       {'sentences':['Tõesti?']},\
                                     ] }
    # Reconstruct the text
    wstokenizer = WhiteSpaceTokensTagger()
    text, tokenization_layers = reconstruct_text(test_text_dict, \
                                                 tokens_tagger=wstokenizer, \
                                                 use_enveloping_layers=True )
    assert any([layer.name=='tokens' for layer in tokenization_layers])
    assert any([layer.name=='compound_tokens' for layer in tokenization_layers])
    assert any([layer.name=='words' for layer in tokenization_layers])
    assert any([layer.name=='sentences' for layer in tokenization_layers])
    assert any([layer.name=='paragraphs' for layer in tokenization_layers])
    
    # Attach layers
    for layer in tokenization_layers:
        text[layer.name] = layer
    tokens     = [layer for layer in tokenization_layers if layer.name=='tokens'][0]
    words      = [layer for layer in tokenization_layers if layer.name=='words'][0]
    sentences  = [layer for layer in tokenization_layers if layer.name=='sentences'][0]
    paragraphs = [layer for layer in tokenization_layers if layer.name=='paragraphs'][0]
    
    # Test that words == tokens (because information about compound tokens was not available)
    assert words.text == tokens.text
    
    # Test relations: paragraphs
    assert text.paragraphs[0].sentences.text == ['Millist', 'hinda', 'oleme', 'nõus', 'maksma', 'enese', 'täiustamise', 'eest?']
    assert text.paragraphs[4].sentences.text == ['Oo,', 'jaa.', 'Mulle', 'meeldis', 'see', 'väga.']

    # Test relations: sentences
    assert text.sentences[1].text == ['Inimestel', 'on', 'palju', 'eetilisi', 'muresid,', 'mis', 'seostuvad', 'vaimset', 'võimekust', 'parandavate', 'ravimite', 'või', 'seadmetega,', 'kuid', 'tõenäoliselt', 'haihtuvad', 'need', 'hetkel,', 'mil', 'turule', 'ilmub', 'esimene', 'selline', 'läbimurdeline', 'vahend,', 'tõdeb', 'Oxfordi', 'Ülikooli', 'filosoof', 'Anders', 'Sandberg', 'intervjuus', 'Arko', 'Oleskile.']
    assert text.sentences[2].text == ['REKLAAM']
    
    # Test relations: words
    assert text.sentences[3].words[4:6].text == ['«Kõrvalnähud»', '(«Limitless»),']
    assert text.sentences[5].words[0:3].text == ['Mulle', 'meeldis', 'see']
    assert text.words[29:33].text == ['esimene', 'selline', 'läbimurdeline', 'vahend,']



def test_reconstruct_text_enveloping_layers_on_empty_text():
    # Tests text reconstruction on an empty input text: the text reconstruction 
    # should not fail even if the input text is empty.
    tokenizer = WhiteSpaceTokensTagger()
    # dict representation of the text
    test_text_dict = {'rubriik': 'KUUM', '_xml_file': 'aja_ee_2001_41.tasak.xml', 'paragraphs': [], \
                      'type': 'artikkel', 'alaosa': 'A-OSA', 'alamrubriik': '', 'title': 'Ühendriikide paisumine', \
                      'ajalehenumber': 'Eesti Ekspress'}
    # Reconstruct the text
    wstokenizer = WhiteSpaceTokensTagger()
    text, tokenization_layers = reconstruct_text(test_text_dict, \
                                                 tokens_tagger=wstokenizer, \
                                                 use_enveloping_layers=True )
    assert any([layer.name=='tokens' for layer in tokenization_layers])
    assert any([layer.name=='compound_tokens' for layer in tokenization_layers])
    assert any([layer.name=='words' for layer in tokenization_layers])
    assert any([layer.name=='sentences' for layer in tokenization_layers])
    assert any([layer.name=='paragraphs' for layer in tokenization_layers])
    tokens     = [layer for layer in tokenization_layers if layer.name=='tokens'][0]
    words      = [layer for layer in tokenization_layers if layer.name=='words'][0]
    sentences  = [layer for layer in tokenization_layers if layer.name=='sentences'][0]
    paragraphs = [layer for layer in tokenization_layers if layer.name=='paragraphs'][0]
    assert len(tokens) == 0
    assert len(words) == 0
    assert len(sentences) == 0
    assert len(paragraphs) == 0



def test_split_reconstructed_text():
    # Tests that the reconstructed text can be split by paragraphs and sentences
    tokenizer = WhiteSpaceTokensTagger()
    # dict representation of the text
    test_text_dict = { 'paragraphs': [ {'sentences':['Millist hinda oleme nõus maksma enese täiustamise eest?']}, \
                                       {'sentences':['REKLAAM', 'Tõesti?']},\
                                     ] }
    # Reconstruct the text
    wstokenizer = WhiteSpaceTokensTagger()
    text, tokenization_layers = reconstruct_text(test_text_dict, \
                                                 tokens_tagger=wstokenizer, \
                                                 use_enveloping_layers=True )
    # Attach layers
    for layer in tokenization_layers:
        text[layer.name] = layer
   # Split by paragraphs
    paragraph_count = 0
    for paragraph in split_by(text, layer='paragraphs', layers_to_keep=['tokens', 'compound_tokens', 'words', 'sentences']):
        paragraph_count += 1
    assert paragraph_count == 2
   # Split by sentences
    sent_count = 0
    for paragraph in split_by(text, layer='sentences', layers_to_keep=['tokens', 'compound_tokens', 'words']):
        sent_count += 1
    assert sent_count == 3


# ===========================================================
#    etTenTen processing 
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
    #print( doc1.layers )