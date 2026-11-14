from estnltk.vabamorf.morf import generate_non_finite_verb_forms
import unittest

class TestGenerateNonFiniteVerbForms(unittest.TestCase):
    
    def test_generate_non_finite_verb_forms_smoke(self):
        infinite_verb_forms = generate_non_finite_verb_forms('teretama')
        self.assertListEqual( sorted(infinite_verb_forms), \
            ['teretada', 'teretades', 'teretama', 'teretamaks', 'teretamas', 'teretamast', 
             'teretamata', 'teretanud', 'teretatama', 'teretatav', 'teretatud', 'teretav'])

        infinite_verb_forms = generate_non_finite_verb_forms('hängima')
        self.assertListEqual( sorted(infinite_verb_forms), \
            ['hängida', 'hängides', 'hängima', 'hängimaks', 'hängimas', 'hängimast', 
            'hängimata', 'hänginud', 'hängitama', 'hängitav', 'hängitud', 'hängiv'])
