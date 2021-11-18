import unittest

from estnltk import Text
from estnltk.taggers import TokensTagger, CompoundTokenTagger, WordTagger
from estnltk.taggers.standard.text_segmentation.whitespace_tokens_tagger import WhiteSpaceTokensTagger
from estnltk.taggers.standard.text_segmentation.pretokenized_text_compound_tokens_tagger import PretokenizedTextCompoundTokensTagger

from estnltk_core.layer import AttributeList

normalized_attr_nm = 'normalized_form'

class WordTaggerTest(unittest.TestCase):

    def test_compound_token_word_normalization(self):
        test_texts = [ 
            { 'text': 'Kel huvi http://www.youtube.com/watch?v=PFD2yIVn4IE\npets 11.07.2012 20:37 lugesin enne kommentaarid ära.', \
              'normalized_words': [ (2,'http://www.youtube.com/watch?v=PFD2yIVn4IE'), (4,'11.07.2012'), (5,'20:37') ] }, \
            { 'text': 'See on v-vä-väga huvitav, aga kas ka ka-su-lik?!', \
              'normalized_words': [ (2,'väga'), (8,'kasulik')] }, \
            { 'text': 'kõ-kõ-kõik v-v-v-ve-ve-ve-vere-taoline on nii m-a-a-a-l-u-n-e...',\
              'normalized_words': [(0, 'kõik'), (1, 'vere-taoline'), (4, 'maaalune')] }, \
            { 'text' : 'Aga nt . hädas oli juba Vana-Hiina suurim ajaloolane Sima Qian (II—I saj. e. m. a.).', \
              'normalized_words': [(1, 'nt.'), (14, 'saj.'), (15, 'e.m.a.')] }, \
            { 'text': "Vaatleme järgmisi arve: -21 134 567 000 123 , 456; 34 507 000 000; -57 000 000; 64 025,25; 1 000; 75 ja 0,45;", \
              'normalized_words': [(4, '-21134567000123,456'), (6, '34507000000'), (8, '-57000000'), (10, '64025,25'), (12, '1000'), (16, '0,45')] }, \
            { 'text' : "Enim langes Ekspress Grupp ( -7,62% ), talle järgnesid Tallink ( -7,35% ) ja Tallinna Kaubamaja ( -6,77% ).",\
              'normalized_words': [(5, '-7,62%'), (12, '-7,35%'), (18, '-6,77%')] }, \
            { 'text': "18 m/s = 64 , 8 km/h , 20 m/s = 72 km/h , 22 m/s = 79 , 2 km/h .", \
              'normalized_words': [(1, 'm/s'), (3, '64,8'), (4, 'km/h'), (7, 'm/s'), (10, 'km/h'), (13, 'm/s'), (15, '79,2'), (16, 'km/h')] }, \
            { 'text': "(arhitektid M. Port, M. Meelak, O. Zhemtshugov, R.-L. Kivi)", \
              'normalized_words': [(2, 'M. Port'), (4, 'M. Meelak'), (6, 'O. Zhemtshugov'), (8, 'R.-L. Kivi')] }, \
            { 'text': "SKT -st või LinkedIn -ist ma eriti ei hoolinud, külastasin hoopis koos James Jr.-iga workshop ' e.", \
              'normalized_words': [(0, 'SKT-st'), (2, 'LinkedIn-ist'), (12, 'Jr.-iga'), (13, "workshop'e")] }, \
        ]
        for test_text in test_texts:
            text = Text( test_text['text'] )
            # Perform analysis
            text.tag_layer(['words'])
            # Collect normalized words
            normalized = []
            for wid, word in enumerate( text.words ):
                if hasattr(word, normalized_attr_nm) and \
                   getattr(word, normalized_attr_nm) != None:
                    normalized_form = getattr(word, normalized_attr_nm)
                    if isinstance(normalized_form, AttributeList):
                        forms_list = [nf for nf in normalized_form if nf != None]
                        if len(forms_list) > 0:
                            normalized.append( (wid, forms_list[0] ) )
                    else:
                        # for backward compatibility:
                        normalized.append( (wid, getattr(word, normalized_attr_nm) ) )
            #print(normalized)
            # Check normalized words
            self.assertListEqual(test_text['normalized_words'], normalized)


    def test_restore_original_word_tokenization(self):
        # Tests that the original word tokenization of a pretokenized text can be 
        # restored using WhiteSpaceTokensTagger, PretokenizedTextCompoundTokensTagger
        # and WordTagger in combination
        tokens_tagger = WhiteSpaceTokensTagger()
        compound_tokens_tagger = PretokenizedTextCompoundTokensTagger()
        test_texts = [ 
            { 'text': 'Eurorebimises võidab kavalam\n'+
                      'Tallinna päevalehtede ühinemisuudise varju jäi möödunud nädalal massiteabes teenimatul hoopis kaalukam sündmus .\n'+
                      'Nimelt otsustas valitsus neljapäevasel kabinetiistungil , et Eesti esitab veel sel aastal ametliku avalduse Euroopa Liitu astumiseks .', \
              'expected_words': ['Eurorebimises', 'võidab', 'kavalam', 'Tallinna', 'päevalehtede', \
                                  'ühinemisuudise', 'varju', 'jäi', 'möödunud', 'nädalal', 'massiteabes',\
                                  'teenimatul', 'hoopis', 'kaalukam', 'sündmus', '.', 'Nimelt', 'otsustas',\
                                  'valitsus', 'neljapäevasel', 'kabinetiistungil', ',', 'et', 'Eesti', \
                                  'esitab', 'veel', 'sel', 'aastal', 'ametliku', 'avalduse', 'Euroopa', \
                                  'Liitu', 'astumiseks', '.'] }, \
            { 'text': 'See oli pool lehekülge umbes aasta vanusest Timesist - lehekülje ülemine pool , '+
                      'nii et sel oli ka kuupäev , - ja sinna oli trükitud ka mingi Partei ülesandega '+
                      'New Yorki saabunud delegatsiooni foto .', \
              'expected_words': ['See', 'oli', 'pool', 'lehekülge', 'umbes', 'aasta', 'vanusest', 'Timesist', \
                                 '-', 'lehekülje', 'ülemine', 'pool', ',', 'nii', 'et', 'sel', 'oli', 'ka', \
                                 'kuupäev', ',', '-', 'ja', 'sinna', 'oli', 'trükitud', 'ka', 'mingi', \
                                 'Partei', 'ülesandega', 'New Yorki', 'saabunud', 'delegatsiooni', 'foto', \
                                 '.' ],\
              'multiwords': [['New', 'Yorki']] }, \
        ]
        for test_text in test_texts:
            text = Text( test_text['text'] )
            # Perform analysis
            tokens_tagger.tag(text)
            if 'multiwords' in test_text:
                # Create new PretokenizedTextCompoundTokensTagger for 
                # analysing specific multiword units
                compound_tokens_tagger = PretokenizedTextCompoundTokensTagger( \
                    multiword_units = test_text['multiwords'])
            compound_tokens_tagger.tag(text)
            text.tag_layer(['words'])
            # Collect results 
            words = []
            normalized = []
            for wid, word in enumerate( text.words ):
                if hasattr(word, normalized_attr_nm) and \
                   getattr(word, normalized_attr_nm) != None:
                    # Take normalized word, if available
                    normalized_form = getattr(word, normalized_attr_nm)
                    if isinstance(normalized_form, AttributeList):
                        forms_list = [nf for nf in normalized_form if nf != None]
                        if len(forms_list) > 0:
                            normalized.append( (wid, forms_list[0] ) )
                        else:
                            # Take surface form of the word
                            words.append( word.text )
                    else:
                        # for backward compatibility:
                        normalized.append( (wid, getattr(word, normalized_attr_nm) ) )
                else:
                    # Take surface form of the word
                    words.append( word.text )
            # Check results
            #print( words )
            self.assertListEqual(test_text['expected_words'], words)


    def test_change_input_and_output_layers_of_wordtagger(self):
        # Tests that input and output layer names of wordtagger can be changed
        tokens_tagger = TokensTagger(output_layer='my_tokens')
        cp_tagger   = CompoundTokenTagger(output_layer='my_compounds', input_tokens_layer='my_tokens')
        word_tagger = WordTagger(output_layer='my_words', input_tokens_layer='my_tokens', 
                                 input_compound_tokens_layer='my_compounds')
        test_texts = [ 
            { 'text': 'Mis lil-li müüs Tiit 10e krooniga?', \
              'expected_words': ['Mis', 'lil-li', 'müüs', 'Tiit', '10e', 'krooniga', '?'] }, \
           
            { 'text': "SKT -st või LinkedIn -ist ma eriti ei hoolinudki, aga workshop ' e külastasin küll.", \
              'expected_words': ['SKT -st', 'või', 'LinkedIn -ist', 'ma', 'eriti', 'ei', 'hoolinudki', ',', 'aga', "workshop ' e", 'külastasin', 'küll', '.'] },\
        ]
        for test_text in test_texts:
            text = Text( test_text['text'] )
            # Perform analysis
            tokens_tagger.tag(text)
            cp_tagger.tag(text)
            word_tagger.tag(text)
            self.assertTrue( 'my_tokens' in text.layers)
            self.assertTrue( 'my_compounds' in text.layers)
            self.assertTrue( 'my_words' in text.layers)
            self.assertFalse( 'tokens' in text.layers)
            self.assertFalse( 'compound_tokens' in text.layers)
            self.assertFalse( 'words' in text.layers)
            words_layer = text['my_words']
            # Fetch result
            word_segmentation = [] 
            for wid, word in enumerate(words_layer):
                word_text = text.text[word.start:word.end]
                word_segmentation.append(word_text)
            #print(word_segmentation)
            # Assert that the tokenization is correct
            self.assertListEqual(test_text['expected_words'], word_segmentation)


    def test_create_pretokenized_text_words_from_detached_layers(self):
        # Tests that a detached 'words' layer can be created from 
        # detached 'compound_tokens' and 'tokens' layers
        # 1) Create text
        pretokenized_text = '''
        <s>
        Kas
        New York
        või
        Mauna Loa
        ?
        </s>
        <s>
        Mauna Loa
        </s>
        '''
        # collect raw words and multiwords
        raw_words = []
        multiword_expressions = []
        raw_tokens = pretokenized_text.split('\n')
        for raw_token in raw_tokens:
            raw_token = raw_token.strip()
            if len(raw_token) == 0:
                continue
            if raw_token not in ['<s>', '</s>']:  # Skip sentence boundary tags
                raw_words.append(raw_token)
                if ' ' in raw_token:
                    multiword_expressions.append(raw_token)
            elif raw_token == '</s>':
                raw_words[-1] += '\n'  # newline == sentence ending
        # convert multiwords to the form of lists of lists of strings
        multiword_expressions = [mw.split() for mw in multiword_expressions]
        # make text
        text = Text(' '.join(raw_words))
        # 2) Create taggers
        tokens_tagger = WhiteSpaceTokensTagger()
        compound_tokens_tagger = PretokenizedTextCompoundTokensTagger( multiword_units = multiword_expressions )
        words_tagger = WordTagger()
        # 3) Create detached layers
        tokens = tokens_tagger.make_layer(text, layers={})
        compound_tokens = compound_tokens_tagger.make_layer(text, layers={'tokens':tokens})
        words = words_tagger.make_layer( text, layers={'tokens':tokens, 'compound_tokens':compound_tokens})
        # Assertions
        self.assertListEqual( [w.text for w in words], ['Kas', 'New York', 'või', 'Mauna Loa', '?', 'Mauna Loa'])
        self.assertEqual(len(tokens), 9)
        self.assertEqual(len(words), 6)
        
