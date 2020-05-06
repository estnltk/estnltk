from estnltk.layer.base_span import ElementaryBaseSpan
from estnltk.core import PACKAGE_PATH
from estnltk.layer.layer import Layer
from estnltk.taggers import Tagger
from estnltk.taggers import SyntaxDependencyRetagger
from estnltk.converters.conll_exporter import sentence_to_conll
import subprocess
import os

RESOURCES = os.path.join(PACKAGE_PATH, 'taggers', 'syntax', 'udpipe_tagger', 'resources')

class UDPipeTagger(Tagger):
    """
    Input layers should be sentences and conll_morph. Conll_morph can be replaced with something similar.
    Version should be conllx or conllu. Different UDPipe model is used with either version, otherwise the
    output does not make sense.
    """
    conf_param = ['model', 'version', 'udpipe_path', 'add_parent_and_children', 'syntax_dependency_retagger', 'output_attributes']

    def __init__(self,
                 model=None,
                 output_layer='udpipe_syntax',
                 input_layers=None,
                 input_syntax_layer='conll_morph',
                 version=None,
                 udpipe_path=None,
                 output_attributes=None,
                 add_parent_and_children=False):


        if input_layers is None:
            input_layers = ['sentences', input_syntax_layer]
        if version is None:
            version = 'conllx'
        if udpipe_path is None:
            udpipe_path = RESOURCES + '\\udpipe'
        if output_attributes is None:
            output_attributes = ('id', 'form', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps', 'misc')
        if model is None:
            if version == 'conllx':
                model = RESOURCES + '\\model_0.output'
            elif version == 'conllu':
                model = RESOURCES + '\\model_1.output'
            else:
                raise Exception('Version should be conllu or conllx. ')

        self.model = model
        self.add_parent_and_children = add_parent_and_children
        self.output_attributes = output_attributes
        if self.add_parent_and_children:
            self.syntax_dependency_retagger = SyntaxDependencyRetagger(conll_syntax_layer=output_layer)
            self.output_attributes += ('parent_span', 'children')
        else:
            self.syntax_dependency_retagger = None
        self.udpipe_path = udpipe_path
        self.output_layer = output_layer
        self.input_layers = input_layers

        self.version = version

    def _make_layer(self, text, layers, status=None):
        conllu_string = sentence_to_conll(text.sentences[0], text[self.input_layers[1]]).encode()

        layer = Layer(name=self.output_layer, text_object=text, attributes=self.output_attributes, ambiguous=True,
                      parent=self.input_layers[1])
        cmd = "%s --parse %s" % (self.udpipe_path, self.model)

        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        process.stdin.write(conllu_string)
        result = process.communicate()[0].decode().strip()
        process.stdin.close()

        start = 0
        for line in result.split('\r\n'):
            line = line.split('\t')
            ID = line[0]
            form = line[1]
            lemma = line[2]
            upostag = line[3]
            xpostag = line[4]
            feats = line[5]
            head = line[6]
            deprel = line[7]
            deps = line[8]
            misc = line[9]
            span = ElementaryBaseSpan(start, start + len(form))
            attributes = {'id': ID, 'form': form, 'lemma': lemma, 'upostag': upostag, 'xpostag': xpostag,
                          'feats': feats, 'head': head, 'deprel': deprel, 'deps': deps, 'misc': misc}
            layer.add_annotation(span, **attributes)
            start += len(form) + 1

        if self.add_parent_and_children:
            # Add 'parent_span' & 'children' to the syntax layer
            self.syntax_dependency_retagger.change_layer(text, {self.output_layer: layer})

        return layer

    def __doc__(self):
        print('Udpipe parser for syntactic analysis.')
