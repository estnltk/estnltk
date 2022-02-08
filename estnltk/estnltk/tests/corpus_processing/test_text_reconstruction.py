from estnltk import Text

from estnltk_core.layer import AmbiguousAttributeList, AttributeList

from estnltk.corpus_processing.parse_koondkorpus import reconstruct_text

from estnltk.taggers.standard.text_segmentation.whitespace_tokens_tagger import WhiteSpaceTokensTagger
from estnltk_core.layer_operations import split_by

# ===========================================================
#    Koondkorpus processing:
#         reconstruction of Texts
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
        text.add_layer(layer)
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
        text.add_layer(layer)
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
        text.add_layer(layer)
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

    
    