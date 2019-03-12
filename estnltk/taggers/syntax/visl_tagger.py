from estnltk.taggers import Tagger
from estnltk.layer.layer import Layer
from estnltk.converters.CG3_exporter import export_CG3
from estnltk.taggers.syntax.vislcg3_syntax import VISLCG3Pipeline, convert_cg3_to_conll
from estnltk import PACKAGE_PATH
import os


class VislTagger(Tagger):
    """Visl"""

    conf_param = ['_visl_line_processor']

    def __init__(self, output_layer: str = 'visl', morph_extended_layer: str = 'morph_extended'):
        self.input_layers = [morph_extended_layer]
        self.output_layer = output_layer
        self.output_attributes = ['id', 'form', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps', 'misc']

        vislcgRulesDir = os.path.relpath(os.path.join(PACKAGE_PATH, 'taggers', 'syntax', 'files'))
        vislcg_path = '/usr/bin/vislcg3'

        self._visl_line_processor = VISLCG3Pipeline(rules_dir=vislcgRulesDir, vislcg_cmd=vislcg_path).process_lines

    def _make_layer(self, text, layers, status):
        morph_extended_layer = layers[self.input_layers[0]]

        layer = Layer(name=self.output_layer, text_object=text, attributes=self.output_attributes,
                      parent=morph_extended_layer._base, ambiguous=True)

        results2 = self._visl_line_processor(export_CG3(text))
        visl_lines = filter(None, convert_cg3_to_conll(results2.split('\n')))

        for visl_line, span in zip(visl_lines, morph_extended_layer):
            values = visl_line.split('\t')
            layer.add_annotation(span,
                                 id=values[0],
                                 form=values[1],
                                 lemma=values[2],
                                 upostag=values[3],
                                 xpostag=values[4],
                                 feats=values[5],
                                 head=values[6],
                                 deprel=values[7],
                                 deps=values[8],
                                 misc=values[9])
        return layer
