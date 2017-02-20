"""Test syntax preprocessing pipeline.

    This small test only indicates that the pipeline is not broken.
    For more elaborated testing please refer to
    estnltk/koondkorpus-experiments/syntax_preprocessing_diff
"""

from estnltk.text import words_sentences
from estnltk.syntax.syntax_preprocessing import SyntaxPreprocessing

def test():
    syntax_preprocessing = SyntaxPreprocessing()
    
    t = words_sentences('Tere maailm! Kuidas Läheb?')
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
                '"<Läheb>"',
                '    "mine" Lb V mod indic pres ps3 sg ps af cap <FinV>',
                '    "mine" Lb V aux indic pres ps3 sg ps af cap <FinV>',
                '    "mine" Lb V main indic pres ps3 sg ps af cap <FinV>',
                '"<?>"',
                '    "?" Z Int',
                '"</s>"']
    
    result = syntax_preprocessing.process_Text(t)
    assert result == expected