from typing import List, Optional
from psycopg2.sql import Composed, SQL

from estnltk.storage.postgres.pg_operations import layer_table_identifier
from estnltk.storage.postgres.pg_operations import collection_table_identifier


class FromClause(Composed):
    """
    `FromClause` specifies which layer table(s) should be joined with the 
    collection table and corresponding join types (the FROM part of the query). 
    If there are no joined layers, this narrows down to the collection table 
    on which the select query is made.
    
    All JOIN-s should be made between the collection table and layer 
    table(s). Joining layer tables with each other is not supported. 
    
    Supported JOIN types:
    * `collection_table` INNER JOIN `layer_table` (default for non-sparse tables);
    * `collection_table` LEFT OUTER JOIN `layer_table` (default for sparse tables);

    The main usecase for the class is to provide an extended FROM statement 
    for the SQL select query.
    """

    __SUPPORTED_JOIN_TYPES = ['INNER JOIN', 'LEFT OUTER JOIN']

    def __init__(self,
                 collection, 
                 joined_layers:List[str], 
                 join_types:Optional[List[str]]=None):
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
                if join_type not in FromClause.__SUPPORTED_JOIN_TYPES:
                    raise ValueError( ('(!) Unexpected join_type={!r}. Supported '+\
                                       'join types are {!r}.').format(join_type, 
                                        FromClause.__SUPPORTED_JOIN_TYPES) )
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

        super().__init__(self.from_clause(collection, self._joined_layers, self._join_types))

    @property
    def required_layers(self):
        return self._joined_layers

    def __and__(self, other):
        if not isinstance(other, FromClause):
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
        return FromClause(self.collection, joined_layers, join_types)

    @staticmethod
    def from_clause(collection, joined_layers, join_types):
        """
        Builds FROM clause with SQL JOIN/ON conditions for given layers.
        If no layers are given (an empty list), the returns only the 
        SQL identifier of the collection table.
        
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
        sql_parts = []
        collection_identifier = \
            collection_table_identifier(collection.storage, collection.name)
        if joined_layers is None:
            joined_layers = []
        for layer_nr, layer in enumerate(joined_layers):
            join_type = join_types[layer_nr]
            if join_type not in FromClause.__SUPPORTED_JOIN_TYPES:
                raise ValueError('(!) Unsupported join type: {!r}'.format(join_type))
            layer_table_id = \
                layer_table_identifier(collection.storage, collection.name, layer)
            join_condition = \
                SQL('{} {} ON {}."id" = {}."text_id"').format( SQL(join_type), 
                                                               layer_table_id,
                                                               collection_identifier,
                                                               layer_table_id )
            sql_parts.append( join_condition )
        from_result = SQL("{}").format(collection_identifier)
        if sql_parts:
            from_result = SQL("{} {}").format(from_result, SQL(" ").join(sql_parts))
        return from_result
