def collection_table_name(collection_name):
    return collection_name


def structure_table_name(collection_name):
    return collection_name + '__structure'


def layer_table_name(collection_name, layer_name):
    return '{}__{}__layer'.format(collection_name, layer_name)


def fragment_table_name(collection_name, fragment_name):
    return '{}__{}__fragment'.format(collection_name, fragment_name)
