import unittest
import regex as re

from estnltk import Text
from estnltk.taggers import TokensTagger, CompoundTokenTagger, WordTagger
from estnltk.taggers.standard.text_segmentation.compound_token_tagger import ALL_1ST_LEVEL_PATTERNS

class CompoundTokenTaggerTest(unittest.TestCase):

    def test_detect_email_and_www(self):
        test_texts = [ 
            { 'text': 'See worm lihtsalt kirjutab alati saatjaks big@boss.com ...', \
              'expected_words': ['See', 'worm', 'lihtsalt', 'kirjutab', 'alati', 'saatjaks', 'big@boss.com', '...'] }, \
            { 'text': 'TELLIMISEKS- saada e-kiri aadressil ek.tellimus@eelk.ee - helista toimetusse 733 7795', \
              'expected_words': ['TELLIMISEKS-', 'saada', 'e-kiri', 'aadressil', 'ek.tellimus@eelk.ee', '-', 'helista', 'toimetusse', '733 7795'] }, \
            { 'text': 'Head Mosaicimist ja sellega harjumist soovib \n neti . kass @ postimees . ee', \
              'expected_words': ['Head', 'Mosaicimist', 'ja', 'sellega', 'harjumist', 'soovib', 'neti . kass @ postimees . ee'] }, \
            { 'text': 'sambamees . siim [ -at- ] siim . pri . ee says ... \n On jõudnud siiagi kuuldused , et rahvas on sassi kamminud', \
              'expected_words': ['sambamees . siim [ -at- ] siim . pri', '.', 'ee', 'says', '...', 'On', 'jõudnud', 'siiagi', 'kuuldused', ',', 'et', 'rahvas', 'on', 'sassi', 'kamminud'] }, \
            { 'text': 'saada meil meie klubi esimehele tonisxxx[at]gmail.com', \
              'expected_words': ['saada', 'meil', 'meie', 'klubi', 'esimehele', 'tonisxxx[at]gmail.com'] }, \
            { 'text': 'Sellised veebileheküljed: www. esindus.ee/korteriturg, www. kavkazcenter.com, http: // www. cavalierklubben.com, http : //www.offa.org/ stats ning http://www.politsei.ee/dotAsset/225706 .', \
              'expected_words': ['Sellised', 'veebileheküljed', ':', 'www. esindus.ee/korteriturg', ',', 'www. kavkazcenter.com', ',', 'http: // www. cavalierklubben.com', ',', 'http : //www.offa.org/', 'stats', 'ning', 'http://www.politsei.ee/dotAsset/225706', '.'] }, \
            { 'text': 'Kel huvi http://www.youtube.com/watch?v=PFD2yIVn4IE\npets 11.07.2012 20:37 lugesin enne kommentaarid ära.', \
              'expected_words': ['Kel', 'huvi', 'http://www.youtube.com/watch?v=PFD2yIVn4IE', 'pets', '11.07.2012', '20:37', 'lugesin', 'enne', 'kommentaarid', 'ära', '.'] }, \
            # Short www addresses (addresses without prefixes "www" or "http")
            { 'text': 'Vastavalt hiljutisele uurimusele washingtontimes.com usub 80% ameeriklastest, et jumal mõjutas evolutsiooni mingil määral.', \
              'expected_words': ['Vastavalt', 'hiljutisele', 'uurimusele', 'washingtontimes.com', 'usub', '80%', 'ameeriklastest', ',', 'et', 'jumal', 'mõjutas', 'evolutsiooni', 'mingil', 'määral', '.'] }, \
            { 'text': 'Teadus.ee-st leidsin kunagi energiahulgad, aga google.com, Postimees.ee, news.com, Delfi.ee, kuhuminna.ee, ekspressjob.ee, CyberSecurity.ru, südameapteek.ee, static.flickr.com pole nii huvitavaid tulemusi andnud.', \
              'expected_words': ['Teadus.ee-st', 'leidsin', 'kunagi', 'energiahulgad', ',', 'aga', 'google.com', ',', 'Postimees.ee', ',', 'news.com', ',', 'Delfi.ee', ',', 'kuhuminna.ee', ',', 'ekspressjob.ee', ',', 'CyberSecurity.ru', ',', 'südameapteek.ee', ',', 'static.flickr.com', 'pole', 'nii', 'huvitavaid', 'tulemusi', 'andnud', '.'] }, \

        ]
        for test_text in test_texts:
            text = Text( test_text['text'] )
            # Perform analysis
            text.tag_layer(['words'])
            words_layer = text['words']
            # Fetch results
            word_segmentation = [] 
            for wid, word in enumerate(words_layer):
                word_text = text.text[word.start:word.end]
                word_segmentation.append(word_text)
            #print(word_segmentation)
            # Assert that the tokenization is correct
            self.assertListEqual(test_text['expected_words'], word_segmentation)


    def test_detect_emoticons(self):
        # 1) Test that tagging emoticons is switched on by default
        test_texts = [ 
            { 'text': 'Linalakast eesti talutütar:P Ausõna, nagu meigitud Raja Teele :D', \
              'expected_words': ['Linalakast', 'eesti', 'talutütar', ':P', 'Ausõna', ',', 'nagu', 'meigitud', 'Raja', 'Teele', ':D'] }, \
            { 'text': 'Võibolla tõesti:) Tegelikult olen alles ametit omandamas:) Aga vahepeal ka suvetööd tehtud, mis pole muidugi see mida tegelikult teha tahaksin:)', \
              'expected_words': ['Võibolla', 'tõesti', ':)', 'Tegelikult', 'olen', 'alles', 'ametit', 'omandamas', ':)', 'Aga', 'vahepeal', 'ka', 'suvetööd', 'tehtud', ',', 'mis', 'pole', 'muidugi', 'see', 'mida', 'tegelikult', 'teha', 'tahaksin', ':)'] }, \
            { 'text': 'Maja on fantastiline, mõte on hea :-)', \
              'expected_words': ['Maja', 'on', 'fantastiline', ',', 'mõte', 'on', 'hea', ':-)'] }, \
            { 'text': ':))) Rumal naine ...lihtsalt rumal:D', \
              'expected_words': [':)))', 'Rumal', 'naine', '...', 'lihtsalt', 'rumal', ':D'] }, \
            { 'text': ':DD Mulle meeldib see osa, et see Jaagu vannitoa remont maksis 17 800.- euri :DD Kas talle tehti ujula või?', \
              'expected_words': [':DD', 'Mulle', 'meeldib', 'see', 'osa', ',', 'et', 'see', 'Jaagu', 'vannitoa', 'remont', 'maksis', '17 800', '.', '-', 'euri', ':DD', 'Kas', 'talle', 'tehti', 'ujula', 'või', '?'] }, \
        ]
        for test_text in test_texts:
            text = Text( test_text['text'] )
            # Perform analysis
            text.tag_layer(['words'])
            words_layer = text['words']
            # Fetch results
            word_segmentation = [] 
            for wid, word in enumerate(words_layer):
                word_text = text.text[word.start:word.end]
                word_segmentation.append(word_text)
            #print(word_segmentation)
            # Assert that the tokenization is correct
            self.assertListEqual(test_text['expected_words'], word_segmentation)
        # 2) Test that tagging emoticons can also be switched off
        test_texts = [ 
            { 'text': 'Maja on fantastiline, mõte on hea :-)', \
              'expected_words': ['Maja', 'on', 'fantastiline', ',', 'mõte', 'on', 'hea', ':', '-', ')'] }, \
            { 'text': ':))) Rumal naine ...lihtsalt rumal:D', \
              'expected_words': [':', ')', ')', ')', 'Rumal', 'naine', '...', 'lihtsalt', 'rumal', ':', 'D'] }, \
        ]
        cp_tagger_2 = CompoundTokenTagger(tag_emoticons=False)
        for test_text in test_texts:
            text = Text( test_text['text'] )
            # Perform analysis
            text.tag_layer(['tokens'])
            cp_tagger_2.tag(text)
            text.tag_layer(['words'])
            words_layer = text['words']
            # Fetch results
            word_segmentation = [] 
            for wid, word in enumerate(words_layer):
                word_text = text.text[word.start:word.end]
                word_segmentation.append(word_text)
            #print(word_segmentation)
            # Assert that the tokenization is correct
            self.assertListEqual(test_text['expected_words'], word_segmentation)


    def test_detect_hashtags_and_usernames(self):
        # Test tagging Twitter-style hashtags and username mentions
        test_texts = [ 
            { 'text': 'Rõuge Veepeo Rannalaval ainult #dnb #dubstep', \
              'expected_words': ['Rõuge', 'Veepeo', 'Rannalaval', 'ainult', '#dnb', '#dubstep'] }, \
            { 'text': '@6elushunnik @kanafilee jah, väga deep, jube lausa #naerma#ajab', \
              'expected_words': ['@6elushunnik', '@kanafilee', 'jah', ',', 'väga', 'deep', ',', 'jube', 'lausa', '#naerma', '#ajab'] }, \
            { 'text': 'RT @Kanaburger: semudega kummituslinna tsekkima :) #Udu#öö#Kummituslinn', \
              'expected_words': ['RT', '@Kanaburger', ':', 'semudega', 'kummituslinna', 'tsekkima', ':)', '#Udu', '#öö', '#Kummituslinn'] }, \
        ]
        cp_tagger_3 = CompoundTokenTagger(tag_hashtags_and_usernames=True)
        for test_text in test_texts:
            text = Text( test_text['text'] )
            # Perform analysis
            text.tag_layer(['tokens'])
            cp_tagger_3.tag(text)
            text.tag_layer(['words'])
            words_layer = text['words']
            # Fetch results
            word_segmentation = [] 
            for wid, word in enumerate(words_layer):
                word_text = text.text[word.start:word.end]
                word_segmentation.append(word_text)
            #print(word_segmentation)
            # Assert that the tokenization is correct
            self.assertListEqual(test_text['expected_words'], word_segmentation)


    def test_detect_xml_tags(self):
        test_texts = [ 
            { 'text': '<u>Kirjavahemärgid, hingamiskohad</u>.', \
              'expected_words': ['<u>', 'Kirjavahemärgid', ',', 'hingamiskohad', '</u>', '.'] }, \
            { 'text': '<a href=”http://sait.ee/” rel=”nofollow”>mingi asi</a>', \
              'expected_words': ['<a href=”http://sait.ee/” rel=”nofollow”>', 'mingi', 'asi', '</a>'] }, \
            { 'text': 'Muidugi ei tööta, seal lõpus on mingi </br> mida ma ära võtta ei saa, võid ta ise ehk ära kustutada :)', \
              'expected_words': ['Muidugi', 'ei', 'tööta', ',', 'seal', 'lõpus', 'on', 'mingi', '</br>', 'mida', 'ma', 'ära', 'võtta', 'ei', 'saa', ',', 'võid', 'ta', 'ise', 'ehk', 'ära', 'kustutada', ':)'] }, \
            { 'text': 'Fail algab tavalise XML-päisega, millele järgneb DOCTYPE definitsioon ja seejärel <fontconfig> tääg:\n\n<dir>/tee/minu/fontide/kataloogi</dir>\n', \
              'expected_words': ['Fail', 'algab', 'tavalise', 'XML-päisega', ',', 'millele', 'järgneb', 'DOCTYPE', 'definitsioon', 'ja', 'seejärel', '<fontconfig>', 'tääg', ':', '<dir>', '/', 'tee', '/', 'minu', '/', 'fontide', '/', 'kataloogi', '</dir>'] }, \
            { 'text': 'Kui kasutada sellist <!--googleoff: index--> märgendust <!--googleon: index--> nagu siin\n\nindekseerib Google lehest vaid', \
              'expected_words': ['Kui', 'kasutada', 'sellist', '<!--googleoff: index-->', 'märgendust', '<!--googleon: index-->', 'nagu', 'siin', 'indekseerib', 'Google', 'lehest', 'vaid'] }, \
            # Negative patterns: should not be detected as XML-tags
            { 'text': 'teaser-tüüpi põhiklippi ja üks veebilehel < http://www.visitestonia.com/ > toimuva tarbijamängu promotsiooniklipp.', \
              'expected_words': ['teaser-tüüpi', 'põhiklippi', 'ja', 'üks', 'veebilehel', '<', 'http://www.visitestonia.com/', '>', 'toimuva', 'tarbijamängu', 'promotsiooniklipp', '.'] }, \
            { 'text': 'Eesti omad tean :\n<panda = panda simpanssi = simpanss maaorava = maaorav kenguru = känguru laiskiainen = ? ? ? laiskloom ? jääkarhu = jääkaru koala = koala karhu = karu\nkilpikonna = kilpkonn taskurapu = ? ? ? ? merisiili = ? ? ? ? meresiil ? vyötiäinen = ? ? ? ? vöö ... ? sisilisko = sisalik hummeri = hummer ? lobster käärme = maduuss ;\n) piikkisika = okassiga\nvalas = valas gorilla = gorilla virtahepo = j6ehobu kirahvi = kirahv norsu = elevant dromedaari = yhekyyryga kaamel , dromedar ? strutsi = jaanalind sarvikuono = ninasarvik\ntiikeri = tiiger merihevonen = merehobu ? leopardi = leopard sauvasirkka = ? ? ? ? see oksataoline putukas hyeena = hyään kameleontti = kameeleont mustekala = ? ? ? ? tindikala ? seepra = sepra\nhai = hai meduusa = meduus ? skorpioni = skorpion pantteri = panter tarantella = tarantel ( myrgiämblik ? ) leijona = l6vi susi = hunt krokotiili = krokotil\nkorppikotka = ? ? ? ? raipesööjast kull nokkaeläin = ? ? ? nokkloom ? mursu = merisiga ? oranki = ? orang ( utang ? ) hirvi = p6der muurahaiskarhu = ? ? ? sipelgakaru galago = ? ? ? ? ei tunne isegi soome keeles ; suurte silmadega väike loom ? ? ? pahkasika = ? ? ? tyykassiga>\n On Fri , 29 Nov 2002', \
              'expected_words': ['Eesti', 'omad', 'tean', ':', '<', 'panda', '=', 'panda', 'simpanssi', '=', 'simpanss', 'maaorava', '=', 'maaorav', 'kenguru', '=', 'känguru', 'laiskiainen', '=', '?', '?', '?', 'laiskloom', '?', 'jääkarhu', '=', 'jääkaru', 'koala', '=', 'koala', 'karhu', '=', 'karu', 'kilpikonna', '=', 'kilpkonn', 'taskurapu', '=', '?', '?', '?', '?', 'merisiili', '=', '?', '?', '?', '?', 'meresiil', '?', 'vyötiäinen', '=', '?', '?', '?', '?', 'vöö', '...', '?', 'sisilisko', '=', 'sisalik', 'hummeri', '=', 'hummer', '?', 'lobster', 'käärme', '=', 'maduuss', ';', ')', 'piikkisika', '=', 'okassiga', 'valas', '=', 'valas', 'gorilla', '=', 'gorilla', 'virtahepo', '=', 'j6ehobu', 'kirahvi', '=', 'kirahv', 'norsu', '=', 'elevant', 'dromedaari', '=', 'yhekyyryga', 'kaamel', ',', 'dromedar', '?', 'strutsi', '=', 'jaanalind', 'sarvikuono', '=', 'ninasarvik', 'tiikeri', '=', 'tiiger', 'merihevonen', '=', 'merehobu', '?', 'leopardi', '=', 'leopard', 'sauvasirkka', '=', '?', '?', '?', '?', 'see', 'oksataoline', 'putukas', 'hyeena', '=', 'hyään', 'kameleontti', '=', 'kameeleont', 'mustekala', '=', '?', '?', '?', '?', 'tindikala', '?', 'seepra', '=', 'sepra', 'hai', '=', 'hai', 'meduusa', '=', 'meduus', '?', 'skorpioni', '=', 'skorpion', 'pantteri', '=', 'panter', 'tarantella', '=', 'tarantel', '(', 'myrgiämblik', '?', ')', 'leijona', '=', 'l6vi', 'susi', '=', 'hunt', 'krokotiili', '=', 'krokotil', 'korppikotka', '=', '?', '?', '?', '?', 'raipesööjast', 'kull', 'nokkaeläin', '=', '?', '?', '?', 'nokkloom', '?', 'mursu', '=', 'merisiga', '?', 'oranki', '=', '?', 'orang', '(', 'utang', '?', ')', 'hirvi', '=', 'p6der', 'muurahaiskarhu', '=', '?', '?', '?', 'sipelgakaru', 'galago', '=', '?', '?', '?', '?', 'ei', 'tunne', 'isegi', 'soome', 'keeles', ';', 'suurte', 'silmadega', 'väike', 'loom', '?', '?', '?', 'pahkasika', '=', '?', '?', '?', 'tyykassiga', '>', 'On', 'Fri', ',', '29', 'Nov', '2002'] }, \
        ]
        for test_text in test_texts:
            text = Text( test_text['text'] )
            # Perform analysis
            text.tag_layer(['words'])
            words_spans = text['words']
            # Fetch results
            word_segmentation = [] 
            for wid, word in enumerate( words_spans ):
                word_text = text.text[word.start:word.end]
                word_segmentation.append(word_text)
            #print(word_segmentation)
            # Assert that the tokenization is correct
            self.assertListEqual(test_text['expected_words'], word_segmentation)


    def test_detect_words_with_hyphens(self):
        test_texts = [ 
            { 'text': 'Mis lil-li müüs Tiit 10e krooniga?', \
              'expected_words': ['Mis', 'lil-li', 'müüs', 'Tiit', '10e', 'krooniga', '?'] }, \
            { 'text': 'See on vää-ää-ääga huvitav!', \
              'expected_words': ['See', 'on', 'vää-ää-ääga', 'huvitav', '!'] },\
            # Tokens with repeated hyphens: keep these together as they make up dashes ('mõttekriipsud')
            { 'text': 'Tõepoolest -- paar aastat tagasi oli olukord teine. Seega -- inimlikust vaatepunktist liiga keeruline.', \
              'expected_words': ['Tõepoolest', '--', 'paar', 'aastat', 'tagasi', 'oli', 'olukord', 'teine', '.', \
                                 'Seega', '--', 'inimlikust', 'vaatepunktist', 'liiga', 'keeruline', '.'] },\
            # Negative patterns: numeric ranges should not be considered as words with hyphens!
            { 'text': "14.04 jäi kaal nulli , 15-17.04. tuli korjet 6 kg kokku.", \
              'expected_words': ['14.04', 'jäi', 'kaal', 'nulli', ',', '15', '-', '17.04', '.', 'tuli', 'korjet', '6', 'kg', 'kokku', '.'] },\
            { 'text': 'Laupäeval 15. mail kell 20.00-23.00 on Tartu Laulupeomuuseumis muuseumiöö puhul etendus "Kalevi pojad".', \
              'expected_words': ['Laupäeval', '15.', 'mail', 'kell', '20.00', '-', '23.00', 'on', 'Tartu', 'Laulupeomuuseumis', 'muuseumiöö', 'puhul', 'etendus', '"', 'Kalevi', 'pojad', '"', '.'] },\
            { 'text': 'Väät suutis vastu panna 76.96-77.53-77.50-77.94-74.10-77.13.', \
              'expected_words': ['Väät', 'suutis', 'vastu', 'panna', '76.96', '-', '77.53', '-', '77.50', '-', '77.94', '-', '74.10', '-', '77.13', '.'] },\
        ]
        for test_text in test_texts:
            text = Text( test_text['text'] )
            # Perform analysis
            text.tag_layer(['words'])
            words_spans = text['words']
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
            { 'text' : '1946/47 õ.a. oli koolis 87 õpilast, neist 50 tütarlast.', \
              'expected_words': ['1946', '/', '47', 'õ.a.', 'oli', 'koolis', '87', 'õpilast', ',', 'neist', '50', 'tütarlast', '.'] }, \
            { 'text' : '(tiirlemisperioodid suhtuvad kui väikesed täisarvud, nt 1:2, 1:3, 3:4 jne - toim.).', \
              'expected_words': ['(', 'tiirlemisperioodid', 'suhtuvad', 'kui', 'väikesed', 'täisarvud', ',', 'nt', '1', ':', '2', ',', '1', ':', '3', ',', '3', ':', '4', 'jne', '-', 'toim.', ')', '.'] }, \
            { 'text' : '2007 a.- 2010 a. koolitusteemade seas olid: maksud, töösuhted, efektiivsed kommunikatsioonitehnikad.', \
              'expected_words': ['2007', 'a.', '-', '2010', 'a.', 'koolitusteemade', 'seas', 'olid', ':', 'maksud', ',', 'töösuhted', ',', 'efektiivsed', 'kommunikatsioonitehnikad', '.'] }, \
            { 'text' : 'Viie Dynastia * perioodil ( 907-960 A.D )', \
              'expected_words': ['Viie', 'Dynastia', '*', 'perioodil', '(', '907', '-', '960', 'A.D', ')'] }, \
            { 'text' : "Tehakse vahet n.ö. eurowave ja hardcore purjedel.", \
              'expected_words': ['Tehakse', 'vahet', 'n.ö.', 'eurowave', 'ja', 'hardcore', 'purjedel', '.'] }, \
            { 'text' : 'Referentne funktsioon on orienteeritud n.ö. referentse grupi väärtustele.', \
              'expected_words': ['Referentne', 'funktsioon', 'on', 'orienteeritud', 'n.ö.', 'referentse', 'grupi', 'väärtustele', '.'] }, \
            { 'text' : 'Asi on n . -ö . kontrolli all .', \
              'expected_words': ['Asi', 'on', 'n . -ö .', 'kontrolli', 'all', '.'] }, \
            { 'text' : 'Tema sõnul ei hõlma ISO 9000 sari turgu ja turuanalüüsi , kuid n . -ö . kliendikesksem osa on plaanitud juurde võtta .', \
              'expected_words': ['Tema', 'sõnul', 'ei', 'hõlma', 'ISO', '9000', 'sari', 'turgu', 'ja', 'turuanalüüsi', ',', 'kuid', 'n . -ö .', 'kliendikesksem', 'osa', 'on', 'plaanitud', 'juurde', 'võtta', '.'] }, \
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
            { 'text' : 'Suitsutatud produktide, s.h. ka peekoni ja hot-dogide söömine on eriti kahjulik.',\
              'expected_words': ['Suitsutatud', 'produktide', ',', 's.h.', 'ka', 'peekoni', 'ja', 'hot-dogide', 'söömine', 'on', 'eriti', 'kahjulik', '.'] },\
            { 'text' : 'Budistlikud keskused (s.h. Khordongi Ühing Eestis jt.) on tõlkinud ka otse algkeeltest.',\
              'expected_words': ['Budistlikud', 'keskused', '(', 's.h.', 'Khordongi', 'Ühing', 'Eestis', 'jt.', ')', 'on', 'tõlkinud', 'ka', 'otse', 'algkeeltest', '.'] },\
            { 'text' : 'Tuulepargi kavandatav koguvõimsus on u. 700 MW.',\
              'expected_words': ['Tuulepargi', 'kavandatav', 'koguvõimsus', 'on', 'u.', '700', 'MW', '.'] },\
            # Negative patterns: no abbreviation:
            { 'text' : 'Pööra end seljatoe poole, vaata üle parema õla.',\
              'expected_words': ['Pööra', 'end', 'seljatoe', 'poole', ',', 'vaata', 'üle', 'parema', 'õla', '.'] },\
        ]
        for test_text in test_texts:
            text = Text( test_text['text'] )
            # Perform analysis
            text.tag_layer(['words'])
            words_layer = text['words']
            # Fetch results
            word_segmentation = [] 
            for wid, word in enumerate(words_layer):
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
              'expected_words': ['Põgenike', 'koguarvuna', 'nimetatakse', 'sageli', '70', '-', '80 000', '.'] },\
            { 'text' : 'Kaheksal juhul sisaldas brokoli 1,5–3,2 korda rohkem taimekaitsevahendi jääki, kui oli lubatud.',\
              'expected_words': ['Kaheksal', 'juhul', 'sisaldas', 'brokoli', '1,5', '–', '3,2', 'korda', 'rohkem', 'taimekaitsevahendi', 'jääki', ',', 'kui', 'oli', 'lubatud', '.'] },\
            { 'text' : 'Seda puhastuspappi saab Photopointist endale soetada 2.99€ eest.',\
              'expected_words': ['Seda', 'puhastuspappi', 'saab', 'Photopointist', 'endale', 'soetada', '2.99', '€', 'eest', '.'] },\
            { 'text' : '10 000 kroonilt kuus 20 000-le minna on lihtsam kui 500 000-lt miljonile.',\
              'expected_words': ['10 000', 'kroonilt', 'kuus', '20 000-le', 'minna', 'on', 'lihtsam', 'kui', '500 000-lt', 'miljonile', '.'] },\
            # Negative examples: \newline should not be allowed in the middle of long number
            { 'text' : 'ENSV II Ülemnõukogu liige 1947-1951.\n31. juuli\n1927 toimus 2. Jõhvi laulu- ja muusikapäev',\
              'expected_words': ['ENSV', 'II', 'Ülemnõukogu', 'liige', '1947', '-', '1951.', '31.', 'juuli', '1927', 'toimus', '2.', 'Jõhvi', 'laulu-', 'ja', 'muusikapäev'] },\
            { 'text' : '15. Bosnia-Hertsegoviina 0 900 77 15\n16. Belgia 0 900 77 16\n17. Prantsusmaa 0 900 77 17\n',\
              'expected_words': ['15.', 'Bosnia-Hertsegoviina', '0 900 77 15', '16.', 'Belgia', '0 900 77 16', '17.', 'Prantsusmaa', '0 900 77 17'] },\
            { 'text' : 'Põllumajandus ja jahindus\n4 799\n5 626\n17,2\n6 808\n21,0',\
              'expected_words': ['Põllumajandus', 'ja', 'jahindus', '4 799', '5 626', '17,2', '6 808', '21,0'] },\
            # Negative examples: do not join space-separated numbers if the last group contains less than 3 numbers
            { 'text' : 'Omaette küsimus on seotud § 8 2. ja 3. lõikega.',\
              'expected_words': ['Omaette', 'küsimus', 'on', 'seotud', '§', '8', '2.', 'ja', '3.', 'lõikega', '.'] },\
            { 'text' : 'Allikas: Eesti Haigekassa nõukogu otsus nr 32 30. novemberist 2001',\
              'expected_words': ['Allikas', ':', 'Eesti', 'Haigekassa', 'nõukogu', 'otsus', 'nr', '32', '30.', 'novemberist', '2001'] },\
            { 'text' : 'Määruses ( EMÜ ) nr 2848/89 9 ( viimati muudetud määrusega ( EÜ ) nr 274/95 10 )',\
              'expected_words': ['Määruses', '(', 'EMÜ', ')', 'nr', '2848', '/', '89', '9', '(', 'viimati', 'muudetud', 'määrusega', '(', 'EÜ', ')', 'nr', '274', '/', '95', '10', ')'] },\
            # Koondkorpus-style decimal numerals -- decimal separators are between two spaces:
            { 'text' : 'Rootsis oli tööstustoodangu juurdekasv septembris augustiga võrreldes 3 , 7% .\n Kullauntsi hind jäi 303 , 00 dollari tasemele .',\
              'expected_words': ['Rootsis', 'oli', 'tööstustoodangu', 'juurdekasv', 'septembris', 'augustiga', 'võrreldes', '3 , 7%', '.', 'Kullauntsi', 'hind', 'jäi', '303 , 00', 'dollari', 'tasemele', '.'] },\
            { 'text' : 'Kolmes tootegrupis - ampullid ( 40 , 9% ) , salvid ( 33 , 4% ) ja tabletid ( 29 , 6% )',\
              'expected_words': ['Kolmes', 'tootegrupis', '-', 'ampullid', '(', '40 , 9%', ')', ',', 'salvid', '(', '33 , 4%', ')', 'ja', 'tabletid', '(', '29 , 6%', ')'] },\
            # Detection of roman numerals
            { 'text': '"Õiguste" all tuleb mõista ainult põhiõigusi, mida II. peatükis nimetatakse lihtsalt õigusteks.', \
              'expected_words': ['"', 'Õiguste', '"', 'all', 'tuleb', 'mõista', 'ainult', 'põhiõigusi', ',', 'mida', 'II.', 'peatükis', 'nimetatakse', 'lihtsalt', 'õigusteks', '.'] },\
            # Detecting of common date & time patterns
            { 'text' : 'Tuvastamata Kasutaja\n03.01.2007 09:15 See oleks pikk samm edasi.',\
              'expected_words': ['Tuvastamata', 'Kasutaja', '03.01.2007', '09:15', 'See', 'oleks', 'pikk', 'samm', 'edasi', '.'] },\
            { 'text' : '• 8. oktoober 2012 16:06 \n naljakas :D aga tublid poisid punases autos :)',\
              'expected_words': ['•', '8.', 'oktoober', '2012', '16:06', 'naljakas', ':D', 'aga', 'tublid', 'poisid', 'punases', 'autos', ':)'] },\
            { 'text' : 'Tei, 06.Jul.2010 20:23 \nRohelise Akadeemia nime all toimuvate arutelude sarja algus.',\
              'expected_words': ['Tei', ',', '06.', 'Jul.', '2010', '20:23', 'Rohelise', 'Akadeemia', 'nime', 'all', 'toimuvate', 'arutelude', 'sarja', 'algus', '.'] },\
            { 'text' : 'Üll 11.01.2010 18:41 100% ostan ennem selle.',\
              'expected_words': ['Üll', '11.01.2010', '18:41', '100%', 'ostan', 'ennem', 'selle', '.'] },\
            { 'text' : 'Eelmüük toimub kuni 08.08.2012a . Peale eelmüügi lõppu piletihinnad 14.-€',\
              'expected_words': ['Eelmüük', 'toimub', 'kuni', '08.08.2012a', '.', 'Peale', 'eelmüügi', 'lõppu', 'piletihinnad', '14', '.-€'] },\
            { 'text' : 'Võsu 04/09/11 18:03 \n Ilus ilm, ning loksa mõõdik näitas kõige rohkem',\
              'expected_words': ['Võsu', '04/09/11', '18:03', 'Ilus', 'ilm', ',', 'ning', 'loksa', 'mõõdik', 'näitas', 'kõige', 'rohkem'] },\
            { 'text' : 'itra 2011-04-22 14:57:04 \n Läksin oma teloga sinna lehele, vajutasin download ja midagi ei juhtunud',\
              'expected_words': ['itra', '2011-04-22', '14:57:04', 'Läksin', 'oma', 'teloga', 'sinna', 'lehele', ',', 'vajutasin', 'download', 'ja', 'midagi', 'ei', 'juhtunud'] },\
            { 'text' : 'Loe edasi \n 20/09/2005 Eesti Akadeemiline Spordliit kuulutab välja järgmised spordi stipendiumid',\
              'expected_words': ['Loe', 'edasi', '20/09/2005', 'Eesti', 'Akadeemiline', 'Spordliit', 'kuulutab', 'välja', 'järgmised', 'spordi', 'stipendiumid'] },\
            # Detecting abbreviations of type <uppercase letter> + <numbers>
            { 'text' : 'Maitsetugevdaja E 621 lõhub teie silmanärve.',\
              'expected_words': ['Maitsetugevdaja', 'E 621', 'lõhub', 'teie', 'silmanärve', '.'] },\
            { 'text' : 'Ühed vanimad säilitusained on naatriumnitrit (E 250) ja naatriumnitraat (E 251).',\
              'expected_words': ['Ühed', 'vanimad', 'säilitusained', 'on', 'naatriumnitrit', '(', 'E 250', ')', 'ja', 'naatriumnitraat', '(', 'E 251', ')', '.'] },\
            # 2nd level fixes to numbers: add sign (but do not mix up with ranges)
            { 'text' : "Euroopas levinud kindlustustasu on 0,1 -0,3% töö või näituse maksumusest .",\
              'expected_words': ['Euroopas', 'levinud', 'kindlustustasu', 'on', '0,1', '-', '0,3%', 'töö', 'või', 'näituse', 'maksumusest', '.'] },\
            { 'text' : "Seni Saksa marga ja USA dollari valuutakorvi suhtes +/-7.5% vahemikus püsinud kroon lasti esmaspäeval vabaks .",\
              'expected_words': ['Seni', 'Saksa', 'marga', 'ja', 'USA', 'dollari', 'valuutakorvi', 'suhtes', '+/-7.5%', 'vahemikus', 'püsinud', 'kroon', 'lasti', 'esmaspäeval', 'vabaks', '.'] },\
            { 'text' : "Enim langes Ekspress Grupp ( -7,62% ), talle järgnesid Tallink ( -7,35% ) ja Tallinna Kaubamaja ( -6,77% ).",\
              'expected_words': ['Enim', 'langes', 'Ekspress', 'Grupp', '(', '-7,62%', ')', ',', 'talle', 'järgnesid', 'Tallink', '(', '-7,35%', ')', 'ja', 'Tallinna', 'Kaubamaja', '(', '-6,77%', ')', '.'] },\
            { 'text' : "Hämmastava tõusu tegi ka Baltika aktsia ( +17,46% ).",\
              'expected_words': ['Hämmastava', 'tõusu', 'tegi', 'ka', 'Baltika', 'aktsia', '(', '+17,46%', ')', '.'] },\
            { 'text' : "Edgar Savisaar - 59 häält - 23,6%\n Toomas Hendrik Ilves - 105 häält - 42,6%\n",\
              'expected_words': ['Edgar', 'Savisaar', '-', '59', 'häält', '-', '23,6%', 'Toomas', 'Hendrik', 'Ilves', '-', '105', 'häält', '-', '42,6%'] },\
            # 2nd level fixes to numbers: add percentages
            # Usual numbers with percentages & numbers with percentages with case endings: avoid mixing up these two
            { 'text' : "Selliseid planeete leiab 30% tähtede ümbert.",\
              'expected_words': ['Selliseid', 'planeete', 'leiab', '30%', 'tähtede', 'ümbert', '.'] },\
            { 'text' : "2% õpetajatest langetas hindamisnorme (lubatud oli 5% skaala muutus)",\
              'expected_words': ['2%', 'õpetajatest', 'langetas', 'hindamisnorme', '(', 'lubatud', 'oli', '5%', 'skaala', 'muutus', ')'] },\
            { 'text' : "PRIA toetas ettevõtmist 90% ulatuses, 10% lisasid omaosalusena Paikuse ja Tahkuranna vald ning Pärnu linn.",\
              'expected_words': ['PRIA', 'toetas', 'ettevõtmist', '90%', 'ulatuses', ',', '10%', 'lisasid', 'omaosalusena', 'Paikuse', 'ja', 'Tahkuranna', 'vald', 'ning', 'Pärnu', 'linn', '.'] },\
            { 'text' : "Avapoolajal kahepunktiviskeid 79%-lise ning kaugviskesid 66%-lise täpsusega tabanud Girona jätkas edu kasvatamist.",\
              'expected_words': ['Avapoolajal', 'kahepunktiviskeid', '79%-lise', 'ning', 'kaugviskesid', '66%-lise', 'täpsusega', 'tabanud', 'Girona', 'jätkas', 'edu', 'kasvatamist', '.'] },\
            { 'text' : "Üle 80%-l ettevõtjatest on lairibaühendus.",\
              'expected_words': ['Üle', '80%-l', 'ettevõtjatest', 'on', 'lairibaühendus', '.'] },\
            { 'text' : "Muidugi pead ei anna ,et asi 100% nii on.",\
              'expected_words': ['Muidugi', 'pead', 'ei', 'anna', ',', 'et', 'asi', '100%', 'nii', 'on', '.'] },\
            { 'text' : "Vaja oleks 100%list",\
              'expected_words': ['Vaja', 'oleks', '100%list'] },\
            
            # Detecting abbreviations that overlap with hyphenations [should not result in error]
            { 'text' : 'Võrreldes küllastatud rasvhapete ja ω-rasvhapete rikka toidu mõju noormeeste verenäitajatele, selgitati, '+\
                       'et apolipoproteiinide B-48 ja B-100 kontsentratsioon oli kõrgem küllastatud rasvhapete rikka toiduga katsealuste veres.',\
              'expected_words': ['Võrreldes', 'küllastatud', 'rasvhapete', 'ja', 'ω-rasvhapete', 'rikka', 'toidu', 'mõju', 'noormeeste', \
                                 'verenäitajatele', ',', 'selgitati', ',', 'et', 'apolipoproteiinide', 'B-48', 'ja', 'B-100', 'kontsentratsioon', \
                                 'oli', 'kõrgem', 'küllastatud', 'rasvhapete', 'rikka', 'toiduga', 'katsealuste', 'veres', '.'] },\
        ]
        for test_text in test_texts:
            text = Text( test_text['text'] )
            # Perform analysis
            text.tag_layer(['words'])
            words_spans = text['words']
            # Fetch results
            word_segmentation = [] 
            for wid, word in enumerate( words_spans ):
                word_text = text.text[word.start:word.end]
                word_segmentation.append(word_text)
            #print(word_segmentation)
            # Assert that the tokenization is correct
            self.assertListEqual(test_text['expected_words'], word_segmentation)


    def test_detect_units(self):
        test_texts = [ 
            { 'text': "18 m/s = 64 , 8 km/h , 20 m/s = 72 km/h , 22 m/s = 79 , 2 km/h .", \
              'expected_words': ['18', 'm/s', '=', '64 , 8', 'km/h', ',', '20', 'm/s', '=', '72', 'km/h', ',', '22', 'm/s', '=', '79 , 2', 'km/h', '.'] },\
            { 'text': "Lätis LMT võrgus 104 EEK/ MB , Leedus Omniteli võrgus 138 EEK/ MB ning Venemaal KB Impulsi võrgus 112 EEK/ MB .", \
              'expected_words': ['Lätis', 'LMT', 'võrgus', '104', 'EEK/ MB', ',', 'Leedus', 'Omniteli', 'võrgus', '138', 'EEK/ MB', 'ning', 'Venemaal', 'KB', 'Impulsi', 'võrgus', '112', 'EEK/ MB', '.'] },\
            { 'text': "See oleks madalam Eesti Vabariigi seadustes sätestatud tasemest (15 mgN/l ja 2,0 mgP/l).", \
              'expected_words': ['See', 'oleks', 'madalam', 'Eesti', 'Vabariigi', 'seadustes', 'sätestatud', 'tasemest', '(', '15', 'mgN/l', 'ja', '2,0', 'mgP/l', ')', '.'] },\
            { 'text': "KIIRUS/KIIRENDUS\nsuurim kiirus , km/h : 190", \
              'expected_words': ['KIIRUS', '/', 'KIIRENDUS', 'suurim', 'kiirus', ',', 'km/h', ':', '190'] },\
            # Negative examples: should not be joined as "units"
            { 'text': "Reuters/AP/BNS/EPL\nItaalia päästemeeskonnad jätkasid tööd Foggia linnas.", \
              'expected_words': ['Reuters', '/', 'AP', '/', 'BNS', '/', 'EPL', 'Itaalia', 'päästemeeskonnad', 'jätkasid', 'tööd', 'Foggia', 'linnas', '.'] },\
        ]
        for test_text in test_texts:
            text = Text( test_text['text'] )
            # Perform analysis
            text.tag_layer(['words'])
            words_spans = text['words']
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
              'expected_words': ['Päevasel', 'ajal', 'on', 'sobivaks', 'temperatuuriks', 'ruumis', '+18', '˚...', '23', '˚', 'C', '.', 'Kui', 'keegi', 'ruumis', 'ei', 'viibi', ',', 'piisab', '15', '˚', '...', '16', '˚', 'C', 'kraadist', '.'] },\
            { 'text': "P.S. Õppige viisakalt kirjutama.", \
              'expected_words': ['P.S.', 'Õppige', 'viisakalt', 'kirjutama', '.'] },\
            { 'text': "P.P.S. Teine vana ilmus ka välja.", \
              'expected_words': ['P.P.S.', 'Teine', 'vana', 'ilmus', 'ka', 'välja', '.'] },\
              
        ]
        for test_text in test_texts:
            text = Text( test_text['text'] )
            # Perform analysis
            text.tag_layer(['words'])
            words_spans = text['words']
            # Fetch results
            word_segmentation = [] 
            for wid, word in enumerate( words_spans ):
                word_text = text.text[word.start:word.end]
                word_segmentation.append(word_text)
            #print(word_segmentation)
            # Assert that the tokenization is correct
            self.assertListEqual(test_text['expected_words'], word_segmentation)


    def test_detect_separated_case_endings(self):
        test_texts = [ 
            # Word/abbreviation + case ending
            { 'text': "SKT -st või LinkedIn -ist ma eriti ei hoolinudki, aga workshop ' e külastasin küll.", \
              'expected_words': ['SKT -st', 'või', 'LinkedIn -ist', 'ma', 'eriti', 'ei', 'hoolinudki', ',', 'aga', "workshop ' e", 'külastasin', 'küll', '.'] },\
            { 'text': "Lisaks sellele, et B260a oskab 3G’st WiFi’t teha, saab hakkama ta ka lauatelefoni kõnede vahendamisega.",\
              'expected_words': ['Lisaks', 'sellele', ',', 'et', 'B260a', 'oskab', '3G’st', 'WiFi’t', 'teha', ',', 'saab', 'hakkama', 'ta', 'ka', 'lauatelefoni', 'kõnede', 'vahendamisega', '.'] },\
            { 'text': "Kes meist ei oleks kuulnud Big Benist, Westminster Abbey’st, London Towerist, Buckingham Palace’ist?",\
              'expected_words': ['Kes', 'meist', 'ei', 'oleks', 'kuulnud', 'Big', 'Benist', ',', 'Westminster', 'Abbey’st', ',', 'London', 'Towerist', ',', 'Buckingham', 'Palace’ist', '?'] },\
            { 'text': "Jalamatte saab osta K-Rauta´st:)",\
              'expected_words': ['Jalamatte', 'saab', 'osta', 'K-Rauta´st', ':)'] },\
            { 'text': "Eestis osaleb erakordne solistide koosseis - New Yorgi Metropolitan Opera'st , Pariisi Opéra'st , Londoni Covent Garden'ist , Moskva Suurest Teatrist .",\
              'expected_words': ['Eestis', 'osaleb', 'erakordne', 'solistide', 'koosseis', '-', 'New', 'Yorgi', 'Metropolitan', "Opera'st", ',', 'Pariisi', "Opéra'st", ',', 'Londoni', 'Covent', "Garden'ist", ',', 'Moskva', 'Suurest', 'Teatrist', '.'] },\
            { 'text': "Mingil hetkel tuuritasid Club Kids'id ringi ka U.S.A.'s.",\
              'expected_words': ['Mingil', 'hetkel', 'tuuritasid', 'Club', "Kids'id", 'ringi', 'ka', 'U', '.', 'S', ".A.'s", '.'] },\
            { 'text': "Wu-shu'l on pikk ajalugu . Wu-shu'd õpetatakse lasteaedades , koolides ja ülikoolides .",\
              'expected_words': ["Wu-shu'l", 'on', 'pikk', 'ajalugu', '.', "Wu-shu'd", 'õpetatakse', 'lasteaedades', ',', 'koolides', 'ja', 'ülikoolides', '.'] },\
            { 'text': "James Jr.-iga parem ärge jamage !",\
              'expected_words': ['James', 'Jr.-iga', 'parem', 'ärge', 'jamage', '!'] },\
            { 'text': "Olen näinud küll kuidas see RDS töötab ja seda ka CD-R'ide peal !!",\
              'expected_words': ['Olen', 'näinud', 'küll', 'kuidas', 'see', 'RDS', 'töötab', 'ja', 'seda', 'ka', "CD-R'ide", 'peal', '!!'] },\
            { 'text': "OK, aga kas Viasat läbi DVB-S'i on vaadatav ?",\
              'expected_words': ['OK', ',', 'aga', 'kas', 'Viasat', 'läbi', "DVB-S'i", 'on', 'vaadatav', '?'] },\
            { 'text': "Ma olen nüüd natuke aega saarlane ja suhtlen live ´is ainult saarlastega, höhö.",\
              'expected_words': ['Ma', 'olen', 'nüüd', 'natuke', 'aega', 'saarlane', 'ja', 'suhtlen', 'live ´is', 'ainult', 'saarlastega', ',', 'höhö', '.'] },\
            { 'text': "Nüüd on vaatluse all ViewSonic`u pisiraal.",\
              'expected_words': ['Nüüd', 'on', 'vaatluse', 'all', 'ViewSonic`u', 'pisiraal', '.'] },\
            # Number + case ending (with separator character)
            { 'text': "Tööajal kella 8.00-st 16.00- ni võtavad sel telefonil kõnesid vastu kuni üheksa IT töötajat.",\
              'expected_words': ['Tööajal', 'kella', '8.00-st', '16.00- ni', 'võtavad', 'sel', 'telefonil', 'kõnesid', 'vastu', 'kuni', 'üheksa', 'IT', 'töötajat', '.'] },\
            { 'text': "Ökonomistid, kes ootasid vastavalt 1%-st langust kuu jooksul ja 2,7%-st tõusu aasta peale.",\
              'expected_words': ['Ökonomistid', ',', 'kes', 'ootasid', 'vastavalt', '1%-st', 'langust', 'kuu', 'jooksul', 'ja', '2,7%-st', 'tõusu', 'aasta', 'peale', '.'] },\
            { 'text': "Üks või enam taimekaitsevahendi jääki leiti 2008. aastal 52,8%-s, 2009. aastal 47,9%-s ning 2010. aastal 46,9%-s.",\
              'expected_words': ['Üks', 'või', 'enam', 'taimekaitsevahendi', 'jääki', 'leiti', '2008.', 'aastal', '52,8%-s', ',', '2009.', 'aastal', '47,9%-s', 'ning', '2010.', 'aastal', '46,9%-s', '.'] },\
            { 'text': "Barclays ootab pigem kasvu vähest aeglustumist praeguselt 2.5%-lt ligikaudu 2.4%-le.",\
              'expected_words': ['Barclays', 'ootab', 'pigem', 'kasvu', 'vähest', 'aeglustumist', 'praeguselt', '2.5%-lt', 'ligikaudu', '2.4%-le', '.'] },\
            { 'text': "Eeldatud 20′st minutist sai miskipärast umbes 40.",\
              'expected_words': ['Eeldatud', '20′st', 'minutist', 'sai', 'miskipärast', 'umbes', '40.'] },\
            { 'text': "See aitab kindlamini tõsta nt annetuste tulumaksuvabastust 5%lt 10%le.",\
              'expected_words': ['See', 'aitab', 'kindlamini', 'tõsta', 'nt', 'annetuste', 'tulumaksuvabastust', '5%lt', '10%le', '.'] },\
            { 'text': "Üleriigilisel üldstreigil nõuame ka 50%-list palgatõusu!",\
              'expected_words': ['Üleriigilisel', 'üldstreigil', 'nõuame', 'ka', '50%-list', 'palgatõusu', '!'] },\
            # Number + case ending : ordinals and years/decades
            { 'text': "BGB 3.-nda raamatu 3.-nda tiitli all loetletud omandi omandamise liigid.",\
              'expected_words': ['BGB', '3.-nda', 'raamatu', '3.-nda', 'tiitli', 'all', 'loetletud', 'omandi', 'omandamise', 'liigid', '.'] },\
            { 'text': "Tiit ja Cinnamon startisid 47.-ndatena.",\
              'expected_words': ['Tiit', 'ja', 'Cinnamon', 'startisid', '47.-ndatena', '.'] },\
            { 'text': "1960.-ndate alguses valmis grupp 3-4-korruselisi sektsioonelamuid.",\
              'expected_words': ['1960.-ndate', 'alguses', 'valmis', 'grupp', '3-4-korruselisi', 'sektsioonelamuid', '.'] },\
            { 'text': "Mitme ehitisega täienes 1870.-ndail aastail ülikool.",\
              'expected_words': ['Mitme', 'ehitisega', 'täienes', '1870.-ndail', 'aastail', 'ülikool', '.'] },\
            { 'text': "1980.-ndatel aastatel laiendati Veeriku elamupiirkonda.",\
              'expected_words':['1980.-ndatel', 'aastatel', 'laiendati', 'Veeriku', 'elamupiirkonda', '.'] },\
            # Number + case ending (without separator dash/hyphen)
            { 'text': "Võistlus avatakse kell 12.40, võistluspäev kestab kella 15.30ni.",\
              'expected_words': ['Võistlus', 'avatakse', 'kell', '12.40', ',', 'võistluspäev', 'kestab', 'kella', '15.30ni', '.'] },\
            { 'text': "Rocca al Mare kooli parklas kella 8.30st kuni 9.45ni.",\
              'expected_words': ['Rocca', 'al', 'Mare', 'kooli', 'parklas', 'kella', '8.30st', 'kuni', '9.45ni', '.'] },\
            { 'text': "Või rääkigu oma ülemustega, et muudetaks lahtiolekuaeg kella 21.45ks.",\
              'expected_words': ['Või', 'rääkigu', 'oma', 'ülemustega', ',', 'et', 'muudetaks', 'lahtiolekuaeg', 'kella', '21.45ks', '.'] },\
            { 'text': "Adriana Fernandez 2 : 24.06 ja portugallanna Manuela Machado 2 : 25.08ga.",\
              'expected_words': ['Adriana', 'Fernandez', '2', ':', '24.06', 'ja', 'portugallanna', 'Manuela', 'Machado', '2', ':', '25.08ga', '.'] },\
            # Negative examples: hyphen/dash between spaces -- most likely is not a case separator ...
            { 'text': "Kelle hinges on süütunne, seda peab süüdistama - ta vajab seda.",\
              'expected_words': ['Kelle', 'hinges', 'on', 'süütunne', ',', 'seda', 'peab', 'süüdistama', '-', 'ta', 'vajab', 'seda', '.'] },\
            { 'text': "Teine professor kaevas koos tudengitega välja paar lepakändu - iga viimase kui juureni.",\
              'expected_words': ['Teine', 'professor', 'kaevas', 'koos', 'tudengitega', 'välja', 'paar', 'lepakändu', '-', 'iga', 'viimase', 'kui', 'juureni', '.'] },\
        ]
        for test_text in test_texts:
            text = Text( test_text['text'] )
            # Perform analysis
            text.tag_layer(['words'])
            words_layer = text['words']
            # Fetch result
            word_segmentation = [] 
            for wid, word in enumerate(words_layer):
                word_text = text.text[word.start:word.end]
                word_segmentation.append(word_text)
            #print(word_segmentation)
            # Assert that the tokenization is correct
            self.assertListEqual(test_text['expected_words'], word_segmentation)

    def test_no_duplicate_tokens(self):
        # Tests that the token compounding does not produce any duplicate token spans
        test_texts = [ 
                       { 'text': "Kas ta loeb seal https://www.postimees.ee-d?",\
                         'expected_compound_tokens': [['https', ':', '/', '/', 'www', '.', 'postimees', '.', 'ee', '-',  'd']] },\
                       { 'text': "Olen +100% kindel.",\
                         'expected_compound_tokens': [['+', '100', '%']] ,\
                         'expected_normalizations': ['+100%'] },\
                     ]
        for test_text in test_texts:
            text = Text( test_text['text'] )
            # Perform analysis
            text.tag_layer(['compound_tokens'])
            # Check results
            for ctid, comp_token in enumerate(text['compound_tokens']):
                tokens = [text.text[sp.start:sp.end] for sp in comp_token.spans]
                #print('>>',tokens)
                # Assert that the tokenization is correct
                self.assertListEqual(test_text['expected_compound_tokens'][ctid], tokens)
                if 'expected_normalizations' in test_text:
                    self.assertEqual(test_text['expected_normalizations'][ctid], comp_token.normalized)


    def test_do_not_compound_on_paragraphs(self):
        # Tests that compound tokens will not be created if compoundable tokens are separated by 
        # paragraph separator strings ('\n\n')
        test_texts = [ 
                       # Note: these examples are rather artificial: it seems rather difficult 
                       # to find contexts where the current compounding patterns can actually be 
                       # broken by paragraph separators
                       { 'text': "Robot Mihkel sai skooriks 26.\n\nI 2000 ületas teda ja sai 28.",\
                         'expected_compound_tokens': [['28', '.']] },\
                       { 'text': "I\n\n.\nouo\nII\n\n.\noeo",\
                         'expected_compound_tokens': [[]] },\
                     ]
        cp_tagger = CompoundTokenTagger()
        #cp_tagger = CompoundTokenTagger(do_not_join_on_strings=[])
        for test_text in test_texts:
            text = Text( test_text['text'] )
            # Perform analysis
            text.tag_layer(['tokens'])
            cp_tagger.tag(text)
            # Check results
            for ctid, comp_token in enumerate(text['compound_tokens']):
                tokens = [text.text[sp.start:sp.end] for sp in comp_token.spans]
                #print('>>',tokens)
                # Assert that the tokenization is correct
                self.assertListEqual(test_text['expected_compound_tokens'][ctid], tokens)
                if 'expected_normalizations' in test_text:
                    self.assertEqual(test_text['expected_normalizations'][ctid], comp_token.normalized)

    def test_compound_token_normalization(self):
        # Tests that the compound tokens are normalized properly
        test_texts = [# Normalization of words from tokenization hints
                      {'text': 'SKT -st või LinkedIn -ist ma eriti ei hooligi, aga 10 000\'es koht huvitab küll.',
                       'expected_compound_tokens': [['SKT', '-', 'st'], ['LinkedIn', '-', 'ist'],['10', '000', "'", 'es']],
                       'expected_normalizations': ['SKT-st', 'LinkedIn-ist', "10000'es"] },
                      # Normalization of words with hyphens
                      {'text': 'Mis lil-li müüs Tiit 10-e krooniga?',
                       'expected_compound_tokens': [['lil', '-', 'li'], ['10', '-', 'e']],
                       'expected_normalizations': ['lilli', '10-e']},
                      {'text': 'kõ-kõ-kõik v-v-v-ve-ve-ve-vere-taoline on m-a-a-a-l-u-n-e...',
                       'expected_compound_tokens': [['kõ', '-', 'kõ', '-', 'kõik'], ['v', '-', 'v', '-', 'v', '-', 've', '-', 've', '-', 've', '-', 'vere', '-', 'taoline'], ['m', '-', 'a', '-', 'a', '-', 'a', '-', 'l', '-', 'u', '-', 'n', '-', 'e']],
                       'expected_normalizations': ['kõik', 'vere-taoline', 'maaalune']},
                      # Normalization of halved words: do not separate hyphens, and do not delete hyphens
                      {'text': 'Kas kindlustus- , väärtpaberi- ja pangainspektsioon ühendatakse?',
                       'expected_compound_tokens': [['kindlustus', '-'], ['väärtpaberi', '-']],
                       'expected_texts': [ 'kindlustus-', 'väärtpaberi-'],
                       'expected_normalizations': [ None, None ]},
                      # Normalization of numbers: keep the point inside two point-separated numbers (e.g. prices and times)
                      {'text': 'Keskturul maksab kartul praegu 3.50 ja Nõmme turul 5 kr.',
                       'expected_compound_tokens': [['3', '.', '50']],
                       'expected_normalizations': [ None ],
                       'expected_texts': [ '3.50' ]},
                      {'text': 'Eile hommikul kell 8.30 või esmaspäeva öösel kl 2.31.',
                       'expected_compound_tokens': [['8', '.', '30'], ['2', '.', '31']],
                       'expected_normalizations': [ None, None ], 
                       'expected_texts': [ '8.30', '2.31' ] },
                      ]
        for test_text in test_texts:
            text = Text( test_text['text'])
            # Perform analysis
            text.tag_layer(['compound_tokens'])
            # Check results
            for ctid, comp_token in enumerate( text['compound_tokens'] ):
                tokens = [text.text[sp.start:sp.end] for sp in comp_token.spans]
                #print('>>',tokens)
                #print('>>',comp_token.normalized)
                # Assert that the tokenization is correct
                self.assertListEqual(test_text['expected_compound_tokens'][ctid], tokens)
                self.assertEqual(test_text['expected_normalizations'][ctid], comp_token.normalized)
                if 'expected_texts' in test_text:
                    self.assertEqual(test_text['expected_texts'][ctid], comp_token.enclosing_text)

    def test_using_custom_abbreviations(self):
        # Tests using a list of custom abbreviations
        # Text #1
        text = Text('Kui Sa oled ntx . venekeelses piirkonnas med. või sots. töötaja, siis Sa lihtsalt PEAD vene keelt oskama. Või meeldib pankrot rohkem!?!')
        
        text.tag_layer(['tokens'])
        my_abbreviations = ['ntx', 'med', 'sots']
        # Perform analysis
        CompoundTokenTagger(tag_abbreviations = True, custom_abbreviations = my_abbreviations).tag(text)
        # Check that compound tokens are detected
        compound_tokens = [ comp_token.enclosing_text for comp_token in text['compound_tokens'] ]
        self.assertListEqual( ['ntx .', 'med.', 'sots.'], compound_tokens )
        norm_compound_tokens = [ comp_token.normalized for comp_token in text['compound_tokens'] ]
        self.assertListEqual( ['ntx.', 'med.', 'sots.'], norm_compound_tokens )
        # Check that token compounding fixes sentence boundaries
        text.tag_layer(['sentences'])
        sentences = [ s.enclosing_text for s in text['sentences'] ]
        self.assertListEqual( ['Kui Sa oled ntx . venekeelses piirkonnas med. või sots. töötaja, siis Sa lihtsalt PEAD vene keelt oskama.', 'Või meeldib pankrot rohkem!?!'], sentences )
        
        # Text #2
        text = Text('Tõmba end või ribadeks ja seda ka min. tasu eest.')
        text.tag_layer(['tokens'])
        my_abbreviations = ['min']
        # Perform analysis
        CompoundTokenTagger(tag_abbreviations = True, custom_abbreviations = my_abbreviations).tag(text)
        # Check sentences
        text.tag_layer(['sentences'])
        sentences = [ s.enclosing_text for s in text['sentences'] ]
        self.assertListEqual( ['Tõmba end või ribadeks ja seda ka min. tasu eest.'], sentences )
        
        # Text #3:
        text = Text("Ekspluateerijal on vastavalt §-dele 84 jj. hüvitamise kohustus .")
        text.tag_layer(['tokens'])
        my_abbreviations = ['jj']
        # Perform analysis
        CompoundTokenTagger(tag_abbreviations = True, custom_abbreviations = my_abbreviations).tag(text)
        # Check sentences
        text.tag_layer(['sentences'])
        sentences = [ s.enclosing_text for s in text['sentences'] ]
        self.assertListEqual( ["Ekspluateerijal on vastavalt §-dele 84 jj. hüvitamise kohustus ."], sentences )



    def test_change_compound_tokens_layer_name(self):
        # Tests that tokens and compound tokens layer names can
        # be changed (and it still works!)
        tokens_tagger = TokensTagger(output_layer='my_tokens')
        cp_tagger = CompoundTokenTagger(output_layer='my_compounds', input_tokens_layer='my_tokens')
        word_tagger = WordTagger(input_tokens_layer='my_tokens', input_compound_tokens_layer='my_compounds')
        test_texts = [ 
            { 'text': 'Mis lil-li müüs Tiit 10e krooniga?', \
              'expected_words': ['Mis', 'lil-li', 'müüs', 'Tiit', '10e', 'krooniga', '?'] }, \
            
            { 'text': 'Maja on fantastiline, mõte on hea :-)', \
              'expected_words': ['Maja', 'on', 'fantastiline', ',', 'mõte', 'on', 'hea', ':-)'] }, \
            
            { 'text': "SKT -st või LinkedIn -ist ma eriti ei hoolinudki, aga workshop ' e külastasin küll.", \
              'expected_words': ['SKT -st', 'või', 'LinkedIn -ist', 'ma', 'eriti', 'ei', 'hoolinudki', ',', 'aga', "workshop ' e", 'külastasin', 'küll', '.'] },\
            { 'text': "Lisaks sellele, et B260a oskab 3G’st WiFi’t teha, saab hakkama ta ka lauatelefoni kõnede vahendamisega.",\
              'expected_words': ['Lisaks', 'sellele', ',', 'et', 'B260a', 'oskab', '3G’st', 'WiFi’t', 'teha', ',', 'saab', 'hakkama', 'ta', 'ka', 'lauatelefoni', 'kõnede', 'vahendamisega', '.'] },\
            { 'text': "Kes meist ei oleks kuulnud Big Benist, Westminster Abbey’st, London Towerist, Buckingham Palace’ist?",\
              'expected_words': ['Kes', 'meist', 'ei', 'oleks', 'kuulnud', 'Big', 'Benist', ',', 'Westminster', 'Abbey’st', ',', 'London', 'Towerist', ',', 'Buckingham', 'Palace’ist', '?'] },\
            { 'text': "Tööajal kella 8.00-st 16.00- ni võtavad sel telefonil kõnesid vastu kuni üheksa IT töötajat.",\
              'expected_words': ['Tööajal', 'kella', '8.00-st', '16.00- ni', 'võtavad', 'sel', 'telefonil', 'kõnesid', 'vastu', 'kuni', 'üheksa', 'IT', 'töötajat', '.'] },\
            
            { 'text': "P.S. Õppige viisakalt kirjutama.", \
              'expected_words': ['P.S.', 'Õppige', 'viisakalt', 'kirjutama', '.'] },\
        ]
        for test_text in test_texts:
            text = Text( test_text['text'] )
            # Perform analysis
            tokens_tagger.tag(text)
            cp_tagger.tag(text)
            self.assertTrue( 'my_tokens' in text.layers)
            self.assertTrue( 'my_compounds' in text.layers)
            self.assertFalse( 'tokens' in text.layers)
            self.assertFalse( 'compound_tokens' in text.layers)
            word_tagger.tag(text)
            words_layer = text['words']
            # Fetch result
            word_segmentation = [] 
            for wid, word in enumerate(words_layer):
                word_text = text.text[word.start:word.end]
                word_segmentation.append(word_text)
            #print(word_segmentation)
            # Assert that the tokenization is correct
            self.assertListEqual(test_text['expected_words'], word_segmentation)


    def test_userdefined_pattern_for_compoundtokentagger(self):
        # Tests that CompoundTokenTagger's patterns can be customized
        example_text_str = 'LED-infotabloo heledus: 5000 cd/m²'
        # Create a new pattern
        new_unit_pattern = \
        { 'comment': '2.3) A pattern for capturing cd/m² units;',
          'example': 'cd/m²',
          'pattern_type': 'unit',
          '_regex_pattern_': re.compile(r'(cd\s*/\s*m²)'),
          '_group_': 1,
          '_priority_': (3, 0),
          'normalized': r"lambda m: re.sub(r'\s' ,'' , m.group(1))",
        }
        
        # Case 0:  token 'cd/m²' will not be formed by default
        text = Text( example_text_str )
        text.tag_layer(['compound_tokens'])
        compound_tokens = [ comp_token.enclosing_text for comp_token in text['compound_tokens'] ]
        self.assertListEqual(['LED-infotabloo'], compound_tokens)
        
        # Case 1: add new rule to the end of default patterns (order should not matter)
        new_patterns = ALL_1ST_LEVEL_PATTERNS[:]
        new_patterns.append( new_unit_pattern )
        assert len(new_patterns) == len(ALL_1ST_LEVEL_PATTERNS) + 1
        # Create a tagger that uses customized rules
        cp_tagger = CompoundTokenTagger(patterns_1 = new_patterns)
        text = Text( example_text_str )
        text.tag_layer(['tokens'])
        cp_tagger.tag(text)
        compound_tokens = [ comp_token.enclosing_text for comp_token in text['compound_tokens'] ]
        self.assertListEqual(['LED-infotabloo', 'cd/m²'], compound_tokens)
        
        # Case 2: insert new rule as the first in default patterns (order should not matter)
        new_patterns = ALL_1ST_LEVEL_PATTERNS[:]
        new_patterns.insert( 0, new_unit_pattern )
        assert len(new_patterns) == len(ALL_1ST_LEVEL_PATTERNS) + 1
        # Create a tagger that uses customized rules
        cp_tagger = CompoundTokenTagger(patterns_1 = new_patterns)
        text = Text( example_text_str )
        text.tag_layer(['tokens'])
        cp_tagger.tag(text)
        compound_tokens = [ comp_token.enclosing_text for comp_token in text['compound_tokens'] ]
        self.assertListEqual(['LED-infotabloo', 'cd/m²'], compound_tokens)
        
        # Case 3: use a custom pattern_type
        new_unit_pattern['pattern_type'] = 'my_unit'
        new_patterns = ALL_1ST_LEVEL_PATTERNS[:]
        new_patterns.append( new_unit_pattern )
        assert len(new_patterns) == len(ALL_1ST_LEVEL_PATTERNS) + 1
        # Create a tagger that uses customized rules
        cp_tagger = CompoundTokenTagger(patterns_1 = new_patterns)
        text = Text( example_text_str )
        text.tag_layer(['tokens'])
        cp_tagger.tag(text)
        compound_tokens = [ comp_token.enclosing_text for comp_token in text['compound_tokens'] ]
        self.assertListEqual(['LED-infotabloo', 'cd/m²'], compound_tokens)


    def test_create_an_empty_compoundtokens_layer_via_make_layer_template(self):
        # Tests that an empty compound tokens layer can be created via _make_layer_template
        # ( technically, this means skipping compound token detection )
        text = Text('Mis lil-li müüs Tiit 10e krooniga?').tag_layer('tokens')
        cp_tagger = CompoundTokenTagger()
        # add empty compound tokens layer
        cp_layer  = cp_tagger._make_layer_template()
        cp_layer.text_object = text
        text.add_layer( cp_layer )
        # add words layer upon it
        text.tag_layer('words')
        # check the words 
        word_texts = [text.text[sp.start:sp.end] for sp in text.words.spans]
        self.assertListEqual(['Mis', 'lil', '-', 'li', 'müüs', 'Tiit', '10e', 'krooniga', '?'], word_texts)


from estnltk.taggers.standard.text_segmentation.pretokenized_text_compound_tokens_tagger import PretokenizedTextCompoundTokensTagger
from estnltk.taggers.standard.text_segmentation.whitespace_tokens_tagger import WhiteSpaceTokensTagger

class PretokenizedTextCompoundTokenTaggerTest(unittest.TestCase):

    def test_change_pretokenized_text_compound_tokens_layer_name(self):
        text = Text('New York nõuab metroo renoveerimiseks raha autojuhtidelt')
        tokens_tagger = WhiteSpaceTokensTagger(output_layer='ws_tokens')
        compound_tokens_tagger = PretokenizedTextCompoundTokensTagger( multiword_units = [['New', 'York']],
                                 input_tokens_layer='ws_tokens', output_layer='ws_compound_tokens' )
        tokens_tagger.tag(text)
        compound_tokens_tagger.tag(text)
        # assert layers
        self.assertTrue( 'ws_tokens' in text.layers)
        self.assertTrue( 'ws_compound_tokens' in text.layers)
        self.assertFalse( 'tokens' in text.layers)
        self.assertFalse( 'compound_tokens' in text.layers)
        # assert compound tokens
        self.assertListEqual(text['ws_compound_tokens'].text, ['New', 'York']) 

