from estnltk.storage import postgres as pg


def get_structure(collection, version):
    if version == '00':
        return pg.v00.CollectionStructure(collection)
    elif version == '1.0':
        return pg.v10.CollectionStructure(collection)
    elif version == '2.0':
        return pg.v20.CollectionStructure(collection)
    elif version == '3.0':
        return pg.v30.CollectionStructure(collection)
    else:
        raise ValueError("version must be '0.0', '1.0', '2.0' or '3.0'")
