from typing import List
import networkx as nx


class Taggers:
    """
    Registry for Taggers and their dependencies.
    """
    def __init__(self, taggers: List) -> None:
        self.rules = {}
        for tagger in taggers:
            self.rules[tagger.layer_name] = tagger
        self.graph = self._make_graph()

    def update(self, tagger):
        self.rules[tagger.layer_name] = tagger
        self.graph = self._make_graph()

    def _make_graph(self):
        graph = nx.DiGraph()
        graph.add_nodes_from(self.rules)
        for layer_name, tagger in self.rules.items():
            for dep in tagger.depends_on:
                graph.add_edge(dep, layer_name)
        assert nx.is_directed_acyclic_graph(graph)
        return graph

    def list_layers(self):
        return nx.topological_sort(self.graph)

    def _repr_html_(self):
        records = []
        for layer_name in self.list_layers():
            records.append(self.rules[layer_name].parameters())
        import pandas
        pandas.set_option('display.max_colwidth', -1)
        df = pandas.DataFrame.from_records(records, columns=['name',
                                                             'layer',
                                                             'attributes',
                                                             'depends_on',
                                                             'configuration'])
        return df.to_html(index=False)


class Resolver:
    """
    Use Taggers to tag layers.
    """
    def __init__(self, taggers: Taggers) -> None:
        self.taggers = taggers

    def update(self, tagger):
        self.taggers.update(tagger)

    def taggers(self):
        return self.taggers

    def list_layers(self):
        return self.taggers.list_layers()

    def apply(self, text: 'Text', layer_name: str) -> 'Text':
        if layer_name in text.layers.keys():
            return text
        for prerequisite in self.taggers.graph.predecessors(layer_name):
            self.apply(text, prerequisite)

        self.taggers.rules[layer_name].tag(text)
        return text


from .taggers import TokensTagger
from .taggers import WordTagger
from .taggers import CompoundTokenTagger
from .taggers import SentenceTokenizer
from .taggers import ParagraphTokenizer
from .taggers.morf import VabamorfTagger
from .taggers import MorphExtendedTagger


def make_resolver(
                 disambiguate=True,
                 guess=True,
                 propername=True,
                 phonetic=False,
                 compound=True):
    vabamorf_tagger = VabamorfTagger(
                                     disambiguate=disambiguate,
                                     guess=guess,
                                     propername=propername,
                                     phonetic=phonetic,
                                     compound=compound
                                     )

    taggers = Taggers([TokensTagger(), WordTagger(), CompoundTokenTagger(),
                       SentenceTokenizer(), ParagraphTokenizer(),
                       vabamorf_tagger, MorphExtendedTagger()])
    return Resolver(taggers)


DEFAULT_RESOLVER = make_resolver()
