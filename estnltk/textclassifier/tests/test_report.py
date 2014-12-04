from __future__ import unicode_literals, print_function

from estnltk.textclassifier.classifier import ClfBase
from estnltk.textclassifier.settings import Settings
from estnltk.textclassifier.reportgenerator import ReportGenerator, ReportGeneratorData
from estnltk.textclassifier.featureextractor import FeatureExtractor
from estnltk.textclassifier.paths import TEST_PATH

import unittest
import os
import pandas as pd


class ReportGeneratorAcceptanceTest(unittest.TestCase):
    
    def test_generation(self):
        # 1. read the settings
        settings = Settings.read(os.path.join(TEST_PATH, 'weather.def'),
                                 os.path.join(TEST_PATH, 'weather.txt'))
        
        # 2. load the dataframe
        dataframe = pd.read_excel(os.path.join(TEST_PATH, 'weather.xlsx'), 'Sheet1')

        # 3. generate cross-validation statistics
        base = ClfBase(FeatureExtractor(settings, dataframe))
        self.assertEqual(len(base.cv_stats), 4)
        for stat in base.cv_stats:
            self.assertTrue(stat is not None)
        
        # 4. train classifier to obrain coeficcients
        clf = base.get_new_classifier()
        clf.fit(base._fe.X, base._fe.y)
        
        # 5. generate report
        repgen = ReportGenerator(ReportGeneratorData(base, clf.coef_))
        self.assertTrue(len(repgen.classification_report) > 100)
        self.assertTrue(len(repgen.misclassified_data) > 100)

