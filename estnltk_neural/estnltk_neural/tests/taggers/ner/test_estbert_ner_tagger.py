import pkgutil
import pytest
import os

from estnltk import Text
from estnltk.downloader import get_resource_paths

def check_if_transformers_is_available():
    return pkgutil.find_loader("transformers") is not None

def check_if_pytorch_is_available():
    return pkgutil.find_loader("torch") is not None

# Try to get the resources path for EstBERTNERTagger model v1. If missing, do nothing. It's up for the user to download the missing resources
ESTBERTNER_V1_PATH = get_resource_paths("estbertner", only_latest=True, download_missing=False)

# Try to get the resources path for EstBERTNERTagger model v2. If missing, do nothing. It's up for the user to download the missing resources
ESTBERTNER_V2_PATH = get_resource_paths("estbertner_v2", only_latest=True, download_missing=False)

def _ner_spans_as_tuples(ner_layer):
    results = []
    for ne_span in ner_layer:
        ner_tag = ne_span.annotations[0]['nertag']
        results.append( \
            (ne_span.start, ne_span.end, ne_span.enclosing_text, ner_tag) )
    return results

@pytest.mark.skipif(not check_if_transformers_is_available(),
                    reason="package tranformers is required for this test")
@pytest.mark.skipif(not check_if_pytorch_is_available(),
                    reason="package pytorch is required for this test")
@pytest.mark.skipif(ESTBERTNER_V1_PATH is None,
                    reason="EstBERTNERTagger's model location not known. "+\
                           "Use estnltk.download('estbertner') to get the missing resources.")
def test_estbertner_v1_out_of_the_box():
    # Test that EstBERTNERTagger works "out_of_the_box" if model v1 is available
    from estnltk_neural.taggers import EstBERTNERTagger
    neural_ner_tagger = EstBERTNERTagger()
    text = Text('Tarmo Kruusimäe : Vaiko Eplik hoiatas ammu kogu Euroopat. Läänemets viib nüüd täide. '+\
                'Homme avatakse Tartu Linnaraamatukogu muusikaosakonnas maalikunstnik Ove Büttneri, '+\
                'graafik Tiit Rammuli, ning Tiina Vilbergi ühisnäitus "Loomaaed".')
    neural_ner_tagger.tag(text)
    output_layer = neural_ner_tagger.output_layers[0]
    assert output_layer in text.layers
    #print( _ner_spans_as_tuples( text[output_layer] ) )
    assert _ner_spans_as_tuples( text[output_layer] ) == \
        [(0, 15, 'Tarmo Kruusimäe', 'PER'), 
         (18, 29, 'Vaiko Eplik', 'PER'), 
         (48, 56, 'Euroopat', 'LOC'), 
         (100, 122, 'Tartu Linnaraamatukogu', 'ORG'), 
         (154, 166, 'Ove Büttneri', 'PER'), 
         (176, 187, 'Tiit Rammul', 'PER'), 
         (195, 209, 'Tiina Vilbergi', 'PER')]


@pytest.mark.skipif(not check_if_transformers_is_available(),
                    reason="package tranformers is required for this test")
@pytest.mark.skipif(not check_if_pytorch_is_available(),
                    reason="package pytorch is required for this test")
@pytest.mark.skipif(ESTBERTNER_V2_PATH is None,
                    reason="EstBERTNERTagger's model location not known. "+\
                           "Use estnltk.download('estbertner_v2') to get the missing resources.")
def test_estbertner_v2_smoke():
    # Test that EstBERTNERTagger works "out_of_the_box" if model v2 location is provided
    from estnltk_neural.taggers import EstBERTNERTagger
    neural_ner_tagger = EstBERTNERTagger( model_location=ESTBERTNER_V2_PATH )
    text = Text('Tarmo Kruusimäe : Vaiko Eplik hoiatas ammu kogu Euroopat. Läänemets viib nüüd täide. '+\
                'Homme avatakse Tartu Linnaraamatukogu muusikaosakonnas maalikunstnik Ove Büttneri, '+\
                'graafik Tiit Rammuli, ning Tiina Vilbergi ühisnäitus "Loomaaed".')
    neural_ner_tagger.tag(text)
    output_layer = neural_ner_tagger.output_layers[0]
    assert output_layer in text.layers
    #print( _ner_spans_as_tuples( text[output_layer] ) )
    assert _ner_spans_as_tuples( text[output_layer] ) == \
        [(0, 3, 'Tar', 'PER'), (3, 14, 'mo Kruusimä', 'PER'), 
         (18, 22, 'Vaik', 'PER'), (22, 29, 'o Eplik', 'PER'), 
         (48, 55, 'Euroopa', 'LOC'), 
         (58, 67, 'Läänemets', 'PER'), 
         (85, 90, 'Homme', 'DATE'), 
         (100, 122, 'Tartu Linnaraamatukogu', 'ORG'), 
         (140, 153, 'maalikunstnik', 'TITLE'), 
         (154, 155, 'O', 'PER'), (155, 166, 've Büttneri', 'PER'), 
         (168, 175, 'graafik', 'TITLE'), 
         (176, 186, 'Tiit Rammu', 'PER'), 
         (195, 209, 'Tiina Vilbergi', 'PER'), 
         (221, 231, '"Loomaaed"', 'PROD')]
