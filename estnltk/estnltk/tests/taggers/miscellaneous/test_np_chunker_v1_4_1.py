import pytest

from estnltk import Text
from estnltk.taggers import VislTagger
from estnltk.taggers.miscellaneous.np_chunker import NounPhraseChunker

from estnltk.taggers.standard.syntax.vislcg3_syntax import check_if_vislcg_is_in_path


@pytest.mark.skipif(not check_if_vislcg_is_in_path('vislcg3'),
                    reason="a directory containing vislcg3 executable must be inside the system PATH")
def test_np_chunker_based_on_visl_syntax():
    visl_tagger = VislTagger()
    np_chunker  = NounPhraseChunker( visl_tagger.output_layer )
    test_data = [
        { 'text':  'Suur karvane kass nurrus punasel diivanil, väike hiir aga hiilis temast mööda.',
          'expected_phrases': ['Suur karvane kass', 'punasel diivanil', 'väike hiir', 'temast'], },
        { 'text':  'Autojuhi lapitekk pälvis linna koduleheküljel paljude kodanike tähelepanu.',
          'expected_phrases': ['Autojuhi lapitekk', 'linna koduleheküljel', 'paljude kodanike tähelepanu'], },
        { 'text':  'Kõige väiksemate tassidega serviis toodi kusagilt vanast tolmusest kapist välja.',
          'expected_phrases': ['Kõige väiksemate tassidega', 'serviis', 'vanast tolmusest kapist'], },
        { 'text':  'Kuna laulupidu on muu hulgas esteetiline, teatavat kunstilise kvaliteedi miinimumi '+\
                   'eeldav nähtus, siis pole ka tehnilised küsimused tühised.',
          'expected_phrases': ['laulupidu', 'muu', 'kunstilise kvaliteedi miinimumi', 'eeldav nähtus',\
                               'tehnilised küsimused'], },
    ]
    for test_item in test_data:
        # Create test text
        text = Text( test_item['text'] )
        # Add prerequisite layers
        text.tag_layer(['words', 'sentences', 'morph_analysis', 'morph_extended'])
        visl_tagger.tag( text )
        # Tag NP chunks
        np_chunker.tag( text )
        # Check results
        assert np_chunker.output_layer in text.layers
        output_phrases = [ np_chunk.enclosing_text for np_chunk in text[np_chunker.output_layer] ]
        #print( output_phrases )
        assert test_item['expected_phrases'] == output_phrases

