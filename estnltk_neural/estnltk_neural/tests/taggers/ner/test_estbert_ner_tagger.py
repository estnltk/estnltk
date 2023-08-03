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
         (176, 188, 'Tiit Rammuli', 'PER'), 
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
        [(0, 15, 'Tarmo Kruusimäe', 'PER'), 
         (18, 29, 'Vaiko Eplik', 'PER'), 
         (48, 56, 'Euroopat', 'LOC'), 
         (58, 67, 'Läänemets', 'PER'), 
         (85, 90, 'Homme', 'DATE'), 
         (100, 122, 'Tartu Linnaraamatukogu', 'ORG'), 
         (140, 153, 'maalikunstnik', 'TITLE'), 
         (154, 166, 'Ove Büttneri', 'PER'), 
         (168, 175, 'graafik', 'TITLE'), 
         (176, 188, 'Tiit Rammuli', 'PER'), 
         (195, 209, 'Tiina Vilbergi', 'PER'), 
         (221, 231, '"Loomaaed"', 'PROD')]


@pytest.mark.skipif(not check_if_transformers_is_available(),
                    reason="package tranformers is required for this test")
@pytest.mark.skipif(not check_if_pytorch_is_available(),
                    reason="package pytorch is required for this test")
@pytest.mark.skipif(ESTBERTNER_V1_PATH is None,
                    reason="EstBERTNERTagger's model location not known. "+\
                           "Use estnltk.download('estbertner') to get the missing resources.")
def test_estbertner_v1_postfixes():
    # Initialize model without any postfixes
    from estnltk_neural.taggers import EstBERTNERTagger
    neural_ner_tagger = EstBERTNERTagger(postfix_expand_suffixes=False, 
                                         postfix_concat_same_type_entities=False, 
                                         postfix_remove_infix_matches=False)
    # 1) Test _postfix_expand_suffixes
    text = Text('Seni Kuressaarel otseliin Pärnuga puudub. '+\
                'Calev konnib Brusselisse. Kanepi alevik nimetatakse Kaiaks. '
                'Helmutil läheb hästi, Ilse vaatas Ellit kahtlustavalt, '+\
                'Rolandi kavalus ei läinud läbi isegi Tartus Gogoli raamatukogus. ')
    neural_ner_tagger.tag(text)
    output_layer = neural_ner_tagger.output_layers[0]
    output_tokens_layer = neural_ner_tagger.output_layers[1]
    #print( _ner_spans_as_tuples( text[output_layer] ) )
    assert _ner_spans_as_tuples( text[output_layer] ) == \
       [(5, 16, 'Kuressaarel', 'LOC'), (26, 31, 'Pärnu', 'LOC'), 
        (42, 45, 'Cal', 'PER'), (55, 63, 'Brusseli', 'LOC'), (68, 81, 'Kanepi alevik', 'LOC'), (94, 98, 'Kaia', 'LOC'), 
        (102, 108, 'Helmut', 'PER'), (124, 126, 'Il', 'PER'), (136, 140, 'Elli', 'PER'), 
        (157, 163, 'Roland', 'PER'), (194, 200, 'Tartus', 'LOC'), (201, 207, 'Gogoli', 'ORG')]
    # Apply _postfix_expand_suffixes
    neural_ner_tagger._postfix_expand_suffixes(text, text[output_layer], text[output_tokens_layer])
    #print( _ner_spans_as_tuples( text[output_layer] ) )
    assert _ner_spans_as_tuples( text[output_layer] ) == \
       [(5, 16, 'Kuressaarel', 'LOC'), (26, 33, 'Pärnuga', 'LOC'), 
        (42, 47, 'Calev', 'PER'), (55, 66, 'Brusselisse', 'LOC'), (68, 81, 'Kanepi alevik', 'LOC'), (94, 100, 'Kaiaks', 'LOC'), 
        (102, 110, 'Helmutil', 'PER'), (124, 128, 'Ilse', 'PER'), (136, 141, 'Ellit', 'PER'), 
        (157, 164, 'Rolandi', 'PER'), (194, 200, 'Tartus', 'LOC'), (201, 207, 'Gogoli', 'ORG')]

    # 2) Test _postfix_concat_same_type_entities
    text = Text('RMK keelas Nipernaadil Rakvere linnametsa siseneda. '+\
                'Myanmari mässulised olid ka kuulnud Bangkokis toimuvast. '+\
                'See sundis MacArthurit lahkuma Kenyast ja siirduma Mecklenburgi. ')
    neural_ner_tagger.tag(text)
    output_layer = neural_ner_tagger.output_layers[0]
    output_tokens_layer = neural_ner_tagger.output_layers[1]
    #print( _ner_spans_as_tuples( text[output_layer] ) )
    assert _ner_spans_as_tuples( text[output_layer] ) == \
        [(0, 3, 'RMK', 'ORG'), (11, 13, 'Ni', 'PER'), (23, 30, 'Rakvere', 'LOC'), 
         (52, 54, 'My', 'LOC'), (88, 97, 'Bangkokis', 'LOC'), 
         (120, 124, 'MacA', 'PER'), (126, 129, 'hur', 'PER'), (140, 143, 'Ken', 'LOC'), (143, 145, 'ya', 'LOC'), 
         (160, 162, 'Me', 'LOC'), (162, 164, 'ck', 'LOC'), (164, 167, 'len', 'LOC'), (167, 172, 'burgi', 'LOC')]
    # Apply postfixes
    neural_ner_tagger._postfix_expand_suffixes(text, text[output_layer], text[output_tokens_layer])
    neural_ner_tagger._postfix_concatenate_same_type_entities(text, text[output_layer])
    #print( _ner_spans_as_tuples( text[output_layer] ) )
    assert _ner_spans_as_tuples( text[output_layer] ) == \
        [(0, 3, 'RMK', 'ORG'), (11, 22, 'Nipernaadil', 'PER'), (23, 30, 'Rakvere', 'LOC'), 
         (52, 60, 'Myanmari', 'LOC'), (88, 97, 'Bangkokis', 'LOC'), 
         (120, 124, 'MacA', 'PER'), (126, 131, 'hurit', 'PER'), (140, 147, 'Kenyast', 'LOC'), (160, 172, 'Mecklenburgi', 'LOC')]


@pytest.mark.skipif(not check_if_transformers_is_available(),
                    reason="package tranformers is required for this test")
@pytest.mark.skipif(not check_if_pytorch_is_available(),
                    reason="package pytorch is required for this test")
@pytest.mark.skipif(ESTBERTNER_V2_PATH is None,
                    reason="EstBERTNERTagger's model location not known. "+\
                           "Use estnltk.download('estbertner_v2') to get the missing resources.")
def test_estbertner_v2_postfixes():
    # Initialize model without any postfixes
    from estnltk_neural.taggers import EstBERTNERTagger
    from estnltk_neural.taggers import EstBERTNERTagger
    neural_ner_tagger = EstBERTNERTagger(model_location=ESTBERTNER_V2_PATH,
                                         postfix_expand_suffixes=False, 
                                         postfix_concat_same_type_entities=False, 
                                         postfix_remove_infix_matches=False)
    # 1) Test _postfix_expand_suffixes
    text = Text('Seni Kuressaarel otseliin Pärnuga puudub. '+\
                'Calev konnib Brusselisse. Kanepi alevik nimetatakse Kaiaks. '
                'Helmutil läheb hästi, Ilse vaatas Ellit kahtlustavalt, '+\
                'Rolandi kavalus ei läinud läbi isegi Tartus Gogoli raamatukogus. ')
    neural_ner_tagger.tag(text)
    output_layer = neural_ner_tagger.output_layers[0]
    output_tokens_layer = neural_ner_tagger.output_layers[1]
    #print( _ner_spans_as_tuples( text[output_layer] ) )
    assert _ner_spans_as_tuples( text[output_layer] ) == \
       [(5, 9, 'Kure', 'GPE'), (9, 15, 'ssaare', 'GPE'), (26, 33, 'Pärnuga', 'GPE'), 
        (42, 47, 'Calev', 'PER'), (55, 58, 'Bru', 'GPE'), (58, 63, 'sseli', 'GPE'), (68, 81, 'Kanepi alevik', 'GPE'), (94, 97, 'Kai', 'GPE'), 
        (102, 105, 'Hel', 'PER'), (124, 128, 'Ilse', 'PER'), (136, 140, 'Elli', 'PER'), 
        (157, 164, 'Rolandi', 'PER'), (194, 199, 'Tartu', 'GPE'), (201, 207, 'Gogoli', 'PROD'), (208, 220, 'raamatukogus', 'ORG')]
    # Apply _postfix_expand_suffixes
    neural_ner_tagger._postfix_expand_suffixes(text, text[output_layer], text[output_tokens_layer])
    #print( _ner_spans_as_tuples( text[output_layer] ) )
    assert _ner_spans_as_tuples( text[output_layer] ) == \
       [(5, 9, 'Kure', 'GPE'), (9, 16, 'ssaarel', 'GPE'), (26, 33, 'Pärnuga', 'GPE'), 
        (42, 47, 'Calev', 'PER'), (55, 58, 'Bru', 'GPE'), (58, 66, 'sselisse', 'GPE'), (68, 81, 'Kanepi alevik', 'GPE'), (94, 100, 'Kaiaks', 'GPE'), 
        (102, 110, 'Helmutil', 'PER'), (124, 128, 'Ilse', 'PER'), (136, 141, 'Ellit', 'PER'), 
        (157, 164, 'Rolandi', 'PER'), (194, 200, 'Tartus', 'GPE'), (201, 207, 'Gogoli', 'PROD'), (208, 220, 'raamatukogus', 'ORG')]

    # 2) Test _postfix_concat_same_type_entities
    text = Text('RMK keelas Nipernaadil Rakvere linnametsa siseneda. '+\
                'Myanmari mässulised olid ka kuulnud Bangkokis toimuvast. '+\
                'See sundis MacArthurit lahkuma Kenyast ja siirduma Mecklenburgi. ')
    neural_ner_tagger.tag(text)
    output_layer = neural_ner_tagger.output_layers[0]
    output_tokens_layer = neural_ner_tagger.output_layers[1]
    #print( _ner_spans_as_tuples( text[output_layer] ) )
    assert _ner_spans_as_tuples( text[output_layer] ) == \
        [(0, 3, 'RMK', 'ORG'), (11, 13, 'Ni', 'PER'), (13, 18, 'perna', 'PER'), (23, 26, 'Rak', 'GPE'), (26, 30, 'vere', 'GPE'), 
         (52, 54, 'My', 'GPE'), (88, 90, 'Ba', 'GPE'), (90, 92, 'ng', 'GPE'), (92, 97, 'kokis', 'GPE'), 
         (120, 122, 'Ma', 'PER'), (122, 125, 'cAr', 'PER'), (125, 127, 'th', 'PER'), (127, 130, 'uri', 'PER'), 
         (140, 142, 'Ke', 'GPE'), (142, 147, 'nyast', 'GPE'), (160, 162, 'Me', 'GPE'), (162, 172, 'cklenburgi', 'GPE')]
    # Apply postfixes
    neural_ner_tagger._postfix_expand_suffixes(text, text[output_layer], text[output_tokens_layer])
    neural_ner_tagger._postfix_concatenate_same_type_entities(text, text[output_layer])
    #print( _ner_spans_as_tuples( text[output_layer] ) )
    assert _ner_spans_as_tuples( text[output_layer] ) == \
        [(0, 3, 'RMK', 'ORG'), (11, 22, 'Nipernaadil', 'PER'), (23, 30, 'Rakvere', 'GPE'), 
         (52, 60, 'Myanmari', 'GPE'), (88, 97, 'Bangkokis', 'GPE'), 
         (120, 131, 'MacArthurit', 'PER'), (140, 147, 'Kenyast', 'GPE'), (160, 172, 'Mecklenburgi', 'GPE')]

