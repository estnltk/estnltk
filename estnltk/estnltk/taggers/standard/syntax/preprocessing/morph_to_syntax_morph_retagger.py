import os
import codecs
import regex as re
from collections import defaultdict

from estnltk import Layer
from estnltk import Annotation
from estnltk.taggers import Retagger
from estnltk.taggers import VabamorfTagger

class MorphToSyntaxMorphRetagger(Retagger):
    """ Converts given analysis from Filosoft's mrf format to syntactic analyzer's
        format, using the morph-category conversion rules from conversion_rules.

        Morph-category conversion rules should be loaded via method
            load_fs_mrf_to_syntax_mrf_translation_rules( rulesFile ),
        usually from a file named 'tmorftrtabel.txt';

        Note that the resulting analysis list is likely longer than the
        original, because the conversion often requires that the
        original Filosoft's analysis is expanded into multiple analysis.

    """
    conf_param = ['fs_to_synt_rules', 'check_output_consistency']

    def __init__(self, input_layer='morph_analysis', output_layer='morph_extended', fs_to_synt_rules_file=None):
        self.input_layers = [input_layer]
        self.output_layer = output_layer
        self.output_attributes = VabamorfTagger.output_attributes
        self.check_output_consistency = False

        if fs_to_synt_rules_file:
            assert os.path.exists(fs_to_synt_rules_file),\
                'Unable to find *fs_to_synt_rules_file* from location ' + fs_to_synt_rules_file
        else:
            fs_to_synt_rules_file = os.path.dirname(__file__)
            fs_to_synt_rules_file = os.path.join(fs_to_synt_rules_file,
                                                 'rules_files/tmorftrtabel.txt')
            assert os.path.exists(fs_to_synt_rules_file),\
                'Missing default *fs_to_synt_rules_file* ' + fs_to_synt_rules_file
        self.fs_to_synt_rules = \
            self.load_fs_mrf_to_syntax_mrf_translation_rules(fs_to_synt_rules_file)

    def _make_layer_template(self):
        """Creates and returns a template of the layer."""
        return Layer(name=self.output_layer,
                     attributes=self.output_attributes,
                     text_object=None,
                     parent=self.input_layers[0],
                     ambiguous=True)

    def _copy_morph_layer(self, morph_layer):
        copied_layer = Layer( name=morph_layer.name,
                              attributes=morph_layer.attributes,
                              text_object=morph_layer.text_object,
                              parent=morph_layer.parent,
                              enveloping=morph_layer.enveloping,
                              ambiguous=morph_layer.ambiguous,
                              default_values=morph_layer.default_values.copy() )
        for span in morph_layer:
            for annotation in span.annotations:
                copied_layer.add_annotation(span.base_span, **annotation)
        return copied_layer

    def _make_layer(self, text, layers, status=None):
        morph_layer = layers[self.input_layers[0]]
        layer = self._copy_morph_layer( morph_layer )
        layer.name = self.output_layer
        layer.parent = morph_layer.name

        self._change_layer(text, {layer.name: layer})

        return layer

    def _change_layer(self, text, layers, status=None):
        layer = layers[self.output_layer]
        for span in layer:
            annotations = list(span.annotations)
            span.clear_annotations()

            for annotation in annotations:
                pos = annotation['partofspeech']
                form = annotation['form']
                # 1) Convert punctuation
                if pos == 'Z':
                    span.add_annotation(annotation)
                else:
                # 2) Convert morphological analyses that have a form specified
                    if form:
                        morph_key = (pos, form)
                    else:
                        morph_key = (pos, '')
                    if morph_key in self.fs_to_synt_rules:
                        rules = self.fs_to_synt_rules[morph_key]
                    else:
                        # parem oleks tmorfttabel.txt täiendada ja võibolla siin hoopis viga visata
                        rules = [morph_key]
                    for pos, form in rules:
                        annotation['partofspeech'] = pos
                        annotation['form'] = form
                        span.add_annotation(Annotation(span, **annotation))

    @staticmethod
    def _esc_que_mark(form):
        ''' Replaces a question mark in form (e.g. 'card ? digit' or 'ord ? roman')  
            with an escaped version of the question mark <?>
        '''
        return form.replace(' ?', ' <?>')

    @staticmethod
    def load_fs_mrf_to_syntax_mrf_translation_rules(fs_to_synt_rules_file):
        ''' Loads rules that can be used to convert from Filosoft's mrf format to
            syntactic analyzer's format. Returns a dict containing rules.
    
            Expects that each line in the input file contains a single rule, and that
            different parts of the rule are separated by @ symbols, e.g.
    
                1@_S_ ?@Substantiiv apellatiiv@_S_ com @Noun common@Nc@NCSX@kesk-
                32@_H_ ?@Substantiiv prooprium@_S_ prop @Noun proper@Np@NPCSX@Kesk-
                313@_A_@Adjektiiv positiiv@_A_ pos@Adjective positive@A-p@ASX@salkus
    
            Only the 2nd element and the 4th element are extracted from each line.
            Both are treated as a pair of strings. The 2nd element will be the key
            of the dict entry, and 4th element will be added to the value of the
            dict entry:
            {('S', '?'): [('S', 'com ')],
             ('H', '?'): [('S', 'prop ')],
             ('A', ''): [('A', 'pos')]
            }
    
            A list is used for storing values because one Filosoft's analysis could
            be mapped to multiple syntactic analyzer's analyses.
    
            Lines that have ¤ in the beginning of the line are skipped.
        '''
        rules = defaultdict(list)
        rules_pattern = re.compile(r'(¤?)[^@]*@(_(.)_\s*([^@]*)|####)@[^@]*@_(.)_\s*([^@]*)')
        with codecs.open(fs_to_synt_rules_file, mode='r', encoding='utf-8') as in_f:
            for line in in_f:
                m = rules_pattern.match(line)
                assert m is not None, ' Unexpected format of the line: ' + line
                if m.group(1): #line starts with '¤'
                    continue
                new_form = MorphToSyntaxMorphRetagger._esc_que_mark(m.group(6)).strip()
                if (m.group(5), new_form) not in rules[(m.group(3), m.group(4))]:
                    rules[(m.group(3), m.group(4))].append((m.group(5), new_form))
        for key, value in rules.items():
            # eelmise versiooniga ühildumiseks
            rules[key] = tuple(value[::-1])
        return rules
