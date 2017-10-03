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

        #   Merge case:   {Numeric_date} {period} + {month_name_long}
        { 'text': 'Järgarvud selgeks !\nLoomulikult algab uus aastatuhat 1 . jaanuaril 2001 .', \
          'expected_sentence_texts': ['Järgarvud selgeks !', 'Loomulikult algab uus aastatuhat 1 . jaanuaril 2001 .'] }, \
        { 'text': 'Kirijenko on sündinud 26 . juulil 1962 . aastal .\nTa on lõpetanud Gorki veetraspordiinseneride instituudi.', \
          'expected_sentence_texts': ['Kirijenko on sündinud 26 . juulil 1962 . aastal .', 'Ta on lõpetanud Gorki veetraspordiinseneride instituudi.'] }, \
        { 'text': 'Erastamisväärtpabereid aga saab kasutada kuni 1998 . aasta 31 . detsembrini .', \
          'expected_sentence_texts': ['Erastamisväärtpabereid aga saab kasutada kuni 1998 . aasta 31 . detsembrini .'] }, \
        { 'text': '1.–10. oktoobrini näeb erinevates Eesti teatrites väga head Vene teatrit.', \
          'expected_sentence_texts': ['1.–10. oktoobrini näeb erinevates Eesti teatrites väga head Vene teatrit.'] }, \
        { 'text': 'Aga selgust ei pruugi enne 15 . augustit tulla .', \
          'expected_sentence_texts': ['Aga selgust ei pruugi enne 15 . augustit tulla .'] }, \

        #   Merge case:   {Numeric_date} {period} + {month_name_short}
        { 'text': 'Riik on hoiatanud oma liitlasi ja partnereid äritegemise eest Teheraniga ( NYT , 5 . okt . ) .\n', \
          'expected_sentence_texts': ['Riik on hoiatanud oma liitlasi ja partnereid äritegemise eest Teheraniga ( NYT , 5 . okt . )', '.'] }, \
        { 'text': '" Ma ei tunne Laidoneri , " vastas Ake .\n5 . sept .', \
          'expected_sentence_texts': ['" Ma ei tunne Laidoneri , " vastas Ake .', '5 . sept .'] }, \

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