from estnltk import Text
from estnltk.taggers.estner.ner_tagger import NerTagger



def test_label_values():
    text = """Norm , 24 tunni keskmine , on 50 mikrogrammi kuupmeetri kohta ja seda võib ületada 35 päeval aastas ,
     mida seni pole õnneks ette tulnud . Tallinna keskkonnaameti keskkonnahoiu osakonna juhataja Madis Kõrvits ütles ,
      et üksikud kõrged näidud ei muuda Tallinna õhku veel kõlbmatuks , kuid rõõmustada pole samuti millegi üle , sest
       2000. aastal pealinnas olnud hea õhk on hakanud autode juurdevoolu tõttu taas saastuma . “ Samas pole paanikaks
        põhjust , ” sõnas Kõrvits .“ Kui saaste hetkeliselt tõuseb , tasub olla toas , pikaajalist ohtu aga pole. ”
         Ta tõi näiteks eelmise nädala rekordpäeva"""
    text = Text(text)
    nertagger = NerTagger()
    nertagger.tag(text)
    nerlayer = (
    "Layer(name='ner', attributes=('nertag', 'name'), spans=SL[EnvelopingSpan(['Tallinna', 'keskkonnaameti'], [{'nertag': 'ORG', 'name': 'po'}]),\n"
    "    EnvelopingSpan(['Madis', 'Kõrvits'], [{'nertag': 'PER', 'name': 'po'}]),\n"
    "    EnvelopingSpan(['Tallinna'], [{'nertag': 'LOC', 'name': 'po'}]),\n"
    "    EnvelopingSpan(['Kõrvits'], [{'nertag': 'PER', 'name': 'po'}])])")
    assert ''.join(nerlayer.split()) == ''.join(str(text.ner).split())


def test_features():
    text = Text('Tallinna õhusaaste suureneb .')
    nertagger = NerTagger()
    nertagger.tag(text)
    features_F = """[[['iu[0]=y', 'fsnt[0]=y', 'p3[0]=tal', 'p4[0]=tall', 's3[0]=inn', 's4[0]=linn', 'aan[0]=y',
     'cu[0]=y', 'lem[0]=tallinn', 'pos[0]=_H_', 'case[0]=g', 'lem[1]=õhusaaste', 'pos[1]=_S_', 'post[1]=saaste',
      'lem[2]=suurene', 'pos[2]=_V_', 'iu[0]|fsnt[0]=y|y', 'lem[0]|lem[1]=tallinn|õhusaaste', 'pos[0]|pos[1]=_H_|_S_']],
       [['p3[0]=õhu', 'p4[0]=õhus', 's3[0]=ste', 's4[0]=aste', 'aan[0]=y', 'iu[-1]=y', 'cu[-1]=y', 'fsnt[-1]=y',
        'cs[2]=y', 'cdt[2]=y', 'lem[0]=õhusaaste', 'pos[0]=_S_', 'pref[0]=õhu', 'post[0]=saaste', 'case[0]=n',
         'lem[-1]=tallinn', 'prop[-1]=y', 'pos[-1]=_H_', 'lem[1]=suurene', 'pos[1]=_V_', 'lem[2]=.', 'pos[2]=_Z_',
          'pun[2]=y', 'lem[0]|lem[-1]=õhusaaste|tallinn', 'lem[0]|lem[1]=õhusaaste|suurene', 'pos[0]|pos[-1]=_S_|_H_',
           'pos[0]|pos[1]=_S_|_V_']], [['p3[0]=suu', 'p4[0]=suur', 's3[0]=ene', 's4[0]=rene', 'aan[0]=y', 'iu[-2]=y',
            'cu[-2]=y', 'fsnt[-2]=y', 'cs[1]=y', 'cdt[1]=y', 'lem[0]=suurene', 'pos[0]=_V_', 'end[0]=b',
             'lem[-1]=õhusaaste', 'pos[-1]=_S_', 'post[-1]=saaste', 'lem[-2]=tallinn', 'prop[-2]=y', 'pos[-2]=_H_',
              'lem[1]=.', 'pos[1]=_Z_', 'pun[1]=y', 'lem[0]|lem[-1]=suurene|õhusaaste', 'lem[0]|lem[1]=suurene|.',
               'pos[0]|pos[-1]=_V_|_S_', 'pos[0]|pos[1]=_V_|_Z_']], [['ao[0]=y', 'cs[0]=y', 'cdt[0]=y', 'lem[0]=.',
                'pos[0]=_Z_', 'pun[0]=y', 'lem[-1]=suurene', 'pos[-1]=_V_', 'lem[-2]=õhusaaste', 'pos[-2]=_S_',
                 'post[-2]=saaste', 'lem[0]|lem[-1]=.|suurene', 'pos[0]|pos[-1]=_Z_|_V_']]]"""
    assert ''.join(str(text.ner_features.F).split()) == ''.join(features_F.split())
