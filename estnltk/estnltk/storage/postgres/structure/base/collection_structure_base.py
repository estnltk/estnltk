from psycopg2.sql import SQL, Literal
from psycopg2.extensions import STATUS_BEGIN

from estnltk import logger
from estnltk.storage.postgres import structure_table_identifier


class CollectionStructureBase:
    def __init__(self, collection, version):
        self.collection = collection

        self._structure = None
        self._modified = True
        self.load()
        self.version = version

    def __bool__(self):
        return bool(self.structure)

    def __iter__(self):
        yield from self.structure

    def __contains__(self, item):
        return item in self.structure

    def __getitem__(self, item):
        return self.structure[item]

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.structure == other.structure
        return False

    @property
    def structure(self):
        if self._modified:
            self._structure = self.load()
            self._modified = False
        return self._structure

    def create_table(self):
        raise NotImplementedError

    def insert(self, layer, layer_type: str, meta: dict = None, loader: str = None, is_sparse: bool = False):
        raise NotImplementedError

    def delete_layer(self, layer_name: str, omit_commit: bool=False):
        self._modified = True
        with self.collection.storage.conn.cursor() as c:
            try:
                c.execute(SQL("DELETE FROM {} WHERE layer_name={};").format(
                    structure_table_identifier(self.collection.storage, self.collection.name),
                    Literal(layer_name)
                )
                )
            except Exception:
                self.collection.storage.conn.rollback()
                raise
            finally:
                if self.collection.storage.conn.status == STATUS_BEGIN:
                    if not omit_commit: # commit can be omitted to avoid releasing a lock
                        # no exception, transaction in progress
                        self.collection.storage.conn.commit()
                    logger.debug(c.query.decode())

    def load(self) -> dict:
        raise NotImplementedError
