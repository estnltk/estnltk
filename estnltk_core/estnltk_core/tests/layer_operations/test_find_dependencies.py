from estnltk_core import Layer
from estnltk_core.common import load_text_class

from estnltk_core.layer_operations.layer_dependencies import find_layer_dependencies

def test_find_layer_dependencies():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    text = Text('Tere!')
    layers = [ Layer('tokens', text_object=text, ambiguous=False),
               Layer('compound_tokens', text_object=text, enveloping='tokens', ambiguous=False),
               Layer('words', text_object=text),
               Layer('sentences', text_object=text, enveloping='words'),
               Layer('paragraphs', text_object=text, enveloping='sentences'),
               Layer('morph_analysis', text_object=text, parent='words'),
               Layer('gt_morph_analysis', text_object=text, parent='morph_analysis'),
               Layer('hfst_morph_analysis', text_object=text, parent='words'),
               Layer('morph_extended', text_object=text, parent='morph_analysis'), 
               Layer('vislcg_syntax', text_object=text, parent='morph_extended'), 
               Layer('vislcg_syntax_sentences', text_object=text, enveloping='vislcg_syntax'), ]
    for layer in layers:
        text.add_layer( layer )
    assert find_layer_dependencies(text, 'tokens') == set()
    assert find_layer_dependencies(text, 'gt_morph_analysis') == {'words', 'morph_analysis'}
    assert find_layer_dependencies(text, 'vislcg_syntax') == {'morph_extended', 'morph_analysis', 'words'}
    assert find_layer_dependencies(text, 'paragraphs') == {'sentences', 'words'}
    assert find_layer_dependencies(text, 'vislcg_syntax_sentences') == \
                                         {'vislcg_syntax', 'morph_extended', 'morph_analysis', 'words'}
    assert find_layer_dependencies(text, 'vislcg_syntax_sentences', include_enveloping=False) == set()
    assert find_layer_dependencies(text, 'vislcg_syntax_sentences', include_parents=False) == {'vislcg_syntax'}


def test_find_layer_dependencies_reverse():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    text = Text('Tere!')
    layers = [ Layer('tokens', text_object=text, ambiguous=False),
               Layer('compound_tokens', text_object=text, enveloping='tokens', ambiguous=False),
               Layer('words', text_object=text),
               Layer('sentences', text_object=text, enveloping='words'),
               Layer('paragraphs', text_object=text, enveloping='sentences'),
               Layer('morph_analysis', text_object=text, parent='words'),
               Layer('gt_morph_analysis', text_object=text, parent='morph_analysis'),
               Layer('hfst_morph_analysis', text_object=text, parent='words'),
               Layer('morph_extended', text_object=text, parent='morph_analysis'), 
               Layer('vislcg_syntax', text_object=text, parent='morph_extended'), 
               Layer('vislcg_syntax_sentences', text_object=text, enveloping='vislcg_syntax'), ]
    for layer in layers:
        text.add_layer( layer )
    assert find_layer_dependencies(text, 'paragraphs', reverse=True) == set()
    assert find_layer_dependencies(text, 'tokens', reverse=True) == {'compound_tokens'}
    assert find_layer_dependencies(text, 'gt_morph_analysis', reverse=True) == set()
    assert find_layer_dependencies(text, 'vislcg_syntax', reverse=True) == {'vislcg_syntax_sentences'}
    assert find_layer_dependencies(text, 'words', reverse=True) == {'vislcg_syntax_sentences', 'morph_analysis',\
                                                                    'vislcg_syntax', 'paragraphs', 'morph_extended',\
                                                                    'sentences', 'gt_morph_analysis', \
                                                                    'hfst_morph_analysis'}
    assert find_layer_dependencies(text, 'words', reverse=True, include_parents=False) == \
                                                                   {'paragraphs', 'sentences'}
    assert find_layer_dependencies(text, 'words', reverse=True, include_enveloping=False) == \
                                                                   {'morph_analysis', 'vislcg_syntax', 'morph_extended',\
                                                                    'gt_morph_analysis', 'hfst_morph_analysis'}

