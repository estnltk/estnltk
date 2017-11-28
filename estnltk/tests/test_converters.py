from estnltk.text import Text
from estnltk.converters import export_CG3
from estnltk.converters import export_dict, import_dict
from estnltk.converters import export_json, import_json
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

test_export_CG3()

T = '''Mis aias sa-das 2te sorti s-saia? Teine lause.

Teine lõik.'''

def test_dict_export_import():
    text = Text('')
    dict_text = export_dict(text)
    text_import = import_dict(dict_text)
    assert text_import == text
    assert dict_text == export_dict(text_import)
    
    text = Text(T).tag_layer(['morph_analysis', 'paragraphs'])
    text.meta['year'] = 2017
    dict_text = export_dict(text)
    text_import = import_dict(dict_text)
    assert text_import == text
    #assert export_dict(text) == export_dict(import_dict(export_dict(text)))

def test_json_export_import():
    text = Text('')
    json_text = export_json(text)
    text_import = import_json(json_text)
    assert text_import == text
    assert json_text == export_json(text_import)
    
    text = Text(T).tag_layer(['morph_analysis', 'paragraphs'])
    text.meta['year'] = 2017
    json_text = export_json(text)
    text_import = import_json(json_text)
    assert text_import == text  
    #assert json_text == export_json(text_import)

    text = Text(T)
    text = import_json(export_json(text))
    text.tag_layer(['tokens'])
    text = import_json(export_json(text))
    text.tag_layer(['compound_tokens'])
    text = import_json(export_json(text))
    text.tag_layer(['words'])
    #text = import_json(export_json(text))
    #text.tag_layer(['normalized_words'])
    text = import_json(export_json(text))
    text.tag_layer(['morph_analysis'])
    text = import_json(export_json(text))
    text.tag_layer(['sentences'])
    text = import_json(export_json(text))
    text.tag_layer(['paragraphs'])
    text = import_json(export_json(text))
    text.tag_layer(['morph_extended'])
    text = import_json(export_json(text))
    assert text == Text(T).tag_layer(['morph_extended', 'paragraphs'])

def test_TCF_export_import():
    text = Text('')
    TCF_text = export_TCF(text)
    text_import = import_TCF(TCF_text)
    assert text_import == text
    assert TCF_text == export_TCF(text_import)
    
    text = Text(T).tag_layer(['morph_analysis', 'sentences'])
    del text.tokens
    del text.words
    TCF_text = export_TCF(text)
    text_import = import_TCF(TCF_text)
    assert text_import == text  
    assert TCF_text == export_TCF(text_import)
