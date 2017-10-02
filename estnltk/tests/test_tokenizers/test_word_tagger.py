import unittest

from estnltk import Text


class WordTaggerTest(unittest.TestCase):

    def test_compound_token_word_normalization(self):
        normalized_attr_nm = 'normalized_form'
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
                    normalized.append( (wid, getattr(word, normalized_attr_nm) ) )
            #print(normalized)
            # Check normalized words
            self.assertListEqual(test_text['normalized_words'], normalized)

