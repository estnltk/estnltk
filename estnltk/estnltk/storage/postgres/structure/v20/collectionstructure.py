from psycopg2.sql import SQL, Literal
from psycopg2.extensions import STATUS_BEGIN

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
            try:
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
            except Exception:
                storage.conn.rollback()
                raise
            finally:
                if storage.conn.status == STATUS_BEGIN:
                    # no exception, transaction in progress
                    storage.conn.commit()
                    logger.debug(c.query.decode())

    def insert(self, layer, layer_type: str, meta: dict = None, loader: str = None, is_sparse: bool = False):
        if is_sparse:
            raise ValueError('(!) Sparse layers not supported in collectionstructure version {}'.format(__version__))
        self._modified = True

        meta = list(meta or [])
        with self.collection.storage.conn.cursor() as c:
            try:
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
            except Exception:
                self.collection.storage.conn.rollback()
                raise
            finally:
                if self.collection.storage.conn.status == STATUS_BEGIN:
                    # no exception, transaction in progress
                    self.collection.storage.conn.commit()
                    logger.debug(c.query.decode())

    def load(self, update_structure:bool =False, omit_commit: bool=False, omit_rollback: bool=False):
        if not self.collection.exists(omit_commit=omit_commit, omit_rollback=omit_rollback):
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
        if update_structure:
            self._structure = structure
            self._modified = False
        return structure
