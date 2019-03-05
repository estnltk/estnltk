from psycopg2.sql import SQL, Literal
from estnltk.storage import postgres as pg


class Structure:
    def __init__(self, collection, version: str = '00'):
        self.collection = collection
        self.version = version
        self._structure = None
        self._modified = True
        self.load()

    def __bool__(self):
        return bool(self.structure)

    def __iter__(self):
        yield from self.structure

    def __contains__(self, item):
        return item in self.structure

    def __getitem__(self, item):
        return self.structure[item]

    def __eq__(self, other):
        if isinstance(other, Structure):
            return self.structure == other.structure
        return False

    @property
    def structure(self):
        if self._modified:
            self._structure = self.load()
            self._modified = False
        return self._structure

    def load(self):
        if not self.collection.exists():
            return None
        if self.version == '00':
            return self.load_00()
        raise Exception()

    def insert(self, layer, layer_type: str, meta: dict, loader: str = None):
        self._modified = True
        if self.version == '00':
            detached = layer_type in {'detached', 'fragmented'}
            return self.insert_00(layer, detached, meta)
        raise Exception()

    def load_00(self):
        structure = {}
        with self.collection.storage.conn.cursor() as c:
            c.execute(SQL("SELECT layer_name, detached, attributes, ambiguous, parent, enveloping, _base, meta "
                          "FROM {};").
                      format(pg.structure_table_identifier(self.collection.storage, self.collection.name)))

            for row in c.fetchall():
                structure[row[0]] = {'detached': row[1],
                                     'attributes': tuple(row[2]),
                                     'ambiguous': row[3],
                                     'parent': row[4],
                                     'enveloping': row[5],
                                     '_base': row[6],
                                     'meta': row[7],
                                     'layer_type': 'detached' if row[1] else 'attached',
                                     'loader': None}
        return structure

    def insert_00(self, layer, detached: bool, meta: dict = None):
        meta = list(meta or [])
        with self.collection.storage.conn.cursor() as c:
            c.execute(SQL("INSERT INTO {} (layer_name, detached, attributes, ambiguous, parent, enveloping, _base, meta) "
                          "VALUES ({}, {}, {}, {}, {}, {}, {}, {});").format(
                pg.structure_table_identifier(self.collection.storage, self.collection.name),
                Literal(layer.name),
                Literal(detached),
                Literal(list(layer.attributes)),
                Literal(layer.ambiguous),
                Literal(layer.parent),
                Literal(layer.enveloping),
                Literal(layer._base),
                Literal(meta)
            )
            )
        self.load_00()
