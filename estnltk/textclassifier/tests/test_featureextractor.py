# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

import unittest

from estnltk.textclassifier.featureextractor import FeatureExtractor
from estnltk.textclassifier.settings import Settings

from pandas import DataFrame


class FeatureExtractorTest(unittest.TestCase):

    def test_featureextractor_yields_features_and_labels(self):
        fe = FeatureExtractor(self.settings(), self.dataframe())
        
        self.assertEqual(fe.X.shape[0],  self.dataframe().shape[0])
        self.assertEqual(len(fe.y), self.dataframe().shape[0])
        self.assertEqual(len(fe.feature_names),  fe.X.shape[1])
        self.assertListEqual(fe.strings, self.sentences())
        self.assertListEqual(fe.labels, self.labels())
    
    def settings(self):
        return Settings(features = ['A', 'C'],
                        label = 'label',
                        confidence = 'confidence',
                        synmap = {})
        
    def dataframe(self):
        return DataFrame({
            'A': ['Mees kõnnib tänaval.', 'Öötööd on pimedad.', 'Arvutid on aeglased.']*10,
            'B': ['Kõik on lollakalt roheline', 'Vahtralehed langevad', 'Rohelised tulnukad.']*10,
            'C': ['Esimene', 'teine', 'kolmas']*10,
            'label': ['Asjad', 'Mu', 'Asjad']*10})

    def sentences(self):
        return ['Mees kõnnib tänaval. Esimene', 'Öötööd on pimedad. teine', 'Arvutid on aeglased. kolmas']*10

    def labels(self):
        return ['Asjad', 'Mu']
