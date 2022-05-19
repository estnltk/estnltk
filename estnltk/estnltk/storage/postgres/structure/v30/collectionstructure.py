import json

from psycopg2.sql import SQL, Literal

from estnltk import logger
from estnltk.converters import layer_to_json
from estnltk.storage import postgres as pg


__version__ = '3.0'


class CollectionStructure(pg.CollectionStructureBase):

    def __init__(self, collection):
        super().__init__(collection, __version__)

    def create_table(self):
        storage = self.collection.storage
        table = pg.table_identifier(storage, pg.structure_table_name(self.collection.name))
        temporary = SQL('TEMPORARY') if storage.temporary else SQL('')
        with storage.conn.cursor() as c:
            c.execute(SQL('CREATE {temporary} TABLE {table} ('
                          'layer_name text primary key, '
                          'attributes text[] not null, '
                          'ambiguous bool not null, '
                          'sparse bool not null, '
                          'parent text, '
                          'enveloping text, '
                          'meta text[], '
                          'layer_type text not null, '
                          'serialisation_module text, '
                          'layer_template jsonb);').format(temporary=temporary,
                                                  table=table))
            logger.debug(c.query.decode())

    def _remove_spans_from_layer_template_json( self, layer_json: str ):
        '''
        Removes spans from the template layer.
        The template layer must be given as a JSON string.
        Returns a JSON string of the layer (with no spans).
        '''
        layer_dict = json.loads(layer_json)
        layer_dict['spans'] = []
        return json.dumps(layer_dict, ensure_ascii=False)

    def insert(self, layer, layer_type: str, meta: dict = None, loader: str = None, is_sparse: bool = False):
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
            c.execute(SQL("INSERT INTO {} (layer_name, attributes, ambiguous, sparse, parent, enveloping, meta, layer_type, serialisation_module, layer_template) "
                          "VALUES ({}, {}, {}, {}, {}, {}, {}, {}, {}, {});").format(
                pg.structure_table_identifier(self.collection.storage, self.collection.name),
                Literal(layer.name),
                Literal(list(layer.attributes)),
                Literal(layer.ambiguous),
                Literal(is_sparse),
                Literal(layer.parent),
                Literal(layer.enveloping),
                Literal(meta),
                Literal(layer_type),
                Literal(layer.serialisation_module),
                Literal(layer_template_json),
            )
            )
            logger.debug(c.query.decode())
        self.collection.storage.conn.commit()

    def load(self):
        if not self.collection.exists():
            return None
        structure = {}
        with self.collection.storage.conn.cursor() as c:
            c.execute(SQL("SELECT layer_name, attributes, ambiguous, sparse, parent, enveloping, meta, layer_type, serialisation_module, layer_template "
                          "FROM {};").
                      format(pg.structure_table_identifier(self.collection.storage, self.collection.name)))

            for row in c.fetchall():
                structure[row[0]] = {'attributes': tuple(row[1]),
                                     'ambiguous': row[2],
                                     'sparse': row[3],
                                     'parent': row[4],
                                     'enveloping': row[5],
                                     'meta': row[6],
                                     'layer_type': row[7],
                                     'serialisation_module': row[8],
                                     'layer_template_dict': row[9]
                                     }
        return structure
