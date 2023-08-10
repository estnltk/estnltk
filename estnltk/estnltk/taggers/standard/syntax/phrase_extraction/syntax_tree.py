import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
import matplotlib.pyplot as plt
#from .syntax_tree_operations import *

from estnltk import Layer


class SyntaxTree:

    """
    Represent syntax layer as a directed graph with various annotations.
    TODO: describe what annotations are available and why they are useful
    Defineerib süntaksipuu networkx suunamata graafina.
    """

    def __init__(self, syntax_layer_sentence: Layer):
        """
        stanza stanza_syntax objektist graafi tegemine"""
        graph = nx.DiGraph()
        for data in syntax_layer_sentence:
            if not isinstance(data['id'], int):
                continue

            # Miks sul on tipuga siduda just need atribuudid
            # Kui sa annad ette span-i, siis on sellest loetav kogu info
            # Ainus pühjus teisi atribuute lisada on nende järgi tippe välja tõmmata
            graph.add_node(
                data['id'],
                lemma=data['lemma'],
                pos=data['upostag'],
                deprel=data['deprel'],
                form=data.text,
                span=data)
            graph.add_edge(
                data['id'] - data['id'] + data['head'],
                data['id'],
                deprel=data['deprel'])

        self.graph = graph
        self.nodes = graph.nodes
        self.edges = graph.edges

        
    #TODO params to
    def drawGraph(self, figure_size=(18.5, 10.5), title_wrap_char=120, fig_dpi=100, **kwargs):
        """Puu/graafi joonistamine
        tipp - lemma
        serv - deprel
        """
        # joonise suurus
        plt.rcParams["figure.figsize"] = figure_size

        pos = graphviz_layout(self.graph, prog='dot')
        labels = nx.get_node_attributes(self.graph, 'text') # lemma
        nx.draw(self.graph, pos, cmap = plt.get_cmap('jet'),labels=labels, with_labels=True)
        edge_labels = nx.get_edge_attributes(self.graph, 'deprel')
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels)

        return plt
        