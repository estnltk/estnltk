from estnltk import Text
from estnltk.taggers.estner.ner_tagger import NerTagger
from estnltk.taggers.estner.word_level_ner_tagger import WordLevelNerTagger


def test_ner():
    text = """Norm , 24 tunni keskmine , on 50 mikrogrammi kuupmeetri kohta ja seda võib ületada 35 päeval aastas ,
     mida seni pole õnneks ette tulnud . Tallinna keskkonnaameti keskkonnahoiu osakonna juhataja Madis Kõrvits ütles ,
      et üksikud kõrged näidud ei muuda Tallinna õhku veel kõlbmatuks , kuid rõõmustada pole samuti millegi üle , sest
       2000. aastal pealinnas olnud hea õhk on hakanud autode juurdevoolu tõttu taas saastuma . “ Samas pole paanikaks
        põhjust , ” sõnas Kõrvits .“ Kui saaste hetkeliselt tõuseb , tasub olla toas , pikaajalist ohtu aga pole. ”
         Ta tõi näiteks eelmise nädala rekordpäeva"""
    text = Text(text)
    nertagger = NerTagger()
    text.tag_layer()
    nertagger.tag(text)
    nerlayer = (
        "Layer(name='ner',attributes=('nertag',),spans=SL[EnvelopingSpan(['Tallinna','keskkonnaameti'],"
        "[{'nertag':'ORG'}]),EnvelopingSpan(['Madis','Kõrvits'],[{'nertag':'PER'}]),EnvelopingSpan(['Tallinna'],"
        "[{'nertag':'LOC'}]),EnvelopingSpan(['Kõrvits'],[{'nertag':'PER'}])])")
    assert ''.join(nerlayer.split()) == ''.join(str(text.ner).split())


def test_word_level_ner():
    text = Text('Tallinna õhusaaste suureneb .')
    nertagger = WordLevelNerTagger()
    text.tag_layer()
    nertagger.tag(text)
    nerlayer = "Layer(name='wordner',attributes=('nertag',),spans=SL[EnvelopingSpan('Tallinna',[{'nertag':'B-LOC'}])," \
               "EnvelopingSpan('õhusaaste',[{'nertag':'O'}]),EnvelopingSpan('suureneb',[{'nertag':'O'}])," \
               "EnvelopingSpan('.',[{'nertag':'O'}])]) "
    assert ''.join(nerlayer.split()) == ''.join(str(text.wordner).split())
