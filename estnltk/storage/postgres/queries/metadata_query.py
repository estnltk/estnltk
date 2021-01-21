from psycopg2.sql import SQL, Literal
from typing import Union, List, Set, Dict

from estnltk.storage.postgres import collection_table_identifier
from estnltk.storage.postgres.queries.query import Query


class JsonbMetadataQuery(Query):
    """
    Selects text objects based on texts' metadata inside the jsonb column.
    (!) Not to be confused with the metadata available as separate database columns.
    Note: this is a very simple query based on metadata key-value pairs that 
          need to be matching. If there are multiple pairs, all must match.
    """
    __slots__ = ['_meta_values',]

    def __init__(self, meta_values : Dict[str, Union[str, List[str]]]):
        # Check args
        if not isinstance(meta_values, dict) or len(meta_values.keys())==0:
            raise ValueError('(!) Invalid meta_values {!r}. Should be a non-empty dictionary listing conditions for metadata attributes/values.'.format( meta_values ))
        for key in meta_values.keys():
            if not isinstance(key, str):
                raise ValueError('(!) Unexpected key {!r} in {!r}. String is expected.'.format(key, meta_values))
            values = meta_values[key]
            if not values:
                raise ValueError('(!) Unexpected value {!r} in {!r}. String or a list of strings is expected.'.format(values, meta_values))
            else:
                if isinstance(values, str):
                    pass
                else:
                    if not isinstance(values, list):
                        raise ValueError('(!) Unexpected value {!r} in {!r}. String or a list of strings is expected.'.format(values, meta_values))
                    for value in values:
                        if not isinstance(value, str):
                            raise ValueError('(!) Unexpected value {!r} in {!r}. String or a list of strings is expected.'.format(values, meta_values))
        # Store args
        self._meta_values = meta_values

    @property
    def required_layers(self) -> Set[str]:
        return set()

    def eval(self, storage, collection_name):
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

