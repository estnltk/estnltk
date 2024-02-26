from estnltk.vabamorf.syllabify import syllabify_word
from estnltk.vabamorf.syllabify import _split_word_for_syllabification
from estnltk.vabamorf.syllabify import _split_compound_word_heuristically
import unittest


# noinspection SpellCheckingInspection
class SyllabificationTest(unittest.TestCase):

    def test_elagu(self):
        actual = syllabify_word('elagu')
        expected = [
            {'accent': 1, 'quantity': 1, 'syllable': 'e'},
            {'accent': 0, 'quantity': 1, 'syllable': 'la'},
            {'accent': 0, 'quantity': 1, 'syllable': 'gu'}]
        self.assertListEqual(expected, actual)

    def test_luuad(self):
        actual = syllabify_word('luuad')
        expected = [{'accent': 1, 'quantity': 2, 'syllable': 'luu'},
                    {'accent': 0, 'quantity': 2, 'syllable': 'ad'}]
        self.assertListEqual(expected, actual)

    def test_lasteaialaps(self):
        actual = syllabify_word('lasteaialaps', split_compounds=True)
        expected = [{'syllable': 'las', 'quantity': 2, 'accent': 1},
                    {'syllable': 'te', 'quantity': 1, 'accent': 0},
                    {'syllable': 'ai', 'quantity': 2, 'accent': 1},
                    {'syllable': 'a', 'quantity': 1, 'accent': 0},
                    {'syllable': 'laps', 'quantity': 3, 'accent': 1}]
        self.assertListEqual(expected, actual)

    def test_split_word_for_syllabification(self):
        # Case 1
        actual = _split_word_for_syllabification('jagamata')
        expected = ['jagamata']
        self.assertListEqual(expected, actual)
        # Case 2
        actual = _split_word_for_syllabification('ja/da-ma/ga///----ja-jah-')
        expected = ['ja', '/', 'da', '-', 'ma', '/', 'ga', '/', '/', '/', '-', '-', '-', '-', 'ja', '-', 'jah', '-']
        self.assertListEqual(expected, actual)
        # Case 3
        actual = _split_word_for_syllabification('-')
        expected = ['-']
        self.assertListEqual(expected, actual)

    def test_syllabification_on_dash_and_slash_symbols(self):
        # Case 1
        actual = syllabify_word('vana-ema')
        expected = [
            {'accent': 1, 'quantity': 1, 'syllable': 'va'},
            {'accent': 0, 'quantity': 1, 'syllable': 'na'},
            {'accent': 1, 'quantity': 3, 'syllable': '-'},
            {'accent': 1, 'quantity': 1, 'syllable': 'e'},
            {'accent': 0, 'quantity': 1, 'syllable': 'ma'}]
        self.assertListEqual(expected, actual)
        # Case 2
        actual = syllabify_word('/')
        expected = [{'accent': 1, 'quantity': 3, 'syllable': '/'}]
        self.assertListEqual(expected, actual)
        # Case 3
        actual = syllabify_word('igavene-tuha/juhan')
        expected = [
            {'accent': 1, 'quantity': 1, 'syllable': 'i'},
            {'accent': 0, 'quantity': 1, 'syllable': 'ga'},
            {'accent': 0, 'quantity': 1, 'syllable': 've'},
            {'accent': 0, 'quantity': 1, 'syllable': 'ne'},
            {'accent': 1, 'quantity': 3, 'syllable': '-'},
            {'accent': 1, 'quantity': 1, 'syllable': 'tu'},
            {'accent': 0, 'quantity': 1, 'syllable': 'ha'},
            {'accent': 1, 'quantity': 3, 'syllable': '/'},
            {'accent': 1, 'quantity': 1, 'syllable': 'ju'},
            {'accent': 0, 'quantity': 2, 'syllable': 'han'}]
        self.assertListEqual(expected, actual)

    def test_split_compound_word_heuristically(self):
        # Case 0
        actual = _split_compound_word_heuristically('')
        expected = ['']
        self.assertListEqual(expected, actual)
        # Case 1
        actual = _split_compound_word_heuristically('ema')
        expected = ['ema']
        self.assertListEqual(expected, actual)
        # Case 2
        actual = _split_compound_word_heuristically('vanaema')
        expected = ['vana', 'ema']
        self.assertListEqual(expected, actual)
        # Case 3
        actual = _split_compound_word_heuristically('vanaemadele')
        expected = ['vana', 'emadele']
        self.assertListEqual(expected, actual)
        # Case 4
        actual = _split_compound_word_heuristically('lasteaialastelegi')
        expected = ['laste', 'aia', 'lastelegi']
        self.assertListEqual(expected, actual)
        # Case 5
        actual = _split_compound_word_heuristically('noorsandideks')
        expected = ['noor', 'sandideks']
        self.assertListEqual(expected, actual)
        # Case 6
        actual = _split_compound_word_heuristically('--')
        expected = ['--']
        self.assertListEqual(expected, actual)
        actual = _split_compound_word_heuristically('-------')
        expected = ['-------']
        self.assertListEqual(expected, actual)

    def test_split_compound_word_heuristically_with_tolerance(self):
        # Split with tolerance for mismatches (default: tolerance=2)
        # Case 0
        actual = _split_compound_word_heuristically('kahekümne')
        expected = ['kahe', 'kümne']
        self.assertListEqual(expected, actual)
        # Case 1
        actual = _split_compound_word_heuristically('kolmekümnene')
        expected = ['kolme', 'kümnene']
        self.assertListEqual(expected, actual)
        # Case 2
        actual = _split_compound_word_heuristically('kolmekümne')
        expected = ['kolme', 'kümne']
        self.assertListEqual(expected, actual)
        # Case 3
        actual = _split_compound_word_heuristically('kolmekümne')
        expected = ['kolme', 'kümne']
        self.assertListEqual(expected, actual)
        # Case 4
        actual = _split_compound_word_heuristically('neljakümne')
        expected = ['nelja', 'kümne']
        self.assertListEqual(expected, actual)
        # Case 5
        actual = _split_compound_word_heuristically('viiekümne')
        expected = ['viie', 'kümne']
        self.assertListEqual(expected, actual)
        # Case 6
        actual = _split_compound_word_heuristically('kuuekümne')
        expected = ['kuue', 'kümne']
        self.assertListEqual(expected, actual)
        # Case 7
        actual = _split_compound_word_heuristically('seitsmekümne')
        expected = ['seitsme', 'kümne']
        self.assertListEqual(expected, actual)
        # Case 8 -- TODO this is not working, needs a fix
        actual = _split_compound_word_heuristically('sellessamas')
        expected = ['selles', 'samas']
        # self.assertListEqual(expected, actual)

    def test_syllabification_with_split_compounds(self):
        # Case 1
        actual = syllabify_word('kalamajja', split_compounds=True)
        expected = [
            {'syllable': 'ka', 'quantity': 1, 'accent': 1},
            {'syllable': 'la', 'quantity': 1, 'accent': 0},
            {'syllable': 'maj', 'quantity': 2, 'accent': 1},
            {'syllable': 'ja', 'quantity': 1, 'accent': 0}]
        self.assertListEqual(expected, actual)
        # Case 2
        actual = syllabify_word('drooniülelennult', split_compounds=True)
        expected = [
            {'syllable': 'droo', 'quantity': 2, 'accent': 1},
            {'syllable': 'ni', 'quantity': 1, 'accent': 0},
            {'syllable': 'ü', 'quantity': 1, 'accent': 1},
            {'syllable': 'le', 'quantity': 1, 'accent': 0},
            {'syllable': 'len', 'quantity': 2, 'accent': 1},
            {'syllable': 'nult', 'quantity': 2, 'accent': 0}]
        self.assertListEqual(expected, actual)
        # Case 3
        actual = syllabify_word('polaarpraktikapakkumistele', split_compounds=True)
        expected = [
            {'syllable': 'po', 'quantity': 1, 'accent': 0},
            {'syllable': 'laar', 'quantity': 3, 'accent': 1},
            {'syllable': 'prak', 'quantity': 2, 'accent': 1},
            {'syllable': 'ti', 'quantity': 2, 'accent': 0},
            {'syllable': 'ka', 'quantity': 1, 'accent': 0},
            {'syllable': 'pak', 'quantity': 3, 'accent': 1},
            {'syllable': 'ku', 'quantity': 1, 'accent': 0},
            {'syllable': 'mis', 'quantity': 2, 'accent': 0},
            {'syllable': 'te', 'quantity': 1, 'accent': 0},
            {'syllable': 'le', 'quantity': 1, 'accent': 0}]
        self.assertListEqual(expected, actual)
