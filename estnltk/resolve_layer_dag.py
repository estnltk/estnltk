from typing import List
import networkx as nx

class Rule:
    def __init__(self, layer_name: str, tagger, depends_on: List[str]) -> None:
        self.depends_on = depends_on
        self.tagger = tagger
        self.layer_name = layer_name


class Resolver:
    def __init__(self, rules: List[Rule]) -> None:

        self.rules = rules
        graph = nx.DiGraph()
        graph.add_nodes_from([i.layer_name for i in self.rules])
        for rule in self.rules:
            for dep in rule.depends_on:
                graph.add_edge(dep, rule.layer_name)

        assert nx.is_directed_acyclic_graph(graph)
        self.graph = graph

    def apply(self, text: 'Text', layer_name: str) -> 'Text':
        if layer_name in text.layers.keys():
            return text
        for prerequisite in self.graph.predecessors(layer_name):
            self.apply(text, prerequisite)

        rule = [i.tagger for i in self.rules if i.layer_name == layer_name][0]
        rule.tag(text)
        return text

#RESOLVER is a registry of taggers and names.
# Taggers must be imported relatively (with a .)
# This section must be at the end of the file.
from .taggers import TokensTagger
from .taggers import WordTokenizer
from .taggers import CompoundTokenTagger
from .taggers import SentenceTokenizer
from .taggers import ParagraphTokenizer
from .taggers.premorph.premorf import WordNormalizingTagger
from .taggers.morf import VabamorfTagger


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
    rules = [
        Rule('tokens', tagger=TokensTagger(), depends_on=[]),
        Rule('compound_tokens', tagger=CompoundTokenTagger(), depends_on=['tokens']),
        Rule('words', tagger=WordTokenizer(), depends_on=['compound_tokens']),
        Rule('sentences', tagger=SentenceTokenizer(), depends_on=['words']),
        Rule('paragraphs', tagger=ParagraphTokenizer(), depends_on=['sentences']),
        Rule('normalized', tagger=WordNormalizingTagger(), depends_on=['words']),
        Rule('morf_analysis', tagger=vabamorf_tagger, depends_on=['normalized']),
        ]

    return Resolver(rules)

DEFAULT_RESOLVER = make_resolver()
