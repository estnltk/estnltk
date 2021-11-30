import networkx as nx

def find_layer_dependencies(text:'Text', layer:str, include_enveloping:bool =True, 
                                                       include_parents:bool =True, 
                                                       reverse:bool= False,
                                                       add_bidirectional_parents:bool=False):
    '''Finds all layers that the given layer depends on. 
       Returns set of dependency layer names. 
       If include_enveloping=True (default), then finds dependency layers over 
          enveloping relations. 
       If include_parents=True (default), then finds dependency layers over 
          parent relations.
       
       Optionally, if reverse=True, then searches for reverse relations: given 
       a (parent) layer, find all layers that are depending on it (descendant
       layers).
       
       Optionally, if add_bidirectional_parents=True, adds parent relations in 
       both ways: child -> parent and parent -> child 
       (this is specifically used by splitting.layers_to_keep_default).
    '''
    if not include_enveloping and not include_parents:
        raise ValueError('(!) Unexpected configuration: '+
              'parameters include_enveloping and include_parents cannot be both False.')
    if layer not in text.layers:
        raise ValueError( '(!) Layer {!r} is missing from the given Text object.'.format(layer) )
    graph = nx.DiGraph()
    for layer_name in text.layers:
        graph.add_node( layer_name )
        layer_object = text[layer_name]
        if include_enveloping and layer_object.enveloping:
            graph.add_edge( layer_object.enveloping, layer_name )
        if include_parents and layer_object.parent:
            if add_bidirectional_parents:
                graph.add_edge( layer_object.parent, layer_name )
                graph.add_edge( layer_name, layer_object.parent )
            else:
                graph.add_edge( layer_object.parent, layer_name )
    return nx.ancestors(graph,layer) if not reverse else nx.descendants(graph,layer)

