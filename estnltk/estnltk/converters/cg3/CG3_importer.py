from typing import List
import re
from estnltk import ElementaryBaseSpan
from estnltk import Text, Layer, Annotation
from estnltk.converters.cg3.cg3_annotation_parser import CG3AnnotationParser
from estnltk.converters.cg3.helpers import cleanup_lines


def import_CG3(file: str, layer_name: str = "syntax_gold") -> List[Text]:
    """

    :param file: file in cg3 format
    :param layer_name: layer name
    :return: list of Text objects with the constructed layer
    """
    with open(file, 'r', encoding='utf-8') as f:
        lines = f.read().split('\n')

    cg3 = CG3AnnotationParser()
    visl_output = cleanup_lines(lines)

    sentence = []
    visl_lines = []
    token_in_progress = False
    texts = []
    for line in visl_output:
        if line and line[0] == '\t':
            if token_in_progress:
                visl_lines[-1].append(line)
            else:
                visl_lines.append([line])
                token_in_progress = True
        else:
            if line == "\"</s>\"":

                text = Text(' '.join(sentence))
                words = Layer(name='words',
                              text_object=text,
                              attributes=[],
                              ambiguous=True
                              )
                sentences = Layer(name='sentences',
                                  text_object=text,
                                  attributes=[],
                                  enveloping='words',
                                  ambiguous=False
                                  )

                normal_attributes = ['id',
                                     'lemma',
                                     'partofspeech',
                                     'deprel',
                                     'head',
                                     'subtype',
                                     'ending',
                                     'capitalized',
                                     'clause_boundary',
                                     'subcat',
                                     'number',
                                     'case',
                                     'inf_form',
                                     'mood',
                                     'number_format',
                                     'person',
                                     'polarity',
                                     'tense',
                                     'unknown_attribute',
                                     'voice']
                syntax = Layer(name=layer_name, attributes=normal_attributes, text_object=text)

                start = 0
                for visl_line, word in zip(visl_lines, sentence):
                    base_span = ElementaryBaseSpan(start, start + len(word))
                    start += len(word) + 1
                    attributes = cg3.parse(visl_line[0])
                    new_attributes = {key: value[0] if type(value) == list else value for key, value in
                                      attributes.items()}
                    syntax.add_annotation(base_span, **new_attributes)
                    words.add_annotation(base_span)

                sentences.add_annotation(words)
                text.add_layer(words)
                text.add_layer(sentences)
                text.add_layer(syntax)

                texts.append(text)

                sentence = []
                visl_lines = []

            elif line and line != "\"<s>\"":
                line = re.sub(r'^\"', '', line)
                line = re.sub(r'\"$', '', line)
                line = re.sub(r'^<', '', line)
                line = re.sub(r'>$', '', line)
                sentence.append(line)
            token_in_progress = False

    return texts
