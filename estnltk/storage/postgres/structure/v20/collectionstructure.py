from psycopg2.sql import SQL, Literal

from estnltk.logger import logger
from estnltk.storage import postgres as pg


__version__ = '2.0'


class CollectionStructure(pg.CollectionStructureBase):

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
                          '_base text, '
                          'meta text[], '
                          'layer_type text not null, '
                          'loader text);').format(temporary=temporary,
                                                  table=table))
            logger.debug(c.query.decode())

    def insert(self, layer, layer_type: str, meta: dict = None, loader: str = None):
        self._modified = True

        meta = list(meta or [])
        with self.collection.storage.conn.cursor() as c:
            c.execute(SQL("INSERT INTO {} (layer_name, attributes, ambiguous, parent, enveloping, _base, meta, layer_type, loader) "
                          "VALUES ({}, {}, {}, {}, {}, {}, {}, {}, {});").format(
                pg.structure_table_identifier(self.collection.storage, self.collection.name),
                Literal(layer.name),
                Literal(list(layer.attributes)),
                Literal(layer.ambiguous),
                Literal(layer.parent),
                Literal(layer.enveloping),
                Literal(layer._base),
                Literal(meta),
                Literal(layer_type),
                Literal('')
            )
            )
        self.collection.storage.conn.commit()

    def load(self):
        if not self.collection.exists():
            return None
        structure = {}
        with self.collection.storage.conn.cursor() as c:
            c.execute(SQL("SELECT layer_name, attributes, ambiguous, parent, enveloping, _base, meta, layer_type, loader "
                          "FROM {};").
                      format(pg.structure_table_identifier(self.collection.storage, self.collection.name)))

            for row in c.fetchall():
                structure[row[0]] = {'attributes': tuple(row[1]),
                                     'ambiguous': row[2],
                                     'parent': row[3],
                                     'enveloping': row[4],
                                     '_base': row[5],
                                     'meta': row[6],
                                     'layer_type': row[7],
                                     'loader': row[8]
                                     }
        return structure
