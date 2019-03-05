from psycopg2.sql import SQL, Literal

from estnltk.logger import logger
from estnltk.storage import postgres as pg


class Structure:
    def __init__(self, collection, version: str = '0'):
        self.collection = collection

        if version not in {'0', '1.0'}:
            raise ValueError("expected version '0' or '1.0', got {!r}".format(version))
        self._version = version

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

    def create_table(self):
        if self._version == '0':
            return self._create_structure_table_0()
        if self._version == '1.0':
            return self._create_structure_table_10()
        raise Exception()

    def load(self):
        if not self.collection.exists():
            return None
        if self._version == '0':
            return self._load_0()
        if self._version == '1.0':
            return self._load_10()
        raise Exception()

    def insert(self, layer, layer_type: str, meta: dict, loader: str = None):
        self._modified = True
        if self._version == '0':
            detached = layer_type in {'detached', 'fragmented'}
            return self._insert_0(layer, detached, meta)
        if self._version == '1.0':
            return self._insert_10(layer, layer_type, meta)
        raise Exception()

    def _create_structure_table_0(self):
        storage = self.collection.storage
        table = pg.table_identifier(storage, pg.structure_table_name(self.collection.name))
        temporary = SQL('TEMPORARY') if storage.temporary else SQL('')
        with storage.conn.cursor() as c:
            c.execute(SQL('CREATE {temporary} TABLE {table} ('
                          'layer_name text primary key, '
                          'detached bool not null, '
                          'attributes text[] not null, '
                          'ambiguous bool not null, '
                          'parent text, '
                          'enveloping text, '
                          '_base text, '
                          'meta text[]);').format(temporary=temporary,
                                                  table=table))
            logger.debug(c.query.decode())

    def _insert_0(self, layer, detached: bool, meta: dict = None):
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
        self._load_0()

    def _load_0(self):
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

    def _create_structure_table_10(self):
        storage = self.collection.storage
        table = pg.table_identifier(storage, pg.structure_table_name(self.collection.name))
        temporary = SQL('TEMPORARY') if storage.temporary else SQL('')
        with storage.conn.cursor() as c:
            c.execute(SQL('CREATE {temporary} TABLE {table} ('
                          'layer_name text primary key, '
                          'layer_type text not null, '
                          'attributes text[] not null, '
                          'ambiguous bool not null, '
                          'parent text, '
                          'enveloping text, '
                          '_base text, '
                          'meta text[]);').format(temporary=temporary,
                                                  table=table))
            logger.debug(c.query.decode())

    def _insert_10(self, layer, layer_type: str, meta: dict = None):
        meta = list(meta or [])
        with self.collection.storage.conn.cursor() as c:
            c.execute(SQL("INSERT INTO {} (layer_name, layer_type, attributes, ambiguous, parent, enveloping, _base, meta) "
                          "VALUES ({}, {}, {}, {}, {}, {}, {}, {});").format(
                pg.structure_table_identifier(self.collection.storage, self.collection.name),
                Literal(layer.name),
                Literal(layer_type),
                Literal(list(layer.attributes)),
                Literal(layer.ambiguous),
                Literal(layer.parent),
                Literal(layer.enveloping),
                Literal(layer._base),
                Literal(meta)
            )
            )
        self._load_10()

    def _load_10(self):
        structure = {}
        with self.collection.storage.conn.cursor() as c:
            c.execute(SQL("SELECT layer_name, layer_type, attributes, ambiguous, parent, enveloping, _base, meta "
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
