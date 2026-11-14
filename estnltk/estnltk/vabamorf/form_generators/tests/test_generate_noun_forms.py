from estnltk.vabamorf.morf import generate_noun_forms
import unittest

class TestGenerateNounForms(unittest.TestCase):
    
    def test_generate_noun_forms_smoke(self):
        noun_forms = generate_noun_forms('päkapikk')
        self.assertListEqual( sorted(noun_forms), \
            ['päkapikk', 'päkapikke', 'päkapikku', 'päkapikkude', 'päkapikkudega', 'päkapikkudeks', 
             'päkapikkudel', 'päkapikkudele', 'päkapikkudelt', 'päkapikkudena', 'päkapikkudeni', 
             'päkapikkudes', 'päkapikkudesse', 'päkapikkudest', 'päkapikkudeta', 'päkapikkusid', 
             'päkapiku', 'päkapikud', 'päkapikuga', 'päkapikuks', 'päkapikul', 'päkapikule', 
             'päkapikult', 'päkapikuna', 'päkapikuni', 'päkapikus', 'päkapikusse', 'päkapikust', 
             'päkapikuta'])
