from estnltk import Span, Layer, Text, ElementaryBaseSpan
from estnltk.converters import export_CG3
from estnltk.converters import export_TCF, import_TCF
from estnltk.tests import new_text


def test_export_CG3():
    t = Text('Tere, maailm! Kuidas Sul läheb?')
    t.tag_layer(['sentences','morph_extended'])
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


def test_TCF_export_import():
    text = Text('')
    TCF_text = export_TCF(text)
    text_import = import_TCF(TCF_text)
    assert text_import == text
    assert TCF_text == export_TCF(text_import)

    text = Text(T_2).tag_layer(['morph_analysis', 'sentences'])
    text.pop_layer('tokens')
    text.pop_layer('words')
    TCF_text = export_TCF(text)
    text_import = import_TCF(TCF_text)
    assert text_import == text  
    assert TCF_text == export_TCF(text_import)

    text = Text('Karin, kes lendab New Yorki, tahab seal veeta puhkuse. Ta tuleb teisel augustil tagasi.')
    text.tag_layer(['paragraphs','morph_analysis'])
    text.pop_layer('tokens')
    # clauses layer
    layer = Layer(name='clauses', enveloping='words')
    layer.add_annotation(text.words[2:6])
    spl = text.words[0:1]
    spl.spans.extend(text.words.spans[7:11])
    layer.add_annotation(spl)
    layer.add_annotation(text.words[12:17])
    text.add_layer(layer)

    # verb_chains layer
    layer = Layer(name='verb_chains', enveloping='words')
    layer.add_annotation(text.words[3:4])
    layer.add_annotation(text.words[7:10:2])
    layer.add_annotation(text.words[13:17:3])
    text.add_layer(layer)

    # time_phrases layer
    layer = Layer(name='time_phrases', enveloping='words')
    layer.add_annotation(text.words[14:16])
    text.add_layer(layer)

    # version 0.4
    assert export_TCF(import_TCF(export_TCF(text))) == export_TCF(text)

    # version 0.5
    assert export_TCF(import_TCF(export_TCF(text, version='0.5')), version='0.5') == export_TCF(text, version='0.5')

    # version 0.5
    text.pop_layer('paragraphs')

    result = import_TCF(export_TCF(text, version='0.5'))
    assert text == result, text.diff(result)

    # version 0.4
    text.pop_layer('clauses')
    text.pop_layer('verb_chains')
    text.pop_layer('time_phrases')
    assert text == import_TCF(export_TCF(text))
