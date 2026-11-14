from estnltk.vabamorf.morf import generate_finite_verb_forms
import unittest

class TestGenerateFiniteVerbForms(unittest.TestCase):
    
    def test_generate_finite_verb_forms_smoke(self):
        finite_verb_forms = generate_finite_verb_forms('teretama')
        self.assertListEqual( sorted(finite_verb_forms), \
            ['tereta', 'teretab', 'teretad', 'teretage', 'teretagem', 'teretagu', 'teretaks', 
             'teretaksid', 'teretaksime', 'teretaksin', 'teretaksite', 'teretame', 'teretan', 
             'teretanuks', 'teretanuksid', 'teretanuksime', 'teretanuksin', 'teretanuksite', 
             'teretanuvat', 'teretas', 'teretasid', 'teretasime', 'teretasin', 'teretasite', 
             'teretatagu', 'teretataks', 'teretatakse', 'teretatavat', 'teretate', 'teretati', 
             'teretatuks', 'teretatuvat', 'teretavad', 'teretavat'] )

        finite_verb_forms = generate_finite_verb_forms('hängima')
        self.assertListEqual( sorted(finite_verb_forms), \
            ['hängi', 'hängib', 'hängid', 'hängige', 'hängigem', 'hängigu', 'hängiks', 
             'hängiksid', 'hängiksime', 'hängiksin', 'hängiksite', 'hängime', 'hängin', 
             'hänginuks', 'hänginuksid', 'hänginuksime', 'hänginuksin', 'hänginuksite', 
             'hänginuvat', 'hängis', 'hängisid', 'hängisime', 'hängisin', 'hängisite', 
             'hängitagu', 'hängitaks', 'hängitakse', 'hängitavat', 'hängite', 'hängiti', 
             'hängituks', 'hängituvat', 'hängivad', 'hängivat'] )
