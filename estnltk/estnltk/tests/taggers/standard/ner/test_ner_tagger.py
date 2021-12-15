import pytest

from estnltk import Text
from estnltk.taggers import WordTagger
from estnltk.taggers import SentenceTokenizer
from estnltk.taggers import VabamorfTagger
from estnltk.taggers.standard.ner.ner_tagger import NerTagger
from estnltk.taggers.standard.ner.word_level_ner_tagger import WordLevelNerTagger

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
    nerlayer = "Layer(name='wordner',attributes=('nertag',),spans=SL[Span('Tallinna',[{'nertag':'B-LOC'}])," \
               "Span('õhusaaste',[{'nertag':'O'}]),Span('suureneb',[{'nertag':'O'}])," \
               "Span('.',[{'nertag':'O'}])]) "
    assert ''.join(nerlayer.split()) == ''.join(str(text.wordner).split())


#@pytest.mark.xfail(reason="customizing layer names needs to be implemented!")
def test_ner_with_customized_layer_names():
    # Test that all NER input layers can be fully customized
    # 1) Create taggers that produce different layer names
    my_word_tagger = WordTagger( output_layer='my_words' )
    my_sentence_tokenizer = SentenceTokenizer( 
                              input_words_layer='my_words',
                              output_layer='my_sentences' )
    my_morph_analyser = VabamorfTagger(
                              output_layer='my_morph',
                              input_words_layer='my_words',
                              input_sentences_layer='my_sentences' )
    # 2) Create test text with prerequisite layers
    text = Text('Kersti Kaljulaid on Eesti Vabariigi viies ja praegune president. Ta on Eesti esimene naispresident.')
    text.tag_layer(['compound_tokens'])
    my_word_tagger.tag( text )
    my_sentence_tokenizer.tag( text )
    my_morph_analyser.tag( text )
    # 3) Annotate with NerTagger
    # TODO: Pass 'my_words' and 'my_sentences' as NerTagger's input_layers
    nertagger = NerTagger(output_layer='named_entities', morph_layer_input=my_morph_analyser.output_layer, words_layer_input=my_word_tagger.output_layer, sentences_layer_input=my_sentence_tokenizer.output_layer)
    nertagger.tag( text )

    # 4) Assertions
    # 4.1) Assert that default layer names are not used at all:
    assert 'words' not in text.layers
    assert 'sentences' not in text.layers
    assert 'morph_analysis' not in text.layers
    assert 'ner' not in text.layers
    # 4.2) Assert that custom layer names are used:
    assert 'my_words' in text.layers
    assert 'my_sentences' in text.layers
    assert 'my_morph' in text.layers
    assert 'named_entities' in text.layers
    # 4.3) Assert NerTagger's results
    nerlayer = (
        "Layer(name='named_entities', attributes=('nertag',), spans=SL[EnvelopingSpan(['Kersti', 'Kaljulaid'], [{'nertag': 'PER'}]),"
        "EnvelopingSpan(['Eesti', 'Vabariigi'], [{'nertag': 'LOC'}]),"
        "EnvelopingSpan(['Eesti'], [{'nertag': 'LOC'}])])")
    assert ''.join(nerlayer.split()) == ''.join(str(text['named_entities']).split())

