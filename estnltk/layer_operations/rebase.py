import networkx as nx


def rebase(text, layer, new_base):
    g = nx.DiGraph()
    for layer_name, l in text.layers.items():
        if l.parent:
            g.add_edge(layer_name, l.parent)
    assert new_base in nx.descendants(g, layer), "can't use '" + new_base + "' as a new base for '"+layer+"'"
    text[layer].parent = new_base
    return text
