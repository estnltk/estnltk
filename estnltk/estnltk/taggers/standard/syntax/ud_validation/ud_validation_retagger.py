import os
import re
import subprocess
import tempfile
from typing import MutableMapping

from estnltk.common import PACKAGE_PATH
from estnltk import Layer
from estnltk.taggers import Retagger

VALIDATION_PATH = os.path.join(PACKAGE_PATH, 'taggers', 'standard', 'syntax', 'ud_validation')


class UDValidationRetagger(Retagger):
    """
    Check syntax layer in UD-format against common errors and inconsistencies
    Adds `syntax_error` attribute to the syntax layer.
    Syntax layer must have attributes `id`, `head`, `lemma`, `upostag`, `xpostag`, `feats`, `deprel`, `dep` and `misc`
    in order to be formatted as conllu and validated by UD validation script from
    https://github.com/universaldependencies/tools/

    Value of attribute `syntax_error` is True if any syntactic errors (such as non-projectivity, unsuitable children etc)
    were discovered, otherwise False. Syntactic errors relating to UPOS-tag are ignored.
    """

    conf_param = []

    def __init__(self, output_layer='stanza_syntax'):
        self.input_layers = [output_layer]
        self.output_layer = output_layer
        self.output_attributes = ()

    def _change_layer(self, raw_text: str, layers: MutableMapping[str, Layer], status: dict):
        layer = layers[self.output_layer]
        attributes = list(layer.attributes)
        if 'syntax_error' not in layer.attributes:
            attributes.extend(('syntax_error',))
        if 'error_message' not in layer.attributes:
            attributes.extend(('error_message',))
        layer.attributes = tuple(attributes)

        # Create conll-string from layer and writing to file
        # for using it as input for validation.py
        conll_str = ''
        for i, span in enumerate(layer):
            annotation = span.annotations[0]
            if i != 0 and annotation['id'] == 1:
                conll_str += '\n'  # Sentence break
            conll_str += '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (
                annotation['id'], annotation.text, annotation['lemma'], annotation['upostag'], annotation['xpostag'],
                annotation['feats'], annotation['head'], annotation['deprel'], annotation['deps'], annotation['misc'])
        conll_str += '\n'

        # Line numbers of raw text that contained syntactic errors
        error_lines, error_messages = ud_validation_errors(conll_str)

        # Iterate over lines (and keep track of empty lines between sentences)
        # to detect if line/word has errors
        raw_text_line_no = 0

        for i, span in enumerate(layer):
            raw_text_line_no += 1
            annotation = span.annotations[0]
            if i != 0 and annotation['id'] == 1:   # Keeping track of empty lines between sentences
                raw_text_line_no += 1
            if raw_text_line_no in error_lines:
                annotation['syntax_error'] = True
                error_idx = error_lines.index(raw_text_line_no)
                error_lines.remove(raw_text_line_no)
                annotation['error_message'] = error_messages.pop(error_idx)
            else:
                annotation['syntax_error'] = False
                annotation['error_message'] = None


def ud_validation_errors(conll_str):
    """
    Validates conllu-format string and returns lines that contain syntactcic errors.
    :param conll_str: string in conllu-format
    :return: list of
    """
    temp_input = tempfile.NamedTemporaryFile('w+', encoding='utf-8', delete=False)
    with open(temp_input.name, 'w', encoding='utf-8') as out:
        out.write(conll_str)

    error_lines = list()
    error_messages = list()

    cmd = 'python ' + VALIDATION_PATH + '/validate.py --lang et --max-err=0 --level 3 ' + temp_input.name

    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=1, stderr=subprocess.PIPE,
                               shell=True, universal_newlines=True)

    result, err = process.communicate()

    for line in err.strip().splitlines():
        finds = re.findall(r"^\[Line ([0-9]+) Node [0-9]+\]: \[L3 Syntax ([^\]]+\]) (.*)$", line)
        for row, error, error_message in finds:
            # Syntax errors concerning UPOS-tags are not of interest as StanzaSyntaxTagger returns
            # (on most cases) VabaMorf's tags as UPOS, which are considered erroneous.
            if 'upos' not in error:
                error_lines.append(int(row))
                error_messages.append(error_message)

    temp_input.close()
    os.remove(temp_input.name)

    return error_lines, error_messages
