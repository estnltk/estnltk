import pytest

from estnltk import Text
from estnltk.taggers import TimexTagger

from estnltk.taggers.standard.timexes.timex_tagger import TimexTagger
from estnltk.taggers.standard.timexes.core_timex_tagger import CoreTimexTagger
from estnltk.taggers.standard.timexes.timex_tagger_preprocessing import make_adapted_cp_tagger

# TimexTagger with output layer enveloping around 'words'
timexes_tagger_enveloping = \
    TimexTagger( mark_part_of_interval=True, output_ordered_dicts=False, enveloped_words_layer='words' )

def test_timex_tagging_1():
    # Test the basic functionality of the TimexTagger
    all_timex_attributes = ['text']+list(CoreTimexTagger.output_attributes)
    
    # 1) Test Timex tagger on empty text
    text = Text('')
    text.tag_layer(['words', 'sentences', 'morph_analysis'])
    timexes_tagger_enveloping.tag( text )

    # Execution should not produce any errors
    assert len(text.words) == 0
    assert len(text.timexes) == 0
    
    # 2) Test Timex tagger on example texts
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
        text.tag_layer('words')
        timexes_tagger_enveloping.tag( text )
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


def test_timex_tagging_2_implicit_durations():
    # Test TimexTagger on detecting timexes with implicit durations/intervals ('part_of_interval' attrib):
    all_timex_attributes = ['text']+list(CoreTimexTagger.output_attributes)+['part_of_interval']
    test_data = [ {'text': 'Rahvusvaheline Festival Jazzkaar toimub 20.- 28. aprillini 2012.',\
                   'dct':'2012-04-15',\
                   'expected_timexes': [ \
                                 {'text':['20.'], 'enclosing_text': '20.', 'tid':'t1', 'type':'DATE', 'value':'2012-04-20', 'temporal_function':False , 'anchor_time_id':None, 'part_of_interval': {'beginPoint': 't1', 'endPoint': 't2', 'tid': 't3', 'value': 'PXXD', 'type': 'DURATION', 'temporalFunction': 'true'} }, \
                                 {'text':['28.', 'aprillini', '2012.'], 'enclosing_text': '28. aprillini 2012.', 'tid':'t2', 'type':'DATE', 'value':'2012-04-28', 'temporal_function':False , 'anchor_time_id':None, 'part_of_interval': {'beginPoint': 't1', 'endPoint': 't2', 'tid': 't3', 'value': 'PXXD', 'type': 'DURATION', 'temporalFunction': 'true'} }, \
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
                  {'text': '18.-20.06.1869 -- Tartus toimus I üldlaulupidu',\
                   'dct':'2013-04-25',\
                   'expected_timexes': [ \
                                 # TODO: timexes are missing 'part_of_interval' for some reason
                                 {'text':['18.'], 'enclosing_text': '18.', 'tid':'t1', 'type':'DATE', 'value':'1869-06-18', 'temporal_function':False , 'anchor_time_id':None, 'part_of_interval': None }, \
                                 {'text':['20.06.1869'], 'enclosing_text': '20.06.1869', 'tid':'t2', 'type':'DATE', 'value':'1869-06-20', 'temporal_function':False , 'anchor_time_id':None, 'part_of_interval': None }, \
                              ]
                  },\
                  {'text': 'Taoluste vastuvõtt toimus 1.04.- 14.04.2011.',\
                   'dct':'2011-04-22',\
                   'expected_timexes': [ \
                                 # TODO: timexes are missing 'part_of_interval' for some reason
                                 {'text':['1.04', '.'], 'tid':'t1', 'type':'DATE', 'value':'2011-04-01', 'temporal_function':False , 'anchor_time_id':None, 'part_of_interval': None }, \
                                 {'text':['14.04.2011'], 'tid':'t2', 'type':'DATE', 'value':'2011-04-14', 'temporal_function':False , 'anchor_time_id':None, 'part_of_interval': None }, \
                              ]
                  },\
                ]
    for test_item in test_data:
        # Prepare text
        text = Text(test_item['text'])
        if 'dct' in test_item:
            text.meta['dct'] = test_item['dct']
        text.tag_layer('words')
        timexes_tagger_enveloping.tag( text )
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


def test_timex_tagging_3_gaps_in_dct():
    # Test TimexTagger on texts that have gaps in their document creation dates
    all_timex_attributes = ['text']+list(CoreTimexTagger.output_attributes)+['part_of_interval']
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
        text.tag_layer('words')
        timexes_tagger_enveloping.tag( text )
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



def test_timex_tagging_4_additional_rules():
    # Test TimexTagger with some additional rules
    all_timex_attributes = ['text']+list(CoreTimexTagger.output_attributes)+['part_of_interval']+['']
    test_data = [ # eile-täna
                  {'text': 'Ma just käisin eile-täna seal jalgrattaga.',\
                   'dct':'2011-08-24',\
                   'expected_timexes': [ \
                       {'text':['eile-täna'], 'enclosing_text': 'eile-täna', 'tid':'t1', 'type':'DURATION', 'value':'P2D', 'temporal_function':True , 'anchor_time_id':'t0', \
                           'begin_point': {'tid': 't2', 'value': '2011-08-23', 'type': 'DATE', 'temporalFunction': 'true'},\
                           'end_point':   {'tid': 't3', 'value': '2011-08-24', 'type': 'DATE', 'temporalFunction': 'true'} }, \
                   ]
                  },\
                  # täna-homme
                  {'text': 'Tundub, et täna-homme on paljudel plaanis ka ise sülti valmistada.',\
                   'dct':'2012-12-21',\
                   'expected_timexes': [ \
                       {'text':['täna-homme'], 'enclosing_text': 'täna-homme', 'tid':'t1', 'type':'DURATION', 'value':'P2D', 'temporal_function':True , 'anchor_time_id':'t0', \
                           'begin_point': {'tid': 't2', 'value': '2012-12-21', 'type': 'DATE', 'temporalFunction': 'true'},\
                           'end_point':   {'tid': 't3', 'value': '2012-12-22', 'type': 'DATE', 'temporalFunction': 'true'} }, \
                   ]
                  },\
                  # homme-ülehomme
                  {'text': 'Hea, et lugema juhtusin, just oli plaan ise homme-ülehomme minna Soome ... :)',\
                   'dct':'2011-08-15',\
                   'expected_timexes': [ \
                       {'text':['homme-ülehomme'], 'tid':'t1', 'type':'DURATION', 'value':'P2D', 'temporal_function':True , 'anchor_time_id':'t0', \
                           'begin_point': {'tid': 't2', 'value': '2011-08-16', 'type': 'DATE', 'temporalFunction': 'true'},\
                           'end_point':   {'tid': 't3', 'value': '2011-08-17', 'type': 'DATE', 'temporalFunction': 'true'} }, \
                   ]
                  },\
                  # eile-üleeile
                  {'text': 'Eile-üleeile viibisin taas pikalt Den Helderis.',\
                   'dct':'2009-07-31',\
                   'expected_timexes': [ \
                       {'text':['Eile-üleeile'], 'tid':'t1', 'type':'DURATION', 'value':'P2D', 'temporal_function':True , 'anchor_time_id':'t0', \
                           'begin_point': {'tid': 't2', 'value': '2009-07-29', 'type': 'DATE', 'temporalFunction': 'true'},\
                           'end_point':   {'tid': 't3', 'value': '2009-07-30', 'type': 'DATE', 'temporalFunction': 'true'} }, \
                   ]
                  },\
                  # ISO format date #1
                  {'text': '2007.05.03\n\nViinata volber möödus rahulikult',\
                   'dct':'2018-12-05',\
                   'expected_timexes': [ \
                       {'text':['2007.05.03'], 'tid':'t1', 'type':'DATE', 'value':'2007-05-03', 'temporal_function':False , 'anchor_time_id':None,  }, \
                   ]
                  },\
                  # ISO format date #2
                  {'text': 'Mõtteid ja ideid saab esitada kultuuripealinna kodulehel ning sündmus peab juhtuma ajavahemikus 2010.01.01 – 2010.12.31.',\
                   'dct':'2018-12-05',\
                   'expected_timexes': [ \
                       {'text':['2010.01.01'], 'tid':'t1', 'type':'DATE', 'value':'2010-01-01', 'temporal_function':False , 'anchor_time_id':None,  }, \
                       {'text':['2010.12.31'], 'tid':'t2', 'type':'DATE', 'value':'2010-12-31', 'temporal_function':False , 'anchor_time_id':None,  }, \
                   ]
                  },\
                  # Negative rules:
                  # Do not extract any timexes from these sentences
                  {'text': 'Kõik , kellele on pakutud müüa arvuti Sun Ultra1 protsessoriplokki ( Part number : 600-3796-02 ; Serial number : 616M1751 ) ,'+\
                           ' andke teada diagnostikakeskusse telefonil 6 406 750.',\
                   'dct':'1999-11-24',\
                   'expected_timexes': []
                  },\
                  
                ]
    for test_item in test_data:
        # Prepare text
        text = Text( test_item['text'] )
        if 'dct' in test_item:
            text.meta['dct'] = test_item['dct']
        text.tag_layer('words')
        timexes_tagger_enveloping.tag( text )
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
        if len( test_item['expected_timexes'] ) == 0:
            assert len( text.timexes ) == 0



def test_timex_tagging_flat_output_layer():
    # TimexTagger with flat output layer (default settings)
    timexes_tagger = \
        TimexTagger( mark_part_of_interval=True, output_ordered_dicts=False)
    all_timex_attributes = ['text']+list(timexes_tagger.output_attributes)
    
    test_data = [ {'text': 'Järgmisel kolmapäeval, kõige hiljemalt kell 18.00 algab viiepäevane koosolek, mida korraldatakse igal aastal.',\
                   'dct':'1999-10-02TXX:XX',\
                   'expected_timexes': [ \
                                 {'text': 'Järgmisel kolmapäeval', 'tid':'t1', 'type':'DATE', 'value':'1999-10-06', 'temporal_function':True , 'anchor_time_id':'t0'}, \
                                 {'text': 'kell 18.00','tid':'t2', 'type':'TIME', 'value':'1999-10-06T18:00', 'temporal_function':True , 'anchor_time_id':'t1'},\
                                 {'text': 'viiepäevane', 'tid':'t3', 'type':'DURATION', 'value':'P5D', 'temporal_function':False},\
                                 {'text': 'igal aastal', 'tid':'t4', 'type':'SET', 'value':'P1Y', 'temporal_function':True, 'quant':'EVERY'}, \
                              ]  }, \
                  # Timexes with implicit interval endpoints ('begin_point' & 'end_point'):
                  {'text': 'Viimase viie aasta jooksul on tuulikute koguvõimsus kasvanud igal aastal ca 33 %.',\
                   'dct':'2012-09-18',\
                   'expected_timexes': [ \
                                 {'text': 'Viimase viie aasta jooksul', 'tid':'t1', 'type':'DURATION', 'value':'P5Y', 'temporal_function':True , 'anchor_time_id':None, 'begin_point': {'temporalFunction': 'true', 'tid': 't2', 'type': 'DATE', 'value': '2007'}, 'end_point':'t0' }, \
                                 {'text': 'igal aastal','tid':'t3', 'type':'SET', 'value':'P1Y', 'temporal_function':True, 'quant':'EVERY'}, \
                              ]
                  },\
                  # Timexes that require different tokenization than the standard pipeline provides
                 {'text': '( 14.11.2001 jõust.01.01.2002 - RT I 2001 , 95 , 587 )',\
                   'dct':'2001-09-18',\
                   'expected_timexes': [ \
                                 {'text': '14.11.2001', 'tid':'t1', 'type':'DATE', 'value':'2001-11-14', 'temporal_function':False , 'anchor_time_id':None}, 
                              ]
                  },\
                 {'text': '24. detsembril kell 18 , 25. detsembril kell 10.30 , 26. ja 31. detsembril kell 17 ja 1. jaanuaril kell 10.30.',\
                   'dct':'2021-12-18',\
                   'expected_timexes': [ \
                                 {'text': '24. detsembril kell 18', 'tid':'t1', 'type':'TIME', 'value':'2021-12-24T18', 'temporal_function':True , 'anchor_time_id':None}, 
                                 {'text': '25. detsembril kell 10.30', 'tid':'t2', 'type':'TIME', 'value':'2021-12-25T10:30', 'temporal_function':True , 'anchor_time_id':None}, 
                                 #  Unfortunately, elliptic '26. (detsembril)' will be missed 
                                 {'text': '31. detsembril kell 17', 'tid':'t3', 'type':'TIME', 'value':'2021-12-31T17', 'temporal_function':True , 'anchor_time_id':None}, 
                                 {'text': '1. jaanuaril kell 10.30', 'tid':'t4', 'type':'TIME', 'value':'2022-01-01T10:30', 'temporal_function':True , 'anchor_time_id':None}, 
                              ]
                  },\
    ]
    for test_item in test_data:
        # Prepare text
        text = Text(test_item['text'])
        if 'dct' in test_item:
            text.meta['dct'] = test_item['dct']
        timexes_tagger.tag( text )
        # Compare attributes and values of all timexes
        for timex_id, expected_timex in enumerate(test_item['expected_timexes']):
            # Expected attributes & values
            expected_attribs = [attr for attr in all_timex_attributes if attr in expected_timex]
            expected_vals    = [expected_timex[attr] for attr in all_timex_attributes if attr in expected_timex]
            # Obtained attributes & values
            result_vals      = list(text.timexes[timex_id, expected_attribs])
            #print(expected_vals, result_vals)
            # Make assertions
            assert expected_vals == result_vals
    timexes_tagger.close()



def test_core_timex_tagger_context_tear_down():
    # Tests after exiting CoreTimexTagger's context manager, the process has been 
    # torn down and no longer available
    text = Text( 'Testimise tekst.' )
    text.tag_layer(['words', 'sentences', 'morph_analysis'])
    # 1) Apply tagger as a context manager
    with CoreTimexTagger() as tagger:
        tagger.tag(text)
    # Check: polling the process should not return None
    assert tagger._java_process._process.poll() is not None
    # Check: After context has been torn down, we should get an assertion error
    with pytest.raises(AssertionError) as e1:
        tagger.tag(text)
    
    # 2) Apply tagger outside with, and use the __exit__() method
    tagger2 = CoreTimexTagger()
    # Check that there is no process at first (lazy initialization)
    assert tagger2._java_process._process is None
    text = Text( 'Testimise tekst.' )
    text.tag_layer(['words', 'sentences', 'morph_analysis'])
    tagger2.tag(text)
    # Check that the process is running after calling tag()
    assert tagger2._java_process._process.poll() is None
    # Terminate the process "manually"
    tagger2.__exit__()
    # Check that the process is terminated
    assert tagger2._java_process._process.poll() is not None


#########################################################
#    Preprocessing for TimexTagger
#########################################################

def test_timex_tagger_preprocessing():
    CP_TAGGER_ADAPTED = make_adapted_cp_tagger()
    # Case 1
    test_text = Text('1991. a. jaanuaris, 2001. aasta lõpul või 1. jaanuaril 2001. a.').tag_layer(['tokens'])
    CP_TAGGER_ADAPTED.tag( test_text )
    test_text.tag_layer( ['words'] )
    assert [t.text for t in test_text.words] == ['1991.', 'a.', 'jaanuaris', ',', '2001.', 'aasta', 'lõpul', 'või', '1.', 'jaanuaril', '2001.', 'a.']

    # Case 2
    test_text = Text('( 14.11.2001 jõust.01.01.2002 - RT I 2001 , 95 , 587 )').tag_layer(['tokens'])
    CP_TAGGER_ADAPTED.tag( test_text )
    test_text.tag_layer( ['words'] )
    #print( [(cp.enclosing_text, cp.type) for cp in test_text.compound_tokens] )
    assert [t.text for t in test_text.words] == ['(', '14.11.2001', 'jõust', '.', '01.01.2002', '-', 'RT', 'I', '2001', ',', '95', ',', '587', ')']

    # Case 3
    test_text = Text('24. detsembril kell 18 , 25. detsembril kell 10.30 , 26. ja 31. detsembril kell 17 ja 1. jaanuaril kell.10.30.').tag_layer(['tokens'])
    CP_TAGGER_ADAPTED.tag( test_text )
    test_text.tag_layer( ['words'] )
    assert [t.text for t in test_text.words] == ['24.', 'detsembril', 'kell', '18', ',', '25.', 'detsembril', 'kell', '10.30', ',', '26.', 'ja', '31.', 'detsembril', 'kell', '17', 'ja', '1.', 'jaanuaril', 'kell', '.', '10.30', '.']

    # Case 4
    test_text = Text('31.detsembril kell 16 ja 23.30 , 1. jaanuaril kell 13.').tag_layer(['tokens'])
    CP_TAGGER_ADAPTED.tag( test_text )
    test_text.tag_layer( ['words'] )
    assert [t.text for t in test_text.words] == ['31.', 'detsembril', 'kell', '16', 'ja', '23.30', ',', '1.', 'jaanuaril', 'kell', '13.']


