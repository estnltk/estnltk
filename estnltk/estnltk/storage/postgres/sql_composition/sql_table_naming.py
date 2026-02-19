def collection_table_name(collection_name):
    return collection_name


def structure_table_name(collection_name):
    return collection_name + '__structure'


def layer_table_name(collection_name, layer_name):
    return '{}__{}__layer'.format(collection_name, layer_name)


def fragment_table_name(collection_name, fragment_name):
    return '{}__{}__fragment'.format(collection_name, fragment_name)


def layer_ngrams_table_name(collection_name, layer_name):
    return '{}__{}__ngrams'.format(collection_name, layer_name)


def deconstruct_table_name(table_name):
    '''Deconstructs `table_name` string into collection name, table suffix, 
       table or layer type, and layer name. 
       Returns dict with the following keys:
       * 'collection' -- collection name or None (unknown structure);
       * 'type' -- table or layer type; one of the following: 
          {None (unknown structure), 'collection', 'structure', 'detached', 
           'fragmented', 'ngrams'}
       * 'layer' -- layer name if this is a layer table or an auxiliary layer 
          table (such as layer ngrams index). Otherwise: None;
       * 'suffix' -- table name suffix;
       Note: this is a heuristic based on the current naming conventions. 
       For a complete validation, the corresponding table structure should 
       also be checked in the database. 
    '''
    table_name_parts = table_name.split('__')
    table_name_struct = \
        {'collection': None, 'layer': None, 'type': None, 'suffix': None}
    if len(table_name_parts) == 1:
        table_name_struct['collection'] = table_name_parts[0]
        table_name_struct['type'] = 'collection'
    elif len(table_name_parts) == 2:
        table_name_struct['collection'] = table_name_parts[0]
        table_name_struct['suffix'] = table_name_parts[-1]
        if table_name_struct['suffix'] == 'structure':
            table_name_struct['type'] = table_name_struct['suffix']
    elif len(table_name_parts) == 3:
        table_name_struct['collection'] = table_name_parts[0]
        table_name_struct['layer'] = table_name_parts[1]
        table_name_struct['suffix'] = table_name_parts[-1]
        if table_name_struct['suffix'] == 'layer':
            table_name_struct['type'] = 'detached'
        elif table_name_struct['suffix'] == 'fragment':
            table_name_struct['type'] = 'fragmented'
        elif table_name_struct['suffix'] == 'ngrams':
            table_name_struct['type'] = table_name_struct['suffix']
    return table_name_struct