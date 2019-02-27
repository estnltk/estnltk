from typing import Sequence
from tqdm import tqdm, tqdm_notebook
from psycopg2.sql import SQL

from estnltk import logger
from estnltk.converters import dict_to_text, dict_to_layer
from estnltk.storage import postgres as pg


class PgSubCollection:
    """
    Wrapper class that provides read-only access to a subset of a collection

    The subset is specified by a SQL select statement that is determined by
    - the selection criterion
    - the set of selected layers
    - the set of meta attributes

    TODO: Complete the description

    ISSUES: How one specifies layer meta attributes? Do they come automatically
    """

    def __init__(self, collection, selection_criterion=None, selected_layers=None, meta_attributes=(),
                 progressbar=None, return_index=True):

        if not collection.exists():
            raise pg.PgCollectionException('collection {!r} does not exist'.format(collection.name))

        self.collection = collection

        if selection_criterion is None:
            self._selection_criterion = pg.WhereClause(collection=self.collection)
        elif isinstance(selection_criterion, pg.WhereClause):
            self._selection_criterion = selection_criterion
        else:
            raise TypeError('unexpected type of selection_criterion: {!r}'.format(type(selection_criterion)))

        self.selected_layers = selected_layers or []
        self.meta_attributes = meta_attributes
        self.progressbar = progressbar
        self.return_index = return_index

    @property
    def selected_layers(self):
        return self._selected_layers

    @selected_layers.setter
    def selected_layers(self, layers: list):
        self._selected_layers = self.dependent_layers(layers)
        self._attached_layers = [layer for layer in self._selected_layers
                                 if not self.collection.structure[layer]['detached']]
        self._detached_layers = [layer for layer in self._selected_layers
                                 if self.collection.structure[layer]['detached']]

    @property
    def layers(self):
        return self.collection.get_layer_names()

    @property
    def sql_query(self):
        """Returns a SQL select statement that defines the subcollection.
        
        BUGS: This function does not handle fragmented layers correctly.
        We need nested sql queries to combine fragments into single object per text_id
        This must be solved by defining a view during creation of fragmented layers
        or some dark magic query composition.
        """

        selected_columns = pg.SelectedColumns(collection=self.collection,
                                              layers=self._detached_layers,
                                              collection_meta=self.meta_attributes,
                                              include_layer_ids=False)

        required_layers = sorted(set(self._detached_layers + self._selection_criterion.required_layers))
        collection_identifier = pg.collection_table_identifier(self.collection.storage, self.collection.name)

        # Required layers are part of the main collection
        if not required_layers:
            if self._selection_criterion:
                return SQL("SELECT {} FROM {} WHERE {}").format(SQL(', ').join(selected_columns),
                                                                collection_identifier,
                                                                self._selection_criterion)
            else:
                return SQL("SELECT {} FROM {}").format(SQL(', ').join(selected_columns), collection_identifier)

        # There are detached layers among required layers

        required_layer_tables = [pg.layer_table_identifier(self.collection.storage, self.collection.name, layer)
                                 for layer in required_layers]

        required_tables = SQL(', ').join((collection_identifier, *required_layer_tables))

        # Join all tables using text_id
        join_condition = SQL(" AND ").join(SQL('{}."id" = {}."text_id"').format(collection_identifier,
                                                                                layer_table_identifier)
                                           for layer_table_identifier in required_layer_tables)

        if self._selection_criterion:
            return SQL("SELECT {} FROM {} WHERE {} AND {}").format(SQL(', ').join(selected_columns),
                                                                   required_tables,
                                                                   join_condition,
                                                                   self._selection_criterion)

        return SQL("SELECT {} FROM {} WHERE {}").format(SQL(', ').join(selected_columns),
                                                        required_tables,
                                                        join_condition)

    @property
    def sql_count_query(self):
        return SQL('SELECT count(*) FROM ({}) AS a').format(self.sql_query)

    @property
    def sql_query_text(self):
        return self.sql_query.as_string(self.collection.storage.conn)

    def dependent_layers(self, selected_layers):
        return self.collection.dependent_layers(selected_layers)

    def select(self, additional_constraint: pg.WhereClause = None, selected_layers: Sequence[str] = None):

        if selected_layers is None:
            selected_layers = self.selected_layers

        if additional_constraint is None:
            self.selected_layers = selected_layers
            return self

        return PgSubCollection(collection=self.collection,
                               selection_criterion=self._selection_criterion & additional_constraint,
                               selected_layers=selected_layers.copy(),
                               meta_attributes=self.meta_attributes,
                               progressbar=self.progressbar,
                               )

    def __iter__(self):
        """
        TODO: Complete description
        """

        # Check that somebody else has not deleted the collection
        # TODO: Improve the error message
        if not self.collection.exists():
            raise pg.PgCollectionException('collection {!r} does not exist'.format(self.collection.name))

        with self.collection.storage.conn.cursor() as c:
            c.execute(self.sql_count_query)
            logger.debug(c.query.decode())
            total = next(c)[0]

        with self.collection.storage.conn.cursor('read', withhold=True) as c:
            c.execute(self.sql_query)
            logger.debug(c.query.decode())
            data_iterator = Progressbar(cursor=c, total=total, initial=0, progressbar_type=self.progressbar)
            for row in data_iterator:
                text_id = row[0]
                data_iterator.set_description('collection_id: {}'.format(text_id), refresh=False)

                text_dict = row[1]
                text = dict_to_text(text_dict, self._attached_layers)
                meta_list = row[2:2 + len(self.meta_attributes)]

                for layer_dict in row[2 + len(self.meta_attributes):]:
                    layer = dict_to_layer(layer_dict, text)
                    text[layer.name] = layer

                if self.meta_attributes:
                    meta = {}
                    for meta_name, meta_value in zip(self.meta_attributes, meta_list):
                        meta[meta_name] = meta_value
                    if self.return_index:
                        yield text_id, text, meta
                    else:
                        yield text, meta
                else:
                    if self.return_index:
                        yield text_id, text
                    else:
                        yield text

    def select_all(self):
        self.selected_layers = self.layers
        return self

    # TODO: ?
    def raw_layer(self):
        raise NotImplementedError()

    # TODO: ?
    def raw_fragment(self):
        raise NotImplementedError()


class Progressbar:
    def __init__(self, cursor, total, initial, progressbar_type):
        self.progressbar_type = progressbar_type

        if progressbar_type is None:
            self.data_iterator = cursor
        elif progressbar_type in {'ascii', 'unicode'}:
            self.data_iterator = tqdm(cursor,
                                      total=total,
                                      initial=initial,
                                      unit='doc',
                                      ascii=progressbar_type == 'ascii',
                                      smoothing=0)
        elif progressbar_type == 'notebook':
            self.data_iterator = tqdm_notebook(cursor,
                                               total=total,
                                               initial=initial,
                                               unit='doc',
                                               smoothing=0)
        else:
            raise ValueError("unknown progressbar type: {!r}, expected None, 'ascii', 'unicode' or 'notebook'"
                             .format(progressbar_type))

    def set_description(self, description, refresh=False):
        if self.progressbar_type is not None:
            self.data_iterator.set_description(description, refresh=refresh)

    def __iter__(self):
        yield from self.data_iterator
