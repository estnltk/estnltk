from estnltk_core import Layer

from estnltk_core.common import load_text_class

def test_layer_display():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    t = Text("0123456789")
    layer = Layer(name='base', ambiguous=False)
    layer.add_annotation((1, 3))
    layer.add_annotation((7, 9))
    t.add_layer( layer )
    
    # In order to fix this, we need 'estnltk.visualisation' which adds dependencies
    # TODO: can we make an extract from 'estnltk.visualisation' concerning only layer.display()
    layer.display()