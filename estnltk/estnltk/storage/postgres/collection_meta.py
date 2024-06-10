from collections import OrderedDict

from psycopg2.sql import SQL, Literal

from estnltk.storage import postgres as pg
from estnltk.storage.postgres.collection import PgCollectionException
from estnltk.storage.postgres.collection_meta_selection import PgCollectionMetaSelection

class PgCollectionMeta:
    """Provides views to collection's metadata. 
       
       Allows to:
       -- retrieve names of metadata columns of the collection;
       -- retrieve names and types of metadata columns of the collection;
       -- retrieve metadata values of documents via indexer operator [];
          note that the access to metadata is read-only.
    """
    
    def __init__(self, collection: pg.PgCollection):
        """
        Initiates new PgCollectionMeta object.
        
        :param collection: PgCollection
            collection which metadata this object handles.
        """
        # Validate collection
        if collection is None:
            raise PgCollectionException("collection cannot be None")
        elif not isinstance(collection, pg.PgCollection):
            raise TypeError('collection must be an instance of PgCollection')
        self.collection = collection
        self._columns = None      # metadata columns of this collection
        self._column_types = None # OrderedDict of pairs (metadata_column, data_type_str)

    def _collection_table_meta(self):
        if not self.collection.exists():
            return None
        with self.collection.storage.conn:
            with self.collection.storage.conn.cursor() as c:
                c.execute(SQL('SELECT column_name, data_type from information_schema.columns '
                              'WHERE table_schema={} and table_name={} '
                              'ORDER BY ordinal_position'
                              ).format(Literal(self.collection.storage.schema), 
                                       Literal(self.collection.name)))
                return OrderedDict(c.fetchall())

    @property
    def column_types(self):
        if self._column_types is None:
            if not self.collection.exists():
                raise PgCollectionException(('collection {!r} does not exist, '+\
                                             'cannot select metadata columns').format( \
                                              self.collection.name))
            # Try to load metadata column information from db
            column_meta = self._collection_table_meta()
            if column_meta is not None:
                # Remove base columns, keep only meta columns
                for base_col in self.collection.structure.collection_base_columns:
                    if base_col in column_meta.keys():
                        column_meta.pop( base_col )
                    else:
                        raise Exception('(!) Corrupt collection structure: missing base column {}'.format(base_col))
                self._column_types = column_meta
        return self._column_types

    @property
    def columns(self):
        if self._columns is None:
            column_types = self.column_types
            if column_types is not None:
                self._columns = [name for (name, col_type) in column_types.items()]
        return self._columns

    def __getitem__(self, item):
        # Get valid metadata attributes/columns
        valid_attributes = self.columns
        if valid_attributes is None or len(valid_attributes) == 0:
            raise PgCollectionException(("collection {!r} does not have any "+\
                                         "metadata columns that can be selected").format(self.collection.name))
        
        # Expected call: collection.meta[index]
        # Returns all metadata of selected document
        if isinstance(item, int):
            return list(PgCollectionMetaSelection(self.collection, 
                                                  selected_indexes=[item],
                                                  selected_attributes=valid_attributes,
                                                  return_index=False))[0]

        # Expected call: collection.meta[start:end]
        # Returns all metadata of selected slice of documents
        if isinstance(item, slice):
            if item.step is not None:
                raise KeyError("Invalid index slice {!r}".format(item))

            return PgCollectionMetaSelection(self.collection, 
                                             selected_slice=item,
                                             selected_attributes=valid_attributes,
                                             return_index=False)

        if isinstance(item, tuple) and len(item) == 2:
            # Expected call: collection.meta[indexes, attributes]
            # Check that the first item specifies an index or a range indexes
            first_ok =  isinstance(item[0], (int, slice)) or \
                       (isinstance(item[0], (tuple, list)) and all(isinstance(i, int) for i in item[0]))
            # Check that the second item specifies an attribute or a list of attributes
            second_ok = isinstance(item[1], str) or \
                        isinstance(item[1], (list, tuple)) and all(isinstance(i, str) for i in item[1])
            if first_ok and second_ok:
                selected_attributes = [item[1]] if isinstance(item[1], str) else item[1]
                # Validate column names
                for attr in selected_attributes:
                    if attr not in valid_attributes:
                        valid_names_str = " Valid column names are: {!r}".format(valid_attributes)
                        raise KeyError("Invalid metadata column name {!r}.{}".format(attr, valid_names_str))
                if isinstance(item[0], int):
                    # Select attribute(s) of a single document
                    # Example: collection.meta[0, ['text_id', 'subcorpus']]
                    # Returns selected metadata of a single document
                    return list(PgCollectionMetaSelection(self.collection, 
                                                          selected_indexes=[item[0]],
                                                          selected_attributes=selected_attributes,
                                                          return_index=False))[0]
                elif isinstance(item[0], slice):
                    # Select attribute(s) from slice of documents
                    # Example: collection.meta[4:7, ['text_id', 'subcorpus']]
                    # Returns selected metadata of slice of documents
                    return PgCollectionMetaSelection(self.collection, 
                                                     selected_slice=item[0],
                                                     selected_attributes=selected_attributes,
                                                     return_index=False)
                else:
                    # Select attribute(s) from multiple documents
                    # Example: collection.meta[[0,2,3,4,8], ['text_id', 'subcorpus']]
                    # Returns selected metadata of selected of documents
                    return PgCollectionMetaSelection(self.collection, 
                                                     selected_indexes=item[0],
                                                     selected_attributes=selected_attributes,
                                                     return_index=False)

        # Expected call: collection.meta[indexes]
        # Returns all metadata of selected documents
        if isinstance(item, (tuple, list)) and len(item) > 0:
            if all(isinstance(i, int) for i in item):
                return PgCollectionMetaSelection(self.collection, 
                                                 selected_indexes=item,
                                                 selected_attributes=valid_attributes,
                                                 return_index=False)

        raise KeyError(item)

