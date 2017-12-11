from estnltk import Text
from estnltk.taggers.morf import VabamorfAnalyzer, VabamorfDisambiguator
from estnltk.taggers.morf import IGNORE_ATTR


def test_morph_disambiguation_with_ignore():
    # Tests that morphological disambiguator can be set to ignore some words
    # Case 1 : test ignoring random words ( do not try this at home! )
    text=Text('Mitmenda koha sai kohale jõudnud mees ?')
    text.tag_layer(['words','sentences'])
    analyzer = VabamorfAnalyzer(extra_attributes=[IGNORE_ATTR])
    analyzer.tag(text)
    mark_ignore = { (14,17) : [],  # sai
                    (33,37) : [],  # mees
                  }
    for spanlist in text.morph_analysis.spans:
        pos_key = (spanlist.start, spanlist.end)
        if pos_key in mark_ignore:
            # Record the pervious spanlist
            mark_ignore[pos_key] = spanlist
        for span in spanlist:
            if pos_key in mark_ignore:
                span._ignore = True
            else:
                span._ignore = False
    disambiguator = VabamorfDisambiguator()
    disambiguator.tag(text)
    # Assert that attribute IGNORE_ATTR has been removed 
    assert not hasattr(text.morph_analysis, IGNORE_ATTR)
    # Check that marked spans remain the same in the new layer
    for spanlist in text.morph_analysis.spans:
        pos_key = (spanlist.start, spanlist.end)
        if pos_key in mark_ignore:
            assert mark_ignore[pos_key] == spanlist

    # Case 2 : test ignoring emoticons
    text=Text('Maja on fantastiline, mõte on hea :-) Tuleme siis kolmeks :)')
    text.tag_layer(['words','sentences'])
    analyzer = VabamorfAnalyzer(extra_attributes=[IGNORE_ATTR])
    analyzer.tag(text)
    # ignore emoticons
    for spanlist in text.morph_analysis.spans:
        pos_key = (spanlist.start, spanlist.end)
        for ctid, comp_token in enumerate( text['compound_tokens'] ):
            if spanlist.start==comp_token.start and \
               spanlist.end==comp_token.end and \
               'emoticon' in comp_token.type:
                # Record location of the emoticon
                mark_ignore[pos_key] = spanlist
        for span in spanlist:
            if pos_key in mark_ignore:
                span._ignore = True
            else:
                span._ignore = False
    disambiguator = VabamorfDisambiguator()
    disambiguator.tag(text)
    # Assert that attribute IGNORE_ATTR has been removed 
    assert not hasattr(text.morph_analysis, IGNORE_ATTR)
    # Check that marked spans remain the same in the new layer
    for spanlist in text.morph_analysis.spans:
        pos_key = (spanlist.start, spanlist.end)
        if pos_key in mark_ignore:
            assert mark_ignore[pos_key] == spanlist


def test_morph_disambiguation_with_ignore_xml():
    # Case 1 : test ignoring xml tags inserted into text
    # TODO: find better example
    text=Text('<b>Jälle</b> <i>peeti</i> kinni mees, aga ta <br> naeris vaid!') 
    text.tag_layer(['words','sentences'])
    analyzer = VabamorfAnalyzer( extra_attributes=[IGNORE_ATTR] )
    analyzer.tag(text)
    #print(text['morph_analysis'].to_records())
    # ignore xml_tags
    mark_ignore = {}
    for spanlist in text.morph_analysis.spans:
        pos_key = (spanlist.start, spanlist.end)
        for ctid, comp_token in enumerate( text['compound_tokens'] ):
            if spanlist.start==comp_token.start and \
               spanlist.end==comp_token.end and \
               'xml_tag' in comp_token.type:
                # Record location of the emoticon
                mark_ignore[pos_key] = spanlist
        for span in spanlist:
            if pos_key in mark_ignore:
                span._ignore = True
            else:
                span._ignore = False
    disambiguator = VabamorfDisambiguator()
    disambiguator.tag(text)
    #print(text['morph_analysis'].to_records())
    # Assert that attribute IGNORE_ATTR has been removed 
    assert not hasattr(text.morph_analysis, IGNORE_ATTR)
    for spanlist in text.morph_analysis.spans:
        # assert that all words have been disambiguated
        assert len(spanlist) == 1
            
