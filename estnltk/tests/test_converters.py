from estnltk.text import Text
from estnltk.converters import export_CG3
from estnltk.converters import text_to_dict, dict_to_text
from estnltk.converters import text_to_json, json_to_text
from estnltk.converters import export_TCF, import_TCF


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


def test_dict_export_import():
    text = Text('')
    dict_text = text_to_dict(text)
    text_import = dict_to_text(dict_text)
    assert text_import == text
    assert dict_text == text_to_dict(text_import)
    
    text = Text(T_2).tag_layer(['morph_analysis', 'paragraphs'])
    text.meta['year'] = 2017
    dict_text = text_to_dict(text)
    text_import = dict_to_text(dict_text)
    assert text_import == text
    assert text_to_dict(text) == text_to_dict(dict_to_text(text_to_dict(text)))

    text_list = [Text(''), Text(T_1), Text(T_2)]
    assert text_list == dict_to_text(text_to_dict(text_list))


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
