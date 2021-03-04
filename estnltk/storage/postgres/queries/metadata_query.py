from psycopg2.sql import SQL, Literal, Identifier
from typing import Union, List, Set, Dict

from estnltk.storage.postgres import collection_table_identifier
from estnltk.storage.postgres.queries.query import Query



def _validate_value_data_type( values, meta_values, data_type:type, data_type_name:str ):
    '''A simple method for metadata' type validation. 
       Probably can be refactored out iff typing will be improved in the future.
    '''
    if values is None:
        raise ValueError('(!) Unexpected value {!r} in {!r}: {type_name} or a list of {type_name}s is expected.'.format(values, meta_values, type_name=data_type_name))
    else:
        if isinstance(values, data_type):
            pass
        else:
            if not isinstance(values, list):
                raise ValueError('(!) Unexpected value {!r} in {!r}: {type_name} or a list of {type_name}s is expected.'.format(values, meta_values, type_name=data_type_name))
            for value in values:
                if not isinstance(value, data_type):
                    raise ValueError('(!) Unexpected value {!r} in {!r}: {type_name} or a list of {type_name}s is expected.'.format(values, meta_values, type_name=data_type_name))
    return


class JsonbMetadataQuery(Query):
    """
    Selects text objects based on texts' metadata inside the jsonb column.
    (!) Not to be confused with the metadata available as separate table columns.
    Note: this is a very simple query based on metadata key-value pairs that 
          need to be matching. If there are multiple pairs, all must match.
    """
    __slots__ = ['_meta_values']

    def __init__(self, meta_values : Dict[str, Union[str, List[str]]]):
        # Check args
        if not isinstance(meta_values, dict) or len(meta_values.keys())==0:
            raise ValueError('(!) Invalid meta_values {!r}. Should be a non-empty dictionary listing conditions for metadata attributes/values.'.format( meta_values ))
        for key in meta_values.keys():
            if not isinstance(key, str):
                raise ValueError('(!) Unexpected key {!r} in {!r}. String is expected.'.format(key, meta_values))
            values = meta_values[key]
            _validate_value_data_type( values, meta_values, str, 'string' )
        # Store args
        self._meta_values = meta_values

    @property
    def required_layers(self) -> Set[str]:
        return set()

    def eval(self, collection: 'PgCollection'):
        collection_name = collection.name
        storage = collection.storage
        table = collection_table_identifier(storage, collection_name)
        meta_conditions = []
        for meta_key in sorted( self._meta_values.keys() ):
            values = self._meta_values[meta_key]
            if not isinstance(values, list):
                values = [values]
            subcondition = SQL('{table}."data" -> {meta} ->> {meta_key} IN ({meta_values})').format(
                           table=table, meta=Literal('meta'), meta_key=Literal(meta_key),
                           meta_values = SQL(', ').join(map(Literal, values)) )
            meta_conditions.append( subcondition )
        return SQL(" AND ").join(meta_conditions)



class MetadataQuery(Query):
    """
    Selects text objects based on texts' metadata columns (collection_table_meta).
    (!) Not to be confused with the metadata inside jsonb data columns.
    Note: this is a very simple query based on metadata key-value pairs that 
          need to be matching. If there are multiple pairs, all must match.
    """
    __slots__ = ['_raw_meta_values', '_meta_values']

    def __init__( self, meta_values : Dict[str, Union[str, List[str]]] ):
        # Check args
        if not isinstance(meta_values, dict) or len(meta_values.keys())==0:
            raise ValueError('(!) Invalid meta_values {!r}. Should be a non-empty dictionary listing conditions for metadata attributes/values.'.format( meta_values ))
        # Store unvalidated data at first
        self._raw_meta_values = meta_values
        self._meta_values = None


    def validate(self, collection: 'PgCollection'):
        """ Validates that this collection has metadata columns required for the query.
            This should be always called before calling eval() method.
        """
        assert collection is not None
        # Get valid metadata column names
        valid_meta_keys = None
        column_meta = collection._collection_table_meta()
        if column_meta is not None:
            column_meta.pop('id')
            column_meta.pop('data')
            valid_meta_keys = column_meta
        # Check for keys and value types
        for key in self._raw_meta_values.keys():
            if not isinstance(key, str):
                raise ValueError('(!) Unexpected key {!r} in {!r}. String is expected.'.format(key, self._raw_meta_values))
            valid_meta_type = None
            if valid_meta_keys is not None:
                if key not in valid_meta_keys.keys():
                    if len(valid_meta_keys.keys()) == 0:
                        raise ValueError('(!) Unexpected meta key {!r} in {!r}. This collection has no metadata columns.'.format(key, self._raw_meta_values))
                    else:
                        raise ValueError('(!) Unexpected meta key {!r} in {!r}. Valid meta keys for the collection are: {!r}.'.format( key, self._raw_meta_values, list(valid_meta_keys.keys()) ) )
                valid_meta_type = valid_meta_keys[key]
            values = self._raw_meta_values[key]
            if valid_meta_type is None or valid_meta_type in ['str', 'text']:
                _validate_value_data_type( values, self._raw_meta_values, str, 'string' )
            elif valid_meta_type in ['int']:
                _validate_value_data_type( values, self._raw_meta_values, int, 'integer' )
        # Store validated data
        self._meta_values = self._raw_meta_values


    @property
    def required_layers(self) -> Set[str]:
        return set()

    def eval(self, collection: 'PgCollection'):
        # Check that the collection has metadata columns
        self.validate( collection )
        # Construct the query
        collection_name = collection.name
        storage = collection.storage
        assert self._meta_values is not None
        table = collection_table_identifier(storage, collection_name)
        meta_conditions = []
        for meta_key in sorted( self._meta_values.keys() ):
            values = self._meta_values[meta_key]
            if not isinstance(values, list):
                values = [values]
            subcondition = SQL('{table}.{meta_key} IN ({meta_values})').format(
                           table=table, meta_key=Identifier(meta_key),
                           meta_values = SQL(', ').join(map(Literal, values)) )
            meta_conditions.append( subcondition )
        return SQL(" AND ").join(meta_conditions)


