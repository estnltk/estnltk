from typing import List, Union
import networkx as nx
import warnings

from estnltk_core.taggers import Tagger, Retagger
from estnltk_core.taggers import TaggerLoader
from estnltk_core.taggers import TaggerLoaded


class TaggersRegistry:
    """Registry of taggers required for layer creation. 
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
    
    TaggerLoaders
    ==============
    TaggersRegistry tries to avoid the initialization of a 
    Tagger or a Retagger until it is really needed by the user 
    (the method create_layer_for_text(...) is called). 
    Therefore, TaggersRegistry's constructor accepts taggers 
    as TaggerLoaders. 
    TaggerLoader declares input layers, output layer and 
    importing path of a tagger, but does not load the tagger 
    until explicitly demanded.
    """
    def __init__(self, taggers: List):
        self._rules = {}
        self._composite_rules = set()
        for tagger_entry in taggers:
            if isinstance(tagger_entry, list):
                # Check that list is not empty
                if len(tagger_entry) == 0:
                    raise ValuerError( '(!) Expected a list of TaggerLoaders, but got an empty list.' )
                # Check that all entries are tagger loaders
                for tagger_loader in tagger_entry:
                    if not isinstance( tagger_loader, TaggerLoader ):
                        raise TypeError( '(!) Expected instance of TaggerLoader, '+\
                                         'but got {!r}'.format( type(tagger_loader) ) )
                self._composite_rules.add( tagger_entry[0].output_layer )
                # Add a composite entry: tagger followed by retaggers
                self._rules[tagger_entry[0].output_layer] = tagger_entry
            else:
                # Add a single tagger loader
                if not isinstance( tagger_entry, TaggerLoader ):
                    raise TypeError( '(!) Expected instance of TaggerLoader, '+\
                                     'but got {!r}'.format( type(tagger_entry) ) )
                self._rules[tagger_entry.output_layer] = tagger_entry
        self._graph = self._make_graph()

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
        if output_layer not in self._composite_rules:
            self._rules[output_layer] = TaggerLoaded( tagger )
        else:
            self._rules[output_layer][0] = TaggerLoaded( tagger )
        self._graph = self._make_graph()

    def add_retagger(self, retagger: Retagger) -> None:
        '''Adds a new retagger to the registry. 
           If the layer already has retaggers, adds the given retagger to 
           the end of retaggers list (so that it will be applied lastly). 
           Raises an exception if there is no tagger for creating the 
           layer in the registry. '''
        if not issubclass( type(retagger), Retagger ):
            raise TypeError('(!) Expected a subclass of Retagger, but got {}.'.format( type(retagger) ) )
        output_layer = retagger.output_layer
        if output_layer not in self._rules:
            raise ValueError( ('(!) Cannot add a retagger for the layer {!r}: '+
                               'no tagger for creating the layer!').format( output_layer ) )
        if output_layer not in self._composite_rules:
            self._rules[output_layer] = [ self._rules[output_layer] ]
            self._composite_rules.add( output_layer )
        self._rules[output_layer].append( TaggerLoaded(retagger) )
        self._graph = self._make_graph()

    def get_tagger(self, layer_name: str) -> Tagger:
        '''Returns tagger responsible for creating given layer.'''
        if layer_name not in self._rules:
            raise Exception('(!) No tagger registered for layer {!r}.'.format( layer_name ) )
        if layer_name in self._composite_rules:
            return self._rules[layer_name][0].tagger
        else:
            return self._rules[layer_name].tagger

    def get_retaggers(self, layer_name: str) -> List[Retagger]:
        '''Returns list of retaggers modifying given layer.'''
        if layer_name not in self._rules:
            raise Exception('(!) No tagger registered for layer {!r}.'.format( layer_name ) )
        if layer_name in self._composite_rules:
            return [rt.tagger for rt in self._rules[layer_name][1:]]
        else:
            return []

    def clear_retaggers(self, layer_name: str) -> None:
        '''Removes all the retaggers modifying the given layer.
           Note: the tagger creating the layer will remain. '''
        if layer_name in self._rules and layer_name in self._composite_rules:
            assert isinstance(self._rules[layer_name], list)
            self._rules[layer_name] = self._rules[layer_name][0]
            self._composite_rules.remove( layer_name )
            # Important: we also need to update the graph
            self._graph = self._make_graph()

    def _make_graph(self) -> None:
        '''Builds a dependency graph from input/output layers of taggers (and retaggers).'''
        graph = nx.DiGraph()
        graph.add_nodes_from(self._rules)
        for layer_name, tagger_entry in self._rules.items():
            taggers_listing = tagger_entry
            if layer_name not in self._composite_rules:
                taggers_listing = [ tagger_entry ]
            for tagger in taggers_listing:
                for dep in tagger.input_layers:
                    if dep != layer_name:
                        if dep not in graph.nodes:
                            warning_msg = ("(!) {}'s input layer {!r} is missing from the layer graph. "+
                                           "Layer {!r} cannot be created.").format( tagger.__class__.__name__, \
                                                                                    dep, tagger.output_layer )
                            warnings.warn( UserWarning(warning_msg) )
                        graph.add_edge(dep, layer_name)
        if not nx.is_directed_acyclic_graph(graph):
            raise Exception('(!) The layer graph is not acyclic! '+\
                            'Please eliminate circular dependencies '+\
                            'between taggers/retaggers.')
        return graph

    def _load_and_validate_taggers( self, layer_name: str ) -> None:
        '''Loads and validates taggers that are required for creating the given layer.
           In case of a successful validation, returns list with required taggers. 
           Otherwise, raises an exception describing the problem. 
           
           Validates that:
           * layer_name is a layer that can be created by taggers of this registry;
           * in case of a composite entry (the layer is created by a tagger and then modified 
             by one or more retaggers), validates that the first item in entry is a tagger and 
             all the following items are retaggers;
           * configuration of taggers/retaggers (output_layer, input_layers, output 
             attributes) matches the configuration declared by tagger loaders;
        '''
        if layer_name not in self._rules:
            raise Exception('(!) No tagger registered for creating layer {!r}.'.format( layer_name ) )
        expected_output = layer_name
        expected_inputs = [dep for dep in self._graph.predecessors(layer_name)]
        if layer_name in self._composite_rules:
            tagger_loaders = self._rules[layer_name]
        else:
            tagger_loaders = [self._rules[layer_name]]
        all_loaded_taggers = []
        is_first_tagger = True
        covered_inputs = []
        for tagger_loader in tagger_loaders:
            # Sanity check
            assert isinstance(tagger_loader, (TaggerLoader, TaggerLoaded))
            # Get the tagger (if not loaded, load it)
            loaded_tagger = tagger_loader.tagger
            # Check loaded tagger's type
            if is_first_tagger:
                if not issubclass( type(loaded_tagger), Tagger ):
                    raise TypeError(('(!) Error at loading taggers for layer {!r}: '+\
                                     'Expected a subclass of Tagger, but got {}.'+\
                                     '').format( layer_name, type(loaded_tagger) ) )
                if issubclass( type(loaded_tagger), Retagger ):
                    raise TypeError(('(!) Error at loading taggers for layer {!r}: '+\
                                     'Expected a subclass of Tagger, not Retagger {}.'+\
                                     '').format( layer_name, type(loaded_tagger) ) )
            else:
                if not issubclass( type(loaded_tagger), Retagger ):
                    raise TypeError(('(!) Error at loading taggers for layer {!r}: '+\
                                     'Expected a subclass of Retagger, but got {}.'+\
                                     '').format( layer_name, type(loaded_tagger) ) )
            # Check tagger's parameters
            # output layer
            if loaded_tagger.output_layer != expected_output:
                raise ValueError( ('(!) Error at loading taggers for layer {!r}: '+\
                                   "Expected {} with output_layer {!r}, not {!r}"+\
                                   '').format( layer_name, loaded_tagger.__class__.__name__, 
                                               expected_output, 
                                               loaded_tagger.output_layer ) )
            # input layers
            for input_layer in loaded_tagger.input_layers:
                if not is_first_tagger and input_layer == layer_name:
                    # Skip retagger's input_layer if it matches with the target layer
                    continue
                if input_layer not in expected_inputs:
                    raise ValueError( ('(!) Error at loading taggers for layer {!r}: '+\
                                       "{}'s input_layer {!r} is not listed in TaggerLoader's input layers {!r}"+\
                                       '').format( layer_name, loaded_tagger.__class__.__name__, 
                                                   input_layer, expected_inputs) )
                else:
                    covered_inputs.append( input_layer )
            # output attributes (if declared)
            if tagger_loader.output_attributes is not None:
                if tuple(tagger_loader.output_attributes) != tuple(loaded_tagger.output_attributes):
                    raise ValueError( ('(!) Error at loading taggers for layer {!r}: '+\
                                       "{}'s output_attributes {!r} do not match with TaggerLoader's output_attributes {!r}"+\
                                       '').format( layer_name, loaded_tagger.__class__.__name__, 
                                                   loaded_tagger.output_attributes, 
                                                   tagger_loader.output_attributes ) )
            all_loaded_taggers.append( tagger_loader.tagger )
            is_first_tagger = False
        # leftover input layers
        if set(covered_inputs) != set(expected_inputs):
            redundant_inputs = set(expected_inputs) - set(covered_inputs)
            raise ValueError( ('(!) Error at loading taggers for layer {!r}: '+\
                              'input layers {!r} declared, but not used by any Tagger or Retagger.'+\
                              '').format( layer_name, redundant_inputs) )
        return all_loaded_taggers

    def create_layer_for_text(self,  layer_name: str,  text: Union['BaseText', 'Text']) -> None:
        '''Creates given layer for the given text using the available taggers/retaggers.
           The method returns None, as the created layer will be attached to the given 
           Text object.
        '''
        loaded_taggers = self._load_and_validate_taggers( layer_name )
        loaded_taggers[0].tag( text )
        if layer_name in self._composite_rules:
            for retagger in loaded_taggers[1:]:
                retagger.retag( text )

    def list_layers(self) -> List[str]:
        '''Lists creatable layers in a topological order.'''
        return nx.topological_sort(self._graph)

    def __str__(self):
        creatable_layers_str = 'creatable_layers={!r}'.format( list(self.list_layers()) )
        return '{classname}({creatable_layers})'.format( classname=self.__class__.__name__, \
                                                         creatable_layers=creatable_layers_str )

    def __repr__(self):
        return str(self)

    def _repr_html_(self):
        records = []
        for layer_name in self.list_layers():
            if layer_name in self._composite_rules:
                # A tagger followed by retagger(s)
                records.append( self._rules[layer_name][0].parameters() )
                for retagger in self._rules[layer_name][1:]:
                    records.append( retagger.parameters() )
            else:
                # A single tagger
                records.append( self._rules[layer_name].parameters() )
        import pandas
        df = pandas.DataFrame.from_records(records, columns=['name',
                                                             'layer',
                                                             'attributes',
                                                             'depends_on',
                                                             'is_loaded'])
        return ('<h4>{}</h4>'.format(self.__class__.__name__))+'\n'+df.to_html(index=False)


