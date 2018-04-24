from estnltk import Text
from estnltk.taggers import TimexTagger


def test_timex_tagging_1():
    all_timex_attributes = ['text']+list(TimexTagger.attributes)
    #all_timex_attributes = list(TimexTagger.attributes)
    tagger = TimexTagger()

    test_data = [ {'text': 'Potsataja ütles eile, et vaatavad nüüd Genaga viie aasta plaanid uuesti üle.',\
                   'dct':'2014-10-05',\
                   'expected_timexes': [ \
                                 {'text':['eile'], 'enclosing_text': 'eile', 'tid':'t1', 'type':'DATE', 'value':'2014-10-04', 'temporal_function':True , 'anchor_time_id':'t0'}, \
                                 {'text':['nüüd'],'tid':'t2', 'type':'DATE', 'value':'PRESENT_REF', 'temporal_function':True , 'anchor_time_id':'t0'},\
                                 {'text':['viie', 'aasta'],'tid':'t3', 'type':'DURATION', 'value':'P5Y', 'temporal_function':False},\
                              ]  },\
                  {'text': 'Järgmisel kolmapäeval, kõige hiljemalt kell 18.00 algab viiepäevane koosolek, mida korraldatakse igal aastal.',\
                   'dct':'1999-10-02TXX:XX',\
                   'expected_timexes': [ \
                                 {'text':['Järgmisel', 'kolmapäeval'], 'enclosing_text': 'Järgmisel kolmapäeval', 'tid':'t1', 'type':'DATE', 'value':'1999-10-06', 'temporal_function':True , 'anchor_time_id':'t0'}, \
                                 {'text':['kell', '18.00'],'tid':'t2', 'type':'TIME', 'value':'1999-10-06T18:00', 'temporal_function':True , 'anchor_time_id':'t1'},\
                                 {'text':['viiepäevane'],'tid':'t3', 'type':'DURATION', 'value':'P5D', 'temporal_function':False},\
                                 {'text':['igal','aastal'],'tid':'t4', 'type':'SET', 'value':'P1Y', 'temporal_function':True, 'quant':'EVERY'}, \
                              ]  }, \

                ]

    for test_item in test_data:
        # Prepare text
        text = Text(test_item['text'])
        if 'dct' in test_item:
            text.meta['dct'] = test_item['dct']
        text.tag_layer(['words', 'sentences', 'morph_analysis'])
        # Tag timexes
        tagger.tag(text)
        # Compare attributes and values of all timexes
        for timex_id, expected_timex in enumerate(test_item['expected_timexes']):
            # Expected attributes & values
            expected_attribs = [attr for attr in all_timex_attributes if attr in expected_timex]
            expected_vals    = [expected_timex[attr] for attr in all_timex_attributes if attr in expected_timex]
            # Obtained attributes & values
            result_vals      = list(text.timexes[timex_id, expected_attribs])
            if 'enclosing_text' in expected_timex:
               result_vals   = [ text.timexes[timex_id].enclosing_text ] + result_vals
               expected_vals = [expected_timex['enclosing_text']] + list(expected_vals)
            #print(expected_vals, result_vals)
            # Make assertions
            assert expected_vals == result_vals

    # Clean-up: Terminate Java process
    tagger._java_process._process.terminate()
