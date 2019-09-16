from psycopg2.sql import SQL, Literal

from estnltk import logger
from estnltk.storage import postgres as pg


__version__ = '2.0'


class CollectionStructure(pg.CollectionStructureBase):

    def __init__(self, collection):
        super().__init__(collection, __version__)

    def create_table(self):
        storage = self.collection.storage
        table = pg.table_identifier(storage, pg.structure_table_name(self.collection.name))
        temporary = SQL('TEMPORARY') if storage.temporary else SQL('')
        with storage.conn.cursor() as c:
            c.execute(SQL('CREATE {temporary} TABLE {table} ('
                          'layer_name text primary key, '
                          'attributes text[] not null, '
                          'ambiguous bool not null, '
                          'parent text, '
                          'enveloping text, '
                          'meta text[], '
                          'layer_type text not null, '
                          'serialisation_module text);').format(temporary=temporary,
                                                  table=table))
            logger.debug(c.query.decode())

    def insert(self, layer, layer_type: str, meta: dict = None, loader: str = None):
        self._modified = True

        meta = list(meta or [])
        with self.collection.storage.conn.cursor() as c:
            c.execute(SQL("INSERT INTO {} (layer_name, attributes, ambiguous, parent, enveloping, meta, layer_type, serialisation_module) "
                          "VALUES ({}, {}, {}, {}, {}, {}, {}, {});").format(
                pg.structure_table_identifier(self.collection.storage, self.collection.name),
                Literal(layer.name),
                Literal(list(layer.attributes)),
                Literal(layer.ambiguous),
                Literal(layer.parent),
                Literal(layer.enveloping),
                Literal(meta),
                Literal(layer_type),
                Literal(layer.serialisation_module)
            )
            )
            logger.debug(c.query.decode())
        self.collection.storage.conn.commit()

    def load(self):
        if not self.collection.exists():
            return None
        structure = {}
        with self.collection.storage.conn.cursor() as c:
            c.execute(SQL("SELECT layer_name, attributes, ambiguous, parent, enveloping, meta, layer_type, serialisation_module "
                          "FROM {};").
                      format(pg.structure_table_identifier(self.collection.storage, self.collection.name)))

            for row in c.fetchall():
                structure[row[0]] = {'attributes': tuple(row[1]),
                                     'ambiguous': row[2],
                                     'parent': row[3],
                                     'enveloping': row[4],
                                     'meta': row[5],
                                     'layer_type': row[6],
                                     'serialisation_module': row[7]
                                     }
        return structure
