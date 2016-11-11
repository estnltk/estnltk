# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import unittest
import datetime
import codecs

from ..text import Text
from ..timex import TimexTagger
from ..names import *

class TimexTest(unittest.TestCase):

    def test_tag_separately(self):
        timextagger = TimexTagger()
        text = Text('3. detsembril 2014 oli näiteks ilus ilm. Aga kaks päeva varem jälle ei olnud.', timex_tagger=timextagger)
        self.assertListEqual(text.timexes, self.timexes)
        # Terminate Java process in order to avoid "OSError: [WinError 6] The handle is invalid"
        # in subsequent Java processing
        timextagger._process.terminate()

    @property
    def timexes(self):
        return [{'end': 18,
                  'id': 0,
                  'start': 0,
                  'temporal_function': False,
                  'text': '3. detsembril 2014',
                  'tid': 't1',
                  'type': 'DATE',
                  'value': '2014-12-03'},
                 {'anchor_id': 0,
                  'anchor_tid': 't1',
                  'end': 61,
                  'id': 1,
                  'start': 45,
                  'temporal_function': True,
                  'text': 'kaks päeva varem',
                  'tid': 't2',
                  'type': 'DATE',
                  'value': '2014-12-01'}]

    def test_document_creation_date(self):
        timextagger = TimexTagger()
        text = Text('Täna on ilus ilm', creation_date=datetime.datetime(1986, 12, 21), timex_tagger=timextagger)
        self.assertEqual(text.timexes[0][TMX_VALUE], '1986-12-21')
        # Terminate Java process in order to avoid "OSError: [WinError 6] The handle is invalid"
        # in subsequent Java processing
        timextagger._process.terminate()

    @property
    def examples(self):
        return ['Linna maksutulu võib tuleval aastal langeda kuni 300 miljonit krooni.',
                'Järgmisel reedel, 2004. aastal',
                'esmaspäeva hommikul, järgmisel reedel kell 14.00',
                'neljapäeviti, hommikuti',
                'selle kuu alguses',
                '1990ndate lõpus',
                '18. sajandil',
                'VI sajandist e. m. a',
                'kolm tundi',
                'viis kuud',
                'kaks minutit',
                'teisipäeviti',
                'kolm päeva igas kuus',
                'kolm korda igas kuus',
                'Ühel kenal päeval',
                'Ühel märtsikuu päeval',
                'mitu tundi',
                'hiljuti',
                'tulevikus',
                '2009. aasta alguses',
                'juuni alguseks 2007. aastal',
                '2009. aasta esimesel poolel',
                'umbes 4 aastat',
                'peaaegu 4 aastat',
                '12-15 märts 2009',
                'eelmise kuu lõpus',
                '2004. aasta suvel',
                'Detsembris oli keskmine temperatuur kaks korda madalam kui kuu aega varem',
                'neljapäeval, 17. juunil',
                'täna, 100 aastat tagasi',
                'neljapäeva öösel vastu reedet',
                'aasta esimestel kuudel',
                'viimase aasta jooksul',
                'viimase kolme aasta jooksul',
                'varasemad aastad, hilisemad aastad',
                'viie-kuue aasta pärast, kahe-kolme aasta tagune',
                'aastaid tagasi',
                'aastate pärast']

    def test_various_examples(self):
        timextagger = TimexTagger()
        creation = datetime.datetime(1986, 12, 21)
        for example in self.examples:
            text = Text(example, creation_date=creation, timex_tagger=timextagger)
            for timex in text.timexes:
                pass
                #print(timex_to_row(example, timex))
        # Terminate Java process in order to avoid "OSError: [WinError 6] The handle is invalid"
        # in subsequent Java processing
        timextagger._process.terminate()


    def test_sentence_splitting_preserves_timexes(self):
        timextagger = TimexTagger()
        text_str = \
        '''
        Valitsus otsustas tänasel istungil kolmapäevase eelnõu üle vaadata, neljapäevasel ja teisipäevasel tagasi lükata, homsel vastu võtta ja eilsel kõrvale jätta. Samas on teada, et laupäevasel ei toimu midagi ja kaks kuud tagasi vastuvõetud pühapäevane eelnõu ei toimi kolmapäeviti. Viimase aasta jooksul pole midagi sellist veel juhtunud.
        '''
        text = Text( text_str, timex_tagger=timextagger )
        # 1) Tag timexes before splitting the text; Remember the result;
        text.tag_timexes()
        timexesBeforeSplit = text.timexes
        # 2) Split the text by sentences and count timexes once again;
        timexesAfterSplit  = []
        for sentence in text.split_by( SENTENCES ):
            if sentence.timexes:
               timexesAfterSplit.extend( sentence.timexes )
        # 3) Both countings should give same amount of timexes:
        self.assertEqual( len(timexesBeforeSplit), len(timexesAfterSplit) )
        # And there should be exactly the same timexes, in exactly the same order
        for i in range( len(timexesBeforeSplit) ):
            self.assertEqual( timexesBeforeSplit[i][TMX_TID], timexesAfterSplit[i][TMX_TID] )
            tmx_text1 = timexesBeforeSplit[i].get(TEXT, '')
            tmx_text2 = timexesAfterSplit[i].get(TEXT, '')
            self.assertEqual( tmx_text1, tmx_text2 )
            #print( timexesAfterSplit[i][START], timexesAfterSplit[i][END] )
        # Terminate Java process in order to avoid "OSError: [WinError 6] The handle is invalid"
        # in subsequent Java processing
        timextagger._process.terminate()



def timex_to_row(example, timex):
    toks = [example]
    toks.append(timex.get(TEXT))
    toks.append(timex.get(TMX_TYPE))
    toks.append(timex.get(TMX_VALUE, ''))
    toks.append(timex.get(TMX_MOD, ''))
    return '\t'.join(toks)
