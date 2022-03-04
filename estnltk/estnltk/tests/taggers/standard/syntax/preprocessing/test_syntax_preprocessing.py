"""Test syntax preprocessing pipeline.

    This small test only indicates that the pipeline is not broken.
    For more elaborated testing please refer to
    estnltk/koondkorpus-experiments/syntax_preprocessing_diff
"""

from estnltk import Text
from estnltk.converters import export_CG3

def test():
    t = Text('Tere maailm! Kuidas Sul läheb?')
    t.tag_layer('morph_extended')
    expected = ['"<s>"',
                '"<Tere>"',
                '    "tere" L0 I cap',
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
