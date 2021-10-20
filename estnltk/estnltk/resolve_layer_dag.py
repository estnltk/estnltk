from typing import List
import networkx as nx

from estnltk_core.taggers import Tagger, Retagger

class Taggers:
    """
    Registry for Taggers, Retaggers and their dependencies.
    Maintains a graph of layers' dependencies, which gives 
    information about prerequisite layers of each layer.
    
    The registry contains two types of entries:
    *) Regular entry  --  a tagger that creates a new layer;
    
    *) Composite entry -- a tagger that creates a new layer,
                          followed by one or more retaggers 
                          modifying the layer;
    """
    def __init__(self, taggers: List) -> None:
        self.rules = {}
        self.composite_rules = set()
        for tagger_entry in taggers:
            if isinstance(tagger_entry, list):
                # Check the first entry is Tagger, 
                # and others are Retaggers
                Taggers.validate_taggers_node_list( tagger_entry )
                self.composite_rules.add( tagger_entry[0].output_layer )
                # Add a composite entry: tagger followed by retaggers
                self.rules[tagger_entry[0].output_layer] = tagger_entry
            else:
                # Add a single tagger
                if not isinstance(tagger_entry, Tagger) or not issubclass( tagger_entry.__class__, Tagger ):
                    raise Exception('(!) Expected a subclass of Tagger, but got {}.'.format(type(tagger_entry)) )
                if issubclass( tagger_entry.__class__, Retagger ):
                    raise Exception('(!) Expected a Tagger, not Retagger ({}).'.format( tagger_entry.__class__.__name__ ) )
                self.rules[tagger_entry.output_layer] = tagger_entry
        self.graph = self._make_graph()

    def update(self, tagger):
        '''Updates the registry with a new tagger. 
           Note that this should be a tagger, not retagger: 
           an exception will be raised if a retagger is passed. 
           TODO: find a better name for this method ?
        '''
        if not isinstance(tagger, Tagger) or not issubclass( tagger.__class__, Tagger ):
            raise Exception('(!) Expected a subclass of Tagger.' )
        if issubclass( tagger.__class__, Retagger ):
            raise Exception('(!) Expected a Tagger, not Retagger.' )
        output_layer = tagger.output_layer
        if output_layer not in self.composite_rules:
            self.rules[output_layer] = tagger
        else:
            new_listing = self.rules[output_layer].copy()
            new_listing[0] = tagger
            Taggers.validate_taggers_node_list( new_listing )
            self.rules[output_layer][0] = tagger
        self.graph = self._make_graph()

    def add_retagger(self, retagger):
        '''Adds a new retagger to the registry. 
           If the layer already has retaggers, adds the given retagger to 
           the end of retaggers list (so that it will be applied lastly). 
           Raises an exception if there is no tagger for creating the 
           layer in the registry. '''
        if not isinstance(tagger, Retagger) or not issubclass( retagger.__class__, Retagger ):
            raise Exception('(!) Expected a subclass of Retagger.' )
        output_layer = retagger.output_layer
        if output_layer not in self.rules:
            raise Exception( '(!) Cannot add a retagger for the layer {!r}: '+
                             'no tagger for creating the layer!'.format( output_layer ) )
        if output_layer not in self.composite_rules:
            self.rules[output_layer] = [ self.rules[output_layer] ]
            self.composite_rules.add( output_layer )
        self.rules[output_layer].append( retagger )
        self.graph = self._make_graph()

    def clear_retaggers(self, layer):
        '''Removes all the retaggers modifying the given layer.'''
        if layer in self.rules and layer in self.composite_rules:
            assert isinstance(self.rules[layer], list)
            self.rules[layer] = self.rules[layer][0]
            self.composite_rules.remove( layer )

    def _make_graph(self):
        '''Builds a dependency graph from input/output layers of taggers (and retaggers).'''
        graph = nx.DiGraph()
        graph.add_nodes_from(self.rules)
        for layer_name, tagger_entry in self.rules.items():
            taggers_listing = tagger_entry
            if layer_name not in self.composite_rules:
                taggers_listing = [ tagger_entry ]
            for tagger in taggers_listing:
                for dep in tagger.input_layers:
                    if dep != tagger.output_layer:
                        graph.add_edge(dep, layer_name)
        assert nx.is_directed_acyclic_graph(graph)
        return graph

    @staticmethod
    def validate_taggers_node_list( taggers: List ):
        '''Validates that the taggers list is suitable for registry's entry.'''
        expect_msg = 'Expected a list containing a Tagger creating a layer, '+\
                     'followed by one or more Retaggers modifying the layer.'
        if not isinstance( taggers, list ):
            raise Exception('(!) '+expect_msg )
        if len(taggers) < 1:
            raise Exception('(!) Unexpected empty list! ' + expect_msg )
        first_tagger = taggers[0]
        if not isinstance(first_tagger, Tagger) or not issubclass( first_tagger.__class__, Tagger ):
            raise Exception('(!) Expected a subclass of Tagger for the first list entry.' )
        if issubclass( first_tagger.__class__, Retagger ):
            raise Exception('(!) The first entry in the taggers list should be Tagger, not Retagger.' )
        target_layer = first_tagger.output_layer
        for tagger in taggers[1:]:
            if not isinstance( tagger, Retagger ) or not issubclass( tagger.__class__, Retagger ):
                raise Exception('(!) Expected a subclass of Retagger, but got {}'.format(type(tagger)))
            if tagger.output_layer != target_layer:
                raise Exception('(!) Unexpected output_layer {!r} in {}!'+\
                                ' Expecting {!r} as the output_layer.'.format( \
                                           tagger.output_layer, \
                                           tagger.__class__.__name__, \
                                           target_layer ) )

    def create_layer_for_text(self, layer_name, text):
        '''Creates given layer for the given text using the available taggers/retaggers.'''
        if layer_name not in self.rules:
            raise Exception('(!) No tagger registered for creating layer {!r}.'.format( layer_name ) )
        if layer_name in self.composite_rules:
            self.rules[layer_name][0].tag( text )
            for retagger in self.rules[layer_name][1:]:
                retagger.retag( text )
        else:
            self.rules[layer_name].tag(text)

    def list_layers(self):
        '''Lists creatable layers in a topological order.'''
        return nx.topological_sort(self.graph)

    def _repr_html_(self):
        records = []
        for layer_name in self.list_layers():
            if layer_name in self.composite_rules:
                records.append( self.rules[layer_name][0].parameters() )
                for retagger in self.rules[layer_name][1:]:
                    records.append( retagger.parameters() )
            else:
                records.append( self.rules[layer_name].parameters() )
        import pandas
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

        self.taggers.create_layer_for_text( layer_name, text )
        return text


from .taggers.text_segmentation.tokens_tagger import TokensTagger
from .taggers.text_segmentation.word_tagger import WordTagger
from .taggers.text_segmentation.compound_token_tagger import CompoundTokenTagger
from .taggers.text_segmentation.sentence_tokenizer import SentenceTokenizer
from .taggers.text_segmentation.paragraph_tokenizer import ParagraphTokenizer
from .taggers.morph_analysis.morf import VabamorfTagger
from .taggers.morph_analysis.vm_est_cat_names import VabamorfEstCatConverter
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
                 compound    =DEFAULT_PARAM_COMPOUND,
                 slang_lex   =False,
                 use_reorderer=True,
                 predisambiguate =False,
                 postdisambiguate=False):
    vabamorf_tagger = VabamorfTagger(
                                     disambiguate=disambiguate,
                                     guess=guess,
                                     propername=propername,
                                     phonetic=phonetic,
                                     compound=compound,
                                     slang_lex=slang_lex,
                                     use_reorderer=use_reorderer,
                                     predisambiguate =predisambiguate,
                                     postdisambiguate=postdisambiguate
                                     )

    taggers = Taggers([TokensTagger(), WordTagger(), CompoundTokenTagger(),
                       SentenceTokenizer(), ParagraphTokenizer(),
                       vabamorf_tagger, MorphExtendedTagger(), ClauseSegmenter(),
                       VabamorfEstCatConverter()])
    return Resolver(taggers)


DEFAULT_RESOLVER = make_resolver()
