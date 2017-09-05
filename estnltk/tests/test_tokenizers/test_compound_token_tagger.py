import unittest

from estnltk import Text


class CompoundTokenTaggerTest(unittest.TestCase):

    def test_detect_hyphenation(self):
        test_texts = [ 
            { 'text': 'Mis lil-li müüs Tiit 10e krooniga?', \
              'expected_words': ['Mis', 'lil-li', 'müüs', 'Tiit', '10e', 'krooniga', '?'] }, \
            { 'text': 'See on vää-ää-ääga huvitav!', \
              'expected_words': ['See', 'on', 'vää-ää-ääga', 'huvitav', '!'] },\
        ]
        for test_text in test_texts:
            text = Text( test_text['text'] )
            # Perform analysis
            text.tag_layer(['words'])
            words_spans = text['words'].spans
            # Fetch results
            word_segmentation = [] 
            for wid, word in enumerate( words_spans ):
                word_text = text.text[word.start:word.end]
                word_segmentation.append(word_text)
            #print(word_segmentation)
            # Assert that the tokenization is correct
            self.assertListEqual(test_text['expected_words'], word_segmentation)

    def test_detect_abbreviations(self):
        test_texts = [ 
            { 'text': 'Õunade, s.o. õunapuu viljade saak tuleb tänavu kehvavõitu.', \
              'expected_words': ['Õunade', ',', 's.o.', 'õunapuu', 'viljade', 'saak', 'tuleb', 'tänavu', 'kehvavõitu', '.'] },\
            { 'text': 'Sellest olenemata võib rakenduseeskirjades muude toodete kohta , v.a eksportimiseks mõeldud lauaveinid ja mpv-kvaliteetveinid , näha ette täiendavaid piiranguid.', \
              'expected_words': ['Sellest', 'olenemata', 'võib', 'rakenduseeskirjades', 'muude', 'toodete', 'kohta', ',', 'v.a', 'eksportimiseks', 'mõeldud', 'lauaveinid', 'ja', 'mpv-kvaliteetveinid', ',', 'näha', 'ette', 'täiendavaid', 'piiranguid', '.'] }, \
            { 'text': 'Vähem ägedad on leppinud kompromissiga: Lao-zi elas küll VI sajandil e. m. a., ise ta aga midagi ei kirjutanud.' ,\
              'expected_words': ['Vähem', 'ägedad', 'on', 'leppinud', 'kompromissiga', ':', 'Lao-zi', 'elas', 'küll', 'VI', 'sajandil', 'e. m. a.', ',', 'ise', 'ta', 'aga', 'midagi', 'ei', 'kirjutanud', '.'] },\
            { 'text': 'Vormistada hiljemalt 19. augustiks k.a., et need siis üldkoosoleku alguses edastada.',\
              'expected_words': ['Vormistada', 'hiljemalt', '19.', 'augustiks', 'k.a.', ',', 'et', 'need', 'siis', 'üldkoosoleku', 'alguses', 'edastada', '.'] },\
            { 'text' : 'Mina pankade aktsiaid (v.a. Jaapan) veel praegu end ostmas investorina ei näe.', \
              'expected_words': ['Mina', 'pankade', 'aktsiaid', '(', 'v.a.', 'Jaapan', ')', 'veel', 'praegu', 'end', 'ostmas', 'investorina', 'ei', 'näe', '.'] }, \
            { 'text' : '(esimene kord mainitakse kirjanduses 1895.a., kuid laiem populaarsus saavutatakse XX saj. seitsmekümnendatel aastatel)', \
              'expected_words': ['(', 'esimene', 'kord', 'mainitakse', 'kirjanduses', '1895.', 'a.', ',', 'kuid', 'laiem', 'populaarsus', 'saavutatakse', 'XX', 'saj.', 'seitsmekümnendatel', 'aastatel', ')'] }, \
            { 'text' : 'Umbes 1. saj e.m.a toimus lahknemine, mille tulemusel tekkis kaks suunda: hinajaana ja mahaja.', \
              'expected_words': ['Umbes', '1.', 'saj', 'e.m.a', 'toimus', 'lahknemine', ',', 'mille', 'tulemusel', 'tekkis', 'kaks', 'suunda', ':', 'hinajaana', 'ja', 'mahaja', '.'] }, \
            { 'text' : 'Budism jõudis Sri Lankale ja Birmasse 2. saj e.m.a, kust juba levis edasi Kagu-Aasiasse.', \
              'expected_words': ['Budism', 'jõudis', 'Sri', 'Lankale', 'ja', 'Birmasse', '2.', 'saj', 'e.m.a', ',', 'kust', 'juba', 'levis', 'edasi', 'Kagu-Aasiasse', '.'] }, \
            { 'text' : 'Aga hädas oli juba Vana-Hiina suurim ajaloolane Sima Qian (II—I saj. e. m. a.).', \
              'expected_words': ['Aga', 'hädas', 'oli', 'juba', 'Vana-Hiina', 'suurim', 'ajaloolane', 'Sima', 'Qian', '(', 'II', '—', 'I', 'saj.', 'e. m. a.', ')', '.'] }, \
            { 'text' : 'Kurla kool liideti hiljem siiski (1936.a.)', \
              'expected_words': ['Kurla', 'kool', 'liideti', 'hiljem', 'siiski', '(', '1936.', 'a.', ')'] }, \
            { 'text' : '(tiirlemisperioodid suhtuvad kui väikesed täisarvud, nt 1:2, 1:3, 3:4 jne - toim.).', \
              'expected_words': ['(', 'tiirlemisperioodid', 'suhtuvad', 'kui', 'väikesed', 'täisarvud', ',', 'nt', '1', ':', '2, 1', ':', '3, 3', ':', '4', 'jne', '-', 'toim.', ')', '.'] }, \
            { 'text' : '2007 a.- 2010 a. koolitusteemade seas olid: maksud, töösuhted, efektiivsed kommunikatsioonitehnikad.', \
              'expected_words': ['2007', 'a.', '-', '2010', 'a.', 'koolitusteemade', 'seas', 'olid', ':', 'maksud', ',', 'töösuhted', ',', 'efektiivsed', 'kommunikatsioonitehnikad', '.'] }, \
            { 'text' : 'Viie Dynastia * perioodil ( 907-960 A.D )', \
              'expected_words': ['Viie', 'Dynastia', '*', 'perioodil', '(', '907-960', 'A.D', ')'] }, \
            { 'text' : 'Arstide Liit esitas oma palganõudmised ( vt. volikogu otsused ), mis EHL volikogu lubas läbi arutada.',\
              'expected_words': ['Arstide', 'Liit', 'esitas', 'oma', 'palganõudmised', '(', 'vt.', 'volikogu', 'otsused', ')', ',', 'mis', 'EHL', 'volikogu', 'lubas', 'läbi', 'arutada', '.'] }, \
            { 'text' : 'Ja selles suhtes võiks Lp. E-Kaitse olla nii soliidne E-kaitse keskkond.',\
              'expected_words': ['Ja', 'selles', 'suhtes', 'võiks', 'Lp.', 'E-Kaitse', 'olla', 'nii', 'soliidne', 'E-kaitse', 'keskkond', '.'] }, \
            { 'text' : 'Lp. hr. Mart Laar, Miks ma ei saa vadata meie riigi eelarved internetis.',\
              'expected_words': ['Lp.', 'hr.', 'Mart', 'Laar', ',', 'Miks', 'ma', 'ei', 'saa', 'vadata', 'meie', 'riigi', 'eelarved', 'internetis', '.'] },\
            { 'text' : 'Eesti Maanoorte esivõistlustel Viljandis 15. nov. 2008 tuli ta esimeseks.',\
              'expected_words': ['Eesti', 'Maanoorte', 'esivõistlustel', 'Viljandis', '15.', 'nov.', '2008', 'tuli', 'ta', 'esimeseks', '.'] },\
            { 'text' : 'Minu kutsu aga saab just 3 veeb. kolme kuuseks.',\
              'expected_words': ['Minu', 'kutsu', 'aga', 'saab', 'just', '3', 'veeb.', 'kolme', 'kuuseks', '.'] },\
            { 'text' : 'keha ei tööta = tõugates , sest olen liiga püsti asendis ( a la Teichmann )',\
              'expected_words': ['keha', 'ei', 'tööta', '=', 'tõugates', ',', 'sest', 'olen', 'liiga', 'püsti', 'asendis', '(', 'a la', 'Teichmann', ')'] },\
            { 'text' : "Täiesti valesti aru saanud Jordani-fenomenist, et a'la üks mees teeb mängu ära.",\
              'expected_words': ['Täiesti', 'valesti', 'aru', 'saanud', 'Jordani-fenomenist', ',', 'et', "a'la", 'üks', 'mees', 'teeb', 'mängu', 'ära', '.'] },\
        ]
        for test_text in test_texts:
            text = Text( test_text['text'] )
            # Perform analysis
            text.tag_layer(['words'])
            words_spans = text['words'].spans
            # Fetch results
            word_segmentation = [] 
            for wid, word in enumerate( words_spans ):
                word_text = text.text[word.start:word.end]
                word_segmentation.append(word_text)
            #print(word_segmentation)
            # Assert that the tokenization is correct
            self.assertListEqual(test_text['expected_words'], word_segmentation)
            
            
    def test_detect_numeric(self):
        test_texts = [ 
            { 'text': '"Õiguste" all tuleb mõista ainult põhiõigusi, mida II. peatükis nimetatakse lihtsalt õigusteks.', \
              'expected_words': ['"', 'Õiguste', '"', 'all', 'tuleb', 'mõista', 'ainult', 'põhiõigusi', ',', 'mida', 'II.', 'peatükis', 'nimetatakse', 'lihtsalt', 'õigusteks', '.'] },\
        ]
        for test_text in test_texts:
            text = Text( test_text['text'] )
            # Perform analysis
            text.tag_layer(['words'])
            words_spans = text['words'].spans
            # Fetch results
            word_segmentation = [] 
            for wid, word in enumerate( words_spans ):
                word_text = text.text[word.start:word.end]
                word_segmentation.append(word_text)
            #print(word_segmentation)
            # Assert that the tokenization is correct
            self.assertListEqual(test_text['expected_words'], word_segmentation)


    def test_detect_names_with_initials(self):
        test_texts = [ 
            { 'text': 'A.H. Tammsaare muuseum Vargamäel tutvustab 19. sajandi taluelu ja A.H. Tammsaare kultuuri- ja kirjanduspärandit.', \
              'expected_words': ['A.H. Tammsaare', 'muuseum', 'Vargamäel', 'tutvustab', '19.', 'sajandi', 'taluelu', 'ja', 'A.H. Tammsaare', 'kultuuri-', 'ja', 'kirjanduspärandit', '.'] },\
            { 'text': 'Karskusliidu saalis oli kõnekoosolek, mille liidu esimees H. B. Rahamägi avas vaimuliku lauluga. ',\
              'expected_words': ['Karskusliidu', 'saalis', 'oli', 'kõnekoosolek', ',', 'mille', 'liidu', 'esimees', 'H. B. Rahamägi', 'avas', 'vaimuliku', 'lauluga', '.'] },\
            { 'text': 'Vat nii moodi ütles USA President J.F.Kennedy mehe kohta kes läks armeega ja oma rahva kannatuste hinnaga sõtta.', \
              'expected_words': ['Vat', 'nii', 'moodi', 'ütles', 'USA', 'President', 'J.F.Kennedy', 'mehe', 'kohta', 'kes', 'läks', 'armeega', 'ja', 'oma', 'rahva', 'kannatuste', 'hinnaga', 'sõtta', '.'] },\
        ]
        for test_text in test_texts:
            text = Text( test_text['text'] )
            # Perform analysis
            text.tag_layer(['words'])
            words_spans = text['words'].spans
            # Fetch results
            word_segmentation = [] 
            for wid, word in enumerate( words_spans ):
                word_text = text.text[word.start:word.end]
                word_segmentation.append(word_text)
            #print(word_segmentation)
            # Assert that the tokenization is correct
            self.assertListEqual(test_text['expected_words'], word_segmentation)

