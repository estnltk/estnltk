import networkx as nx

def find_layer_dependencies(text:'Text', layer:'Layer', include_enveloping:bool =True, 
                                                        include_parents:bool =True, 
                                                        reverse:bool= False,
                                                        add_bidirectional_parents:bool=False):
    '''Finds all layers that the given layer depends on. 
       Returns list of dependency layer names. 
       If include_enveloping=True (default), then finds dependency layers over 
          enveloping relations. 
       If include_parents=True (default), then traces dependency layers over 
          parent relations.
       
       Optionally, if reverse=True, then searches for reverse relations: given 
       the parent layer, finds all its children and/or layers enveloping it. 
       
       Optionally, if add_bidirectional_parents=True, adds parent relations in 
       both ways: child -> parent and parent -> child 
       (this is specifically used by splitting.layers_to_keep_default).
    '''
    if not include_enveloping and not include_parents:
        raise ValueError('(!) Unexpected configuration: '+
              'parameters include_enveloping and include_parents cannot be both False.')
    graph = nx.DiGraph()
    for layer_name in text.layers:
        layer_object = text[layer_name]
        if include_enveloping and layer_object.enveloping:
            if not reverse:
                graph.add_edge( layer_name, layer_object.enveloping )
            else:
                graph.add_edge( layer_object.enveloping, layer_name )
        if include_parents and layer_object.parent:
            if add_bidirectional_parents:
                graph.add_edge( layer_name, layer_object.parent )
                graph.add_edge( layer_object.parent, layer_name )
            elif not reverse:
                graph.add_edge( layer_name, layer_object.parent )
            else:
                graph.add_edge( layer_object.parent, layer_name )
    return nx.descendants(graph,layer) if layer in graph.nodes else set()

