from typing import Union

import json

from psycopg2.sql import SQL, Literal
from psycopg2.extensions import STATUS_BEGIN

from estnltk import logger
from estnltk.converters import layer_to_json
from estnltk_core import Layer
from estnltk_core import RelationLayer
from estnltk.storage import postgres as pg


__version__ = '4.0'


class CollectionStructure(pg.CollectionStructureBase):

    def __init__(self, collection):
        super().__init__(collection, __version__)
        self._base_columns = ['id', 'data', 'hidden']

    def create_layer_info_table(self):
        storage = self.collection.storage
        table = pg.table_identifier(storage, pg.structure_table_name(self.collection.name))
        temporary = SQL('TEMPORARY') if storage.temporary else SQL('')
        with storage.conn.cursor() as c:
            try:
                c.execute(SQL('CREATE {temporary} TABLE {table} ('
                              'layer_name text primary key, '
                              'attributes text[] not null, '
                              'span_names text[], '
                              'ambiguous bool not null, '
                              'sparse bool not null, '
                              'parent text, '
                              'enveloping text, '
                              'meta text[], '
                              'layer_type text not null, '
                              'serialisation_module text, '
                              'layer_template jsonb);').format(temporary=temporary,
                                                      table=table))
            except Exception:
                storage.conn.rollback()
                raise
            finally:
                if storage.conn.status == STATUS_BEGIN:
                    # no exception, transaction in progress
                    storage.conn.commit()
                    logger.debug(c.query.decode())

    def _remove_spans_from_layer_template_json( self, layer_json: str ):
        '''
        Removes spans from the template layer.
        The template layer must be given as a JSON string.
        Returns a JSON string of the layer (with no spans or relations).
        '''
        layer_dict = json.loads(layer_json)
        if 'spans' in layer_dict.keys():
            layer_dict['spans'] = []
        elif 'relations' in layer_dict.keys():
            layer_dict['relations'] = []
        return json.dumps(layer_dict, ensure_ascii=False)

    def insert(self, layer: Union[Layer, RelationLayer], layer_type: str, meta: dict = None, loader: str = None, is_sparse: bool = False):
        self._modified = True
        # Layer's sparsity attributes
        if not isinstance(is_sparse, bool):
            raise TypeError('(!) Argument is_sparse should be a boolean.')
        if layer_type == 'attached':
            # an attached layer cannot be sparse
            is_sparse = False
        layer_template_json = None
        if is_sparse:
            layer_template_json = layer_to_json(layer)
            if len(layer) > 0:
                # Hack: remove spans from the layer (we need an empty template)
                layer_template_json = self._remove_spans_from_layer_template_json( layer_template_json )
        # Meta attributes
        meta = list(meta or [])
        with self.collection.storage.conn.cursor() as c:
            try:
                # Attribute parent is not available for RelationLayer
                parent = layer.parent if isinstance(layer, Layer) else None
                # Note: currently, span_names encodes layer class. 
                # If span_names is None, then we have Layer, otherwise we have RelationLayer;
                span_names = list(layer.span_names) if isinstance(layer, RelationLayer) else None
                c.execute(SQL("INSERT INTO {} (layer_name, attributes, span_names, ambiguous, sparse, parent, enveloping, meta, layer_type, serialisation_module, layer_template) "
                              "VALUES ({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {});").format(
                    pg.structure_table_identifier(self.collection.storage, self.collection.name),
                    Literal(layer.name),
                    Literal(list(layer.attributes)),
                    Literal(span_names),
                    Literal(layer.ambiguous),
                    Literal(is_sparse),
                    Literal(parent),
                    Literal(layer.enveloping),
                    Literal(meta),
                    Literal(layer_type),
                    Literal(layer.serialisation_module),
                    Literal(layer_template_json),
                )
                )
            except Exception:
                self.collection.storage.conn.rollback()
                raise
            finally:
                if self.collection.storage.conn.status == STATUS_BEGIN:
                    # no exception, transaction in progress
                    self.collection.storage.conn.commit()
                    logger.debug(c.query.decode())

    def load(self, update_structure:bool =False, omit_commit: bool=False, omit_rollback: bool=False):
        if not self.collection.exists(omit_commit=omit_commit, omit_rollback=omit_rollback):
            return None
        structure = {}
        with self.collection.storage.conn.cursor() as c:
            c.execute(SQL("SELECT layer_name, attributes, span_names, ambiguous, sparse, parent, enveloping, meta, layer_type, serialisation_module, layer_template "
                          "FROM {};").
                      format(pg.structure_table_identifier(self.collection.storage, self.collection.name)))

            for row in c.fetchall():
                structure[row[0]] = {'attributes': tuple(row[1]),
                                     'span_names': tuple(row[2]) if row[2] is not None else None,
                                     'ambiguous': row[3],
                                     'sparse': row[4],
                                     'parent': row[5],
                                     'enveloping': row[6],
                                     'meta': row[7],
                                     'layer_type': row[8],
                                     'serialisation_module': row[9],
                                     'layer_template_dict': row[10],
                                     'is_relation_layer': row[2] is not None
                                     }
                # Validate that 'layer_template_dict' was automatically converted to dict. 
                # If it is still a string, something went wrong with the data conversion in 
                # SQL fetching (or at the initial insertion into the database)
                layer_template_dict = structure[row[0]]['layer_template_dict']
                if layer_template_dict is not None:
                    if not isinstance( layer_template_dict, dict ):
                        raise TypeError( ('(!) Failed loading layer {!r} structure: layer_template_dict '+\
                                          'should be dict, not {}.').format( row[0], type(layer_template_dict) ) )
        if update_structure:
            self._structure = structure
            self._modified = False
        return structure
