import os
import stanza
from stanza.models.common.doc import Document
from estnltk.layer.layer import Layer
from estnltk.core import PACKAGE_PATH
from estnltk.taggers import Tagger
from estnltk.taggers import SyntaxDependencyRetagger


RESOURCES = os.path.join(PACKAGE_PATH, 'taggers', 'syntax', 'stanza_tagger', 'stanza_resources')

class StanzaSyntaxTagger(Tagger):
    """
    Tags dependency syntactic analysis with stanza
    """

    conf_param = ['model_path', 'add_parent_and_children', 'syntax_dependency_retagger']

    def __init__(self,
                 model_path=None,
                 output_layer='stanza_syntax',
                 sentences_layer='sentences',
                 input_syntax_layer='conll_morph',
                 add_parent_and_children=False,
                 ):
        if model_path is None:
            model_path = RESOURCES

        self.model_path = model_path
        self.add_parent_and_children = add_parent_and_children
        self.output_layer = output_layer
        self.output_attributes = ('id', 'lemma', 'upostag', 'xpostag', 'head', 'deprel')
        if add_parent_and_children:
            self.syntax_dependency_retagger = SyntaxDependencyRetagger(conll_syntax_layer=output_layer)
            self.output_attributes += ('parent_span', 'children')
        self.input_layers = [sentences_layer, input_syntax_layer]

    def _make_layer(self, text, layers, status=None):

        nlp = stanza.Pipeline(lang='et', dir=self.model_path, processors='depparse',
                              depparse_pretagged=True, logging_level='WARN')

        sentences_layer = layers[self.input_layers[0]]

        conll_layer = layers[self.input_layers[1]]

        layer = Layer(name=self.output_layer, text_object=text,
                      attributes=self.output_attributes, ambiguous=True,
                      parent=self.input_layers[1])

        data = []

        for sentence in sentences_layer:
            sentence_analysis = []
            for span in sentence.conll_morph:
                id = span.id[0]
                text = span.form[0]
                lemma = span.lemma[0]
                upos = span.upostag[0]
                xpos = span.xpostag[0]

                dict = {'id': id, 'text': text, 'lemma': lemma, 'upos': upos, 'xpos': xpos}
                sentence_analysis.append(dict)

            data.append(sentence_analysis)

        document = Document(data)
        doc = nlp(document)

        extracted_data = [analysis for sentence in doc.to_dict() for analysis in sentence]

        for line, span in zip(extracted_data, conll_layer):
            id = line['id']
            lemma = line['lemma']
            upostag = line['upos']
            xpostag = line['xpos']
            head = line['head']
            deprel = line['deprel']

            attributes = {'id': id, 'lemma': lemma, 'upostag': upostag, 'xpostag': xpostag,
                          'head': head, 'deprel': deprel}

            layer.add_annotation(span, **attributes)

        if self.add_parent_and_children:
            # Add 'parent_span' & 'children' to the syntax layer
            self.syntax_dependency_retagger.change_layer(text, {self.output_layer: layer})

        return layer
