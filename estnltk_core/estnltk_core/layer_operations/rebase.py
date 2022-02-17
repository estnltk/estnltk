import networkx as nx

from .layer_dependencies import find_layer_dependencies

def rebase(text, layer, new_base):
    """
    Changes parent of the layer to new_base.

    Parameters
    ----------
    text: Union[BaseText, 'Text']
        Text object containing both the target layer and the new_base layer.
    layer: Union[BaseLayer, Layer]
        Target layer which parent layer will be changed.
    new_base: str
        Name of the new parent layer. Rebasing can be applied successfully
        only if the new parent layer is direct or indirect parent of the
        current parent layer.

    Returns
    -------
    Union[BaseText, 'Text']
        Text object in which the target layer has been rebased
    """
    dependency_layers = find_layer_dependencies(text, layer, 
                                                 include_enveloping=False,
                                                 include_parents=True)
    if new_base not in dependency_layers:
        raise ValueError("can't use '" + new_base + "' as a new base for '"+layer+"'")
    text[layer].parent = new_base
    return text
