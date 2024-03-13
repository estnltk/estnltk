from psycopg2.sql import SQL, Literal, Identifier
from psycopg2.extensions import STATUS_BEGIN

from estnltk import logger
from estnltk.storage.postgres import structure_table_identifier
from estnltk.storage.postgres import collection_table_name
from estnltk.storage.postgres import pytype2dbtype
from estnltk.storage.postgres import collection_table_identifier

class CollectionStructureBase:
    def __init__(self, collection, version):
        self.collection = collection

        self._structure = None
        self._modified = True
        self._base_columns = ['id', 'data']
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

    def create_collection_table(self, meta_columns=None, description=None):
        """Creates collection table for storing Text objects with attached layers and (optinal) metadata columns. 
           Also, adds automatically a GIN index for the jsonb column:

           CREATE INDEX idx_table_data ON table USING gin ((data -> 'layers') jsonb_path_ops);
           
           The types for meta columns can be int, bigint, float, str and datetime. For more information consult 
           the source code. 
        """
        storage = self.collection.storage
        collection_name = self.collection.name
        assert storage.conn.autocommit == False
        assert isinstance(collection_name, str)

        columns = [SQL('id BIGSERIAL PRIMARY KEY'),
                   SQL('data jsonb')]
        if 'hidden' in self.collection_base_columns:
            columns.append( SQL('hidden BOOLEAN DEFAULT FALSE') )
        assert len(columns) == len(self.collection_base_columns), f'{columns} != {self.collection_base_columns}'
        if meta_columns is not None:
            for col_name, col_type in meta_columns.items():
                if col_name in self.collection_base_columns:
                    raise ValueError( ('(!) Invalid metadata column name {!r}: '+\
                                       'cannot use column names overlapping with '+\
                                       'base column names {!r}.').format(col_name, self.collection_base_columns) )
                columns.append(SQL('{} {}').format(Identifier(col_name), SQL(pytype2dbtype[col_type])))

        temp = SQL('TEMPORARY') if storage.temporary else SQL('')
        table_name = collection_table_name(collection_name)
        table = collection_table_identifier(storage, table_name)

        with storage.conn.cursor() as c:
            try:
                c.execute(SQL("CREATE {} TABLE {} ({});").format(
                    temp, table, SQL(', ').join(columns)))
                logger.debug(c.query.decode())
                c.execute(
                    SQL("CREATE INDEX {index} ON {table} USING gin ((data->'layers') jsonb_path_ops);").format(
                        index=Identifier('idx_%s_data' % table_name),
                        table=table))
                logger.debug(c.query.decode())
                if isinstance(description, str):
                    c.execute(SQL("COMMENT ON TABLE {} IS {}").format(
                        table, Literal(description)))
                    logger.debug(c.query.decode())
            except:
                storage.conn.rollback()
                raise
            finally:
                if storage.conn.status == STATUS_BEGIN:
                    # no exception, transaction in progress
                    storage.conn.commit()

    def create_layer_info_table(self):
        """Creates table which contains information about collection's layers. 
           Note that this table does not store actual layers, but only decribes layers. 
        """
        raise NotImplementedError

    def insert(self, layer, layer_type: str, meta: dict = None, loader: str = None, is_sparse: bool = False):
        """Inserts new layer description into the layer information table."""
        raise NotImplementedError

    def delete_layer(self, layer_name: str, omit_commit: bool=False):
        """Removes the layer from the layer information table."""
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

    def load(self, update_structure:bool =False, omit_commit: bool=False, omit_rollback: bool=False) -> dict:
        """Loads information about all layers from the layer information table."""
        raise NotImplementedError

    @property
    def collection_base_columns(self):
        return self._base_columns