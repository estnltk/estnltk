from psycopg2.sql import SQL, Literal
from typing import Set

from estnltk.storage.postgres import collection_table_identifier
from estnltk.storage.postgres.queries.query import Query


class SliceQuery(Query):
    """
    Selects text objects corresponding to the index slice. As usual left end is included and right excluded.
    """

    __slots__ = ['start', 'stop']

    def __init__(self, start: int, stop: int):
        self.start = start
        self.stop = stop

    @property
    def required_layers(self) -> Set[str]:
        return set()

    def eval(self, collection: 'PgCollection'):
        collection_name = collection.name
        storage = collection.storage
        table = collection_table_identifier(storage, collection_name)

        if self.start is not None:
            if self.stop is not None:
                return SQL('{table}.id >= {start} AND {table}.id < {stop}').format(
                    table=table, start=Literal(self.start), stop=Literal(self.stop))
            else:
                return SQL('{table}.id >= {start}').format(table=table, start=Literal(self.start))
        elif self.stop is not None:
            return SQL('{table}.id < {stop}').format(table=table, stop=Literal(self.stop))
        else:
            return SQL('TRUE')
