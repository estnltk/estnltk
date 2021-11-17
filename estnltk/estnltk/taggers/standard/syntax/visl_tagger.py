from os import linesep as OS_NEWLINE

from estnltk.common import abs_path
from estnltk.taggers import Tagger
from estnltk import Layer
from estnltk.converters.cg3.CG3_exporter import export_CG3
from estnltk.converters.cg3.cg3_annotation_parser import CG3AnnotationParser
from estnltk.taggers.standard.syntax.vislcg3_syntax import VISLCG3Pipeline
from collections import defaultdict


class VislTagger(Tagger):
    """Visl tagger"""

    conf_param = ['_visl_line_processor', '_parser', 'fix_selfreferences']

    def __init__(self, output_layer: str = 'visl',
                 morph_extended_layer: str = 'morph_extended',
                 vislcg3_pipeline: VISLCG3Pipeline = None,
                 annotation_parser: CG3AnnotationParser = None,
                 fix_selfreferences: bool = True):
        self.input_layers = [morph_extended_layer]
        self.output_layer = output_layer
        self.output_attributes = ('id', 'lemma', 'ending', 'partofspeech', 'subtype', 'mood', 'tense', 'voice',
                                  'person', 'inf_form', 'number', 'case', 'polarity', 'number_format', 'capitalized',
                                  'finiteness', 'subcat', 'clause_boundary', 'deprel', 'head')
        self.fix_selfreferences = fix_selfreferences
        if vislcg3_pipeline is not None:
            # Use a custom vislcg3_pipeline
            if isinstance(vislcg3_pipeline, VISLCG3Pipeline):
                self._visl_line_processor = vislcg3_pipeline.process_lines
            else:
                raise TypeError('(!) vislcg3_pipeline must be an instance of VISLCG3Pipeline')
        else:
            # Use default vislcg3_pipeline
            vislcgRulesDir = abs_path('taggers/standard/syntax/files')
            self._visl_line_processor = VISLCG3Pipeline(rules_dir=vislcgRulesDir).process_lines
        if annotation_parser is not None:
            # Use a custom annotation_parser
            if isinstance(annotation_parser, CG3AnnotationParser):
                self._parser = annotation_parser.parse
            else:
                raise TypeError('(!) annotation_parser must be an instance of CG3AnnotationParser')
        else:
            # Use default annotation_parser
            self._parser = CG3AnnotationParser().parse

    def _make_layer_template(self):
        """Creates and returns a template of the layer."""
        return Layer(name=self.output_layer, 
                     text_object=None, 
                     attributes=self.output_attributes, 
                     parent=self.input_layers[0], 
                     ambiguous=True)

    def _make_layer(self, text, layers, status):
        morph_extended_layer = layers[self.input_layers[0]]

        layer = self._make_layer_template()
        layer.text_object = text

        visl_output = self._visl_line_processor(export_CG3(text))

        visl_lines = []
        token_in_progress = False
        roots = defaultdict(int)
        sentence_count = 0
        for line in visl_output.split(OS_NEWLINE):
            if line and line[0] == '\t':
                analysed_line = self._parser(line)
                values = get_values(analysed_line, self.output_attributes)
                if token_in_progress:
                    visl_lines[-1].append(values)
                else:
                    if values['id'] == '1':  # new sentence starts
                        if sentence_count not in roots.keys() and sentence_count != 0:
                            roots[sentence_count] = -1  # add no root, if no root in the sentence
                        sentence_count += 1
                    if values['head'] == '0':
                        roots[sentence_count] = int(values['id'])
                    visl_lines.append([values])
                    token_in_progress = True
            else:
                token_in_progress = False

        if sentence_count not in roots.keys() and sentence_count != 0:
            roots[sentence_count] = -1  # add no root, if no root in the sentence
        sentence_count = 0
        root = None
        for i, zipped_values in enumerate(zip(visl_lines, morph_extended_layer)):
            token_lines, span = zipped_values
            for j, values in enumerate(token_lines):
                values['id'] = int(values['id']) if values['id'] != '_' else 1
                values['head'] = int(values['head']) if values['head'] != '_' else 0
                id = values['id']
                head = values['head']
                if id == 1 and j == 0:
                    sentence_count += 1
                    root = roots.get(sentence_count)

                if id == head and self.fix_selfreferences:
                    if values['partofspeech'] == 'Z':  # punctuation
                        if id > 1:  # can assign to previous span
                            values['head'] = head - 1
                        elif id == 1 and len(visl_lines) > (i + 1):  # first span
                            if visl_lines[i + 1][0]['id'] != '1':  # next span is not in next sentence
                                values['head'] = head + 1
                            else:
                                values['head'] = 0
                        else:  # first span, next span not existing
                            values['head'] = 0
                    else:
                        if root != -1:
                            values['head'] = root
                        else:  # no roots, assign new root
                            values['head'] = 0

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
