from os import linesep as OS_NEWLINE

from estnltk.core import rel_path
from estnltk.taggers import Tagger
from estnltk.layer.layer import Layer
from estnltk.converters.CG3_exporter import export_CG3
from estnltk.converters.cg3_annotation_parser import CG3AnnotationParser
from estnltk.taggers.syntax.vislcg3_syntax import VISLCG3Pipeline


class VislTagger(Tagger):
    """Visl tagger"""

    conf_param = ['_visl_line_processor', '_parser']

    def __init__(self, output_layer: str = 'visl', morph_extended_layer: str = 'morph_extended'):
        self.input_layers = [morph_extended_layer]
        self.output_layer = output_layer
        self.output_attributes = ('id', 'lemma', 'ending', 'partofspeech', 'subtype', 'mood', 'tense', 'voice',
                                  'person', 'inf_form', 'number', 'case', 'polarity', 'number_format', 'capitalized',
                                  'finiteness', 'subcat', 'clause_boundary', 'deprel', 'head')

        vislcgRulesDir = rel_path('taggers/syntax/files')
        vislcg_path = '/usr/bin/vislcg3'

        self._visl_line_processor = VISLCG3Pipeline(rules_dir=vislcgRulesDir, vislcg_cmd=vislcg_path).process_lines
        self._parser = CG3AnnotationParser().parse

    def _make_layer(self, text, layers, status):
        morph_extended_layer = layers[self.input_layers[0]]

        layer = Layer(name=self.output_layer, text_object=text, attributes=self.output_attributes,
                      parent=morph_extended_layer._base, ambiguous=True)

        visl_output = self._visl_line_processor(export_CG3(text))

        visl_lines = []
        token_in_progress = False
        for line in visl_output.split( OS_NEWLINE ):
            if line and line[0] == '\t':
                if token_in_progress:
                    visl_lines[-1].append(line)
                else:
                    visl_lines.append([line])
                    token_in_progress = True
            else:
                token_in_progress = False

        for token_lines, span in zip(visl_lines, morph_extended_layer):
            for token_line in token_lines:
                analysed_line = self._parser(token_line)
                values = get_values(analysed_line, self.output_attributes)
                layer.add_annotation(span, **values)
        return layer


def get_values(analysed_line, output_attributes):
    values = {}
    for attribute in output_attributes:
        if attribute in analysed_line:
            if len(analysed_line[attribute]) == 1:
                values[attribute] = analysed_line[attribute][0]
            else:
                values[attribute] = analysed_line[attribute]
        else:
            values[attribute] = '_'
    return values
