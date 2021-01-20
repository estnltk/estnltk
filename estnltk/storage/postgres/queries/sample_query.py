from psycopg2.sql import SQL, Literal
from typing import Union, List, Set

from estnltk.storage.postgres import collection_table_identifier
from estnltk.storage.postgres.queries.query import Query


class SampleQuery(Query):
    """
    Selects a random sample of text objects. Uses Postgre's TABLESAMPLE clause.
    For details, see:
      1) https://www.2ndquadrant.com/en/blog/tablesample-in-postgresql-9-5-2/
      2) https://www.postgresql.org/docs/13/sql-select.html > TABLESAMPLE
    """

    __slots__ = ['_method', '_percentage', '_seed']

    def __init__(self, percentage:Union[int, float], method:str='BERNOULLI', seed:Union[int, float]=None):
        # Check args
        if method not in ['SYSTEM', 'BERNOULLI']:
            raise ValueError('(!) Sampling method {} not supported. Use {} or {}.'.format( method, 'SYSTEM', 'BERNOULLI' ))
        if percentage < 0 or percentage > 100:
            raise ValueError('(!) Invalid percentage value {}.'.format( percentage ))
        if seed is not None and not isinstance(seed, (int, float)):
            raise ValueError('(!) Invalid seed value {}. Used int or float.'.format( seed ))
        # Store args
        self._method = method
        self._percentage = percentage
        self._seed = seed

    @property
    def required_layers(self) -> Set[str]:
        return set()

    def eval(self, storage, collection_name):
        table = collection_table_identifier(storage, collection_name)
        if self._seed is not None:
            sample_sql = SQL('SELECT {table}."id" FROM {table} TABLESAMPLE {sampling_method}({percentage}) REPEATABLE({seed})').format( 
                                      table=table, sampling_method=SQL(self._method), percentage=Literal(self._percentage), seed=Literal(self._seed) )
        else:
            sample_sql = SQL('SELECT {table}."id" FROM {table} TABLESAMPLE {sampling_method}({percentage})').format( 
                                      table=table, sampling_method=SQL(self._method), percentage=Literal(self._percentage) )
        return SQL('{table}."id" = ANY({subquery})').format( table=table, subquery=sample_sql )
        