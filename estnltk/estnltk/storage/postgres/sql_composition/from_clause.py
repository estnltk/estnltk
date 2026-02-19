from typing import List, Optional
from psycopg2.sql import Composed, SQL

from estnltk.storage.postgres import deconstruct_table_name
from estnltk.storage.postgres.pg_operations import table_identifier
from estnltk.storage.postgres.pg_operations import collection_table_identifier



class FromClause(Composed):
    """
    `FromClause` specifies which layer (or auxiliary) table(s) should be joined with 
    the collection table and corresponding join types (the FROM part of the query). 
    If there are no joined tables, this narrows down to the collection table on which 
    the select query is made.

    All JOIN-s should be made between the collection table and layer (or auxiliary) 
    table(s). Joining layer (or auxiliary) tables with each other is not supported. 
    
    Supported JOIN types:
    * `collection_table` INNER JOIN `layer_table`/`aux_table` (default for non-sparse tables);
    * `collection_table` LEFT OUTER JOIN `layer_table`/`aux_table` (default for sparse tables);

    The main usecase for the class is to provide an extended FROM statement 
    for the SQL select query.
    """

    __SUPPORTED_JOIN_TYPES = ['INNER JOIN', 'LEFT OUTER JOIN']

    def __init__(self,
                 collection, 
                 joined_tables:List[str], 
                 join_types:Optional[List[str]]=None):
        self.collection = collection
        
        if not isinstance(joined_tables, list):
            raise TypeError('(!) joined_tables must be a list with table names')
        
        if join_types is not None:
            if not isinstance(join_types, list):
                raise TypeError('(!) join_types must be a list with join types')
            if len(joined_tables) != len(join_types):
                raise ValueError('(!) number of joined_tables does not match with '+\
                                 'the number of join_types')
        else:
            join_types = []
        # validate or add join types
        for table_no, table in enumerate(joined_tables):
            if not isinstance(table, str):
                raise TypeError( ('(!) a table name string expected, '+\
                                  'but got {}').format(type(table)))
            # Attempt to parse table type and layer name from table name
            table_name_parts = deconstruct_table_name(table)
            layer_name = table_name_parts['layer']
            table_type = table_name_parts['type']
            # A sanity check
            if (layer_name is None) or (table_type not in ['detached', 'fragmented', 'layer_ngrams']):
                raise ValueError(f'(!) Unexpected table name {table!r}. Should '+\
                                 'be either a layer table name or a ngrams index '+\
                                 'table name.')
            if table_no < len(join_types):
                # Validate given join type
                join_type = join_types[table_no]
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
                if collection.is_sparse( layer_name ):
                    join_types.append('LEFT OUTER JOIN')
                else:
                    join_types.append('INNER JOIN')

        self._joined_tables = joined_tables
        self._join_types = join_types

        super().__init__(self.from_clause(collection, self._joined_tables, self._join_types))

    @property
    def required_tables(self):
        return self._joined_tables

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

        joined_tables = self._joined_tables + other._joined_tables
        join_types    = self._join_types + other._join_types
        return FromClause(self.collection, joined_tables, join_types)

    @staticmethod
    def from_clause(collection, joined_tables, join_types):
        """
        Builds FROM clause with SQL JOIN/ON conditions for given tables. 
        If no tables are given (an empty list), the returns only the 
        SQL identifier of the collection table.
        
        :param collection:
            instance of the EstNLTK PostgreSQL collection
        :param joined_tables:
            names of tables to be joined with the collection. 
            can be either layer tables or auxiliary tables of 
            this collection. 
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
        if joined_tables is None:
            joined_tables = []
        for table_no, table in enumerate(joined_tables):
            join_type = join_types[table_no]
            if join_type not in FromClause.__SUPPORTED_JOIN_TYPES:
                raise ValueError('(!) Unsupported join type: {!r}'.format(join_type))
            # Attempt to parse table type and layer name from table name
            table_name_parts = table.split('__')
            layer_name = None
            table_type = None
            if (table_name_parts[-1]) in ['layer', 'layer_ngrams', 'fragment'] and \
               len(table_name_parts) > 2:
                table_type = table_name_parts[-1]
                layer_name = table_name_parts[-2]
            if table_type is None:
                raise ValueError(f'(!) Unexpected table name {table!r}. Should '+\
                                 'be either a layer table name or a ngrams index '+\
                                 'table name.')
            # Create JOIN condition
            table_id = table_identifier(collection.storage, table)
            join_condition = \
                SQL('{} {} ON {}."id" = {}."text_id"').format( SQL(join_type), 
                                                               table_id,
                                                               collection_identifier,
                                                               table_id )
            sql_parts.append( join_condition )
        from_result = SQL("{}").format(collection_identifier)
        if sql_parts:
            from_result = SQL("{} {}").format(from_result, SQL(" ").join(sql_parts))
        return from_result
