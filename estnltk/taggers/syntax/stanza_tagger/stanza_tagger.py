import os
import random

import stanza
from stanza.models.common.doc import Document
from estnltk.layer.layer import Layer
from estnltk.core import PACKAGE_PATH
from estnltk.taggers import Tagger
from estnltk.taggers import SyntaxDependencyRetagger
from taggers.syntax.stanza_tagger.ud_validation_retagger import UDValidationRetagger

RESOURCES = os.path.join(PACKAGE_PATH, 'taggers', 'syntax', 'stanza_tagger', 'stanza_resources')


class StanzaSyntaxTagger(Tagger):
    """
    Tags dependency syntactic analysis with Stanza
    """

    conf_param = ['model_path', 'model_name', 'add_parent_and_children', 'syntax_dependency_retagger',
                  'input_type', 'dir', 'mark_syntax_error', 'ud_validation_retagger']

    def __init__(self,
                 output_layer='stanza_syntax',
                 sentences_layer='sentences',
                 words_layer='words',
                 input_morph_layer='morph_analysis',
                 input_type='morph_only',  # or 'morph_extended', 'sentences'
                 add_parent_and_children=False,
                 depparse_path=None,
                 mark_syntax_error=False,
                 use_gpu=False
                 ):

        self.add_parent_and_children = add_parent_and_children
        self.mark_syntax_error = mark_syntax_error
        self.output_layer = output_layer
        self.output_attributes = ('id', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps', 'misc')
        self.input_type = input_type
        self.dir = RESOURCES

        if add_parent_and_children:
            self.syntax_dependency_retagger = SyntaxDependencyRetagger(conll_syntax_layer=output_layer)
            self.output_attributes += ('parent_span', 'children')

        if mark_syntax_error:
            self.ud_validation_retagger = UDValidationRetagger(output_layer=output_layer)
            self.output_attributes += ('syntax_error', 'error_message')

        if self.input_type not in ['sentences', 'morph_only', 'morph_extended']:
            raise ValueError('Invalid input type {}'.format(input_type))

        if depparse_path and not os.path.isfile(depparse_path):
            raise ValueError('Invalid path: {}'.format(depparse_path))
        elif depparse_path and os.path.isfile(depparse_path):
            self.model_path = depparse_path
        else:
            if input_type == 'morph_only':
                self.model_path = os.path.join(RESOURCES, 'et', 'depparse', 'morph_analysis.pt')
            if input_type == 'morph_extended':
                self.model_path = os.path.join(RESOURCES, 'et', 'depparse', 'morph_extended.pt')
            if input_type == 'sentences':
                self.model_path = os.path.join(RESOURCES, 'et', 'depparse', 'stanza_depparse.pt')

        if self.input_type == 'sentences':
            self.input_layers = [sentences_layer, words_layer]
            self.nlp = stanza.Pipeline(lang='et', processors='tokenize,pos,lemma,depparse',
                                       dir=self.dir,
                                       tokenize_pretokenized=True,
                                       depparse_model_path=self.model_path,
                                       use_gpu=self.use_gpu,
                                       logging_level='WARN')  # Logging level chosen so it does not display
            # information about downloading model

        elif self.input_type in ['morph_only', 'morph_extended']:
            self.input_layers = [sentences_layer, input_morph_layer, words_layer]
            self.nlp = stanza.Pipeline(lang='et', processors='depparse',
                                       dir=self.dir,
                                       depparse_pretagged=True,
                                       depparse_model_path=self.model_path,
                                       use_gpu=self.use_gpu,
                                       logging_level='WARN')

    def _make_layer(self, text, layers, status=None):

        if self.input_type in ['morph_only', 'morph_extended']:
            # stanza on pretagged morph analysis
            nlp = stanza.Pipeline(lang='et', processors='depparse',
                                  dir=self.dir,
                                  depparse_pretagged=True,
                                  depparse_model_path=self.model_path,
                                  use_gpu=False,
                                  logging_level='WARN')

            sentences_layer = layers[self.input_layers[0]]
            data = []

            for sentence in sentences_layer:
                sentence_analysis = []

                # TODO Replace sentence.__getattr__ with appropriate code
                for i, span in enumerate(sentence.__getattr__(self.input_layers[1])):
                    annotation = random.choice(span.annotations)
                    id = i + 1
                    wordform = span.text
                    lemma = annotation['lemma']

                    feats = ''

                    if annotation['form']:
                        feats = annotation['form']

                    if self.input_type == 'morph_extended':
                        feats = attributes_to_feats(feats, annotation)

                    if not feats:
                        feats = '_'

                    else:
                        # Make and join keyed features.
                        feats = '|'.join([a + '=' + a for a in feats.strip().split(' ') if a])
                    xpos = annotation['partofspeech']  # xpos and upos have the same value
                    dict = {'id': id, 'text': wordform, 'lemma': lemma, 'feats': feats, 'upos': xpos, 'xpos': xpos}
                    sentence_analysis.append(dict)

                data.append(sentence_analysis)

            document = Document(data)

        # Stanza pipeline on pretagged tokens/sentences.
        else:
            sentences_layer = layers[self.input_layers[0]]
            document = [sentence.text for sentence in sentences_layer]

        parent_layer = layers[self.input_layers[1]]

        layer = Layer(name=self.output_layer,
                      text_object=text,
                      attributes=self.output_attributes,
                      parent=self.input_layers[1],
                      ambiguous=False,
                      )

        doc = self.nlp(document)

        extracted_data = [analysis for sentence in doc.to_dict() for analysis in sentence]

        for line, span in zip(extracted_data, parent_layer):
            id = line['id']
            lemma = line['lemma']
            upostag = line['upos']
            xpostag = line['xpos']
            if 'feats' not in line.keys():
                feats = '_'
            else:
                feats = line['feats']
            head = line['head']
            deprel = line['deprel']

            attributes = {'id': id, 'lemma': lemma, 'upostag': upostag, 'xpostag': xpostag, 'feats': feats,
                          'head': head, 'deprel': deprel, 'deps': '_', 'misc': '_'}

            layer.add_annotation(span, **attributes)

        if self.add_parent_and_children:
            # Add 'parent_span' & 'children' to the syntax layer.
            self.syntax_dependency_retagger.change_layer(text, {self.output_layer: layer})

        if self.mark_syntax_error:
            # Add 'syntax_error' to the layer.
            self.ud_validation_retagger.change_layer(text, {self.output_layer: layer})

        return layer


def add_punctuation_type(feats, annotation):
    """ Adds value of `punctuation_type` field to feats """
    if not annotation['punctuation_type']:
        return feats
    return feats + ' ' + annotation['punctuation_type']


def add_pronoun_type(feats, annotation):
    """ Adds values of `pronoun_type` field to feats. In case of personal pronoun, adds keyword 'pers' """
    if not annotation['pronoun_type']:
        return feats
    pron_type = annotation['pronoun_type']
    if 'ps1' in pron_type or 'ps2' in pron_type or 'ps3' in pron_type:
        feats += ' pers'
    if isinstance(annotation['pronoun_type'], str):
        return feats + ' ' + annotation['pronoun_type']
    for pron in annotation['pronoun_type']:
        feats += ' ' + pron
    return feats


def attributes_to_feats(feats, annotation):
    """Making input more similar to experiment models' input.
    {'sup', 'Grt', 'ger', 'roman', 'partic', 'inf', 'digit'} are not used by VislTagger
    but are used in morph_extended layer, so they are kept.
    """
    feats = add_pronoun_type(feats, annotation)
    feats = add_punctuation_type(feats, annotation)
    feats = feats.replace('_', '')
    feats = feats.replace('<?>', '')
    return feats.replace('invalid', '')
