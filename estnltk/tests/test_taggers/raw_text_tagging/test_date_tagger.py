import datetime
from estnltk import Text
from estnltk.taggers import DateTagger


def test_date_tagger():
    datetagger = DateTagger()

    text = Text('''07.07.2011 14:25 - KOLK, REIN - D04946 - E170 - kardioloogia. 
Tuleb 28.05., enne KTG.
pt.-l 2007a.-l diagnoositud sügatõbi:',
'11.09.13. tehtud S.Rhesonatiivi 1250TÜ i/m',
'Eelmine kord 2009 ja diagnoosika jäi reaktiivne artropaatia',
            'haava revideerimine od kl 21.20',
' 17.09.2013.a. kell 06:09 sünnib elus ajaline T 3250/50.',
'Kontrolli 20.04.2013 kell 11.00 I-korrus, 
'Lõikus 4.1.2013.',
'Kontrollile- 09.2011'
"05.09.2012 tehtud SKG
1.09 angiograafia leid 
02.09 kell 09.15 taastus siinusrütm''')

    datetagger.tag(text)

    assert text['dates'].to_dict() == {
        'name': 'dates',
        'attributes': ('date_text',
                       'type',
                       'probability',
                       'groups',
                       'extracted_values'),
        'parent': None,
        'enveloping': None,
        'ambiguous': False,
        'meta': {},
        'spans': [{'base_span': (0, 16),
                   'annotations': [{
                       'groups': "{'DAY': '07', 'MONTH': '07', 'YEAR': '2011', 'hour': '14', 'minute': '25', 'second': None}",
                       'probability': '0.9',
                       'date_text': '07.07.2011 14:25',
                       'type': 'date_time',
                       'extracted_values': datetime.datetime(2011, 7, 7,
                                                             14, 25)}]},
                  {'base_span': (69, 74),
                   'annotations': [{'groups': "{'DAY': '28', 'MONTH': '05'}",
                                    'probability': '0.3',
                                    'date_text': '28.05',
                                    'type': 'partial_date',
                                    'extracted_values': None}]},
                  {'base_span': (93, 98),
                   'annotations': [{'groups': "{'LONGYEAR': '2007'}",
                                    'probability': '0.8',
                                    'date_text': '2007a',
                                    'type': 'partial_date',
                                    'extracted_values': None}]},
                  {'base_span': (128, 136),
                   'annotations': [
                       {'groups': "{'DAY': '11', 'MONTH': '09', 'YEAR': '13'}",
                        'probability': '0.8',
                        'date_text': '11.09.13',
                        'type': 'date',
                        'extracted_values': datetime.date(2013, 9, 11)}]},
                  {'base_span': (187, 191),
                   'annotations': [{'groups': "{'LONGYEAR': '2009'}",
                                    'probability': '0.4',
                                    'date_text': '2009',
                                    'type': 'partial_date',
                                    'extracted_values': None}]},
                  {'base_span': (272, 280),
                   'annotations': [
                       {'groups': "{'hour': '21', 'minute': '20', 'second': None}",
                        'probability': '1.0',
                        'date_text': 'kl 21.20',
                        'type': 'time',
                        'extracted_values': datetime.time(21, 20)}]},
                  {'base_span': (285, 309),
                   'annotations': [{
                       'groups': "{'DAY': '17', 'MONTH': '09', 'YEAR': '2013', 'hour': '06', 'minute': '09', 'second': None}",
                       'probability': '1.0',
                       'date_text': '17.09.2013.a. kell 06:09',
                       'type': 'date_time',
                       'extracted_values': datetime.datetime(2013, 9, 17,
                                                             6, 9)}]},
                  {'base_span': (354, 375),
                   'annotations': [{
                       'groups': "{'DAY': '20', 'MONTH': '04', 'YEAR': '2013', 'hour': '11', 'minute': '00', 'second': None}",
                       'probability': '1.0',
                       'date_text': '20.04.2013 kell 11.00',
                       'type': 'date_time',
                       'extracted_values': datetime.datetime(2013, 4, 20,
                                                             11, 0)}]},
                  {'base_span': (395, 403),
                   'annotations': [
                       {'groups': "{'DAY': '4', 'MONTH': '1', 'YEAR': '2013'}",
                        'probability': '0.8',
                        'date_text': '4.1.2013',
                        'type': 'date',
                        'extracted_values': datetime.date(2013, 1, 4)}]},
                  {'base_span': (421, 428),
                   'annotations': [{'groups': "{'MONTH': '09', 'LONGYEAR': '2011'}",
                                    'probability': '0.6',
                                    'date_text': '09.2011',
                                    'type': 'partial_date',
                                    'extracted_values': None}]},
                  {'base_span': (431, 441),
                   'annotations': [
                       {'groups': "{'DAY': '05', 'MONTH': '09', 'YEAR': '2012'}",
                        'probability': '0.8',
                        'date_text': '05.09.2012',
                        'type': 'date',
                        'extracted_values': datetime.date(2012, 9, 5)}]},
                  {'base_span': (453, 457),
                   'annotations': [{'groups': "{'DAY': '1', 'MONTH': '09'}",
                                    'probability': '0.3',
                                    'date_text': '1.09',
                                    'type': 'partial_date',
                                    'extracted_values': None}]},
                  {'base_span': (477, 493),
                   'annotations': [{
                       'groups': "{'DAY': '02', 'MONTH': '09', 'hour': "
                                 "'09', 'minute': '15', "
                                 "'second': None}",
                       'probability': '0.8',
                       'date_text': '02.09 kell 09.15',
                       'type': 'partial_date',
                       'extracted_values': datetime.time(9, 15)}]}]}
