from typing import Sequence, List
from psycopg2.sql import Composed, SQL

from estnltk.storage.postgres.pg_operations import layer_table_identifier
from estnltk.storage.postgres.pg_operations import collection_table_identifier


class JoinClause(Composed):
    """
    `JoinClause` class is a sequence of SQL strings with JOIN conditions 
    that extend the FROM part of a SQL select query. 
    
    In case of an empty sequence (no joined layers), this narrows down to 
    the collection table FROM which the select query is made.
    
    All JOIN-s should be made between the collection table and layer 
    table(s). Connecting layer tables with each other is not supported. 
    
    Supported JOIN types:
    * `collection_table` INNER JOIN `layer_table`;
    * `collection_table` LEFT OUTER JOIN `layer_table`;

    The main usecase for the class is to provide an extended FROM statement 
    for the SQL select query.
    """

    def __init__(self,
                 collection, 
                 joined_layers:List[str], 
                 join_types:List[str]=None):
        self.collection = collection
        
        if not isinstance(joined_layers, list):
            raise TypeError('(!) joined_layers must be a list with layer names')
        if join_types is not None:
            if not isinstance(join_types, list):
                raise TypeError('(!) join_types must be a list with join types')
            if len(joined_layers) != len(join_types):
                raise ValueError('(!) number of joined_layers does not match with '+\
                                'the number of join_types')
        else:
            join_types = []
        supported_join_types = ['INNER JOIN', 'LEFT OUTER JOIN']
        # validate or add join types
        for layer_nr, layer in enumerate(joined_layers):
            if not isinstance(layer, str):
                raise TypeError( ('(!) a layer name string expected, '+\
                                  'but got {}').format(type(layer)))
            if layer_nr < len(join_types):
                # Validate given join type
                join_type = join_types[layer_nr]
                if isinstance(join_type, str):
                    join_type = join_type.upper()
                if join_type not in supported_join_types:
                    raise ValueError( ('(!) Unexpected join_type={!r}. Supported '+\
                                       'join types are {!r}.').format(join_type, 
                                        supported_join_types) )
            else:
                # Use default join types:
                # non-sparse layer -> INNER JOIN
                # sparse layer -> LEFT OUTER JOIN
                if collection.is_sparse(layer):
                    join_types.append('LEFT OUTER JOIN')
                else:
                    join_types.append('INNER JOIN')

        self._joined_layers = joined_layers
        self._join_types = join_types

        super().__init__(self.join_clause(collection, self._joined_layers, self._join_types))

    @property
    def required_layers(self):
        return self._joined_layers

    def __and__(self, other):
        if not isinstance(other, JoinClause):
            raise TypeError('unsupported operand type for &: {!r}'.format(type(other)))
        if self.collection is not other.collection:
            raise ValueError("can't combine JoinClauses with different collections: {!r} and {!r}".format(
                self.collection.name, other.collection.name))

        if not other:
            return self
        if not self:
            return other

        joined_layers = self._joined_layers + other._joined_layers
        join_types    = self._join_types + other._join_types
        return JoinClause(self.collection, joined_layers, join_types)

    @staticmethod
    def join_clause(collection, joined_layers, join_types):
        """
        Builds FROM clause with SQL JOIN/ON conditions for given layers.
        
        :param collection:
            instance of the EstNLTK PostgreSQL collection
        :param joined_layers:
            names of layers to be joined with the collection. 
            these must be layers that are in separate layer 
            tables.
        :param join_types:
            list of join types for layers. Supported join types:
            ['INNER JOIN', 'LEFT OUTER JOIN']
        :return:
            collection_identifier with added SQL JOIN/ON conditions 
            or simply collection_identifier if there are no conditions
        """
        supported_join_types = ['INNER JOIN', 'LEFT OUTER JOIN']
        sql_parts = []
        collection_identifier = \
            collection_table_identifier(collection.storage, collection.name)
        for layer_nr, layer in enumerate(joined_layers):
            join_type = join_types[layer_nr]
            if join_type not in supported_join_types:
                raise ValueError('(!) Unsupported join type: {!r}'.format(join_type))
            layer_table_id = \
                layer_table_identifier(collection.storage, collection.name, layer)
            join_condition = \
                SQL('{} {} ON {}."id" = {}."text_id"').format( SQL(join_type), 
                                                               layer_table_id,
                                                               collection_identifier,
                                                               layer_table_id )
            sql_parts.append( join_condition )
        join_result = SQL("{}").format(collection_identifier)
        if sql_parts:
            join_result = SQL("{} {}").format(join_result, SQL(" ").join(sql_parts))
        return join_result
