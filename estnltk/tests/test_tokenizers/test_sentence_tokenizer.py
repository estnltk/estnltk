from estnltk.text import Text


def test_merge_mistakenly_split_sentences():
    # Tests that mistakenly split sentences have been properly merged
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

        #   Merge case:   {period_ending_content_of_brackets} + {lowercase_or_comma}
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

        #   Merge case:   {brackets_start} {content_in_brackets} + {lowercase_or_comma} {content_in_brackets} {brackets_end}
        { 'text': '( " Mis siis õieti tahetakse ? " , 1912 ) .', \
          'expected_sentence_texts': ['( " Mis siis õieti tahetakse ? " , 1912 ) .'] }, \
        { 'text': 'Kirjandusel ( resp. raamatul ) on läbi aegade olnud erinevaid funktsioone .', \
          'expected_sentence_texts': ['Kirjandusel ( resp. raamatul ) on läbi aegade olnud erinevaid funktsioone .'] }, \
        { 'text': 'Bisweed on alles 17aastane (loe: ta läheb sügisel 11. klassi!) ja juba on tema heliloomingut välja andnud mitmed plaadifirmad.', \
          'expected_sentence_texts': ['Bisweed on alles 17aastane (loe: ta läheb sügisel 11. klassi!) ja juba on tema heliloomingut välja andnud mitmed plaadifirmad.'] }, \
        { 'text': '( " Easy FM , soft hits ! " ) .', \
          'expected_sentence_texts': ['( " Easy FM , soft hits ! " ) .'] }, \
    ]
    for test_text in test_texts:
        text = Text( test_text['text'] )
        # Perform analysis
        text.tag_layer(['words', 'sentences'])
        # Collect results 
        sentence_texts = \
            [sentence.enclosing_text for sentence in text['sentences'].spans]
        #print(sentence_texts)
        # Make assertions
        assert sentence_texts == test_text['expected_sentence_texts']