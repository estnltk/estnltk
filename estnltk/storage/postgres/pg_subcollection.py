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
                 progressbar=None, return_index=False):

        if not collection.exists():
            raise pg.PgCollectionException('collection does not exist')

        self.collection = collection
        self._selection_criterion = selection_criterion
        self.selected_layers = selected_layers or []
        self.meta_attributes = meta_attributes
        self.progressbar = progressbar
        self.return_index = return_index

    @property
    def selected_layers(self):
        return self._selected_layers

    @selected_layers.setter
    def selected_layers(self, value: list):
        self._selected_layers = self.dependent_layers(value)
        self._attached_layers = [layer for layer in self._selected_layers
                                 if not self.collection.structure[layer]['detached']]
        self._detached_layers = [layer for layer in self._selected_layers
                                 if self.collection.structure[layer]['detached']]

    @property
    def sql_query(self):
        """Returns a SQL select statement that defines the subcollection.
        
        BUGS: This function does not handle fragmented layers correctly.
        We need nested sql queries to combine fragments into single object per text_id
        This must be solved by defining a view during creation of fragmented layers
        or some dark magic query composition.
        """

        selected_columns = pg.SelectedColumns_2(collection=self.collection,
                                                layers=self._detached_layers,
                                                collection_meta=self.meta_attributes)

        required_layers = sorted(set(self._detached_layers + self._selection_criterion.required_layers))
        collection_identifier = pg.collection_table_identifier(self.collection.storage, self.collection.name)

        # Required layers are part of the main collection
        if not required_layers:
            if not self._selection_criterion.seq:
                return SQL("SELECT {} FROM {}").format(SQL(', ').join(selected_columns), collection_identifier)

            else:
                return SQL("SELECT {} FROM {} WHERE {}").format(SQL(', ').join(selected_columns),
                                                                collection_identifier,
                                                                self._selection_criterion)

        # There are detached layers among required layers
        # TODO: Simplify code by defining requred_layer_tables instead of required_tables
        required_tables = [collection_identifier]
        for layer in required_layers:
            required_tables.append(pg.layer_table_identifier(self.collection.storage, self.collection.name, layer))
        required_tables = SQL(', ').join(required_tables)

        # Join all tables using text_id
        join_condition = SQL(" AND ").join(SQL('{}."id" = {}."text_id"').format(
                                               collection_identifier,
                pg.layer_table_identifier(self.collection.storage, self.collection.name, layer))
                                           for layer in required_layers)

        if not self._selection_criterion.seq:
            return SQL("SELECT {} FROM {} WHERE {}").format(SQL(', ').join(selected_columns),
                                                                           required_tables,
                                                                           join_condition)
        else:
            return SQL("SELECT {} FROM {} WHERE {} AND {}").format(SQL(', ').join(selected_columns),
                                                                   required_tables,
                                                                   join_condition,
                                                                   self._selection_criterion)

    @property
    def sql_query_text(self):
        return self.sql_query.as_string(self.collection.storage.conn)

    def dependent_layers(self, selected_layers):
        """Returns all layers that depend on selected layers including selected layers.

           Returned layers are ordered ...
           The latter provides a correct order for loading and re-attaching detached layers

           TODO: Complete description
        """
        layers_extended = []

        # TODO: kirjuta ümber vastavalt fotole
        # Rekursioonita on raske tagada õiget kihtide järjekorda
        # Tahvlil olev algoritm tegi depth-first järjestus. 
        # Sul on vaja topoloogilist järjestust. See asi siin ei pruugi töötada
        #
        # Võimalikud lahendused on
        # 1. Otsida Algoritmide ja andmestruktuuride raamatust topoloogiline sort
        # 2. Lisada collection_structure tabelisse igale kihile autoinrementiga järjekorranumber
        #    ja järjestada kihid vastavalt id numbrile
        # 3. Defineerida serialiseerimine nii, et pole vahet mis järjekorras kihid luuakse
        #    - Selleks peab saama EnvelopingSpani sisu defineerida avaldisega
        #    - Peab defineerima Layer.evaluate, mis kõik avaldised asendab hetkel tekkivate väärtustega
        #    See lahendus lubab vaevata ka depencency_layer deserialiseerimist
        #
        # Mina eelistaksin lahendust 2 ja tulevikus 3

        def include_dep(layer):
            if layer is None:
                return
            for dep in (self.collection.structure[layer]['parent'], self.collection.structure[layer]['enveloping']):
                include_dep(dep)
            if layer not in layers_extended:
                layers_extended.append(layer)

        for layer in selected_layers:
            if layer not in self.collection.structure:
                raise pg.PgCollectionException('there is no layer {!r} in the collection {!r}'.format(
                                               layer, self.collection.name))
            include_dep(layer)

        return layers_extended

    #TODO: final signature select(self, additional_constraint, selected_layers) 
    def select(self, additional_constraint=None, selected_layers=None,
               query=None, layer_query=None, layer_ngram_query=None, keys=None, missing_layer: str = None):

        #TODO: Remove dead code

        #----DEAD-CODE------
        layers_extended = []

        def include_dep(layer):
            if layer is None:
                return
            for dep in (self.collection.structure[layer]['parent'], self.collection.structure[layer]['enveloping']):
                include_dep(dep)
            if layer not in layers_extended:
                layers_extended.append(layer)

        for layer in self.selected_layers or []:
            if layer not in self.collection.structure:
                raise pg.PgCollectionException('there is no layer {!r} in the collection {!r}'.format(
                                               layer, self.collection.name))
            include_dep(layer)
        #-----DEAD-CODE-----

        #TODO: Replace with self._detached_layers
        detached_layer_names = [layer for layer in layers_extended if self.collection.structure[layer]['detached']]

        additional_constraint = pg.WhereClause(collection=self.collection,
                                               query=query,
                                               layer_query=layer_query,
                                               layer_ngram_query=layer_ngram_query,
                                               keys=keys,
                                               missing_layer=missing_layer)

        #---DEAD-CODE-----
        selected_columns = pg.SelectedColumns(collection=self.collection,
                                              layer_query=layer_query,
                                              layer_ngram_query=layer_ngram_query,
                                              layers=detached_layer_names,
                                              collection_meta=self.meta_attributes)
        #---DEAD-CODE-----

        #TODO:
        #if not additional_constraint.seq: return self
        if self._selection_criterion is None and self._selected_columns is None:
            self._selection_criterion = additional_constraint
            self._selected_columns = selected_columns
            return self

        #TODO add the constraint to the where_clause
        # return PgSubCollection(collection, self._where_clause & additional_constraint, self.selected_layers)
        return PgSubCollection(collection=self.collection,
                               selection_criterion=self._selection_criterion & additional_constraint,
                               selected_layers=self.selected_layers.copy(),
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
            raise pg.PgCollectionException('collection does not exist')

        def data_iterator():
            with self.collection.storage.conn.cursor('read', withhold=True) as c:
                c.execute(self.sql_query)
                logger.debug(c.query.decode())
                for row in c:
                    text_id = row[0]
                    text_dict = row[1]
                    text = dict_to_text(text_dict, self._attached_layers)
                    meta_list = row[2:2 + len(self.meta_attributes)]
                    detached_layers = {}
                    if len(row) > 2 + len(self.meta_attributes):
                        for i in range(2 + len(self.meta_attributes), len(row), 2):
                            layer_id = row[i]
                            layer_dict = row[i + 1]
                            layer = dict_to_layer(layer_dict, text,
                                                  {k: v['layer'] for k, v in detached_layers.items()})
                            detached_layers[layer.name] = {'layer': layer, 'layer_id': layer_id}

                    for layer_name in self._detached_layers:
                        text[layer_name] = detached_layers[layer_name]['layer']
                    if self.meta_attributes:
                        meta = {}
                        for meta_name, meta_value in zip(self.meta_attributes, meta_list):
                            meta[meta_name] = meta_value
                        yield text_id, text, meta
                    else:
                        yield text_id, text
            c.close()

        if self.progressbar not in {'ascii', 'unicode', 'notebook'}:
            yield from data_iterator()
            return

        #BUG: The size of subcollection is not equal to the collection
        #TODO: Define property sql_count_query or find out how execute return the size of the outcome 
        total = pg.count_rows(self.collection.storage, self.collection.name)
        initial = 0
        if self.missing_layer is not None:
            initial = self.collection.storage.count_rows(
                    table_identifier=pg.layer_table_identifier(self.collection.storage,
                                                               self.collection.name, self.missing_layer))
        if self.progressbar == 'notebook':
            iter_data = tqdm_notebook(data_iterator(),
                                      total=total,
                                      initial=initial,
                                      unit='doc',
                                      smoothing=0)
        else:
            iter_data = tqdm(data_iterator(),
                             total=total,
                             initial=initial,
                             unit='doc',
                             ascii=(self.progressbar == 'ascii'),
                             smoothing=0)
        for data in iter_data:
            iter_data.set_description('collection_id: {}'.format(data[0]), refresh=False)
            yield data

    #Make sure that it calls self.select_layers = all_layers
    #TODO define property all_layers
    def select_all(self):
        layers = self.collection.get_layer_names()
        return self.select(layers=layers)

    def raw_layer(self):
        pass

    def raw_fragment(self):
        pass
