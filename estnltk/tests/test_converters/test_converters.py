from estnltk import Span, Layer, Text
from estnltk.converters import export_CG3
from estnltk.converters import text_to_json, json_to_text
from estnltk.converters import export_TCF, import_TCF
from estnltk.converters import annotation_to_json, json_to_annotation
from estnltk.tests import new_text


def test_export_CG3():
    t = Text('Tere, maailm! Kuidas Sul läheb?')
    t.analyse('syntax_preprocessing')
    expected = ['"<s>"',
                '"<Tere>"',
                '    "tere" L0 I cap',
                '"<,>"',
                '    "," Z Com', 
                '"<maailm>"',
                '    "maa_ilm" L0 S com sg nom',
                '"<!>"',
                '    "!" Z Exc',
                '"</s>"',
                '"<s>"',
                '"<Kuidas>"',
                '    "kuidas" L0 D cap',
                '"<Sul>"',
                '    "sina" Ll P pers ps2 sg ad cap',
                '"<läheb>"',
                '    "mine" Lb V mod indic pres ps3 sg ps af <FinV>',
                '    "mine" Lb V aux indic pres ps3 sg ps af <FinV>',
                '    "mine" Lb V main indic pres ps3 sg ps af <FinV>',
                '"<?>"',
                '    "?" Z Int',
                '"</s>"']
    
    result = export_CG3(t)
    assert result == expected


T_1 = "Tere, maailm!"
T_2 = '''Mis aias sa-das 2te sorti s-saia? Teine lause.

Teine lõik.'''


def test_json_export_import():
    text = Text('')
    json_text = text_to_json(text)
    text_import = json_to_text(json_text)
    assert text_import == text
    assert json_text == text_to_json(text_import)
    
    text = Text(T_2).tag_layer(['morph_analysis', 'paragraphs'])
    text.meta['year'] = 2017
    json_text = text_to_json(text)
    text_import = json_to_text(json_text)
    assert text_import == text  
    assert json_text == text_to_json(text_import)

    text = Text(T_2)

    text = json_to_text(text_to_json(text))
    text.tag_layer(['tokens'])

    text = json_to_text(text_to_json(text))
    text.tag_layer(['compound_tokens'])

    text = json_to_text(text_to_json(text))
    text.tag_layer(['words'])

    text = json_to_text(text_to_json(text))
    text.tag_layer(['morph_analysis'])

    text = json_to_text(text_to_json(text))
    text.tag_layer(['sentences'])

    text = json_to_text(text_to_json(text))
    text.tag_layer(['paragraphs'])

    text = json_to_text(text_to_json(text))
    text.tag_layer(['morph_extended'])

    text = json_to_text(text_to_json(text))
    assert text == Text(T_2).tag_layer(['morph_extended', 'paragraphs'])

    text_list = [text, Text(''), Text(T_1), Text(T_2)]
    assert text_list == json_to_text(text_to_json(text_list))


def test_annotation_json_export_import():
    layer = Layer('my_layer', attributes=['attr', 'attr_0'])
    span = Span(0, 1, layer=layer)

    annotation = new_text(5).layer_0[0][0]

    a = json_to_annotation(span, annotation_to_json(annotation))
    assert a == annotation


def test_TCF_export_import():
    text = Text('')
    TCF_text = export_TCF(text)
    text_import = import_TCF(TCF_text)
    assert text_import == text
    assert TCF_text == export_TCF(text_import)

    text = Text(T_2).tag_layer(['morph_analysis', 'sentences'])
    del text.tokens
    del text.words
    TCF_text = export_TCF(text)
    text_import = import_TCF(TCF_text)
    assert text_import == text  
    assert TCF_text == export_TCF(text_import)

    text = Text('Karin, kes lendab New Yorki, tahab seal veeta puhkuse. Ta tuleb teisel augustil tagasi.')
    text.analyse('segmentation')
    text.analyse('morphology')
    # clauses layer
    layer = Layer(name='clauses', enveloping='words')
    layer.add_span(text.words[2:6])
    spl = text.words[0:1]
    spl.spans.extend(text.words.spans[7:11])
    layer.add_span(spl)
    layer.add_span(text.words[12:17])
    text['clauses'] = layer

    # verb_chains layer
    layer = Layer(name='verb_chains', enveloping='words')
    layer.add_span(text.words[3:4])
    layer.add_span(text.words[7:10:2])
    layer.add_span(text.words[13:17:3])
    text['verb_chains'] = layer

    # time_phrases layer
    layer = Layer(name='time_phrases', enveloping='words')
    layer.add_span(text.words[14:16])
    text['time_phrases'] = layer

    # version 0.4
    assert export_TCF(import_TCF(export_TCF(text))) == export_TCF(text)

    # version 0.5
    assert export_TCF(import_TCF(export_TCF(text, version='0.5')), version='0.5') == export_TCF(text, version='0.5')

    # version 0.5
    del text.paragraphs

    result = import_TCF(export_TCF(text, version='0.5'))
    assert text == result, text.diff(result)

    # version 0.4
    del text.clauses
    del text.verb_chains
    del text.time_phrases
    assert text == import_TCF(export_TCF(text))
