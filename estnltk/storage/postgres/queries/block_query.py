from typing import Set

from psycopg2.sql import SQL, Literal

from estnltk.storage import postgres as pg
from estnltk.storage.postgres.queries.query import Query


class BlockQuery(Query):
    """Constructs database query condition to select a block of texts.

    """
    def __init__(self, module: int, reminder: int):
        """Select a block of texts for which `id % module = reminder`.

        :param module: int
            total number of blocks
        :param reminder: int
            selected block 0 <= reminder < module

        """
        assert isinstance(module, int)
        assert isinstance(reminder, int)
        assert 0 <= reminder < module, (reminder, module)

        self.module = module
        self.reminder = reminder

    @property
    def required_layers(self) -> Set[str]:
        return set()

    def eval(self, collection: 'PgCollection'):
        collection_name = collection.name
        storage = collection.storage
        return SQL('{table}."id" % {module} = {reminder}').format(
                    table=pg.collection_table_identifier(storage, collection_name),
                    module=Literal(self.module), reminder=Literal(self.reminder))
