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