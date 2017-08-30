import unittest

from estnltk.taggers.text_segmentation.tokens_tagger import TokensTagger
from estnltk import Text
tokenizer = TokensTagger()


class TokensTaggerTest(unittest.TestCase):

    def test_separate_accumulated_punctuation(self):
        text = Text('Ta elas küll VI sajandil e.m.a., ise ta aga midagi ei kirjutanud.')
        expected_tokens = ['Ta', 'elas', 'küll', 'VI', 'sajandil', 'e', '.', 'm', '.', 'a', '.', ',', 'ise', 'ta', 'aga', 'midagi', 'ei', 'kirjutanud', '.']
        result = tokenizer.tag(text)
        spans  = [(sp.start, sp.end) for sp in result['tokens'].spans]
        tokens = [text.text[start:end] for (start, end) in spans]
        self.assertListEqual(expected_tokens, tokens)
        
        text = Text('(nõue hakkas kehtima 1989.a.).')
        expected_tokens = ['(', 'nõue', 'hakkas', 'kehtima', '1989', '.', 'a', '.', ')', '.']
        result = tokenizer.tag(text)
        spans  = [(sp.start, sp.end) for sp in result['tokens'].spans]
        tokens = [text.text[start:end] for (start, end) in spans]
        self.assertListEqual(expected_tokens, tokens)
        
        text = Text('Tuleks kaasata ka OÜ Ketal Võru (kes soos kaevetöid tegema tahaks hakata – toim.);')
        expected_tokens = ['Tuleks', 'kaasata', 'ka', 'OÜ', 'Ketal', 'Võru', '(', 'kes', 'soos', 'kaevetöid', 'tegema', 'tahaks', 'hakata', '–', 'toim', '.', ')', ';']
        result = tokenizer.tag(text)
        spans  = [(sp.start, sp.end) for sp in result['tokens'].spans]
        tokens = [text.text[start:end] for (start, end) in spans]
        self.assertListEqual(expected_tokens, tokens)


    def test_separate_mistakenly_conjoined_sentences(self):
        text1 = Text('Iga päev teeme valikuid.Valime kõike.')
        expected_tokens = ['Iga', 'päev', 'teeme', 'valikuid', '.', 'Valime', 'kõike', '.']
        result = tokenizer.tag(text1)
        spans  = [(sp.start, sp.end) for sp in result['tokens'].spans]
        tokens = [text1.text[start:end] for (start, end) in spans]
        self.assertListEqual(expected_tokens, tokens)
        
        text2 = Text('Ja siis veel ühe.Ja veel ühe.')
        expected_tokens = ['Ja', 'siis', 'veel', 'ühe', '.', 'Ja', 'veel', 'ühe', '.'] 
        result = tokenizer.tag(text2)
        spans  = [(sp.start, sp.end) for sp in result['tokens'].spans]
        tokens = [text2.text[start:end] for (start, end) in spans]
        self.assertListEqual(expected_tokens, tokens)
