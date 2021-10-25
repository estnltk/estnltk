from typing import List, Union
import networkx as nx

from estnltk_core.taggers import Tagger, Retagger

class Taggers:
    """Registry for layers and taggers required for layer creation. 
    Maintains a graph of layers' dependencies, which gives 
    information about prerequisite layers of each layer, 
    and holds taggers (and retaggers) that are needed for 
    layer creation. 
    
    Each entry (node in the graph) maps name of a layer to 
    the components that are required for making the layer. 
    There are two types of entries:
    *) Regular entry -- a layer created by a single tagger;
    *) Composite entry -- a layer created by a tagger, and 
                          then modified by one or more retaggers;
    
    Entries / nodes are organised as a directed acyclic graph, 
    in which arcs point from prerequisite layers to dependent 
    layers.
    
    TODO: rename: TaggerRegistry or LayerRegistry ?
    """
    def __init__(self, taggers: List) -> None:
        self.rules = {}
        self.composite_rules = set()
        for tagger_entry in taggers:
            if isinstance(tagger_entry, list):
                # Check the first entry is a tagger, 
                # and others are retaggers
                Taggers.validate_taggers_node_list( tagger_entry )
                self.composite_rules.add( tagger_entry[0].output_layer )
                # Add a composite entry: tagger followed by retaggers
                self.rules[tagger_entry[0].output_layer] = tagger_entry
            else:
                # Add a single tagger
                if not issubclass( type(tagger_entry), Tagger ):
                    raise TypeError('(!) Expected a subclass of Tagger, but got {}.'.format( type(tagger_entry) ) )
                if issubclass( type(tagger_entry), Retagger ):
                    raise TypeError('(!) Expected a subclass of Tagger, not Retagger ({}).'.format( tagger_entry.__class__.__name__ ) )
                self.rules[tagger_entry.output_layer] = tagger_entry
        self.graph = self._make_graph()

    def update(self, tagger: Union[Tagger, Retagger] ) -> None:
        '''Updates the registry with the given tagger or retagger.
        '''
        if issubclass( type(tagger), Retagger ):
            self.add_retagger( tagger )
        elif issubclass( type(tagger), Tagger ):
            self.add_tagger( tagger )
        else:
            raise TypeError('(!) Expected a subclass of Tagger or Retagger, not {}.'.format(type(tagger)) )

    def add_tagger(self, tagger: Tagger) -> None:
        '''Adds a tagger to the registry. 
           If the registry already contains an entry for creating 
           tagger's output_layer, then the old entry will be 
           overwritten: this will be the new tagger for creating 
           the layer. 
           Note that the argument should be a tagger, not retagger: 
           an exception will be raised if a retagger is passed. '''
        if not issubclass( type(tagger), Tagger ):
            raise TypeError('(!) Expected a subclass of Tagger, but got {}.'.format( type(tagger) ) )
        if issubclass( type(tagger), Retagger ):
            raise TypeError('(!) Expected a subclass of Tagger, not Retagger ({}).'.format( tagger.__class__.__name__ ) )
        output_layer = tagger.output_layer
        if output_layer not in self.composite_rules:
            self.rules[output_layer] = tagger
        else:
            new_listing = self.rules[output_layer].copy()
            new_listing[0] = tagger
            Taggers.validate_taggers_node_list( new_listing )
            self.rules[output_layer][0] = tagger
        self.graph = self._make_graph()

    def add_retagger(self, retagger: Retagger) -> None:
        '''Adds a new retagger to the registry. 
           If the layer already has retaggers, adds the given retagger to 
           the end of retaggers list (so that it will be applied lastly). 
           Raises an exception if there is no tagger for creating the 
           layer in the registry. '''
        if not issubclass( type(retagger), Retagger ):
            raise TypeError('(!) Expected a subclass of Retagger, but got {}.'.format( type(retagger) ) )
        output_layer = retagger.output_layer
        if output_layer not in self.rules:
            raise ValueError( ('(!) Cannot add a retagger for the layer {!r}: '+
                               'no tagger for creating the layer!').format( output_layer ) )
        if output_layer not in self.composite_rules:
            self.rules[output_layer] = [ self.rules[output_layer] ]
            self.composite_rules.add( output_layer )
        self.rules[output_layer].append( retagger )
        self.graph = self._make_graph()

    def clear_retaggers(self, layer_name: str) -> None:
        '''Removes all the retaggers modifying the given layer.
           Note: the tagger creating the layer will remain. '''
        if layer_name in self.rules and layer_name in self.composite_rules:
            assert isinstance(self.rules[layer_name], list)
            self.rules[layer_name] = self.rules[layer_name][0]
            self.composite_rules.remove( layer_name )
            # Important: we also need to update the graph
            self.graph = self._make_graph()

    def _make_graph(self) -> None:
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
        if not nx.is_directed_acyclic_graph(graph):
            raise Exception('(!) The layer graph is not acyclic! '+\
                            'Please eliminate circular dependencies '+\
                            'between taggers/retaggers.')
        return graph

    @staticmethod
    def validate_taggers_node_list( taggers: List[ Union[Tagger, Retagger] ] ) -> None:
        '''Validates that the taggers list is suitable for registry's entry.
           A suitable list contains either a single tagger, or a tagger 
           followed by one or more retaggers modifying the same layer.
        '''
        expect_msg = 'Expected a list containing a tagger creating a layer, '+\
                     'followed by one or more retaggers modifying the layer.'
        if not isinstance( taggers, list ):
            raise TypeError('(!) '+expect_msg )
        if len(taggers) < 1:
            raise ValueError('(!) Unexpected empty list! ' + expect_msg )
        first_tagger = taggers[0]
        if not issubclass( type(first_tagger), Tagger ):
            raise TypeError('(!) Expected a subclass of Tagger for the first list entry, but got {}.'.format( type(first_tagger) ) )
        if issubclass( type(first_tagger), Retagger ):
            raise TypeError('(!) The first entry in the taggers list should be a tagger, not retagger ({}).'.format( type(first_tagger) ) )
        target_layer = first_tagger.output_layer
        for tagger in taggers[1:]:
            if not issubclass( type(tagger), Retagger ):
                raise TypeError('(!) Expected a subclass of Retagger, but got {}'.format(type(tagger)))
            if tagger.output_layer != target_layer:
                raise ValueError( ('(!) Unexpected output_layer {!r} in {}!'+\
                                   ' Expecting {!r} as the output_layer.').format( \
                                           tagger.output_layer, \
                                           tagger.__class__.__name__, \
                                           target_layer ) )

    def create_layer_for_text(self,  layer_name: str,  text: Union['BaseText', 'Text']) -> None:
        '''Creates given layer for the given text using the available taggers/retaggers.
           The method returns None, as the created layer will be attached to the given 
           Text object.
        '''
        if layer_name not in self.rules:
            raise Exception('(!) No tagger registered for creating layer {!r}.'.format( layer_name ) )
        if layer_name in self.composite_rules:
            self.rules[layer_name][0].tag( text )
            for retagger in self.rules[layer_name][1:]:
                retagger.retag( text )
        else:
            self.rules[layer_name].tag(text)

    def list_layers(self) -> List[str]:
        '''Lists creatable layers in a topological order.'''
        return nx.topological_sort(self.graph)

    def _repr_html_(self):
        records = []
        for layer_name in self.list_layers():
            if layer_name in self.composite_rules:
                # A tagger followed by retagger(s)
                records.append( self.rules[layer_name][0].parameters() )
                for retagger in self.rules[layer_name][1:]:
                    records.append( retagger.parameters() )
            else:
                # A single tagger
                records.append( self.rules[layer_name].parameters() )
        import pandas
        df = pandas.DataFrame.from_records(records, columns=['name',
                                                             'layer',
                                                             'attributes',
                                                             'depends_on',
                                                             'configuration'])
        return df.to_html(index=False)


class Resolver:
    """Resolver resolves layer dependencies and handles layer creation. 
       Upon creating a layer, it uses the Taggers registry to (recursively) 
       find and create all the prerequisite layers of the target layer."""

    def __init__(self, taggers: Taggers) -> None:
        self.taggers = taggers

    def update(self, tagger: Union[Tagger, Retagger]) -> None:
        '''Updates the Taggers registry with the given tagger or retagger.'''
        self.taggers.update(tagger)

    def taggers(self):
        '''Returns the Taggers registry of this Resolver.'''
        return self.taggers

    def clear_retaggers(self, layer_name: str) -> None:
        '''Removes all the retaggers modifying the given layer.
           Note: the tagger creating the layer will remain. '''
        self.taggers.clear_retaggers(layer_name)

    def list_layers(self) -> List[str]:
        '''Lists layers that can be created by this resolver in the order 
           in which they should be created.'''
        return self.taggers.list_layers()

    def apply(self, text: Union['BaseText', 'Text'], layer_name: str) -> Union['BaseText', 'Text']:
        '''Creates the given layer along with all the prerequisite layers. 
           The layers will be attached to the input Text object. 
           Returns the input Text object.
        '''
        if layer_name in text.layers:
            return text
        if layer_name not in self.taggers.graph.nodes:
            raise Exception('(!) No tagger registered for creating layer {!r}.'.format( layer_name ) )
        for prerequisite in self.taggers.graph.predecessors(layer_name):
            self.apply(text, prerequisite)

        self.taggers.create_layer_for_text( layer_name, text )
        return text

    def _repr_html_(self):
        if self.taggers:
            return self.taggers._repr_html_()
