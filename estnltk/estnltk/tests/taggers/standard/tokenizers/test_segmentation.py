def test_segmentation_taggers():
    T = '''Aadressilt bla@bla.ee tuli 10 000 kirja. Kirjad, st. spamm saabus 10 tunni jooksul.

A. H. Tammsaare 1935. aastal: 1,0 m / s = 3,67 km/h.'''
    #
    # Test: add layers directly using corresponding taggers
    #
    from estnltk import Text
    text = Text(T)

    from estnltk.taggers import TokensTagger
    tokens_tagger = TokensTagger()
    tokens_tagger.tag(text)
    assert text['tokens'].text == ['Aadressilt', 'bla', '@', 'bla', '.', 'ee',
                                   'tuli', '10', '000', 'kirja', '.', 'Kirjad',
                                   ',', 'st', '.', 'spamm', 'saabus', '10',
                                   'tunni', 'jooksul', '.', 'A', '.', 'H', '.',
                                   'Tammsaare', '1935', '.', 'aastal', ':', '1',
                                   ',', '0', 'm', '/', 's', '=', '3', ',', '67',
                                   'km', '/', 'h', '.']

    from estnltk.taggers import CompoundTokenTagger
    compound_token_tagger = CompoundTokenTagger()
    text.tag_layer(['tokens'])
    compound_token_tagger.tag(text)
    assert text['compound_tokens'].text == ['bla', '@', 'bla', '.', 'ee',
                                            '10', '000',
                                            'st', '.',
                                            'A', '.', 'H', '.', 'Tammsaare',
                                            '1935', '.',
                                            '1', ',', '0',
                                            'm', '/', 's',
                                            '3', ',', '67',
                                            'km', '/', 'h']

    from estnltk.taggers import WordTagger
    word_tagger = WordTagger()
    text.tag_layer(['compound_tokens'])
    word_tagger.tag(text)
    assert text['words'].text == ['Aadressilt', 'bla@bla.ee', 'tuli', '10 000', 
                                  'kirja', '.', 'Kirjad', ',', 'st.', 'spamm', 
                                  'saabus', '10', 'tunni', 'jooksul',
                                  '.', 'A. H. Tammsaare', '1935.', 'aastal', ':',
                                  '1,0', 'm / s', '=', '3,67', 'km/h', '.']


    from estnltk.taggers import SentenceTokenizer
    sentence_tokenizer = SentenceTokenizer()
    text.tag_layer(['words'])
    sentence_tokenizer.tag(text)
    assert text['sentences'].text == ['Aadressilt', 'bla@bla.ee', 'tuli', '10 000', 'kirja', '.',
                                      'Kirjad', ',', 'st.', 'spamm', 'saabus', '10', 'tunni', 'jooksul', '.',
                                      'A. H. Tammsaare', '1935.', 'aastal', ':', '1,0', 'm / s', '=', '3,67', 'km/h', '.']


    from estnltk.taggers import ParagraphTokenizer
    paragraph_tokenizer = ParagraphTokenizer()
    paragraph_tokenizer.tag(text) 
    assert text['paragraphs'].text == ['Aadressilt', 'bla@bla.ee', 'tuli', '10 000', 'kirja', '.',
                                       'Kirjad', ',', 'st.', 'spamm', 'saabus', '10', 'tunni', 'jooksul', '.',
                                       'A. H. Tammsaare', '1935.', 'aastal', ':', '1,0', 'm / s', '=', '3,67', 'km/h', '.']
    
    #
    # Test: tag_layer vs analyse
    #
    # (note: analyse is deprecated, 
    #        use tag_layer instead)
    #
    text1 = Text(T).tag_layer(['paragraphs'])
    text2 = Text(T).tag_layer(['paragraphs'])
    text2.pop_layer('tokens')
    # Validate that elements match
    assert text1['words'].text == text2['words'].text
    assert text1['sentences'].text == text2['sentences'].text
    assert text1['paragraphs'].text == text2['paragraphs'].text
    # Validate that auxiliary layers were removed if analyse was applied
    assert text1.layers == {'compound_tokens', 'tokens', 'words', 'sentences', 'paragraphs'}
    assert text2.layers == {'words', 'sentences', 'paragraphs'}
    
    #
    # Test: tag via tag_layer method
    #
    tx = '''Aadressilt bla@bla.ee tuli 10 000 kirja, st. spammi aadressile foo@foo.ee 10 tunni jooksul 2017. aastal. 
A. H. Tammsaare: 1,0 m / s = 3, 67 km/h.'''
    text = Text(tx).tag_layer(['words'])
    assert text['words'].text == ['Aadressilt', 'bla@bla.ee', 'tuli', '10 000', 
                                  'kirja', ',', 'st.', 'spammi', 'aadressile', 'foo@foo.ee', 
                                  '10', 'tunni', 'jooksul', '2017.', 'aastal', '.', 
                                  'A. H. Tammsaare', ':', '1,0', 'm / s', '=', '3', ',', '67', 'km/h', '.']

