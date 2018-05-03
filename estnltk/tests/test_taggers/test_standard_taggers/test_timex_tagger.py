from estnltk import Text
from estnltk.taggers import TimexTagger


def test_timex_tagging_1():
    # Test the basic functionality of the TimexTagger
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
                  # Timexes with implicit interval endpoints ('begin_point' & 'end_point'):
                  {'text': 'Viimase viie aasta jooksul on tuulikute koguvõimsus kasvanud igal aastal ca 33 %.',\
                   'dct':'2012-09-18',\
                   'expected_timexes': [ \
                                 {'text':['Viimase', 'viie', 'aasta', 'jooksul'], 'enclosing_text': 'Viimase viie aasta jooksul', 'tid':'t1', 'type':'DURATION', 'value':'P5Y', 'temporal_function':True , 'anchor_time_id':None, 'begin_point': {'temporalFunction': 'true', 'tid': 't2', 'type': 'DATE', 'value': '2007'}, 'end_point':'t0' }, \
                                 {'text':['igal','aastal'],'tid':'t3', 'type':'SET', 'value':'P1Y', 'temporal_function':True, 'quant':'EVERY'}, \
                              ]
                  },\
                  {'text': 'Kohapärimuse valdkonnas on järgmise kahe aasta jooksul vaja teha ulatuslikku teavitustööd ja korraldada koolitusi.',\
                   'dct':'2013-12-01',\
                   'expected_timexes': [ \
                                 {'text':['järgmise', 'kahe', 'aasta', 'jooksul'], 'enclosing_text': 'järgmise kahe aasta jooksul', 'tid':'t1', 'type':'DURATION', 'value':'P2Y', 'temporal_function':True , 'anchor_time_id':None, 'begin_point': 't0', 'end_point':{'temporalFunction': 'true', 'tid': 't2', 'type': 'DATE', 'value': '2015'} }, \
                              ]
                  },
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



def test_timex_tagging_2_implicit_durations():
    # Test TimexTagger on detecting timexes with implicit durations/intervals ('part_of_interval' attrib):
    all_timex_attributes = ['text']+list(TimexTagger.attributes)+['part_of_interval']
    tagger = TimexTagger( mark_part_of_interval=True )
    test_data = [ {'text': 'Rahvusvaheline Festival Jazzkaar toimub 20.- 28. aprillini.',\
                   'dct':'2012-04-15',\
                   'expected_timexes': [ \
                                 {'text':['20.'], 'enclosing_text': '20.', 'tid':'t1', 'type':'DATE', 'value':'2012-04-20', 'temporal_function':True , 'anchor_time_id':'t0', 'part_of_interval': {'beginPoint': 't1', 'endPoint': 't2', 'tid': 't3', 'value': 'PXXD', 'type': 'DURATION', 'temporalFunction': 'true'} }, \
                                 {'text':['28.', 'aprillini'], 'enclosing_text': '28. aprillini', 'tid':'t2', 'type':'DATE', 'value':'2012-04-28', 'temporal_function':True , 'anchor_time_id':'t0', 'part_of_interval': {'beginPoint': 't1', 'endPoint': 't2', 'tid': 't3', 'value': 'PXXD', 'type': 'DURATION', 'temporalFunction': 'true'} }, \
                              ]
                  },\
                  {'text': 'Filmi lühendatud versiooni saab näha ringvaatena 18.- 23. maini kinos Ateena .',\
                   'dct':'2013-04-30',\
                   'expected_timexes': [ \
                                 {'text':['18.'], 'enclosing_text': '18.', 'tid':'t1', 'type':'DATE', 'value':'2013-05-18', 'temporal_function':True , 'anchor_time_id':'t0', 'part_of_interval': {'beginPoint': 't1', 'endPoint': 't2', 'tid': 't3', 'value': 'PXXD', 'type': 'DURATION', 'temporalFunction': 'true'} }, \
                                 {'text':['23.', 'maini'], 'enclosing_text': '23. maini', 'tid':'t2', 'type':'DATE', 'value':'2013-05-23', 'temporal_function':True , 'anchor_time_id':'t0', 'part_of_interval': {'beginPoint': 't1', 'endPoint': 't2', 'tid': 't3', 'value': 'PXXD', 'type': 'DURATION', 'temporalFunction': 'true'} }, \
                              ]
                  },\
                  {'text': 'Kui varem räägiti aastatest 2015- 2016, siis nüüd oli ajaline tärmin nihkunud 2018.- 2019. aastasse.',\
                   'dct':'2013-12-02',\
                   'expected_timexes': [ \
                                 {'text':['aastatest','2015'], 'tid':'t1', 'type':'DATE', 'value':'2015', 'temporal_function':False, 'anchor_time_id':None, 'part_of_interval': {'beginPoint': 't1', 'endPoint': 't2', 'tid': 't3', 'value': 'PXXY', 'type': 'DURATION', 'temporalFunction': 'true'} }, \
                                 {'text':['2016'], 'tid':'t2', 'type':'DATE', 'value':'2016', 'temporal_function':False, 'anchor_time_id':None, 'part_of_interval': {'beginPoint': 't1', 'endPoint': 't2', 'tid': 't3', 'value': 'PXXY', 'type': 'DURATION', 'temporalFunction': 'true'} }, \
                                 {'text':['nüüd'],'tid':'t4', 'type':'DATE', 'value':'PRESENT_REF', 'temporal_function':True, 'anchor_time_id':'t0'},\
                                 {'text':['2018.'], 'tid':'t5', 'type':'DATE', 'value':'2018', 'temporal_function':False, 'anchor_time_id':None, 'part_of_interval': {'beginPoint': 't5', 'endPoint': 't6', 'tid': 't7', 'value': 'PXXY', 'type': 'DURATION', 'temporalFunction': 'true'} }, \
                                 {'text':['2019.', 'aastasse'], 'tid':'t6', 'type':'DATE', 'value':'2019', 'temporal_function':False, 'anchor_time_id':None, 'part_of_interval': {'beginPoint': 't5', 'endPoint': 't6', 'tid': 't7', 'value': 'PXXY', 'type': 'DURATION', 'temporalFunction': 'true'} }, \
                              ]
                  },\
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



def test_timex_tagging_3_gaps_in_dct():
    # Test TimexTagger on texts that have gaps in their document creation dates
    all_timex_attributes = ['text']+list(TimexTagger.attributes)+['part_of_interval']
    tagger = TimexTagger( mark_part_of_interval=True )
    test_data = [ {'text': 'Rahvusvaheline Festival Jazzkaar toimub 20.- 28. aprillini.',\
                   'dct':'2012-04-XX',\
                   'expected_timexes': [ \
                                 {'text':['20.'], 'enclosing_text': '20.', 'tid':'t1', 'type':'DATE', 'value':'2012-04-20', 'temporal_function':True , 'anchor_time_id':'t0', 'part_of_interval': {'beginPoint': 't1', 'endPoint': 't2', 'tid': 't3', 'value': 'PXXD', 'type': 'DURATION', 'temporalFunction': 'true'} }, \
                                 {'text':['28.', 'aprillini'], 'enclosing_text': '28. aprillini', 'tid':'t2', 'type':'DATE', 'value':'2012-04-28', 'temporal_function':True , 'anchor_time_id':'t0', 'part_of_interval': {'beginPoint': 't1', 'endPoint': 't2', 'tid': 't3', 'value': 'PXXD', 'type': 'DURATION', 'temporalFunction': 'true'} }, \
                              ]
                  },\
                  {'text': 'Sel aastal jäi maikrahvivalimine maikuus ära.',\
                   'dct':'2010-XX-XX',\
                   'expected_timexes': [ \
                                 {'text':['Sel', 'aastal'], 'enclosing_text': 'Sel aastal', 'tid':'t1', 'type':'DATE', 'value':'2010', 'temporal_function':True , 'anchor_time_id':'t0' }, \
                                 {'text':['maikuus'], 'enclosing_text': 'maikuus', 'tid':'t2', 'type':'DATE', 'value':'XXXX-XX', 'temporal_function':True , 'anchor_time_id':'t0' }, \
                              ]
                  },\
                  {'text': 'Kui kirjutamise aeg puudu, on üsna raske öelda, mida mõeldakse neljapäeva või tuleva aasta all. 2010 a. on selge.',\
                   'dct':'XXXX-XX-XX',\
                   'expected_timexes': [ \
                                 {'text':['neljapäeva'], 'enclosing_text': 'neljapäeva', 'tid':'t1', 'type':'DATE', 'value':'XXXX-XX-XX', 'temporal_function':True , 'anchor_time_id':'t0' }, \
                                 {'text':['tuleva', 'aasta'], 'enclosing_text': 'tuleva aasta', 'tid':'t2', 'type':'DATE', 'value':'XXXX', 'temporal_function':True , 'anchor_time_id':'t0' }, \
                                 {'text':['2010', 'a.'], 'enclosing_text': '2010 a.', 'tid':'t3', 'type':'DATE', 'value':'2010', 'temporal_function':False }, \
                              ]
                  },\
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
