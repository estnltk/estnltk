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
        if layer_name in text.layers:
            return text
        for prerequisite in self.taggers.graph.predecessors(layer_name):
            self.apply(text, prerequisite)

        self.taggers.rules[layer_name].tag(text)
        return text


from .taggers.text_segmentation.tokens_tagger import TokensTagger
from .taggers.text_segmentation.word_tagger import WordTagger
from .taggers.text_segmentation.compound_token_tagger import CompoundTokenTagger
from .taggers.text_segmentation.sentence_tokenizer import SentenceTokenizer
from .taggers.text_segmentation.paragraph_tokenizer import ParagraphTokenizer
from .taggers.morph_analysis.morf import VabamorfTagger
from .taggers.syntax_preprocessing.morph_extended_tagger import MorphExtendedTagger
from .taggers.text_segmentation.clause_segmenter import ClauseSegmenter    # Requires Java

# Load default configuration for morph analyser
from .taggers.morph_analysis.morf_common import DEFAULT_PARAM_DISAMBIGUATE, DEFAULT_PARAM_GUESS
from .taggers.morph_analysis.morf_common import DEFAULT_PARAM_PROPERNAME, DEFAULT_PARAM_PHONETIC
from .taggers.morph_analysis.morf_common import DEFAULT_PARAM_COMPOUND


def make_resolver(
                 disambiguate=DEFAULT_PARAM_DISAMBIGUATE,
                 guess       =DEFAULT_PARAM_GUESS,
                 propername  =DEFAULT_PARAM_PROPERNAME,
                 phonetic    =DEFAULT_PARAM_PHONETIC,
                 compound    =DEFAULT_PARAM_COMPOUND):
    vabamorf_tagger = VabamorfTagger(
                                     disambiguate=disambiguate,
                                     guess=guess,
                                     propername=propername,
                                     phonetic=phonetic,
                                     compound=compound
                                     )

    taggers = Taggers([TokensTagger(), WordTagger(), CompoundTokenTagger(),
                       SentenceTokenizer(), ParagraphTokenizer(),
                       vabamorf_tagger, MorphExtendedTagger(), ClauseSegmenter()])
    return Resolver(taggers)


DEFAULT_RESOLVER = make_resolver()
