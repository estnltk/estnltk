import pytest

from estnltk import Text
from estnltk.converters import layer_to_dict
from estnltk.web_taggers import GrammarCorrectorWebTagger


# Fix for DeprecationWarning: httpserver_listen_address fixture will be converted to session scope in version 1.0.0
@pytest.fixture(scope="session")
def httpserver_listen_address():
    return ("127.0.0.1", 8000)


def test_grammar_corrector_web_tagger_text_with_no_errors(httpserver):
    # Case 1: Test text without grammar errors
    text = Text('Olgu!')
    text.tag_layer('sentences')
    # Mock response
    response_json_dict = \
        {'corrected_text': 'Olgu!', 
         'corrections': []}
    httpserver.expect_request('/grammar').respond_with_json(response_json_dict)
    # Tag corrections
    tagger = GrammarCorrectorWebTagger(url=httpserver.url_for('/grammar'))
    tagger.tag(text)
    # Check results
    assert tagger.output_layer in text.layers
    assert len(text[tagger.output_layer]) == 0  # No suggested corrections 


def test_grammar_corrector_web_tagger_erroneous_sentence(httpserver):
    # Case 2: Test text with one erroneous sentence
    text = Text('See onn üks väega viggane lause')
    text.tag_layer('sentences')
    # Mock response
    response_json_dict = \
        {'corrected_text': 'a very vague sentence.',
         'corrections': [{'replacements': [{'value': 'a very vague sentence.'}],
                          'span': {'end': 31,
                                   'start': 0,
                                   'value': 'See onn üks väega viggane lause'}}]}
    httpserver.expect_request('/grammar').respond_with_json(response_json_dict)
    tagger = GrammarCorrectorWebTagger(url=httpserver.url_for('/grammar'))
    tagger.tag(text)
    # Check results
    assert tagger.output_layer in text.layers
    assert layer_to_dict( text[tagger.output_layer] ) == \
        {'ambiguous': True,
         'attributes': ('correction',),
         'enveloping': None,
         'meta': {},
         'name': 'grammar_corrections',
         'parent': None,
         'secondary_attributes': (),
         'serialisation_module': None,
         'spans': [{'annotations': [{'correction': 'a very vague sentence.'}],
                    'base_span': (0, 31)}]}


def test_grammar_corrector_web_tagger_erroneous_text(httpserver):
    # Case 3: Test text with 3 erroneous sentences
    text = Text('Gramatikliste veade parantamine on põõnev ülessanne. Ükss väega vikase lause olema see. Mudel oskama selles ikka parandusi teha.')
    text.tag_layer('sentences')
    # Mock response
    response_json_dict = \
        {'corrected_text': 'Grammatiliste vigade parandamine on põnev ülesanne. Üks '
                           'väga vigane lause on see. Mudel oskab selles ikka '
                           'parandusi teha.',
         'corrections': [{'replacements': [{'value': 'Grammatiliste vigade '
                                                     'parandamine'}],
                          'span': {'end': 31,
                                   'start': 0,
                                   'value': 'Gramatikliste veade parantamine'}},
                         {'replacements': [{'value': 'põnev ülesanne.'}],
                          'span': {'end': 52,
                                   'start': 35,
                                   'value': 'põõnev ülessanne.'}},
                         {'replacements': [{'value': 'Üks väga vigane'}],
                          'span': {'end': 70,
                                   'start': 53,
                                   'value': 'Ükss väega vikase'}},
                         {'replacements': [{'value': 'on'}],
                          'span': {'end': 82, 'start': 77, 'value': 'olema'}},
                         {'replacements': [{'value': 'oskab'}],
                          'span': {'end': 100, 'start': 94, 'value': 'oskama'}}]}
    httpserver.expect_request('/grammar').respond_with_json(response_json_dict)
    tagger = GrammarCorrectorWebTagger(url=httpserver.url_for('/grammar'))
    tagger.tag(text)
    # Check results
    assert tagger.output_layer in text.layers
    assert layer_to_dict( text[tagger.output_layer] ) == \
        {'ambiguous': True,
         'attributes': ('correction',),
         'enveloping': None,
         'meta': {},
         'name': 'grammar_corrections',
         'parent': None,
         'secondary_attributes': (),
         'serialisation_module': None,
         'spans': [{'annotations': [{'correction': 'Grammatiliste vigade parandamine'}],
                    'base_span': (0, 31)},
                   {'annotations': [{'correction': 'põnev ülesanne.'}],
                    'base_span': (35, 52)},
                   {'annotations': [{'correction': 'Üks väga vigane'}],
                    'base_span': (53, 70)},
                   {'annotations': [{'correction': 'on'}], 'base_span': (77, 82)},
                   {'annotations': [{'correction': 'oskab'}], 'base_span': (94, 100)}]}
