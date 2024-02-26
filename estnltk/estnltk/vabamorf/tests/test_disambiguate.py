import unittest
from estnltk.vabamorf.tests.morph_extra import analyze, disambiguate


# noinspection SpellCheckingInspection
class TestDisambiguator(unittest.TestCase):
    """
    Tests for morphological disambiguation.
    """

    # EINO SANTANEN. Muodon vanhimmat
    # http://luulet6lgendus.blogspot.com/
    sentences = '''KÕIGE VANEM MUDEL
    
    Pimedas luusivad robotid,
    originaalsed tšehhi robotid kahekümnendatest.
    Robota! kisendavad nad, uhked originaalsed robotid,
    hüüdes iseenda nime.
    Robota! möirgavad nad, naftasegused elukad,
    hiiglase vaimusünnitised, robotid:
    kurvameelsetena kauguses,
    ebamäärastena kauguses,
    mattudes vastuoludesse,
    muutudes peaaegu julmaks oma õiglusejanus.
    Robota! Kui päike pageb monoliitide kohalt,
    tähistavad nad vägisi
    öö salajast geomeetriat.
    Õudne on inimesel vaadata
    neid metsikuid mudeleid.
    
    Kuuntele, romantiikkaa, 2002'''.split('\n')

    def test_disambiguator(self):
        # Test the separate disambiguate function against 
        # the built-in disambiguate=True function.
        # Both must work the same.
        for sentence in self.sentences:
            an_with = analyze(sentence)
            an_without = analyze(sentence, disambiguate=False)
            disamb = disambiguate(an_without)
            self.assertListEqual(an_with, disamb)

    def _get_root_tokens(self, analysis_result):
        root_tokens = []
        for word_annotation in analysis_result:
            root_tokens.append([])
            for analysis in word_annotation['analysis']:
                root_tokens[-1].append(analysis['root'])
        return root_tokens

    def test_disambiguator_preserves_phonetics(self):
        sentence = \
            'Laboriarst: milline on vaatamata päikeserohkele suvele ' + \
            'ja reisimisele olukord D-vitamiiniga sügisel?'
        #
        # Case 1: analysis and disambiguation without phonetics (default)
        #
        analysis = analyze(sentence, disambiguate=False)
        root_tokens1 = self._get_root_tokens(analysis)
        self.assertListEqual(root_tokens1, [
            ['Labori_arst', 'Laboriarst:', 'labori_arst'],
            ['milline'],
            ['ole', 'ole'],
            ['vaata', 'vaata=mata', 'vaatamata', 'vaatamata'],
            ['päikese_rohke'],
            ['suvi'],
            ['ja'],
            ['reisimine'],
            ['olu_kord'],
            ['D-vitamiin'],
            ['sügis']]
        )
        disamb = disambiguate(analysis)
        root_tokens2 = self._get_root_tokens(disamb)
        self.assertListEqual(root_tokens2, [
            ['labori_arst'],
            ['milline'],
            ['ole', 'ole'],
            ['vaatamata'],
            ['päikese_rohke'],
            ['suvi'],
            ['ja'],
            ['reisimine'],
            ['olu_kord'],
            ['D-vitamiin'],
            ['sügis']]
        )
        #
        # Case 2: analysis and disambiguation with phonetics
        #
        analysis = analyze(sentence, disambiguate=False, phonetic=True)
        root_tokens1 = self._get_root_tokens(analysis)
        self.assertListEqual(root_tokens1, [
            ['Labori_<arst', 'Laboriarst:', 'labori_<arst'],
            ['mil]line'],
            ['ole', 'ole'],
            ['v<aata', 'v<aata=mata', 'v<aatamata', 'v<aatamata'],
            ['p<äikese_r<ohke'],
            ['suvi'],
            ['ja'],
            ['r<eisimine'],
            ['olu_k<ord'],
            ['D-v?itam<iin'],
            ['sügis']]
        )
        disamb = disambiguate(analysis, phonetic=True)
        root_tokens2 = self._get_root_tokens(disamb)
        self.assertListEqual(root_tokens2, [
            ['labori_<arst'],
            ['mil]line'],
            ['ole', 'ole'],
            ['v<aatamata'],
            ['p<äikese_r<ohke'],
            ['suvi'],
            ['ja'],
            ['r<eisimine'],
            ['olu_k<ord'],
            ['D-v?itam<iin'],
            ['sügis']]
        )
