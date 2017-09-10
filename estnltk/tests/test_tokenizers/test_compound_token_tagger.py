import unittest

from estnltk import Text


class CompoundTokenTaggerTest(unittest.TestCase):

    def test_detect_email(self):
        test_texts = [ 
            { 'text': 'See worm lihtsalt kirjutab alati saatjaks big@boss.com ...', \
              'expected_words': ['See', 'worm', 'lihtsalt', 'kirjutab', 'alati', 'saatjaks', 'big@boss.com', '...'] }, \
            { 'text': 'TELLIMISEKS- saada e-kiri aadressil ek.tellimus@eelk.ee - helista toimetusse 733 7795', \
              'expected_words': ['TELLIMISEKS-', 'saada', 'e-kiri', 'aadressil', 'ek.tellimus@eelk.ee', '-', 'helista', 'toimetusse', '733 7795'] }, \
            { 'text': 'Head Mosaicimist ja sellega harjumist soovib \n neti . kass @ postimees . ee', \
              'expected_words': ['Head', 'Mosaicimist', 'ja', 'sellega', 'harjumist', 'soovib', 'neti . kass @ postimees . ee'] }, \
            { 'text': 'sambamees . siim [ -at- ] siim . pri . ee says ... \n On jõudnud siiagi kuuldused , et rahvas on sassi kamminud', \
              'expected_words': ['sambamees . siim [ -at- ] siim . pri', '.', 'ee', 'says', '...', 'On', 'jõudnud', 'siiagi', 'kuuldused', ',', 'et', 'rahvas', 'on', 'sassi', 'kamminud'] }, \
            { 'text': 'Sellised veebileheküljed: www. esindus.ee/korteriturg, www. kavkazcenter.com, http: // www. cavalierklubben.com, http : //www.offa.org/ stats ning http://www.politsei.ee/dotAsset/225706 .', \
              'expected_words': ['Sellised', 'veebileheküljed', ':', 'www. esindus.ee/korteriturg', ',', 'www. kavkazcenter.com', ',', 'http: // www. cavalierklubben.com', ',', 'http : //www.offa.org/', 'stats', 'ning', 'http://www.politsei.ee/dotAsset/225706', '.'] }, \

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
              'expected_words': ['(', 'tiirlemisperioodid', 'suhtuvad', 'kui', 'väikesed', 'täisarvud', ',', 'nt', '1', ':', '2', ',', '1', ':', '3', ',', '3', ':', '4', 'jne', '-', 'toim.', ')', '.'] }, \
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
            # Detection of (long) number expressions
            { 'text': "Vaatleme järgmisi arve: -21 134 567 000 123 , 456; 34 507 000 000; -57 000 000; 64 025,25; 1 000; 75 ja 0,45;", \
              'expected_words': ['Vaatleme', 'järgmisi', 'arve', ':', '-21 134 567 000 123 , 456', ';', '34 507 000 000', ';', '-57 000 000', ';', '64 025,25', ';', '1 000', ';', '75', 'ja', '0,45', ';'] },\
            { 'text': 'Hukkus umbes 90 000 inimest ja põgenes üle 70 000, kelle hulgas oli 7500 rannarootslast.', \
              'expected_words': ['Hukkus', 'umbes', '90 000', 'inimest', 'ja', 'põgenes', 'üle', '70 000', ',', 'kelle', 'hulgas', 'oli', '7500', 'rannarootslast', '.'] },\
            { 'text': 'Põgenike koguarvuna nimetatakse sageli 70-80 000.', \
              'expected_words': ['Põgenike', 'koguarvuna', 'nimetatakse', 'sageli', '70', '-80 000', '.'] },\
            { 'text' : 'Kaheksal juhul sisaldas brokoli 1,5–3,2 korda rohkem taimekaitsevahendi jääki, kui oli lubatud.',\
              'expected_words': ['Kaheksal', 'juhul', 'sisaldas', 'brokoli', '1,5', '–', '3,2', 'korda', 'rohkem', 'taimekaitsevahendi', 'jääki', ',', 'kui', 'oli', 'lubatud', '.'] },\
            { 'text' : 'Seda puhastuspappi saab Photopointist endale soetada 2.99€ eest.',\
              'expected_words': ['Seda', 'puhastuspappi', 'saab', 'Photopointist', 'endale', 'soetada', '2.99', '€', 'eest', '.'] },\
            { 'text' : '10 000 kroonilt kuus 20 000-le minna on lihtsam kui 500 000-lt miljonile.',\
              'expected_words': ['10 000', 'kroonilt', 'kuus', '20 000', '-', 'le', 'minna', 'on', 'lihtsam', 'kui', '500 000', '-', 'lt', 'miljonile', '.'] },\
            # Koondkorpus-style decimal numerals -- decimal separators are between two spaces:
            { 'text' : 'Rootsis oli tööstustoodangu juurdekasv septembris augustiga võrreldes 3 , 7% .\n Kullauntsi hind jäi 303 , 00 dollari tasemele .',\
              'expected_words': ['Rootsis', 'oli', 'tööstustoodangu', 'juurdekasv', 'septembris', 'augustiga', 'võrreldes', '3 , 7', '%', '.', 'Kullauntsi', 'hind', 'jäi', '303 , 00', 'dollari', 'tasemele', '.'] },\
            { 'text' : 'Kolmes tootegrupis - ampullid ( 40 , 9% ) , salvid ( 33 , 4% ) ja tabletid ( 29 , 6% )',\
              'expected_words': ['Kolmes', 'tootegrupis', '-', 'ampullid', '(', '40 , 9', '%', ')', ',', 'salvid', '(', '33 , 4', '%', ')', 'ja', 'tabletid', '(', '29 , 6', '%', ')'] },\
            # Detection of roman numerals
            { 'text': '"Õiguste" all tuleb mõista ainult põhiõigusi, mida II. peatükis nimetatakse lihtsalt õigusteks.', \
              'expected_words': ['"', 'Õiguste', '"', 'all', 'tuleb', 'mõista', 'ainult', 'põhiõigusi', ',', 'mida', 'II.', 'peatükis', 'nimetatakse', 'lihtsalt', 'õigusteks', '.'] },\
            # Detecting of common date & time patterns
            { 'text' : 'Tuvastamata Kasutaja\n03.01.2007 09:15 See oleks pikk samm edasi.',\
              'expected_words': ['Tuvastamata', 'Kasutaja', '03.01.2007', '09:15', 'See', 'oleks', 'pikk', 'samm', 'edasi', '.'] },\
            { 'text' : '• 8. oktoober 2012 16:06 \n naljakas :D aga tublid poisid punases autos :)',\
              'expected_words': ['•', '8.', 'oktoober', '2012', '16:06', 'naljakas', ':', 'D', 'aga', 'tublid', 'poisid', 'punases', 'autos', ':', ')'] },\
            { 'text' : 'Tei, 06.Jul.2010 20:23 \nRohelise Akadeemia nime all toimuvate arutelude sarja algus.',\
              'expected_words': ['Tei', ',', '06.', 'Jul.', '2010', '20:23', 'Rohelise', 'Akadeemia', 'nime', 'all', 'toimuvate', 'arutelude', 'sarja', 'algus', '.'] },\
            { 'text' : 'Üll 11.01.2010 18:41 100% ostan ennem selle.',\
              'expected_words': ['Üll', '11.01.2010', '18:41', '100', '%', 'ostan', 'ennem', 'selle', '.'] },\
            { 'text' : 'Võsu 04/09/11 18:03 \n Ilus ilm, ning loksa mõõdik näitas kõige rohkem',\
              'expected_words': ['Võsu', '04/09/11', '18:03', 'Ilus', 'ilm', ',', 'ning', 'loksa', 'mõõdik', 'näitas', 'kõige', 'rohkem'] },\
            { 'text' : 'itra 2011-04-22 14:57:04 \n Läksin oma teloga sinna lehele, vajutasin download ja midagi ei juhtunud',\
              'expected_words': ['itra', '2011-04-22', '14:57:04', 'Läksin', 'oma', 'teloga', 'sinna', 'lehele', ',', 'vajutasin', 'download', 'ja', 'midagi', 'ei', 'juhtunud'] },\
            { 'text' : 'Loe edasi \n 20/09/2005 Eesti Akadeemiline Spordliit kuulutab välja järgmised spordi stipendiumid',\
              'expected_words': ['Loe', 'edasi', '20/09/2005', 'Eesti', 'Akadeemiline', 'Spordliit', 'kuulutab', 'välja', 'järgmised', 'spordi', 'stipendiumid'] },\
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
            { 'text': 'Rünnakut juhtisid lipnikud O. Lauri ja A. Nurk.', \
              'expected_words': ['Rünnakut', 'juhtisid', 'lipnikud', 'O. Lauri', 'ja', 'A. Nurk', '.'] },\
            { 'text': "(arhitektid M. Port, M. Meelak, O. Zhemtshugov, R.-L. Kivi)", \
              'expected_words': ['(', 'arhitektid', 'M. Port', ',', 'M. Meelak', ',', 'O. Zhemtshugov', ',', 'R.-L. Kivi', ')'] },\

            # Negative examples: no name with initials should be detected from the following:
            { 'text': "Ei. See pole kassi moodi.", \
              'expected_words': ['Ei', '.', 'See', 'pole', 'kassi', 'moodi', '.'] },\
            { 'text': "Rock-ansambli Dr. Hook and the Medicine Show legendaarne kitarrimängija.", \
              'expected_words': ['Rock-ansambli', 'Dr.', 'Hook', 'and', 'the', 'Medicine', 'Show', 'legendaarne', 'kitarrimängija', '.'] },\
            { 'text': "Augusti ajalooline kuumarekord on 38º C. Talved on harva külmad, kuid võib olla erandeid.", \
              'expected_words': ['Augusti', 'ajalooline', 'kuumarekord', 'on', '38º', 'C', '.', 'Talved', 'on', 'harva', 'külmad', ',', 'kuid', 'võib', 'olla', 'erandeid', '.'] },\
            { 'text': "Päevasel ajal on sobivaks temperatuuriks ruumis +18˚... 23˚C. Kui keegi ruumis ei viibi, piisab 15˚ ... 16˚C kraadist.", \
              'expected_words': ['Päevasel', 'ajal', 'on', 'sobivaks', 'temperatuuriks', 'ruumis', '+', '18', '˚...', '23', '˚', 'C', '.', 'Kui', 'keegi', 'ruumis', 'ei', 'viibi', ',', 'piisab', '15', '˚', '...', '16', '˚', 'C', 'kraadist', '.'] },\
            { 'text': "P.S. Õppige viisakalt kirjutama.", \
              'expected_words': ['P', '.', 'S', '.', 'Õppige', 'viisakalt', 'kirjutama', '.'] },\
            { 'text': "P.P.S. Teine vana ilmus ka välja.", \
              'expected_words': ['P', '.', 'P', '.', 'S', '.', 'Teine', 'vana', 'ilmus', 'ka', 'välja', '.'] },\
              
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

