import os
import re
import subprocess
import tempfile
from typing import MutableMapping

from estnltk.core import PACKAGE_PATH
from estnltk.layer.layer import Layer
from estnltk.taggers.retagger import Retagger

VALIDATION_PATH = os.path.join(PACKAGE_PATH, 'taggers', 'syntax', 'stanza_tagger', 'stanza_resources')


class UDValidationRetagger(Retagger):
    """Adds `syntax_error` attribute to the syntax layer.
    Syntax layer must have attributes `id`, `head`, `lemma`, `upostag`, `xpostag`, `feats`, `deprel`, `dep` and `misc`
    in order to be formatted as conllu and validated by UD validation script from
    https://github.com/universaldependencies/tools/

    Value of attribute `syntax_error` is 1 if any syntactic errors (such as non-projectivity, unsuitable children etc)
    were discovered, otherwise 0. Syntactic errors relating to UPOS-tag are ignored.
    """

    conf_param = []

    def __init__(self, output_layer='stanza_syntax'):
        print(output_layer)
        self.input_layers = [output_layer]
        self.output_layer = output_layer
        self.output_attributes = ()

    def _change_layer(self, raw_text: str, layers: MutableMapping[str, Layer], status: dict):
        layer = layers[self.output_layer]
        attributes = list(layer.attributes)
        attributes.extend(attr for attr in ['syntax_error']
                          if attr not in layer.attributes)
        layer.attributes = tuple(attributes)

        # create conll-string similarly to conll_morph_to_str.py
        conll_str = ''
        for i, span in enumerate(layer):
            annotation = span.annotations[0]
            if i != 0 and annotation.id == 1:
                conll_str += '\n'
            conll_str += '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (
                annotation.id, annotation.text, annotation.lemma, annotation.upostag, annotation.xpostag,
                annotation.feats, annotation.head, annotation.deprel, annotation.deps, annotation.misc)

        conll_str += '\n'

        temp_conll = tempfile.NamedTemporaryFile('w+', encoding='utf-8', delete=False)
        with open(temp_conll.name, 'w', encoding='utf-8') as out:
            out.write(conll_str)
        syntax_errors = ud_validation_errors(temp_conll.name)
        temp_conll.close()
        os.remove(temp_conll.name)

        # go over lines to mark erroneous words
        line_no = 0

        for i, span in enumerate(layer):
            line_no += 1
            annotation = span.annotations[0]
            if i != 0 and annotation.id == 1:
                line_no += 1
            if line_no in syntax_errors:
                annotation.syntax_error = 1
            else:
                annotation.syntax_error = 0


def ud_validation_errors(filename):
    """
    :return: List of line numbers where syntax errors are in given file
    """
    errors = list()
    temp = tempfile.NamedTemporaryFile('w+', encoding='utf-8', delete=False)
    subprocess.run('python ' + VALIDATION_PATH + '/validate.py --lang et --max-err=0 --level 3 ' + filename,
                   stderr=temp)
    temp.seek(0)
    for line in temp:
        finds = re.findall(r"^\[Line ([0-9]+) Node [0-9]+\]: \[L3 Syntax ([^\]]+\])", line)
        for row, error in finds:
            if 'upos' not in error:
                errors.append(int(row))

    temp.close()
    os.remove(temp.name)

    return errors
