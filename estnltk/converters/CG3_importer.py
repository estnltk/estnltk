from estnltk.converters.cg3_annotation_parser import CG3AnnotationParser
from estnltk.taggers.syntax import vislcg3_syntax
from estnltk import Text, Layer, ElementaryBaseSpan


def import_CG3(file: str, layer_name: str):
    '''

    :param file: file containing text in VISL CG3 format
    :param layer_name: name of the layer to attach to the text objects
    :return: list of text objects with the layer attached
    '''
    with open(file, 'r', encoding='utf-8') as f:
        lines = f.read().split('\n')

    cg3 = CG3AnnotationParser()
    visl_output = vislcg3_syntax.cleanup_lines(lines)

    sentences = []
    sentence = []
    visl_lines = []
    token_in_progress = False
    for line in visl_output:
        if line and line[0] == '\t':
            if token_in_progress:
                visl_lines[-1].append(line)
            else:
                visl_lines.append([line])
                token_in_progress = True
        else:
            if line == "\"</s>\"":
                sentences.append(Text(" ".join(sentence)))
                sentence = []
            elif line and line != "\"<s>\"":
                sentence.append(line.replace("\"", "").replace("<", "").replace(">", ""))
            token_in_progress = False

    i = 0
    texts = []
    for text in sentences:
        text.analyse('segmentation')
        normal_attributes = ['id', 'lemma', 'ending', 'partofspeech', 'deprel', 'head', 'subtype', 'number', 'case',
                             'inf_form', 'mood', 'number_format', 'person', 'polarity', 'tense', 'unknown_attribute',
                             'voice']
        layer = Layer(name=layer_name, attributes=normal_attributes, text_object=text)

        for span in text.words:
            token_line = visl_lines[i][0]
            i += 1
            new_span = ElementaryBaseSpan(span.start, span.end)
            attributes = cg3.parse(token_line)
            layer.add_annotation(new_span, **attributes)

        text.add_layer(layer)
        texts.append(text)

    return texts








