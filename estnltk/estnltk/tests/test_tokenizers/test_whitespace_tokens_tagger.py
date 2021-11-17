from estnltk.taggers.standard.text_segmentation.whitespace_tokens_tagger import WhiteSpaceTokensTagger
from estnltk import Text


def test_split_text_into_tokens_by_whitespaces():
    # Tests that the text can by split into tokens 
    # by whitespaces only
    tokenizer = WhiteSpaceTokensTagger()
    test_texts = [ 
        { 'text': 'Eurorebimises võidab kavalam\n'
                  'Tallinna päevalehtede ühinemisuudise varju jäi möödunud nädalal massiteabes teenimatul hoopis kaalukam sündmus .\n'
                  'Nimelt otsustas valitsus neljapäevasel kabinetiistungil , et Eesti esitab veel sel aastal ametliku avalduse Euroopa Liitu astumiseks .',
          'expected_tokens': ['Eurorebimises', 'võidab', 'kavalam', 'Tallinna', 'päevalehtede',
                              'ühinemisuudise', 'varju', 'jäi', 'möödunud', 'nädalal', 'massiteabes',
                              'teenimatul', 'hoopis', 'kaalukam', 'sündmus', '.', 'Nimelt', 'otsustas',
                              'valitsus', 'neljapäevasel', 'kabinetiistungil', ',', 'et', 'Eesti',
                              'esitab', 'veel', 'sel', 'aastal', 'ametliku', 'avalduse', 'Euroopa',
                              'Liitu', 'astumiseks', '.'] },
    ]
    for test_text in test_texts:
        text = Text( test_text['text'] )
        # Perform analysis
        tokenizer.tag(text)
        # Collect results 
        spans  = [(sp.start, sp.end) for sp in text['tokens']]
        tokens = [text.text[start:end] for (start, end) in spans]
        #print(tokens)
        # Check results
        assert test_text['expected_tokens'] == tokens
