import pytest
from estnltk import Text
from estnltk.converters import layer_to_dict
from estnltk.web_taggers import SoftmaxEmbTagSumWebTagger

# Fix for DeprecationWarning: httpserver_listen_address fixture will be converted to session scope in version 1.0.0
@pytest.fixture(scope="session")
def httpserver_listen_address():
    return ("127.0.0.1", 8000)


def test_softmax_emb_tag_sum_web_tagger(httpserver):
    layer_dict = {
        'name': 'softmax_emb_tag_sum',
        'attributes': ('morphtag', 'pos', 'form'),
        'secondary_attributes': (),
        'parent': 'words',
        'enveloping': None,
        'ambiguous': False,
        'serialisation_module': None,
        'meta': {},
        'spans': [
            {'base_span': (0, 3), 'annotations': [{'morphtag': 'POS=P|NUMBER=sg|CASE=nom', 'pos': 'P', 'form': 'sg n'}]},
            {'base_span': (4, 6), 'annotations': [{'morphtag': 'POS=V|VERB_TYPE=main|MOOD=indic|TENSE=pres|PERSON=ps3|NUMBER=sg|VERB_PS=ps|VERB_POLARITY=af', 'pos': 'V', 'form': 'b'}]},
            {'base_span': (7, 12), 'annotations': [{'morphtag': 'POS=S|NOUN_TYPE=com|NUMBER=sg|CASE=nom', 'pos': 'S', 'form': 'sg n'}]},
            {'base_span': (12, 13), 'annotations': [{'morphtag': 'POS=Z|PUNCT_TYPE=Fst', 'pos': 'Z', 'form': ''}]}
        ]
    }
    path = '/1.6.7beta/tag/softmax_emb_tag_sum'
    httpserver.expect_request(path).respond_with_json(layer_dict)

    text = Text('See on lause.')
    text.tag_layer('morph_analysis')

    tagger = SoftmaxEmbTagSumWebTagger(url=httpserver.url_for(path), output_layer='softmax_emb_tag_sum')

    tagger.tag(text)
    assert layer_to_dict(text.softmax_emb_tag_sum) == layer_dict
