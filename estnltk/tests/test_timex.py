# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import unittest
import datetime
import codecs

from ..text import Text

class TimexTest(unittest.TestCase):

    def test_tag_separately(self):
        text = self.document
        self.assertListEqual(text.timexes, self.timexes)

    @property
    def document(self):
        return Text('3. detsembril 2014 oli näiteks ilus ilm. Aga kaks päeva varem jälle ei olnud.')

    @property
    def timexes(self):
        return [{'end': 18,
                  'id': 0,
                  'start': 0,
                  'temporal_function': False,
                  'text': '3 . detsembril 2014',
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
        text = Text('Täna on ilus ilm', creation_date=datetime.datetime(1986, 12, 21))
        self.assertEqual(text.timexes[0]['value'], '1986-12-21')

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
        creation = datetime.datetime(1986, 12, 21)
        for example in self.examples:
            text = Text(example, creation_date=creation)
            for timex in text.timexes:
                pass
                #print(timex_to_row(example, timex))

def timex_to_row(example, timex):
    toks = [example]
    toks.append(timex.get('text'))
    toks.append(timex.get('type'))
    toks.append(timex.get('value', ''))
    toks.append(timex.get('mod', ''))
    return '\t'.join(toks)
