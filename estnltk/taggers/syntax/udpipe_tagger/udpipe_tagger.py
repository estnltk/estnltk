import os
from os import linesep as OS_NEWLINE
from collections import OrderedDict
from conllu.parser import parse_nullable_value
from estnltk.layer.base_span import ElementaryBaseSpan
from estnltk.core import PACKAGE_PATH
from estnltk.layer.layer import Layer
from estnltk.taggers import Tagger
from estnltk.taggers import SyntaxDependencyRetagger
from estnltk.converters.conll_exporter import sentence_to_conll
import subprocess

RESOURCES = os.path.join(PACKAGE_PATH, 'taggers', 'syntax', 'udpipe_tagger', 'resources')


def check_if_udpipe_is_in_path(udpipe_cmd: str):
    ''' Checks whether given udpipe is in system's PATH. Returns True, there is
        a file with given name (udpipe_cmd) in the PATH, otherwise returns False;

        The idea borrows from:  http://stackoverflow.com/a/377028
    '''
    if os.getenv("PATH") == None:
        return False

    for path in os.environ["PATH"].split(os.pathsep):
        path1 = path.strip('"')
        file1 = os.path.join(path1, udpipe_cmd)
        if os.path.isfile(file1) or os.path.isfile(file1 + '.exe'):
            return True
    return False


class UDPipeTagger(Tagger):
    """
    Tags dependency syntactic analysis with UDPipe.
    """
    conf_param = ['model', 'version', 'add_parent_and_children', 'syntax_dependency_retagger',
                  'udpipe_cmd']

    def __init__(self,
                 model=None,
                 output_layer='udpipe_syntax',
                 sentences_layer='sentences',
                 input_syntax_layer='conll_morph',
                 version='conllx',
                 add_parent_and_children=False,
                 udpipe_cmd=None):

        if udpipe_cmd is None:
            self.udpipe_cmd = 'udpipe'
        else:
            self.udpipe_cmd = udpipe_cmd

        if model is None:
            if version == 'conllx':
                model = os.path.join(RESOURCES, 'model_0.output')
            elif version == 'conllu':
                model = os.path.join(RESOURCES, 'model_1.output')
            else:
                raise Exception('Version should be conllu or conllx. ')

        self.model = model
        self.add_parent_and_children = add_parent_and_children
        self.output_attributes = (
            'id', 'form', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps', 'misc')
        if self.add_parent_and_children:
            self.syntax_dependency_retagger = SyntaxDependencyRetagger(conll_syntax_layer=output_layer)
            self.output_attributes += ('parent_span', 'children')
        else:
            self.syntax_dependency_retagger = None

        self.output_layer = output_layer
        self.input_layers = [sentences_layer, input_syntax_layer]

        self.version = version

        # Check for existence of udpipe executable
        if not os.path.exists(self.udpipe_cmd):
            # If the full path is not accessible, check whether the command is in PATH
            if not check_if_udpipe_is_in_path(self.udpipe_cmd):
                msg = " Could not find UDPipe executable: " + str(self.udpipe_cmd) + "!\n" + \
                      " Please make sure that UDPipe is installed in your system and\n" + \
                      " available from system's PATH variable. Alternatively, you can\n" + \
                      " provide the location of UDPipe executable via the input\n" + \
                      " argument 'udpipe_cmd'. "
                raise Exception(msg)

    def _make_layer(self, text, layers, status=None):
        sentences_layer = layers[self.input_layers[0]]
        conll_layer = layers[self.input_layers[1]]
        layer = Layer(name=self.output_layer, text_object=text, attributes=self.output_attributes, ambiguous=True,
                      parent=self.input_layers[1])
        # Collecting all sentences as an input to the model
        conll_strings = []
        for sentence in sentences_layer:
            output = sentence_to_conll(sentence, layers[self.input_layers[1]])
            conll_strings.append(output)

        input_string = ''.join(conll_strings).encode()
        # Creating command for the udpipe model
        cmd = "%s --parse %s" % (self.udpipe_cmd, self.model)
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        process.stdin.write(input_string)
        result = process.communicate()[0].decode().strip()
        process.stdin.close()
        result = result.replace(OS_NEWLINE + OS_NEWLINE, OS_NEWLINE)  # removing double newlines
        for line, span in zip(result.split(OS_NEWLINE), conll_layer):
            line = line.split('\t')
            ID = int(line[0])
            form = line[1]
            lemma = line[2]
            upostag = line[3]
            xpostag = line[4]
            feats = line[5]
            head = int(line[6])
            deprel = line[7]
            deps = line[8]
            misc = line[9]
            feats = OrderedDict([
                (part.split("=")[0], parse_nullable_value(part.split("=")[1]) if "=" in part else "")
                for part in feats.split("|") if parse_nullable_value(part.split("=")[0]) is not None
            ])
            attributes = {'id': ID, 'form': form, 'lemma': lemma, 'upostag': upostag, 'xpostag': xpostag,
                          'feats': feats, 'head': head, 'deprel': deprel, 'deps': deps, 'misc': misc}
            layer.add_annotation(span, **attributes)

        if self.add_parent_and_children:
            # Add 'parent_span' & 'children' to the syntax layer
            self.syntax_dependency_retagger.change_layer(text, {self.output_layer: layer})

        return layer

    def __doc__(self):
        print('Udpipe parser for syntactic analysis.')