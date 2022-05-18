from psycopg2.sql import SQL, Literal

from estnltk import logger
from estnltk.storage import postgres as pg


__version__ = '1.0'


class CollectionStructure(pg.CollectionStructureBase):

    def __init__(self, collection):
        super().__init__(collection, __version__)

    def create_table(self):
        storage = self.collection.storage
        table = pg.table_identifier(storage, pg.structure_table_name(self.collection.name))
        temporary = SQL('TEMPORARY') if storage.temporary else SQL('')
        storage.conn.commit()
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

    def insert(self, layer, layer_type: str, meta: dict = None, loader: str = None, is_sparse: bool = False):
        if is_sparse:
            raise ValueError('(!) Sparse layers not supported in collectionstructure version {}'.format(__version__))
        self._modified = True

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
                Literal(None),
                Literal(meta)
            )
            )
            logger.debug(c.query.decode())
        self.collection.storage.conn.commit()

    def load(self):
        if not self.collection.exists():
            return None
        structure = {}
        with self.collection.storage.conn.cursor() as c:
            c.execute(SQL("SELECT layer_name, layer_type, attributes, ambiguous, parent, enveloping, _base, meta "
                          "FROM {};").
                      format(pg.structure_table_identifier(self.collection.storage, self.collection.name)))

            for row in c.fetchall():
                structure[row[0]] = {'layer_type': row[1],
                                     'attributes': tuple(row[2]),
                                     'ambiguous': row[3],
                                     'parent': row[4],
                                     'enveloping': row[5],
                                     '_base': row[6],
                                     'meta': row[7],
                                     'loader': None}
        return structure
