import regex as re

from estnltk import Text
from estnltk.taggers import TokensTagger, CompoundTokenTagger, WordTagger
from estnltk.taggers import SentenceTokenizer
from estnltk.taggers.standard.text_segmentation.sentence_tokenizer import merge_patterns


def test_merge_mistakenly_split_sentences_1():
    # Tests that mistakenly split sentences have been properly merged
    # 1: splits related to numeric ranges, dates and times
    test_texts = [ 
        #   Merge case:   {Numeric_range_start} {period} + {dash} {Numeric_range_end}
        { 'text': 'Tartu Muinsuskaitsepäevad toimusid 1988. a 14. - 17. aprillil. Tegelikult oli soov need teha nädal hiljem.', \
          'expected_sentence_texts': ['Tartu Muinsuskaitsepäevad toimusid 1988. a 14. - 17. aprillil.', 'Tegelikult oli soov need teha nädal hiljem.'] }, \
        { 'text': 'Bioloogiaolümpiaadi lõppvoor gümnaasiumile, mis algselt oli planeeritud 15. — 16.aprillile, on ümber tõstetud 28. –29.aprillile.', \
          'expected_sentence_texts': ['Bioloogiaolümpiaadi lõppvoor gümnaasiumile, mis algselt oli planeeritud 15. — 16.aprillile, on ümber tõstetud 28. –29.aprillile.'] }, \
        { 'text': 'Seekordne Mulgi konverents plaanitakse pidada 20. – 21. aprill 2012. Esimesel päeval toimub konverents Karksi Valla Kultuurimajas.', \
          'expected_sentence_texts': ['Seekordne Mulgi konverents plaanitakse pidada 20. – 21. aprill 2012.', 'Esimesel päeval toimub konverents Karksi Valla Kultuurimajas.'] }, \
        { 'text': 'USA teadlased tegid uuringu, milles võeti aluseks 1950. – 2008. aasta temperatuurid ning sellel ajavahemikul korda saadetud kuritööd.', \
          'expected_sentence_texts': ['USA teadlased tegid uuringu, milles võeti aluseks 1950. – 2008. aasta temperatuurid ning sellel ajavahemikul korda saadetud kuritööd.'] }, \

        #   Merge case:   {Numeric_year} {period} {|a|} + {lowercase}
        { 'text': '04.02.2001.a. kell 00.40 tuli väljakutse Tallinnas ühte korterisse.', \
          'expected_sentence_texts': ['04.02.2001.a. kell 00.40 tuli väljakutse Tallinnas ühte korterisse.'] }, \
        { 'text': 'Luunja sai vallaõigused 1991.a. kevadel.', \
          'expected_sentence_texts': ['Luunja sai vallaõigused 1991.a. kevadel.'] }, \
        { 'text': 'Manifest 2, mis kinnitati 2011.a. mais Budapestis.', \
          'expected_sentence_texts': ['Manifest 2, mis kinnitati 2011.a. mais Budapestis.'] }, \
        { 'text': 'Samas ujutatakse turg üle võlgnike varaga.\n Praegune 2009.a. riigieelarve tulude maht on prognoositud 97,8 miljardit EEK.', \
          'expected_sentence_texts': ['Samas ujutatakse turg üle võlgnike varaga.', 'Praegune 2009.a. riigieelarve tulude maht on prognoositud 97,8 miljardit EEK.'] }, \
        { 'text': 'Samas teatas investeeringute suurenemisest rohkem ettevõtteid kui aasta tagasi (2005.a. 46%, 2004.a. 35%).', \
          'expected_sentence_texts': ['Samas teatas investeeringute suurenemisest rohkem ettevõtteid kui aasta tagasi (2005.a. 46%, 2004.a. 35%).'] }, \
        { 'text': 'Uuringu esialgsed tulemused muutuvad kättesaadavaks 2002.a. maikuus.', \
          'expected_sentence_texts': ['Uuringu esialgsed tulemused muutuvad kättesaadavaks 2002.a. maikuus.'] }, \
        { 'text': '1930.õ.a. õppis koolis 61 õpilast. 1937.õ.a. otsustati lõputunnistus välja anda 8 lõpetajale.', \
          'expected_sentence_texts': ["1930.õ.a. õppis koolis 61 õpilast.", '1937.õ.a. otsustati lõputunnistus välja anda 8 lõpetajale.'] }, \
        { 'text': '1946/47 õ.a. oli koolis 87 õpilast, neist 50 tütarlast.', \
          'expected_sentence_texts': ['1946/47 õ.a. oli koolis 87 õpilast, neist 50 tütarlast.'] }, \
        { 'text': 'Kui 1996 . a . tabati 7047 sellealast LE rikkumist , siis eelmisel aastal oli see arv 675 .', \
          'expected_sentence_texts': ['Kui 1996 . a . tabati 7047 sellealast LE rikkumist , siis eelmisel aastal oli see arv 675 .'] }, \

        #   Merge case:   {Date_with_year} {period} + {time}
        { 'text': 'Gert 02.03.2009. 14:40 Tahaks kindlalt sinna kooli:P', \
          'expected_sentence_texts': ['Gert 02.03.2009. 14:40 Tahaks kindlalt sinna kooli:P'] }, \
        #   Merge case:   {|kell|} {time_HH.} + {MM}
        { 'text': 'Kell 15 . 50 tuli elekter Tallinna tagasi .', \
          'expected_sentence_texts': ['Kell 15 . 50 tuli elekter Tallinna tagasi .'] }, \
        { 'text': 'Kell 22 . 00\nTV 3\n“ Thelma\n” ,\nUSA 1991\nRežii : Ridley Scott\n', \
          'expected_sentence_texts': ['Kell 22 . 00\nTV 3\n“ Thelma\n” ,\nUSA 1991\nRežii : Ridley Scott'] }, \

        #   Merge case:   {Numeric_year} {period} + {|aasta|}
        { 'text': 'BRK-de traditsioon sai alguse 1964 . aastal Saksamaal Heidelbergis.', \
          'expected_sentence_texts': ['BRK-de traditsioon sai alguse 1964 . aastal Saksamaal Heidelbergis.'] }, \
        { 'text': 'Tartu Teaduspargil valmib 2005/2006. aastal uus maja.', \
          'expected_sentence_texts': ['Tartu Teaduspargil valmib 2005/2006. aastal uus maja.'] }, \
        { 'text': 'Alates 2008/2009. õppeaastast õpivad kõik 10-nda õpilased C-võõrkeelena saksa keelt.', \
          'expected_sentence_texts': ['Alates 2008/2009. õppeaastast õpivad kõik 10-nda õpilased C-võõrkeelena saksa keelt.'] }, \
        { 'text': 'Kui meie majandus on langenud 2004.–2005. aasta tasemele, peavad sinna tagasi langema ka sissetulekud.', \
          'expected_sentence_texts': ['Kui meie majandus on langenud 2004.–2005. aasta tasemele, peavad sinna tagasi langema ka sissetulekud.'] }, \
        { 'text': '2000. aastal Sydneyst võideti kuldmedal,2004. aastal Ateenas teenisid nad koos hõbeda.', \
          'expected_sentence_texts': ['2000. aastal Sydneyst võideti kuldmedal,2004. aastal Ateenas teenisid nad koos hõbeda.'] }, \
        { 'text': 'Sügisel kaotas naine töö ja ka mehe äri hakkas allamäge veerema. «2009. aasta jaanuaris võtsin ennast töötuna arvele.', \
          'expected_sentence_texts': ['Sügisel kaotas naine töö ja ka mehe äri hakkas allamäge veerema.', '«2009. aasta jaanuaris võtsin ennast töötuna arvele.'] }, \

        #   Merge case:   {Numeric|Roman_numeral_century} {period} {|sajand|} + {lowercase}
        { 'text': 'Kui sealt alla sammusin siis leitsin 15. saj. pärit surnuaia .\nVõi oli isegi pikem aeg , 19. saj. lõpust , kusagilt lugesin .', \
          'expected_sentence_texts': ['Kui sealt alla sammusin siis leitsin 15. saj. pärit surnuaia .', 'Või oli isegi pikem aeg , 19. saj. lõpust , kusagilt lugesin .'] }, \
        { 'text': 'Ioonia filosoofia Mileetose koolkonnd (VI-V saj. e. Kr.) olid esimene kreeka filosoofiakoolkond.', \
          'expected_sentence_texts': ['Ioonia filosoofia Mileetose koolkonnd (VI-V saj. e. Kr.) olid esimene kreeka filosoofiakoolkond.'] }, \
        { 'text': 'Otsimisega oli hädas juba Vana-Hiina suurim ajaloolane Sima Qian (II—I saj. e. m. a.). Ta kaebab allikate vähesuse ja vastuolulisuse üle.', \
          'expected_sentence_texts': ['Otsimisega oli hädas juba Vana-Hiina suurim ajaloolane Sima Qian (II—I saj. e. m. a.).', 'Ta kaebab allikate vähesuse ja vastuolulisuse üle.'] }, \
        #   Merge case:   {BCE_or_ACE} {period} + {lowercase}
        { 'text': 'Aastaks 325 p.Kr. olid erinevad kristlikud sektid omavahel tülli läinud.', \
          'expected_sentence_texts': ['Aastaks 325 p.Kr. olid erinevad kristlikud sektid omavahel tülli läinud.'] }, \
        { 'text': 'Suur rahvasterändamine oli avanud IV-nda sajandiga p. Kr. segaduste ja sõdade ajastu.', \
          'expected_sentence_texts': ['Suur rahvasterändamine oli avanud IV-nda sajandiga p. Kr. segaduste ja sõdade ajastu.'] }, \

        #   Merge case:   {Numeric_date} {period} + {month_name_long}
        { 'text': 'Aga selgust ei pruugi enne 15 . augustit tulla .', \
          'expected_sentence_texts': ['Aga selgust ei pruugi enne 15 . augustit tulla .'] }, \
        { 'text': 'Järgarvud selgeks !\nLoomulikult algab uus aastatuhat 1 . jaanuaril 2001 .', \
          'expected_sentence_texts': ['Järgarvud selgeks !', 'Loomulikult algab uus aastatuhat 1 . jaanuaril 2001 .'] }, \
        { 'text': 'Kirijenko on sündinud 26 . juulil 1962 . aastal .\nTa on lõpetanud Gorki veetraspordiinseneride instituudi.', \
          'expected_sentence_texts': ['Kirijenko on sündinud 26 . juulil 1962 . aastal .', 'Ta on lõpetanud Gorki veetraspordiinseneride instituudi.'] }, \
        { 'text': 'Erastamisväärtpabereid aga saab kasutada kuni 1998 . aasta 31 . detsembrini .', \
          'expected_sentence_texts': ['Erastamisväärtpabereid aga saab kasutada kuni 1998 . aasta 31 . detsembrini .'] }, \
        { 'text': '1.–10. oktoobrini näeb erinevates Eesti teatrites väga head Vene teatrit.', \
          'expected_sentence_texts': ['1.–10. oktoobrini näeb erinevates Eesti teatrites väga head Vene teatrit.'] }, \
        { 'text': 'Nad tähistavad oma sünnipäeva töiselt – 3 . septembril on Vanemuise kontserdimajas galakontsert . Ning juubeliaasta lõppkontsert toimub 22 . oktoobril Sakala keskuses .', \
          'expected_sentence_texts': ['Nad tähistavad oma sünnipäeva töiselt – 3 . septembril on Vanemuise kontserdimajas galakontsert .', 'Ning juubeliaasta lõppkontsert toimub 22 . oktoobril Sakala keskuses .'] }, \
          
        #   Merge case:   {Numeric_date} {period} + {month_name_short}
        { 'text': 'Riik on hoiatanud oma liitlasi ja partnereid äritegemise eest Teheraniga ( NYT , 5 . okt . ) .\n', \
          'expected_sentence_texts': ['Riik on hoiatanud oma liitlasi ja partnereid äritegemise eest Teheraniga ( NYT , 5 . okt . ) .'] }, \
        { 'text': '" Ma ei tunne Laidoneri , " vastas Ake .\n5 . sept .', \
          'expected_sentence_texts': ['" Ma ei tunne Laidoneri , " vastas Ake .', '5 . sept .'] }, \

        #   Merge case:   {First_10_Roman_numerals} {period} + {lowercase_or_dash}
        { 'text': 'Rooma ja Kartaago vahel III. - II. sajandil enne meie ajastut Vahemeremaade valitsemise pärast toimunud sõjad.', \
          'expected_sentence_texts': ['Rooma ja Kartaago vahel III. - II. sajandil enne meie ajastut Vahemeremaade valitsemise pärast toimunud sõjad.'] }, \
        { 'text': 'Konkursitöid võetakse vastu 7. - 18. detsembrini aadressil Malmi 8, III. korrus, ruum 37.', \
          'expected_sentence_texts': ['Konkursitöid võetakse vastu 7. - 18. detsembrini aadressil Malmi 8, III. korrus, ruum 37.'] }, \
        
        #   Merge case:   {Number} {period} + {lowercase}
        { 'text': '6 . augustil mängitakse ette sügisringi 4 . vooru kohtumine.', \
          'expected_sentence_texts': ['6 . augustil mängitakse ette sügisringi 4 . vooru kohtumine.'] }, \
        { 'text': '28 . novembril 1918 ründas Nõukogude Vene 6 . diviis Narvat .', \
          'expected_sentence_texts': ['28 . novembril 1918 ründas Nõukogude Vene 6 . diviis Narvat .'] }, \
        { 'text': 'Esimene kobar moodustub üheksanda lehe kohal , teised iga 2. –3 . lehe kohal .', \
          'expected_sentence_texts': ['Esimene kobar moodustub üheksanda lehe kohal , teised iga 2. –3 . lehe kohal .'] }, \
        { 'text': '3 . koht - Anna Jarek ( Poola ) , 2 . koht - Sarah Johnnson ( Rootsi ) , 1 . koht - Elva Björk Barkardottir', \
          'expected_sentence_texts': ['3 . koht - Anna Jarek ( Poola ) , 2 . koht - Sarah Johnnson ( Rootsi ) , 1 . koht - Elva Björk Barkardottir'] }, \
          
        #   Merge case:   {Number} {period} + {hyphen}
        { 'text': '« mootorratta raam , hind 2000. - EEK »', \
          'expected_sentence_texts': ['« mootorratta raam , hind 2000. - EEK »'] }, \
        { 'text': 'Siiski tahavad erinevad tegelejad asja eest nii 1500. - kuni 3000. - krooni saada.', \
          'expected_sentence_texts': ['Siiski tahavad erinevad tegelejad asja eest nii 1500. - kuni 3000. - krooni saada.'] }, \
        { 'text': 'Meelis\nelusees ei ostaks , kui siis 1000. - eest , ja vaenlasele ka ei soovita', \
          'expected_sentence_texts': ['Meelis\nelusees ei ostaks , kui siis 1000. - eest , ja vaenlasele ka ei soovita'] }, \
        { 'text': 'Samas jaga inffi kus saaks SCS 2000. - , ise olen odavaimat näinud ca 2400-2500. - .', \
          'expected_sentence_texts': ['Samas jaga inffi kus saaks SCS 2000. - , ise olen odavaimat näinud ca 2400-2500. - .'] }, \

    ]
    for test_text in test_texts:
        text = Text( test_text['text'] )
        # Perform analysis
        text.tag_layer(['words', 'sentences'])
        # Collect results 
        sentence_texts = [sentence.enclosing_text for sentence in text['sentences']]
        #print(sentence_texts)
        # Check results
        assert sentence_texts == test_text['expected_sentence_texts']



def test_merge_mistakenly_split_sentences_2():
    # Tests that mistakenly split sentences have been properly merged
    # 2: splits related to sentence parts in parentheses
    test_texts = [ 
        #   Merge case:   {period_ending_content_of_parentheses} + {lowercase_or_comma}
        { 'text': 'Lugesime Menippose (III saj. e.m.a.) satiiri...', \
          'expected_sentence_texts': ['Lugesime Menippose (III saj. e.m.a.) satiiri...'] }, \
        { 'text': 'Eestlastest jõudsid punktikohale Tipp ( 2. ) ja Täpp ( 4. ) ja Käpp ( 7. ) .', \
          'expected_sentence_texts': ['Eestlastest jõudsid punktikohale Tipp ( 2. ) ja Täpp ( 4. ) ja Käpp ( 7. ) .'] }, \
        { 'text': 'Murelik lugeja kurdab ( EPL 31.03. ) , et valla on pääsenud kolmas maailmasõda .', \
          'expected_sentence_texts': ['Murelik lugeja kurdab ( EPL 31.03. ) , et valla on pääsenud kolmas maailmasõda .'] }, \
        { 'text': 'Eesti Päevalehes ( 21.01. ) ilmunud uudisnupuke kuulub kahjuks libauudiste rubriiki .', \
          'expected_sentence_texts': ['Eesti Päevalehes ( 21.01. ) ilmunud uudisnupuke kuulub kahjuks libauudiste rubriiki .'] }, \
        { 'text': 'Teine kysimus : kas kohanime ajaloolises tekstis ( nt . 18. saj . ) kirjutada tolleaegse nimetusega v6i tänapäevase ?', \
          'expected_sentence_texts': ['Teine kysimus : kas kohanime ajaloolises tekstis ( nt . 18. saj . ) kirjutada tolleaegse nimetusega v6i tänapäevase ?'] }, \
        { 'text': 'Keiser Taianuse ( 93-117 p .\nKr . ) basseinist Colosseumi lähedal kraapis üks tööline sel kevadel välja huvitava leiu.', \
          'expected_sentence_texts': ['Keiser Taianuse ( 93-117 p .\nKr . ) basseinist Colosseumi lähedal kraapis üks tööline sel kevadel välja huvitava leiu.'] }, \
        { 'text': 'Ja kui ma sain 40 , olin siis Mikuga ( Mikk Mikiveriga - Toim. ) abi-elus .', \
          'expected_sentence_texts': ['Ja kui ma sain 40 , olin siis Mikuga ( Mikk Mikiveriga - Toim. ) abi-elus .'] }, \
        { 'text': 'Originaalis on joogis arrak ( riisiviin - toim. ) , rumm , tee , vesi ja suhkur ,\nseletab Demjanov .', \
          'expected_sentence_texts': ['Originaalis on joogis arrak ( riisiviin - toim. ) , rumm , tee , vesi ja suhkur ,\nseletab Demjanov .'] }, \
        { 'text': '“Praktiline töö läbib kontrolli DVSi (Saksamaa Keevitusliit – toim.) laboris ja selle alusel väljastatakse sertifikaat,” rääkis Einla.', \
          'expected_sentence_texts': ['“Praktiline töö läbib kontrolli DVSi (Saksamaa Keevitusliit – toim.) laboris ja selle alusel väljastatakse sertifikaat,” rääkis Einla.'] }, \
        { 'text': 'Lõpuks otsustasingi kandideerida ning tänane ( reede õhtul - toim. ) võit tuli mulle küll täieliku üllatusena .', \
          'expected_sentence_texts': ['Lõpuks otsustasingi kandideerida ning tänane ( reede õhtul - toim. ) võit tuli mulle küll täieliku üllatusena .'] }, \

        #   Merge case:   {parentheses_start} {content_in_parentheses} + {content_in_parentheses} {parentheses_end}
        { 'text': '( " Easy FM , soft hits ! " ) .', \
          'expected_sentence_texts': ['( " Easy FM , soft hits ! " ) .'] }, \
        { 'text': '( " Mis siis õieti tahetakse ? " , 1912 ) .', \
          'expected_sentence_texts': ['( " Mis siis õieti tahetakse ? " , 1912 ) .'] }, \
        { 'text': 'Kirjandusel ( resp. raamatul ) on läbi aegade olnud erinevaid funktsioone .', \
          'expected_sentence_texts': ['Kirjandusel ( resp. raamatul ) on läbi aegade olnud erinevaid funktsioone .'] }, \
        { 'text': 'Bisweed on alles 17aastane (loe: ta läheb sügisel 11. klassi!) ja juba on tema heliloomingut välja andnud mitmed plaadifirmad.', \
          'expected_sentence_texts': ['Bisweed on alles 17aastane (loe: ta läheb sügisel 11. klassi!) ja juba on tema heliloomingut välja andnud mitmed plaadifirmad.'] }, \
        { 'text': 'Riik on hoiatanud oma liitlasi ja partnereid äritegemise eest Teheraniga ( NYT , 5 . okt . ) .\n', \
          'expected_sentence_texts': ['Riik on hoiatanud oma liitlasi ja partnereid äritegemise eest Teheraniga ( NYT , 5 . okt . ) .'] }, \
        { 'text': 'Varustage aabits oma nimega ning tooge see selle nädala jooksul (23 . – 26. 08) oma rühmaõpetaja kätte!', \
          'expected_sentence_texts': ['Varustage aabits oma nimega ning tooge see selle nädala jooksul (23 . – 26. 08) oma rühmaõpetaja kätte!'] }, \
        
        #   Merge case:   {parentheses_start} {content_in_parentheses} + {numeric_patterns} {parentheses_end}
        { 'text': 'Haiglasse toimetati kaassõitjad Vladimir ( s.1982 ) ja Jelena ( s.1981 ) .', \
          'expected_sentence_texts': ['Haiglasse toimetati kaassõitjad Vladimir ( s.1982 ) ja Jelena ( s.1981 ) .'] }, \
        { 'text': 'Mootorratast juhtinud Meelis ( s.1985 ) ning mootorratta tagaistmel olnud Kadri ( s . 1984 ) .', \
          'expected_sentence_texts': ['Mootorratast juhtinud Meelis ( s.1985 ) ning mootorratta tagaistmel olnud Kadri ( s . 1984 ) .'] }, \
        { 'text': 'Dokumentide järgi tehti kindlaks , et tegu on Uunoga ( s. 1940 ) .\nSündmuse täpsemad asjaolud on selgitamisel .', \
          'expected_sentence_texts': ['Dokumentide järgi tehti kindlaks , et tegu on Uunoga ( s. 1940 ) .', 'Sündmuse täpsemad asjaolud on selgitamisel .'] }, \
        { 'text': '( JO L 349 du 24.12.1998 , p. 47 )\n( EFT L 349 af 24.12.1998 , s. 47 )', \
          'expected_sentence_texts': ['( JO L 349 du 24.12.1998 , p. 47 )\n( EFT L 349 af 24.12.1998 , s. 47 )'] }, \
        { 'text': '( “ Usun Eestisse ” , lk. 198 )', \
          'expected_sentence_texts': ['( “ Usun Eestisse ” , lk. 198 )'] }, \
        { 'text': 'On lihtsalt olemas üks teine mõõde : rahvuskultuuriline missioon ( lk. 217 ) .', \
          'expected_sentence_texts': ['On lihtsalt olemas üks teine mõõde : rahvuskultuuriline missioon ( lk. 217 ) .'] }, \
        { 'text': 'Enam vähenevad kulutused kartuli ostmiseks ( -15 . 20 ) .', \
          'expected_sentence_texts': ['Enam vähenevad kulutused kartuli ostmiseks ( -15 . 20 ) .'] }, \
          
        #   Merge case:   {content_in_parentheses} + {single_sentence_ending_symbol}          
        { 'text': 'Pani eestvedajaks mõne rahvasportlasest poliitiku ( kui neid ikka on ? ) .', \
          'expected_sentence_texts': ['Pani eestvedajaks mõne rahvasportlasest poliitiku ( kui neid ikka on ? ) .'] }, \
        { 'text': 'See oli siis see 60 krooni ( või rubla ? ) .\nMiks on see põletav küsimus ?', \
          'expected_sentence_texts': ['See oli siis see 60 krooni ( või rubla ? ) .', 'Miks on see põletav küsimus ?'] }, \
        { 'text': 'Vähk ( 20.07. - 09.08. ) .\nVähkkasvajana vohav horoskoobihullus on nakatanud Sindki .', \
          'expected_sentence_texts': ['Vähk ( 20.07. - 09.08. ) .', 'Vähkkasvajana vohav horoskoobihullus on nakatanud Sindki .'] }, \
        { 'text': 'Yerlikaya oli protesti sisse andnud ja see rahuldati ( ? ! ) . \nMöllu oli saalis tublisti .', \
          'expected_sentence_texts': ['Yerlikaya oli protesti sisse andnud ja see rahuldati ( ? ! ) .', 'Möllu oli saalis tublisti .'] }, \
        { 'text': 'CD müüdi 400 krooniga ( alghind oli 100 kr. ) .\nOsteti viis tööd , neist üks õlimaal .', \
          'expected_sentence_texts': ['CD müüdi 400 krooniga ( alghind oli 100 kr. ) .', 'Osteti viis tööd , neist üks õlimaal .'] }, \
        { 'text': 'Neenetsi rahvusringkonnas ( kõlab juba ise sürrealistlikult ! ) .\nVähem kummaline polnud tema tegevus Küsimuste ja Vastuste toimetajana .', \
          'expected_sentence_texts': ['Neenetsi rahvusringkonnas ( kõlab juba ise sürrealistlikult ! ) .', 'Vähem kummaline polnud tema tegevus Küsimuste ja Vastuste toimetajana .'] }, \
          
        #   Merge-and-split case:   {sentence_ending_punct} + {parentheses_end}<end> {uppercase}
        { 'text': '(Hm!)\nJa kui lugesid,siis käidi laulmas täiesti stiihiliselt.', \
          'expected_sentence_texts': ['(Hm!)', 'Ja kui lugesid,siis käidi laulmas täiesti stiihiliselt.'] }, \
        { 'text': '(Kihnu keeli – massakas.) Ütleme, et järvetuulte poolt pargitud.', \
          'expected_sentence_texts': ['(Kihnu keeli – massakas.)', 'Ütleme, et järvetuulte poolt pargitud.'] }, \
        { 'text': '( Naerab . )\nEriti siis , kui sõidan mootorratta või jalgrattaga .', \
          'expected_sentence_texts': ['( Naerab . )', 'Eriti siis , kui sõidan mootorratta või jalgrattaga .'] }, \
        { 'text': '(Arvatagu ära, mida see tähendab!)\nEetrihäälte kõne on reostatud nugisõnadega .', \
          'expected_sentence_texts': ['(Arvatagu ära, mida see tähendab!)', 'Eetrihäälte kõne on reostatud nugisõnadega .'] }, \
        { 'text': '( Muigab laialt . )\nTegelikult muidugi püüan kogu nädalalõpu võistlusele keskenduda ja lasen end lõdvaks alles pühapäeva õhtul , kui koju jõuan .', \
          'expected_sentence_texts': ['( Muigab laialt . )', 'Tegelikult muidugi püüan kogu nädalalõpu võistlusele keskenduda ja lasen end lõdvaks alles pühapäeva õhtul , kui koju jõuan .'] }, \
        { 'text': '( kellele ei meeldiks ? )\nKui ma tavaliselt ise sõidan ( keegi on kõrvalistujana , mul ju veel titekad ) , siis ma rikun liikluseeskirju liiga tihti ( ületan kiirust , ei näita suunda ... ) .', \
          'expected_sentence_texts': ['( kellele ei meeldiks ? )', 'Kui ma tavaliselt ise sõidan ( keegi on kõrvalistujana , mul ju veel titekad ) , siis ma rikun liikluseeskirju liiga tihti ( ületan kiirust , ei näita suunda ... ) .'] }, \
        
     ]
    for test_text in test_texts:
        text = Text( test_text['text'] )
        # Perform analysis
        text.tag_layer(['words', 'sentences'])
        # Collect results 
        sentence_texts = \
            [sentence.enclosing_text for sentence in text['sentences']]
        #print(sentence_texts)
        # Check results
        assert sentence_texts == test_text['expected_sentence_texts']



def test_merge_mistakenly_split_sentences_3_fix_double_quotes():
    # Tests that mistakenly split sentences have been properly merged
    # 3.1: fixes double quotes based on local context;
    test_texts = [ 
        #   Merge case:   {sentence_ending_punct} {ending_quotes}? + {comma_or_semicolon} {lowercase_letter}
        { 'text': 'ETV-s esietendub homme " Õnne 13 ! " , mis kuu aja eest jõudis lavale Ugalas .', \
          'expected_sentence_texts': ['ETV-s esietendub homme " Õnne 13 ! " , mis kuu aja eest jõudis lavale Ugalas .'] }, \
        { 'text': 'Naise küsimusele : " Kes on tema uus sekretär ? " , vastas Jaak suure entusiasmiga .', \
          'expected_sentence_texts': ['Naise küsimusele : " Kes on tema uus sekretär ? " , vastas Jaak suure entusiasmiga .'] }, \
        { 'text': 'Lavale astuvad jõulise naissolistiga Conflict OK ! , kitarripoppi mängivad Claires Birthday ja Seachers .', \
          'expected_sentence_texts': ['Lavale astuvad jõulise naissolistiga Conflict OK ! , kitarripoppi mängivad Claires Birthday ja Seachers .'] }, \
        { 'text': 'Tolle taha jääb xxxx miljoni krooni eest nn. " varjatud ainet " .', \
          'expected_sentence_texts': ['Tolle taha jääb xxxx miljoni krooni eest nn. " varjatud ainet " .'] }, \
        { 'text': 'kui sokratese " segav " kohalolek on " välistatud " ja nn. " ellimineeritud " ...', \
          'expected_sentence_texts': ['kui sokratese " segav " kohalolek on " välistatud " ja nn. " ellimineeritud " ...'] }, \
        { 'text': 'Enne " Romeo ja Juliat " koostasid kaks inkvisiitorit " Malleus Maleficarumi " nn. " nöiavasara "', \
          'expected_sentence_texts': ['Enne " Romeo ja Juliat " koostasid kaks inkvisiitorit " Malleus Maleficarumi " nn. " nöiavasara "'] }, \
          
        #   Merge case:   {sentence_ending_punct} + {only_ending_quotes}
        { 'text': 'Aitäh ! "', \
          'expected_sentence_texts': ['Aitäh ! "'] }, \
        { 'text': 'Mitte meie rühmas , vaid terves polgus ! ”', \
          'expected_sentence_texts': ['Mitte meie rühmas , vaid terves polgus ! ”'] }, \
        { 'text': '“ Tuleb kasutada lund ja jääd , kuni neid veel on . ”', \
          'expected_sentence_texts': ['“ Tuleb kasutada lund ja jääd , kuni neid veel on . ”'] }, \
        { 'text': '“ Akendega on nüüd klaar .\nKas värvin ka raamid ära ? ”', \
          'expected_sentence_texts': ['“ Akendega on nüüd klaar .', 'Kas värvin ka raamid ära ? ”'] }, \
        { 'text': '« See amet on nii raske ! »', \
          'expected_sentence_texts': ['« See amet on nii raske ! »'] }, \
        { 'text': '« Ma sõin tavaliselt kolm hamburgerit päevas , kujutate ette ? »', \
          'expected_sentence_texts': ['« Ma sõin tavaliselt kolm hamburgerit päevas , kujutate ette ? »'] }, \
        { 'text': 'Küsisin mõistlikku summat , arvan .\nNüüd ootan nende pakkumist . »', \
          'expected_sentence_texts': ['Küsisin mõistlikku summat , arvan .', 'Nüüd ootan nende pakkumist . »'] }, \
        
        #   Negative cases: do not merge these into one sentence:
        { 'text': '" Aga kui sumo ära toidab , tuleb ametit vahetada , " leiab ta .\n" Müüja-turvam= ehe töö pole unistuste tipp .', \
          'expected_sentence_texts': ['" Aga kui sumo ära toidab , tuleb ametit vahetada , " leiab ta .', '" Müüja-turvam= ehe töö pole unistuste tipp .'] }, \
        { 'text': 'Kuid " Trainspottingus " pole tegemist individualistliku protestiga .\n" Train-spotting " on generatsioonifilm , kollektiivne protest .', \
          'expected_sentence_texts': ['Kuid " Trainspottingus " pole tegemist individualistliku protestiga .', '" Train-spotting " on generatsioonifilm , kollektiivne protest .'] }, \

        #   Merge-and-split: {ending_punctuation} + {ending_quotes}<end> {starting_quotes}
        { 'text': '« Ei kedagi . »\n\n« Peate midagi ümber korraldama ka oma elus ? » pärib Merle .', \
          'expected_sentence_texts': ['« Ei kedagi . »', '« Peate midagi ümber korraldama ka oma elus ? » pärib Merle .'] }, \
        { 'text': '« Tõsiselt , jah ?\nVäga tore ! »\n\n« Mis siin ikka ! » tähendab vanahärra ükskõikselt .', \
          'expected_sentence_texts': ['« Tõsiselt , jah ?', 'Väga tore ! »', '« Mis siin ikka ! » tähendab vanahärra ükskõikselt .'] }, \
        { 'text': '"Imelik! Kas siis selle peale võib solvuda?" "Noh, ta ei armasta, kui keegi tema prilliklaasidele hingab."', \
          'expected_sentence_texts': ['"Imelik!', 'Kas siis selle peale võib solvuda?"', '"Noh, ta ei armasta, kui keegi tema prilliklaasidele hingab."'] }, \
        { 'text': '« Meeste lihas on tühjem , aga võtab taastamistegevust vastu paremini kui varem . »\n\n« Meie treeningutel on üks uus peateema ! » elavneb Alaver .', \
          'expected_sentence_texts': ['« Meeste lihas on tühjem , aga võtab taastamistegevust vastu paremini kui varem . »', '« Meie treeningutel on üks uus peateema ! » elavneb Alaver .'] }, \
        { 'text': '"Kuulge, et pidite mu pojal opereerima ainult mandlid, aga nüüd olete ka purihambad välja tõmmanud!" "Nojah, me panime ta eksikombel liiga kauaks magama ja ei tahtnud lasta aega kaotsi minna."', \
          'expected_sentence_texts': ['"Kuulge, et pidite mu pojal opereerima ainult mandlid, aga nüüd olete ka purihambad välja tõmmanud!"', '"Nojah, me panime ta eksikombel liiga kauaks magama ja ei tahtnud lasta aega kaotsi minna."'] }, \
        #   Merge-and-split: {ending_punctuation} + {ending_quotes}<end> {starting_brackets}
        { 'text': '« Kus on minu mesi ? »\n( Inglise keeles tähendab mesi ehk honey ka kallimat . )', \
          'expected_sentence_texts': ['« Kus on minu mesi ? »', '( Inglise keeles tähendab mesi ehk honey ka kallimat . )'] }, \
        { 'text': '« Aga sellega tuli harjuda . »\n\n( Irdi ajal mängis Helend Vanemuises Brechti Švejki . )\n\nNäitemängust vabal ajal töötas Helend valla maksunõudjana .',\
          'expected_sentence_texts': ['« Aga sellega tuli harjuda . »', '( Irdi ajal mängis Helend Vanemuises Brechti Švejki . )', 'Näitemängust vabal ajal töötas Helend valla maksunõudjana .'] }, \

        #   Merge case:   {sentence_ending_punct} {ending_quotes} + {only_sentence_ending_punct}
        { 'text': '" See pole ju üldse kallis .\nNii ilus ! " . \nNõmmel elav pensioniealine Maret .', \
          'expected_sentence_texts': ['" See pole ju üldse kallis .', 'Nii ilus ! " .', 'Nõmmel elav pensioniealine Maret .'] }, \
        { 'text': 'Marjana küsis iga asja kohta " Kak eta porusski ? " . \nKuidas ma keele selgeks sain', \
          'expected_sentence_texts': ['Marjana küsis iga asja kohta " Kak eta porusski ? " .', 'Kuidas ma keele selgeks sain'] }, \
        { 'text': 'Tal polnud aimugi , kust ta järgmise kaustiku saab .\n" . . . jätkan tolle esimese päeva taastamist .', \
          'expected_sentence_texts': ['Tal polnud aimugi , kust ta järgmise kaustiku saab .\n" . . .', 'jätkan tolle esimese päeva taastamist .'] }, \
        { 'text': '" Kuidas saada miljonäriks ? " . \nSelge see , et miljonimängus peavad olema kõige raskemad küsimused .', \
          'expected_sentence_texts': ['" Kuidas saada miljonäriks ? " .', 'Selge see , et miljonimängus peavad olema kõige raskemad küsimused .'] }, \
        { 'text': '" Ega siin ei maksa tooste oodata , hakkama aga kohe võtma ! " . \nMa ei taha seda ärajäänud kohtumist presidendi kaela ajada .', \
          'expected_sentence_texts': ['" Ega siin ei maksa tooste oodata , hakkama aga kohe võtma ! " .', 'Ma ei taha seda ärajäänud kohtumist presidendi kaela ajada .'] }, \
    ]
    for test_text in test_texts:
        text = Text( test_text['text'] )
        # Perform analysis
        text.tag_layer(['words', 'sentences'])
        # Collect results 
        sentence_texts = \
            [sentence.enclosing_text for sentence in text['sentences']]
        #print(sentence_texts)
        # Check results
        assert sentence_texts == test_text['expected_sentence_texts']


def test_fix_double_quotes_2():
    # Tests that knowledge about quotations in the whole text is used to repair sentence boundaries
    # 3.2: fixes double quotes based on global counts of quotation marks;
    sentence_tokenizer = SentenceTokenizer( fix_double_quotes_based_on_counts=True )
    test_texts = [ 
        # if an ending double quotes start a sentence, then move the quotes to the end of the previous sentence
        { 'text': 'Kertu küsib : “ Miks sa naeratad kogu aeg ? ”\nMaailm on nii ilus .', \
          'expected_sentence_texts': ['Kertu küsib : “ Miks sa naeratad kogu aeg ? ”', 'Maailm on nii ilus .'] }, \
        { 'text': 'Mis te nende tähtedega teete ?\n“ Maha müün . ” See ei tähenda , et nii peabki .', \
          'expected_sentence_texts': ['Mis te nende tähtedega teete ?', '“ Maha müün . ”', 'See ei tähenda , et nii peabki .'] }, \
        { 'text': '“ Minul pole häda midägit .\nPension käib ja puha . ”\nTraktor aias on poja oma .', \
          'expected_sentence_texts': ['“ Minul pole häda midägit .', 'Pension käib ja puha . ”', 'Traktor aias on poja oma .'] }, \
        { 'text': 'Päris eakatest räägib näiteks " Looduse lapsed . " Piletihinnad on madalamad kui muidu kinodes , 25-60 krooni .', \
          'expected_sentence_texts': ['Päris eakatest räägib näiteks " Looduse lapsed . "', \
                                      'Piletihinnad on madalamad kui muidu kinodes , 25-60 krooni .'] }, \
        
        # if the movable ending quote is followed by the attribution part of the quote (describing "who uttered the quote"), then 
        # moves the  ending  quotation  mark along with the attribution part to the end of the previous sentence;
        { 'text': 'Inspektor Lestrade ja lahkus kiiresti , jälitatuna koerast . '+\
                  '“ Kuidas sul siis sedapuhku Sussexis läks ? ” tundis Watson tule kohal käsi kuivatades huvi . '+\
                  "“ Ma näen , et Baskerville'ide koer on jälle kutsikad saanud ! ” ", \
          'expected_sentence_texts': ['Inspektor Lestrade ja lahkus kiiresti , jälitatuna koerast .', \
                                      '“ Kuidas sul siis sedapuhku Sussexis läks ? ” tundis Watson tule kohal käsi kuivatades huvi .', \
                                      "“ Ma näen , et Baskerville'ide koer on jälle kutsikad saanud ! ”"] }, \
        { 'text': '" Oot , ma teen lahti " " Oh , küll ma ise , " ütlen pudelikaelast kõvasti kinni haarates . " Mis-mis ?! "', \
          'expected_sentence_texts': ['" Oot , ma teen lahti "', \
                                      '" Oh , küll ma ise , " ütlen pudelikaelast kõvasti kinni haarates .', \
                                      '" Mis-mis ?! "'] }, \
        
        # if there are consecutive pairs of double quotes (without separating comma or lowercase word), assume these 
        # should mark different sentences: split after ending quotes
        { 'text': '“ Kuule , mida te Lestradega siin tegite ? ” “ Aga see on ju elementaarne , ” imestas Watson . “ Kas sa siis ise ei näinud ? ”', \
          'expected_sentence_texts': ['“ Kuule , mida te Lestradega siin tegite ? ”', \
                                      '“ Aga see on ju elementaarne , ” imestas Watson .', \
                                      '“ Kas sa siis ise ei näinud ? ”'] }, \
        { 'text': '" Kuidas sul muidu päev läks ? Kas see võrukael Tiit ka midagi kokku keeras ? "  '+\
                  '" Tead , ma olen nii väsinud ... " " Hea küll , hea küll ! Ma ei päri rohkem ! "', \
          'expected_sentence_texts': ['" Kuidas sul muidu päev läks ?', \
                                      'Kas see võrukael Tiit ka midagi kokku keeras ? "', \
                                      '" Tead , ma olen nii väsinud ... "', \
                                      '" Hea küll , hea küll !', \
                                      'Ma ei päri rohkem ! "'] }, \
        { 'text': '" Ja veel . Tõde on kusagil olemas . Varem või hiljem ... "  '+\
                  '" Hea küll , hea küll , " tõrjus Jan ja lonkis tagasi palatisse .', \
          'expected_sentence_texts': ['" Ja veel .', 'Tõde on kusagil olemas .', \
                                      'Varem või hiljem ... "', \
                                      '" Hea küll , hea küll , " tõrjus Jan ja lonkis tagasi palatisse .'] }, \
    ]
    for test_text in test_texts:
        text = Text( test_text['text'] )
        # Perform analysis
        text.tag_layer(['words'])
        sentence_tokenizer.tag( text )
        # Collect results 
        sentence_texts = \
            [sentence.enclosing_text for sentence in text['sentences']]
        #print(sentence_texts)
        # Check results
        assert sentence_texts == test_text['expected_sentence_texts']


def test_merge_mistakenly_split_sentences_4():
    # Tests that mistakenly split sentences have been properly merged
    # 4: splits related to compound tokens
    #    Actually, these cases are throughly tested in test_compound_token_tagger.py,
    #    so here, there are only few test cases
    test_texts = [ 
        # No sentence break inside abbreviation 'P.S.'
        { 'text': 'P.S. Ootan! Kes julgeb tulla abiks siia mulle.', \
          'expected_sentence_texts': ['P.S. Ootan!', 'Kes julgeb tulla abiks siia mulle.'] }, \
        { 'text': 'Ehk lepime kokku, et see on kurb.\nP.S. Olen valmis sinuga Elu24 lugusid näiteks nädal aega lugema.', \
          'expected_sentence_texts': ['Ehk lepime kokku, et see on kurb.', 'P.S. Olen valmis sinuga Elu24 lugusid näiteks nädal aega lugema.'] }, \
        # No sentence break after month abbreviation
        { 'text': "Laululahingu esimesest poolfinaalist pääses edasi HaleBopp Singers!\n27.apr.2008\n", \
          'expected_sentence_texts': ['Laululahingu esimesest poolfinaalist pääses edasi HaleBopp Singers!', '27.apr.2008'] }, \
        # No sentence break after: 'nr', 'lk', ...
        { 'text': "Hõimurahvaste Aeg Nr. 7 lk. 22.\n", \
          'expected_sentence_texts': ['Hõimurahvaste Aeg Nr. 7 lk. 22.'] }, \
        { 'text': "1991 aasta väljaandes lk. 19-23.\n", \
          'expected_sentence_texts': ['1991 aasta väljaandes lk. 19-23.'] }, \
        # No sentence break inside short www address :
        { 'text': "Portaal e-treening.ee on mõeldud kajastama Eesti rahvasporti. Mida teenusesse WordPress.com üleminekust oodata?", \
          'expected_sentence_texts': ['Portaal e-treening.ee on mõeldud kajastama Eesti rahvasporti.', 'Mida teenusesse WordPress.com üleminekust oodata?'] }, \
        # No sentence break after abbreviations: 'e.', 't.', 'n.n.', 'jne.' ...
        # e.
        { 'text': "Taimetoitlus e. vegetaarlus e. vegetarism", \
          'expected_sentence_texts': ['Taimetoitlus e. vegetaarlus e. vegetarism'] }, \
        { 'text': "Vt ka tomatillo e. mehhiko füüsal ja maasikfüüsal.", \
          'expected_sentence_texts': ['Vt ka tomatillo e. mehhiko füüsal ja maasikfüüsal.'] }, \
        # t.
        { 'text': "Ülekäigukoht on kulgenud piki kõrgemaid seljandikke või saari Laia - Vene t. joonel.", \
          'expected_sentence_texts': ['Ülekäigukoht on kulgenud piki kõrgemaid seljandikke või saari Laia - Vene t. joonel.'] }, \
        # t., a.
        { 'text': "1926. a. valmis raudbetoonsild (Vabaduse sild) üle Emajõe Laia - Vene t. joonel, põlenud puusilla kohal.", \
          'expected_sentence_texts': ['1926. a. valmis raudbetoonsild (Vabaduse sild) üle Emajõe Laia - Vene t. joonel, põlenud puusilla kohal.'] }, \
        # ca., sh.
        { 'text': 'Üle poole eesti lugudest ja ca. pool kogumikust üldse (sh. jutuvõistluse esikümne tagumine ots) oli omaaegse "Jutulabori" ja "Marduste" kehvema poole tase.', \
          'expected_sentence_texts': ['Üle poole eesti lugudest ja ca. pool kogumikust üldse (sh. jutuvõistluse esikümne tagumine ots) oli omaaegse "Jutulabori" ja "Marduste" kehvema poole tase.'] }, \
        # n.n.
        { 'text': "Ja pole ka siin näinud n.n. eestlastest soome proffe.", \
          'expected_sentence_texts': ['Ja pole ka siin näinud n.n. eestlastest soome proffe.'] }, \
        # jm.
        { 'text': "“Tundlikkus”, “paindlikkus” jm. emotsionaalse sisekeskkonna regulaatorid.", \
          'expected_sentence_texts': ['“Tundlikkus”, “paindlikkus” jm. emotsionaalse sisekeskkonna regulaatorid.'] }, \
        { 'text': "Kussjuures ilusti ka ära seletati see ja jooniste, tabelite jm. selgeks tehti.", \
          'expected_sentence_texts': ["Kussjuures ilusti ka ära seletati see ja jooniste, tabelite jm. selgeks tehti."] }, \
        # mh.
        { 'text': "Autor käsitleb mh. kõigi aegade müstikute kogemusi.", \
          'expected_sentence_texts': ["Autor käsitleb mh. kõigi aegade müstikute kogemusi."] }, \
        # jms.
        { 'text': "Peab ju uued telekad, tellid, läpparid jms. ostma!", \
          'expected_sentence_texts': ["Peab ju uued telekad, tellid, läpparid jms. ostma!"] }, \
        # P.S., jms.
        { 'text': "P.S. Kultuuri ja hariduse jms. vastu ei ole mul midagi või silmaringi laiendamise vastu.", \
          'expected_sentence_texts': ["P.S. Kultuuri ja hariduse jms. vastu ei ole mul midagi või silmaringi laiendamise vastu."] }, \
        # jne.
        { 'text': "Eesti oludes tähendaks see , et oleks Tallinna , Tartu , Pärnu , Narva jne. ülikool .", \
          'expected_sentence_texts': ["Eesti oludes tähendaks see , et oleks Tallinna , Tartu , Pärnu , Narva jne. ülikool ."] }, \
        { 'text': "Seega arvatavasti palju vastuväiteid jne. kogu protsessis.", \
          'expected_sentence_texts': ["Seega arvatavasti palju vastuväiteid jne. kogu protsessis."] }, \
        { 'text': "Vaadake Euroopa Liidu võrdluses jne.jne. Kõik on, aga DIALOOGI ei ole!", \
          'expected_sentence_texts': ["Vaadake Euroopa Liidu võrdluses jne.jne.", "Kõik on, aga DIALOOGI ei ole!"] }, \
        # jpm., jpt.
        { 'text': "Etnograafiat, geograafiat, murdeid, soome-ugri keeli, filosoofiat jpt. teadusharusid.", \
          'expected_sentence_texts': ["Etnograafiat, geograafiat, murdeid, soome-ugri keeli, filosoofiat jpt. teadusharusid."] }, \
        { 'text': "Maitsestatakse piprasegude , mee , sinepi , sojakastme jpm. hõrgutavate maitseainete ja lisanditega .", \
          'expected_sentence_texts': ["Maitsestatakse piprasegude , mee , sinepi , sojakastme jpm. hõrgutavate maitseainete ja lisanditega ."] }, \
        # jt.      ( Merge case:   {abbreviation} {period} + {comma_or_semicolon} )
        { 'text': 'Mitmete uuringutega on leitud, et Trifluralin võib olla genotoksiline (Ribas jt., 1995; Gebel jt., 1997; Kaya jt., 2004) ning mõjutada paljunemis- ja ainevahetushormoone (Rawlings jt., 1998).', \
          'expected_sentence_texts': ['Mitmete uuringutega on leitud, et Trifluralin võib olla genotoksiline (Ribas jt., 1995; Gebel jt., 1997; Kaya jt., 2004) ning mõjutada paljunemis- ja ainevahetushormoone (Rawlings jt., 1998).'] }, \
        # mnt., pst.
        { 'text': "Pärnu-Tori mnt. km 6,14-6,54 . No Vabaduse pst. l on juba pikemat aega 2 rea asemel poolteist rida ;(", \
          'expected_sentence_texts': ["Pärnu-Tori mnt. km 6,14-6,54 .", 'No Vabaduse pst. l on juba pikemat aega 2 rea asemel poolteist rida ;('] }, \
        # tbl.
        { 'text': "Esialgu kirjutas 1/2 L-Tyroxini, hiljem 1 tbl. päevas.", \
          'expected_sentence_texts': ["Esialgu kirjutas 1/2 L-Tyroxini, hiljem 1 tbl. päevas."] }, \
        # vms., vmt.
        { 'text': "Aeg-ajalt on vaja mõnda firmat vms. uurida lähemalt... Ja kuidas need klassid vms. on.", \
          'expected_sentence_texts': ["Aeg-ajalt on vaja mõnda firmat vms. uurida lähemalt...", 'Ja kuidas need klassid vms. on.'] }, \
        # ingl. 
        { 'text': "“ Marvellous , marvellous !\n( Imeline - ingl. k. ) , ” kordas hertsog lauluviisi lõppedes ja plaksutas .", \
          'expected_sentence_texts': ["“ Marvellous , marvellous !", "( Imeline - ingl. k. ) , ” kordas hertsog lauluviisi lõppedes ja plaksutas ."] }, \
        # näit.
        { 'text': "Kas see tähendab, et valimised peaks toimuma näit. iga kuu?", \
          'expected_sentence_texts': ["Kas see tähendab, et valimised peaks toimuma näit. iga kuu?"] }, \
        { 'text': "Mõlemad võivad aga toimuda ka erinevatel aegadel nagu näit. ost /kauba/ kohale saatmisega / Versendungskauf / .", \
          'expected_sentence_texts': ["Mõlemad võivad aga toimuda ka erinevatel aegadel nagu näit. ost /kauba/ kohale saatmisega / Versendungskauf / ."] }, \

    ]
    for test_text in test_texts:
        text = Text( test_text['text'] )
        # Perform analysis
        text.tag_layer(['words', 'sentences'])
        # Collect results 
        sentence_texts = \
            [sentence.enclosing_text for sentence in text['sentences']]
        #print(sentence_texts)
        # Check results
        assert sentence_texts == test_text['expected_sentence_texts']


def test_merge_mistakenly_split_sentences_5():
    # Tests that mistakenly split sentences have been properly merged
    # 5: splits related to initials of names
    test_texts = [ 
        #   {uppercase_letter} {period} + {not_uppercase_followed_by_lowercase}
        { 'text': "Seriaalid “ Salmonid ” ja “ V.E.R.I ”", \
          'expected_sentence_texts': ["Seriaalid “ Salmonid ” ja “ V.E.R.I ”"] }, \
        { 'text': "Usun , et esitada võiks seda J.M.K.E. ja Villu Tamme .", \
          'expected_sentence_texts': ["Usun , et esitada võiks seda J.M.K.E. ja Villu Tamme ."] }, \
        { 'text': "Mängin 36 auguga (tavaliselt kulgeb mäng läbi 18 augu – K. A.).", \
          'expected_sentence_texts': ["Mängin 36 auguga (tavaliselt kulgeb mäng läbi 18 augu – K. A.)."] }, \
        { 'text': "« Homme ( täna\nA. K. ) lähen jälle .\nAga lihtsama laulu laulsin ära , »", \
          'expected_sentence_texts': ["« Homme ( täna\nA. K. ) lähen jälle .", "Aga lihtsama laulu laulsin ära , »"] }, \
        { 'text': 'Mõlemad kogenud mängumehed loodavad , et meeskond suudab veel A. le Coqile vastu hakata .', \
          'expected_sentence_texts': ["Mõlemad kogenud mängumehed loodavad , et meeskond suudab veel A. le Coqile vastu hakata ."] }, \
        { 'text': "„Seis on segane ja peaks selgemaks saama homseks-ülehomseks (tänaseks-homseks – A. S.).”", \
          'expected_sentence_texts': ["„Seis on segane ja peaks selgemaks saama homseks-ülehomseks (tänaseks-homseks – A. S.).”"] }, \
        { 'text': "“K. C. seal härrasmehe nime ees tähendab Kadri’s Choise,” selgitab selle täku välja valinud Kadri.", \
          'expected_sentence_texts': ["“K. C. seal härrasmehe nime ees tähendab Kadri’s Choise,” selgitab selle täku välja valinud Kadri."] }, \
        { 'text': 'Jätkustsenaariumiga (ehk siis liberaalse "õhukese riigi poliitika" jätkumisega - J.K.) seotud oht', \
          'expected_sentence_texts': ['Jätkustsenaariumiga (ehk siis liberaalse "õhukese riigi poliitika" jätkumisega - J.K.) seotud oht'] }, \
        { 'text': "Curtis Hansoni “ L.A. räpased saladused ” korruptsioonist 1950. aastatel oli just sobiv näide.", \
          'expected_sentence_texts': ["Curtis Hansoni “ L.A. räpased saladused ” korruptsioonist 1950. aastatel oli just sobiv näide."] }, \
        { 'text': "E . V . sai tagasi tema isalt õigusvastaselt võõrandatud elamu , kuid tal on probleeme isale kuulunud krundi tagasisaamisega .", \
          'expected_sentence_texts': ["E . V . sai tagasi tema isalt õigusvastaselt võõrandatud elamu , kuid tal on probleeme isale kuulunud krundi tagasisaamisega ."] }, \
        { 'text': "Segaduse rahvusvaheliste maksetega põhjustas kinnijooksnud maksekorralduste programmi S.W.I.F.T. sõnumite edastamise programm MERVA .", \
          'expected_sentence_texts': ["Segaduse rahvusvaheliste maksetega põhjustas kinnijooksnud maksekorralduste programmi S.W.I.F.T. sõnumite edastamise programm MERVA ."] }, \
        { 'text': 'Möödunud advendiajast saati teenib Eesti Evangeeliumi Luteriusu Kiriku (E.E.L.K.) Toronto Peetri koguduses senine Eesti Kirikute Nõukogu täitevsekretär.', \
          'expected_sentence_texts': ['Möödunud advendiajast saati teenib Eesti Evangeeliumi Luteriusu Kiriku (E.E.L.K.) Toronto Peetri koguduses senine Eesti Kirikute Nõukogu täitevsekretär.'] }, \
        { 'text': "Selline tugev pomm näitas ka Jabulani (peatselt algava MMi ametlik pall — P.L.) võlusid, pall lendas kuidagi väga imelikult ja füüsikaseaduste vastaselt.", \
          'expected_sentence_texts': ["Selline tugev pomm näitas ka Jabulani (peatselt algava MMi ametlik pall — P.L.) võlusid, pall lendas kuidagi väga imelikult ja füüsikaseaduste vastaselt."] }, \

        { 'text': "siin kommentaariumis ongi läbilõige 00nia ühiskonnast. M.O.T.T. igaüks sikutab vankrit enda poole", \
          'expected_sentence_texts': ["siin kommentaariumis ongi läbilõige 00nia ühiskonnast.", "M.O.T.T. igaüks sikutab vankrit enda poole"] }, \
        { 'text': "Lisaks sellele valiti nominentide hulgast välja neli edukat turismiobjekti/ projekti, milleks said Vanaõue Puhkekeskus, Otepää Golf, Kalevipoja Uisumaraton ja MTÜ R.A.A.A.M. teatrietendused Suurel Munamäel", \
          'expected_sentence_texts': ["Lisaks sellele valiti nominentide hulgast välja neli edukat turismiobjekti/ projekti, milleks said Vanaõue Puhkekeskus, Otepää Golf, Kalevipoja Uisumaraton ja MTÜ R.A.A.A.M. teatrietendused Suurel Munamäel"] }, \

        { 'text': "Selle seltsi mainekamate uurijatena tuleb nimetada G. Adelheimi, O. M. von Stackelbergi ja E. von Notbecki.", \
          'expected_sentence_texts': ["Selle seltsi mainekamate uurijatena tuleb nimetada G. Adelheimi, O. M. von Stackelbergi ja E. von Notbecki."] }, \

    ]
    for test_text in test_texts:
        text = Text( test_text['text'] )
        # Perform analysis
        text.tag_layer(['words', 'sentences'])
        # Collect results 
        sentence_texts = \
            [sentence.enclosing_text for sentence in text['sentences']]
        #print(sentence_texts)
        # Check results
        assert sentence_texts == test_text['expected_sentence_texts']


def test_split_mistakenly_merged_sentences_1():
    # Tests that mistakenly merged sentences are properly split
    # 1: merges related to missing whitespace between words and punctuation
    test_texts = [ 
        { 'text': 'Kas on ikka niipalju vaja ?Ei ole ju .', \
          'expected_sentence_texts': ['Kas on ikka niipalju vaja ?', 'Ei ole ju .'] }, \
        { 'text': 'Totaalne ülemõtlemine!Ei julge ka väita, et oleks kuivaks jäänud:)', \
          'expected_sentence_texts': ['Totaalne ülemõtlemine!', 'Ei julge ka väita, et oleks kuivaks jäänud:)'] }, \
        { 'text': 'milles üldse seisneb selle ravimi toime?Mida ta teeb ja kuidas/kuhu toimib?Mis juhtub kui ma võtaksin alkoholi?', \
          'expected_sentence_texts': ['milles üldse seisneb selle ravimi toime?', 'Mida ta teeb ja kuidas/kuhu toimib?', 'Mis juhtub kui ma võtaksin alkoholi?'] }, \
        { 'text': 'Iga päev teeme valikuid.Valime kõike alates pesupulbrist ja lõpetades autopesulatega.Jah, iga päev teeme valikuid.', \
          'expected_sentence_texts': ['Iga päev teeme valikuid.', 'Valime kõike alates pesupulbrist ja lõpetades autopesulatega.', 'Jah, iga päev teeme valikuid.'] }, \
    ]
    for test_text in test_texts:
        text = Text( test_text['text'] )
        # Perform analysis
        text.tag_layer(['words', 'sentences'])
        # Collect results 
        sentence_texts = \
            [sentence.enclosing_text for sentence in text['sentences']]
        #print(sentence_texts)
        # Check results
        assert sentence_texts == test_text['expected_sentence_texts']


def test_use_emoticons_as_sentence_endings():
    # Tests that emoticons are used as sentence boundaries
    test_texts = [ 
        # Emoticons as sentence boundaries: a simple case
        { 'text': 'Minu esimene blogi.... kõlab hästi:P Aga tegelikult on paberile vist parem kirjutada....', \
          'expected_sentence_texts': ['Minu esimene blogi.... kõlab hästi:P', \
                                      'Aga tegelikult on paberile vist parem kirjutada....'] }, \
        { 'text': 'Nii habras, ilus ja minu oma :) Kõige parem mis kunagi juhtuda saab :):) Magamata öid mul muidugi ei olnud.', \
          'expected_sentence_texts': ['Nii habras, ilus ja minu oma :)', \
                                      'Kõige parem mis kunagi juhtuda saab :):)',\
                                      'Magamata öid mul muidugi ei olnud.'] }, \
        { 'text': 'Aga lihtsalt puid läheb 10 korda vähem :D Nii lihtne see ongi :D!!', \
          'expected_sentence_texts': ['Aga lihtsalt puid läheb 10 korda vähem :D', \
                                      'Nii lihtne see ongi :D!!'] }, \
        { 'text': 'Mosse M2140 on ka ägedam masin kui see bemm :DD Nõsutun siin eelpoolkommenteerijaga', \
          'expected_sentence_texts': ['Mosse M2140 on ka ägedam masin kui see bemm :DD', \
                                      'Nõsutun siin eelpoolkommenteerijaga'] }, \
        { 'text': 'Dataprojektorit peeti ilmselt silmas, usun :-) See selleks.', \
          'expected_sentence_texts': ['Dataprojektorit peeti ilmselt silmas, usun :-)', \
                                      'See selleks.'] }, \
        { 'text': 'Linalakast eesti talutütar:P Ausõna, nagu meigitud Raja Teele :D', \
          'expected_sentence_texts': ['Linalakast eesti talutütar:P', \
                                      'Ausõna, nagu meigitud Raja Teele :D'] }, \
        # Emoticons as sentence boundaries: a case of repeated emoticons
        { 'text': 'KUUSKÜMMEND KOLM KÕRVITSAT???? :O :O :O See on ju iga koka õudusunenägu :)', \
          'expected_sentence_texts': ['KUUSKÜMMEND KOLM KÕRVITSAT???? :O :O :O', \
                                      'See on ju iga koka õudusunenägu :)'] }, \
        { 'text': 'ikkagi maailmas 2. koht joogipaneku poolest ju.. :D:D:D', \
          'expected_sentence_texts': ['ikkagi maailmas 2. koht joogipaneku poolest ju.. :D:D:D'] }, \
        # Emoticons as sentence boundaries: a case of emoticons following sentence punctuation
        { 'text': 'Appi milline loll jutt... :D Ma ei joo eini', \
          'expected_sentence_texts': ['Appi milline loll jutt... :D', 'Ma ei joo eini'] }, \
        # Emoticons as sentence boundaries: if emoticons are following sentence-ending punctuation,
        # then assume they need to be attached to the previous sentence ...
        { 'text': 'Ma sihin rohkem neid sügismaratone! :D Aga muidu ma julgen Riiat soovitada küll!!!', \
          'expected_sentence_texts': ['Ma sihin rohkem neid sügismaratone! :D', 'Aga muidu ma julgen Riiat soovitada küll!!!'] }, \
        { 'text': 'Oled sa armunud praegu? :) Kui ei siis oli arvatavasti auravärv siiski.', \
          'expected_sentence_texts': ['Oled sa armunud praegu? :)', 'Kui ei siis oli arvatavasti auravärv siiski.'] }, \
        { 'text': 'ka tema ei tea sõnade pool ja pooled tähendust . :( Ehk on see siiski taas D e lfi kirjatsura vaimusünnitis.', \
          'expected_sentence_texts': ['ka tema ei tea sõnade pool ja pooled tähendust . :(', 'Ehk on see siiski taas D e lfi kirjatsura vaimusünnitis.'] }, \
        { 'text': 'aga las läks oma teed,nagunii august poleks läbi mahtunud. :))) Vot sääne äge päiva.\nMis asi see pumm pumm veel on?', \
          'expected_sentence_texts': ['aga las läks oma teed,nagunii august poleks läbi mahtunud. :)))', 'Vot sääne äge päiva.', 'Mis asi see pumm pumm veel on?'] }, \
    ]
    sentence_tokenizer = SentenceTokenizer(use_emoticons_as_endings=True)
    for test_text in test_texts:
        text = Text( test_text['text'] )
        # Perform analysis
        text.tag_layer(['words'])
        sentence_tokenizer.tag(text)
        # Collect results 
        sentence_texts = \
            [sentence.enclosing_text for sentence in text['sentences']]
        #print(sentence_texts)
        # Check results
        assert sentence_texts == test_text['expected_sentence_texts']



def test_use_double_newline_as_sentence_endings():
    # Tests that double newlines (paragraph endings) are used as sentence endings
    test_texts = [ 
        { 'text': 'Võrdluseks siiski ka kolmapäevased ajad :\n\n'+\
                  '1 Panis McLaren 1.24.838\n\n'+\
                  '2 Trulli Jordan 1.25.411\n\n'+\
                  '3 Alesi Prost 1.26.673\n\n'+\
                  '4 Button Williams 1.27.197\n\n'+\
                  '5 Burti Jaguar 1.27.818\n\n',\
          'expected_sentence_texts': ['Võrdluseks siiski ka kolmapäevased ajad :', \
                                      '1 Panis McLaren 1.24.838',\
                                      '2 Trulli Jordan 1.25.411',
                                      '3 Alesi Prost 1.26.673',\
                                      '4 Button Williams 1.27.197',\
                                      '5 Burti Jaguar 1.27.818'] }, \
        { 'text': 'Tänased tulemused :\n\n'+\
                  'New Jersey - Portland 82 : 94\n\n'+\
                  'Los Angeles Clippers - Dallas 76 : 90\n\n'+\
                  'Tabel :\n\n'+\
                  'Idakonverents\n\n'+\
                  'Atlandi divisjon\n\n'+\
                  'PHILADELPHIA 7 0 1.000 -\n\n'+\
                  'NEW YORK 5 2 .\n',\
          'expected_sentence_texts': ['Tänased tulemused :', \
                                      'New Jersey - Portland 82 : 94',\
                                      'Los Angeles Clippers - Dallas 76 : 90',
                                      'Tabel :',\
                                      'Idakonverents',\
                                      'Atlandi divisjon',\
                                      'PHILADELPHIA 7 0 1.000 -',\
                                      'NEW YORK 5 2 .'] }, \
        { 'text': 'Põgenemise kronoloogia\n\n'+\
                  'REEDE\n\n'+\
                  '17.40 Viljandist arestimajast väljub politseiauto Ülo Voitkaga\n\n'+\
                  '17.47 Tallinna lennuväljalt stardib helikopter Aivar Voitkaga\n\n'+\
                  '18.15 Voitkad jõuavad kodutallu , nad aheldatakse käeraudadega kokku\n\n'+\
                  '18.20 Sauna eesruumis algab ülekuulamine , rahvaloendaja ootab oma järjekorda\n\n'+\
                  '18.32 Ülo kaebab kõhuvalu ja palub tualetti\n\n'+\
                  '18.41 Käeraudadega kokku aheldatud vennad lähevad välikemmergusse .',\
          'expected_sentence_texts': ['Põgenemise kronoloogia', \
                                      'REEDE',\
                                      '17.40 Viljandist arestimajast väljub politseiauto Ülo Voitkaga',
                                      '17.47 Tallinna lennuväljalt stardib helikopter Aivar Voitkaga',\
                                      '18.15 Voitkad jõuavad kodutallu , nad aheldatakse käeraudadega kokku',\
                                      '18.20 Sauna eesruumis algab ülekuulamine , rahvaloendaja ootab oma järjekorda',\
                                      '18.32 Ülo kaebab kõhuvalu ja palub tualetti',\
                                      '18.41 Käeraudadega kokku aheldatud vennad lähevad välikemmergusse .'] }, \
        { 'text': 'Espanyol - Real Valladolid 1 : 0 ( Raul Tamudo 80 ) , 17 000\n\n'+\
                  'Numancia - Barcelona 1 : 1 ( Ruben Navarro 63 - Patrick Kluivert 32 ) , 10 000\n\n'+\
                  'Osasuna - Malaga 3 : 3 ( Alex Fernandez 35 , Leonel Gancedo 69 , Ivan Rosado 75 - Francisco Rufete 22 , Dely Valdes 33 , Ariel Zarate 90 ) , 15 000\n\n'+\
                  'Rayo Vallecano - Real Oviedo 0 : 2 ( Frederic Danjou 5 , Oli 65 ) , 11 000\n\n'+\
                  'Real Mallorca - Real Madrid 1 : 0 ( Alberto Luque 39 ) , 23 000\n\n'+\
                  'Real Sociedad - Alaves 1 : 1 ( Oscar de Paula 42 - Cosmin Contra 59 ) , 30 000\n\n'+\
                  'Real Zaragoza - Athletic Bilbao 2 : 2 ( Jamelli 19 , Juan Eduardo Esnaider 29 - Tiko 23 , Ismael Urzaiz 74 ) , 21 000\n\n'+\
                  'Villarreal - Racing Santander 4 : 2 ( Diego Cagna 11 , Jorge Lopez 39 , Martin Palermo 54 , Gica Craioveanu 75 - Federico Magallanes 76 , Javier Mazzoni 90 ) , 16 000',\
          'expected_sentence_texts': ['Espanyol - Real Valladolid 1 : 0 ( Raul Tamudo 80 ) , 17 000', \
                                      'Numancia - Barcelona 1 : 1 ( Ruben Navarro 63 - Patrick Kluivert 32 ) , 10 000',\
                                      'Osasuna - Malaga 3 : 3 ( Alex Fernandez 35 , Leonel Gancedo 69 , Ivan Rosado 75 - Francisco Rufete 22 , Dely Valdes 33 , Ariel Zarate 90 ) , 15 000',
                                      'Rayo Vallecano - Real Oviedo 0 : 2 ( Frederic Danjou 5 , Oli 65 ) , 11 000',\
                                      'Real Mallorca - Real Madrid 1 : 0 ( Alberto Luque 39 ) , 23 000',\
                                      'Real Sociedad - Alaves 1 : 1 ( Oscar de Paula 42 - Cosmin Contra 59 ) , 30 000',\
                                      'Real Zaragoza - Athletic Bilbao 2 : 2 ( Jamelli 19 , Juan Eduardo Esnaider 29 - Tiko 23 , Ismael Urzaiz 74 ) , 21 000',\
                                      'Villarreal - Racing Santander 4 : 2 ( Diego Cagna 11 , Jorge Lopez 39 , Martin Palermo 54 , Gica Craioveanu 75 - Federico Magallanes 76 , Javier Mazzoni 90 ) , 16 000'] }, \
        { 'text': '\n\n22.09.2008 17:10\n\n'+\
                  '#9\n\n'+\
                  'Miisu Kiisu\n\n'+\
                  'Registreerus: -\n\n'+\
                  'Postitusi: -\n\n'+\
                  'Ma ei tea kas olen loll aga pole kuulnudki sellisest asjast ...\n\n',\
          'expected_sentence_texts': ['22.09.2008 17:10', \
                                      '#9',\
                                      'Miisu Kiisu',
                                      'Registreerus: -',\
                                      'Postitusi: -',\
                                      'Ma ei tea kas olen loll aga pole kuulnudki sellisest asjast ...'] }, \
        { 'text': 'Telkimisvõimalus\n\n'+\
                  'ei ole\n\n'+\
                  'Kattega lõkkekoht\n\n'+\
                  'ei ole\n\n'+\
                  'Vaatamisväärsused\n\n'+\
                  'Rada kulgeb algul piki Valgejõe ja selle harujõgede orgude kõrgeil kaldail Vasaristi joastikuni, siis mööda vanu külateid Pärlijõe oruni, sealt üle jõe ja piki orunõlva läbi noorte männimetsade Viru rabani.',\
          'expected_sentence_texts': ['Telkimisvõimalus', \
                                      'ei ole',\
                                      'Kattega lõkkekoht',
                                      'ei ole',\
                                      'Vaatamisväärsused',\
                                      'Rada kulgeb algul piki Valgejõe ja selle harujõgede orgude kõrgeil kaldail Vasaristi joastikuni, siis mööda vanu külateid Pärlijõe oruni, sealt üle jõe ja piki orunõlva läbi noorte männimetsade Viru rabani.'] }, \
    ]
    sentence_tokenizer = SentenceTokenizer(fix_paragraph_endings=True)
    for test_text in test_texts:
        text = Text( test_text['text'] )
        # Perform analysis
        text.tag_layer(['words'])
        sentence_tokenizer.tag(text)
        # Collect results 
        sentence_texts = \
            [sentence.enclosing_text for sentence in text['sentences']]
        #print(sentence_texts)
        # Check results
        assert sentence_texts == test_text['expected_sentence_texts']



def test_fix_repeated_sentence_ending_punctuation_1():
    # Tests that mistakenly separated sentence ending punctuation will be properly attached to the sentence
    test_texts = [
        #   Merge case:   {sentence_ending_punct} + {only_sentence_ending_punct}
        { 'text': 'SEE EI OLNUD TSIKLI ÕLI ! ! ! ! ! ! !', \
          'expected_sentence_texts': ['SEE EI OLNUD TSIKLI ÕLI ! ! ! ! ! ! !'] }, \
        { 'text': 'see on kindel meteroloogiline fakt\n. .\n!', \
          'expected_sentence_texts': ['see on kindel meteroloogiline fakt\n. .\n!'] }, \
        { 'text': 'Issand Jumal , Sa näed ja ei mürista ! ! ! ? ? ?', \
          'expected_sentence_texts': ['Issand Jumal , Sa näed ja ei mürista ! ! ! ? ? ?'] }, \
        { 'text': 'Aga äkki ongi nümfomaanid reaalselt olemas ? ? ?', \
          'expected_sentence_texts': ['Aga äkki ongi nümfomaanid reaalselt olemas ? ? ?'] }, \
        { 'text': "loodetavasti läheb KE jaoks üle… Jeez… lahe..…", \
          'expected_sentence_texts': ['loodetavasti läheb KE jaoks üle…', 'Jeez… lahe..…'] }, \
        { 'text': 'arvati , et veel sellel aastal j6uab kohale ; yess ! ! !', \
          'expected_sentence_texts': ['arvati , et veel sellel aastal j6uab kohale ; yess ! ! !'] }, \
        { 'text': 'müüks ära sellise riista nagu IZ- Planeta 5 ! ?\nEtte tänades aivar .', \
          'expected_sentence_texts': ['müüks ära sellise riista nagu IZ- Planeta 5 ! ?', 'Ette tänades aivar .'] }, \
        { 'text': 'teine võimalus: elektrikud saavad karistatud voolu läbi.!!!!!!!!!!! !\n', \
          'expected_sentence_texts': ['teine võimalus: elektrikud saavad karistatud voolu läbi.!!!!!!!!!!! !'] }, \
        { 'text': 'Mis ajast Odüsseus ja Caesar KESKAJAL elasid ? ! ?\nOlex võinud väiksest peast vähe rohkem antiikmütoloogiat lugeda.', \
          'expected_sentence_texts': ['Mis ajast Odüsseus ja Caesar KESKAJAL elasid ? ! ?', 'Olex võinud väiksest peast vähe rohkem antiikmütoloogiat lugeda.'] }, \
        { 'text': 'Kiirusta ja osta kohe , kui sul veel pole ! !\nKvaliteettoodang !', \
          'expected_sentence_texts': ['Kiirusta ja osta kohe , kui sul veel pole ! !', 'Kvaliteettoodang !'] }, \
        { 'text': 'Seaduse täitmist reguleerib meil esmaselt siiski politsei. . . Ja ma ei loe kuskilt välja teemast et sa oled üritanud temaga vestelda.', \
          'expected_sentence_texts': ['Seaduse täitmist reguleerib meil esmaselt siiski politsei. . .', 'Ja ma ei loe kuskilt välja teemast et sa oled üritanud temaga vestelda.'] }, \
        { 'text': 'See oli meenutus tänastest eelmistest aaretest. Mari . . aarde leidsime, logisime ja peitsime tagasi.', \
          'expected_sentence_texts': ['See oli meenutus tänastest eelmistest aaretest.', 'Mari . .', 'aarde leidsime, logisime ja peitsime tagasi.'] }, \
        { 'text': 'grafiit määrdega tald muutub kuivaks\n? ? . . kuidas sellest = aru saada kui see nii on ?', \
          'expected_sentence_texts': ['grafiit määrdega tald muutub kuivaks\n? ? . .', 'kuidas sellest = aru saada kui see nii on ?'] }, \
        { 'text': "Teha “ viimane suur rööv ” ( milline klišee . . .\n ! ! ) , ajada ligi 5 miljoni dollari väärtuses kalliskividele . . .", \
          'expected_sentence_texts': ['Teha “ viimane suur rööv ” ( milline klišee . . .\n ! ! ) , ajada ligi 5 miljoni dollari väärtuses kalliskividele . . .'] }, \

        #  NB! Problematic stuff:
        { 'text': 'Ja kui süda pole puhas... ??? ??? ??? aiai.', \
          'expected_sentence_texts': ['Ja kui süda pole puhas... ??? ??? ??? aiai.'] }, \
        { 'text': 'Seal on forum kust saab osta , müüa , vahetada , rääkida ja ...... !!\nkÕik sInna !', \
          'expected_sentence_texts': ['Seal on forum kust saab osta , müüa , vahetada , rääkida ja ...... !!\nkÕik sInna !'] }, \

    ]
    for test_text in test_texts:
        text = Text( test_text['text'] )
        # Perform analysis
        text.tag_layer(['words', 'sentences'])
        # Collect results 
        sentence_texts = \
            [sentence.enclosing_text for sentence in text['sentences']]
        #print(sentence_texts)
        # Check results
        assert sentence_texts == test_text['expected_sentence_texts']



def test_fix_repeated_sentence_ending_punctuation_2():
    # Tests that sentence endings are properly detected iff the ending punctuation is prolonged/repeated
    test_texts = [ 
        #  Split case: add a sentence boundary after repeated / prolonged punctuation
        { 'text': 'Hispaanias tuli suur isu vaadata töömeile… Ja nii ma seal puhkasin, kuid samas tegin tööd… See oli lihtsalt nii-nii mõnus feeling :)', \
          'expected_sentence_texts': ['Hispaanias tuli suur isu vaadata töömeile…', \
                                      'Ja nii ma seal puhkasin, kuid samas tegin tööd…', \
                                      'See oli lihtsalt nii-nii mõnus feeling :)' ] }, \
        { 'text': 'Sõin küll tavalisest rohkem..Koguaeg oli tunne, et olen rase.', \
          'expected_sentence_texts': ['Sõin küll tavalisest rohkem..', \
                                      'Koguaeg oli tunne, et olen rase.'] }, \
        { 'text': 'Kas tõesti ??????!!!! Äi usu!', \
          'expected_sentence_texts': ['Kas tõesti ??????!!!!', \
                                      'Äi usu!'] }, \
        { 'text': 'Ja ikka ei usu!!!!?????? Äi usu!', \
          'expected_sentence_texts': ['Ja ikka ei usu!!!!??????', \
                                      'Äi usu!'] }, \

        # Negative examples: repeated punctuation preceded by [, ( or " should not end the sentence
        { 'text': 'Siirad tänusõnad külastajatele ja [ ... ]', \
          'expected_sentence_texts': ['Siirad tänusõnad külastajatele ja [ ... ]'] }, \
        { 'text': 'Mind natuke häirib see , kuidas lugupeetud autor toob sisse fraasi - " ... kas see oleks valijate tahe ? "', \
          'expected_sentence_texts': ['Mind natuke häirib see , kuidas lugupeetud autor toob sisse fraasi - " ... kas see oleks valijate tahe ? "'] }, \
        { 'text': 'Tõtt öelda olin valmis kriitikaks nende pidevalt korduvate " ...eel " lõppude suhtes , aga huvitav - keegi pole nurisenud .', \
          'expected_sentence_texts': ['Tõtt öelda olin valmis kriitikaks nende pidevalt korduvate " ...eel " lõppude suhtes , aga huvitav - keegi pole nurisenud .'] }, \
    ]
    for test_text in test_texts:
        text = Text( test_text['text'] )
        # Perform analysis
        text.tag_layer(['words', 'sentences'])
        # Collect results 
        sentence_texts = \
            [sentence.enclosing_text for sentence in text['sentences']]
        #print(sentence_texts)
        # Check results
        assert sentence_texts == test_text['expected_sentence_texts']



def test_apply_sentence_tokenizer_on_empty_text():
    # Applying sentence tokenizer on empty text should not produce any errors
    text = Text( '' )
    text.tag_layer(['words', 'sentences'])
    assert len(text.words) == 0
    assert len(text.sentences) == 0



def test_record_fixes_of_sentence_tokenizer():
    # Tests whether an attribute describing the fixes is added to the results of sentence tokenization
    sentence_tokenizer = SentenceTokenizer(record_fix_types=True)
    test_texts = [ 
        { 'text': '17 . okt. 1998 a . laekus firmale täpselt 700.- eeku.', \
          'expected_sentence_texts': ['17 . okt. 1998 a . laekus firmale täpselt 700.- eeku.'],
          'expected_sentence_fixes': [['numeric_date', 'numeric_date', 'numeric_year', 'numeric_monetary']] }, \
        { 'text': 'Seda ma ei teadnud... Ja tegelikult ei saanudki teada ! !! ', \
          'expected_sentence_texts': ['Seda ma ei teadnud...', 'Ja tegelikult ei saanudki teada ! !!'],
          'expected_sentence_fixes': [[], ['repeated_ending_punct']] }, \
        { 'text': 'Herbes de Provence maitseainesegu\n\n'+\
                  'Teistes keeltes\n\n'+\
                  'English: herbes de Provence, Provençal herbs\n\n'+\
                  'French: herbes de Provence',\
          'expected_sentence_texts': ['Herbes de Provence maitseainesegu', 'Teistes keeltes', \
                                      'English: herbes de Provence, Provençal herbs' ,\
                                      'French: herbes de Provence'],
          'expected_sentence_fixes': [['double_newline_ending'], ['double_newline_ending'], \
                                      ['double_newline_ending'], []] }, \
    ]
    for test_text in test_texts:
        text = Text( test_text['text'] )
        # Perform analysis
        text.tag_layer(['words'])
        sentence_tokenizer.tag(text)
        # Collect results 
        sentence_texts = \
            [sentence.enclosing_text for sentence in text['sentences']]
        sentence_fixes = \
            [sentence.fix_types for sentence in text['sentences']]
        #print(sentence_texts)
        #print(sentence_fixes)
        # Check results
        assert sentence_texts == test_text['expected_sentence_texts']
        assert sentence_fixes == test_text['expected_sentence_fixes']



def test_sentence_tokenizer_with_custom_base_tokenizer():
    # Test that the base tokenizer of the sentence tokenizer can be customized
    from nltk.tokenize.simple import LineTokenizer
    sentence_tokenizer = SentenceTokenizer( base_sentence_tokenizer=LineTokenizer() )
    test_texts = [ 
        { 'text': 'See on tekst\nKus iga lause\nOn eraldi real.\nJa nii on.', \
          'expected_sentence_texts': ['See on tekst', \
                                      'Kus iga lause', \
                                      'On eraldi real.',\
                                      'Ja nii on.' ] }, \
    ]
    for test_text in test_texts:
        text = Text( test_text['text'] )
        # Perform analysis
        text.tag_layer(['words'])
        sentence_tokenizer.tag(text)
        # Collect results 
        sentence_texts = \
            [sentence.enclosing_text for sentence in text['sentences']]
        # Check results
        assert sentence_texts == test_text['expected_sentence_texts']



def test_merge_rules_do_not_conflict_paragraph_fixes():
    # Test that the merge rules do not conflict with paragraph fixes
    # ( paragraph fixes will have the highest priority: no merge rule 
    #   will be applied in places where two sentences have been separated 
    #   by paragraph markers )
    test_texts = [ 
        { 'text': 'ats\n\n'+\
                  'Seda te küll ei taha (aga kui siiski tahate, siis: jõudu!)\n\n'+\
                  'pets\n\n'+\
                  'Jah, jõudu tarvis!', \
          'expected_sentence_texts': ['ats', \
                                      'Seda te küll ei taha (aga kui siiski tahate, siis: jõudu!)', \
                                      'pets',\
                                      'Jah, jõudu tarvis!' ] }, \
    ]
    for test_text in test_texts:
        text = Text( test_text['text'] )
        # Perform analysis
        text.tag_layer(['words', 'sentences'])
        # Collect results 
        sentence_texts = \
            [sentence.enclosing_text for sentence in text['sentences']]
        # Check results
        assert sentence_texts == test_text['expected_sentence_texts']



def test_layer_names_can_be_changed():
    # Tests that names of input and output layers of SentenceTokenizer can be changed
    tokens_tagger = TokensTagger(output_layer='my_tokens')
    cp_tagger   = CompoundTokenTagger(output_layer='my_compounds', 
                                      input_tokens_layer='my_tokens')
    word_tagger = WordTagger(output_layer='my_words', 
                             input_tokens_layer='my_tokens', 
                             input_compound_tokens_layer='my_compounds')
    sentence_tokenizer = SentenceTokenizer(output_layer='my_sentences', 
                                           input_words_layer='my_words', 
                                           input_compound_tokens_layer='my_compounds')
    test_texts = [ 
        { 'text': 'Nii habras, ilus ja minu oma :) Kõige parem mis kunagi juhtuda saab :):) '+\
                  'Magamata öid mul muidugi ei olnud.', \
          'expected_sentence_texts': ['Nii habras, ilus ja minu oma :)', \
                                      'Kõige parem mis kunagi juhtuda saab :):)',\
                                      'Magamata öid mul muidugi ei olnud.'] }, \
        { 'text': 'CD müüdi 400 krooniga ( alghind oli 100 kr. ) .\nOsteti viis tööd , neist üks õlimaal .', \
          'expected_sentence_texts': ['CD müüdi 400 krooniga ( alghind oli 100 kr. ) .', \
                                      'Osteti viis tööd , neist üks õlimaal .'] }, \
        { 'text': 'Totaalne ülemõtlemine!Ei julge ka väita, et oleks kuivaks jäänud:) Mis?!', \
          'expected_sentence_texts': ['Totaalne ülemõtlemine!', 'Ei julge ka väita, et oleks kuivaks jäänud:)', \
                                      'Mis?!'] }, \
    ]
    for test_text in test_texts:
        text = Text( test_text['text'] )
        # Perform analysis
        tokens_tagger.tag(text)
        cp_tagger.tag(text)
        word_tagger.tag(text)
        sentence_tokenizer.tag(text)
        assert 'my_sentences' in text.layers
        assert 'sentences' not in text.layers
        # Collect results 
        sentence_texts = \
            [sentence.enclosing_text for sentence in text['my_sentences']]
        #print(sentence_texts)
        # Check results
        assert sentence_texts == test_text['expected_sentence_texts']



def test_make_sentences_template_layer():
    sentence_tokenizer = SentenceTokenizer()
    layer_template = sentence_tokenizer.get_layer_template()
    assert len(layer_template) == 0
    assert sentence_tokenizer.output_layer == layer_template.name
    assert sentence_tokenizer.output_attributes == layer_template.attributes



def test_sentence_tokenizer_with_custom_merge_patterns():
    # Example text
    example_str = 'Meie puuvarud: 3 rm. märgasid lepahalge sellest aastast, 4 rm. poolkuivasid '+\
                  'halge eelmisest aastast ning kuivi halge 2 rm. Kas sellest piisab?'
    # Case 1: broken sentence without post-correction
    text = Text(example_str)
    text.tag_layer(['sentences'])
    assert len(text.sentences) == 4
    
    # Case 2: fix broken sentence with a custom rule
    # Create a new post-correction
    rm_fix = \
    { 'comment'  : '{rm} {period} + {lowercase letter}', \
      'example'  : '"Meie puuvarud: 3 rm." + "märgasid lepahalge"', \
      'fix_type' : 'abbrev_common', \
      'regexes'  : [ re.compile(r'(.+)?\srm\s*\.$', re.DOTALL), \
                     re.compile(r'^([a-zöäüõžš])\s*(.*)?$', re.DOTALL)], \
    }
    # Update (copy of) default patterns with a new pattern
    new_merge_patterns = merge_patterns[:]
    new_merge_patterns.append( rm_fix )
    # Create a tokenzier that uses customized patterns
    custom_sentence_tokenizer = SentenceTokenizer( patterns = new_merge_patterns )
    text = Text( example_str )
    text.tag_layer(['words'])
    custom_sentence_tokenizer.tag( text )
    sentence_texts = \
        [sentence.enclosing_text for sentence in text['sentences']]
    expected_sentence_texts = \
        [ 'Meie puuvarud: 3 rm. märgasid lepahalge sellest aastast, 4 rm. poolkuivasid halge eelmisest aastast ning kuivi halge 2 rm.',
          'Kas sellest piisab?' ]
    assert sentence_texts == expected_sentence_texts

