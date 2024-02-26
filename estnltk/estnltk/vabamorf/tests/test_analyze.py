import unittest
import operator

from functools import reduce
from estnltk.vabamorf.morf import trim_phonetics, get_group_tokens, postprocess_analysis, convert
from estnltk.vabamorf.morf_extra import analyze

# noinspection PyUnresolvedReferences
from estnltk.vabamorf.vabamorf import Analysis


# noinspection SpellCheckingInspection
class TrimPhoneticsTest(unittest.TestCase):
    
    def test_tilde(self):
        self.assertEqual(trim_phonetics('~'), '~')

    def test_tilde_repetition(self):
        self.assertEqual(trim_phonetics('~~~'), '~~~')

    def test_questionmark(self):
        self.assertEqual(trim_phonetics('?'), '?')

    def test_questionmark_repetition_1(self):
        self.assertEqual(trim_phonetics('???'), '???')

    def test_questionmark_repetition_2(self):
        self.assertEqual(trim_phonetics('??????'), '??????')

    def test_rbracket(self):
        self.assertEqual(trim_phonetics(']'), ']')
        
    def test_lessthan(self):
        self.assertEqual(trim_phonetics('<'), '<')
        
    def test_phonetics(self):
        self.assertEqual(trim_phonetics('~~???ab]c<d'), 'abcd')


# noinspection SpellCheckingInspection
class TokensTest(unittest.TestCase):

    def get_tokens(self, root):
        return reduce(operator.add, get_group_tokens(root))

    def test_simple(self):
        tokens = self.get_tokens('all_+maa_raud_tee_jaam~~+')
        self.assertListEqual(tokens, ['all', 'maa', 'raud', 'tee', 'jaam'])

    def test_hyphen_grouping(self):
        tokens = self.get_tokens('saunameheks-tallimeheks-majahoidjaks')
        self.assertListEqual(tokens, ['saunameheks', 'tallimeheks', 'majahoidjaks'])

    def test_underscore(self):
        tokens = self.get_tokens('_')
        self.assertListEqual(tokens, ['_'])
        
    def test_plus(self):
        tokens = self.get_tokens('+')
        self.assertListEqual(tokens, ['+'])
        
    def test_equalmark(self):
        tokens = self.get_tokens('=')
        self.assertListEqual(tokens, ['='])
    
    def test_ltmark(self):
        tokens = self.get_tokens('<')
        self.assertListEqual(tokens, ['<'])
   
    def test_bracketclose(self):
        tokens = self.get_tokens(']')
        self.assertListEqual(tokens, [']'])
        
    def test_hyphen(self):
        tokens = self.get_tokens('-')
        self.assertListEqual(tokens, ['-'])


# noinspection SpellCheckingInspection
class AnalysisAsDictTest(unittest.TestCase):
    
    def test_verb_phonetic_compound(self):
        self.assertDictEqual(postprocess_analysis(self.verbanalysis(), True, True),
                             self.verb_phonetic_compound())
    
    def test_verb_compound(self):
        self.assertDictEqual(postprocess_analysis(self.verbanalysis(), False, True),
                             self.verb_compound())
    
    def test_verb_phonetic(self):
        self.assertDictEqual(postprocess_analysis(self.verbanalysis(), True, False),
                             self.verb_phonetic())
    
    def test_verb(self):
        self.assertDictEqual(postprocess_analysis(self.verbanalysis(), False, False),
                             self.verb())

    def verbanalysis(self):
        return Analysis(convert('l<aul'),
                        convert('b'),
                        convert(''),
                        convert('V'),
                        convert('b'))
    
    def verb_phonetic_compound(self):
        return {'clitic': '',
                'ending': 'b',
                'form': 'b',
                'lemma': 'laulma',
                'partofspeech': 'V',
                'root_tokens': ['laul'],
                'root': 'l<aul'}
    
    def verb_compound(self):
        return {'clitic': '',
                'ending': 'b',
                'form': 'b',
                'lemma': 'laulma',
                'partofspeech': 'V',
                'root_tokens': ['laul'],
                'root': 'laul'}
                
    def verb_phonetic(self):
        return {'clitic': '',
                'ending': 'b',
                'form': 'b',
                'lemma': 'laulma',
                'partofspeech': 'V',
                'root_tokens': ['laul'],
                'root': 'l<aul'}

    def verb(self):
        return {'clitic': '',
                'ending': 'b',
                'form': 'b',
                'lemma': 'laulma',
                'partofspeech': 'V',
                'root_tokens': ['laul'],
                'root': 'laul'}

    def substantiveanalysis(self):
        return Analysis(convert('lennuki_k<an]dja'),
                        convert('ile'),
                        convert(''),
                        convert('S'),
                        convert('pl all'))

    def test_substantive_phonetic_compound(self):
        self.assertDictEqual(postprocess_analysis(self.substantiveanalysis(), True, True),
                             self.substantive_phonetic_compound())
    
    def test_substantive_compound(self):
        self.assertDictEqual(postprocess_analysis(self.substantiveanalysis(), False, True),
                             self.substantive_compound())
    
    def test_substantive_phonetic(self):
        self.assertDictEqual(postprocess_analysis(self.substantiveanalysis(), True, False),
                             self.substantive_phonetic())
    
    def test_substantive(self):
        self.assertDictEqual(postprocess_analysis(self.substantiveanalysis(), False, False),
                             self.substantive())

    def substantive_phonetic_compound(self):
        return {'clitic': '',
                'ending': 'ile',
                'form': 'pl all',
                'lemma': 'lennukikandja',
                'partofspeech': 'S',
                'root_tokens': ['lennuki', 'kandja'],
                'root': 'lennuki_k<an]dja'}

    def substantive_compound(self):
        return {'clitic': '',
                'ending': 'ile',
                'form': 'pl all',
                'lemma': 'lennukikandja',
                'partofspeech': 'S',
                'root_tokens': ['lennuki', 'kandja'],
                'root': 'lennuki_kandja'}
                
    def substantive_phonetic(self):
        return {'clitic': '',
                'ending': 'ile',
                'form': 'pl all',
                'lemma': 'lennukikandja',
                'partofspeech': 'S',
                'root_tokens': ['lennuki', 'kandja'],
                'root': 'lennukik<an]dja'}
                
    def substantive(self):
        return {'clitic': '',
                'ending': 'ile',
                'form': 'pl all',
                'lemma': 'lennukikandja',
                'partofspeech': 'S',
                'root_tokens': ['lennuki', 'kandja'],
                'root': 'lennukikandja'}
                

# noinspection SpellCheckingInspection
class TextIsSameAsListTest(unittest.TestCase):

    # http://luuletused.ee/1005/elu/hetke-volu  (by Seebivaht)
    SAMPLE_TEXT = '''Ma tahaks suudelda päikesekiiri
    vat nii ihalevad mu huuled päikese suule..
    Ma tahaks tantsida kesksuvises vihmas
    vat nii tunglevad minu tunded südames suures
    
    Keegi kord ütles, et ära karda
    armastus saab aja jooksul ainult kasvada
    Võta kõik vastu, mis sulle pakutakse,
    sest see, mis sulle antakse
    on sinu jaoks loodud'''

    def test_same(self):
        self.run_test(False, False, False)
        
    def test_same_guess(self):
        self.run_test(True, False, False)
    
    def test_same_phonetic(self):
        self.run_test(False, True, False)
    
    def test_same_compound(self):
        self.run_test(False, False, True)
    
    def test_same_heuristic_phonetic(self):
        self.run_test(True, True, False)

    def test_same_heuristic_compound(self):
        self.run_test(True, False, True)
        
    def test_same_phonetic_compound(self):
        self.run_test(False, True, True)
    
    def run_test(self, guess, phonetic, compound):
        text_output = analyze(self.text(),
                              guess=guess,
                              phonetic=phonetic,
                              compound=compound)
        list_output = analyze(self.text().split(),
                              guess=guess,
                              phonetic=phonetic,
                              compound=compound)
        self.assertListEqual(text_output, list_output)
    
    def text(self):
        return self.SAMPLE_TEXT


# noinspection SpellCheckingInspection
class DisambiguationTest(unittest.TestCase):

    # http://luuletused.ee/1005/elu/hetke-volu  (by Seebivaht)
    SAMPLE_TEXT = '''Ma tahaks suudelda päikesekiiri
    vat nii ihalevad mu huuled päikese suule..
    Ma tahaks tantsida kesksuvises vihmas
    vat nii tunglevad minu tunded südames suures
    
    Keegi kord ütles, et ära karda
    armastus saab aja jooksul ainult kasvada
    Võta kõik vastu, mis sulle pakutakse,
    sest see, mis sulle antakse
    on sinu jaoks loodud'''

    def test_disambiguation(self):
        yes = analyze(self.SAMPLE_TEXT, disambiguate=True)
        no = analyze(self.SAMPLE_TEXT, disambiguate=False)

        self.assertEqual(len(yes), len(no))
        for first, second in zip(yes, no):
            yes = len(first['analysis'])
            no = len(second['analysis'])
            self.assertLessEqual(yes, no)


class NameGroupingTest(unittest.TestCase):
    """
    The C++ module vabamorf used to concatenate cases like "New York" a sa single token
    in previous versions, which was an unexpected feature. It should not happen anymore.
    """

    def test_grouping(self):
        analysis = analyze('See on New York')
        self.assertEqual(4, len(analysis))
