# -*- coding: utf-8 -*-
''' NER settings '''

from __future__ import unicode_literals, print_function
import os

from estnltk.core import PACKAGE_PATH


NER_PACKAGE_PATH = os.path.join(PACKAGE_PATH, 'taggers', 'estner')

CLASSES = ['PER', 'ORG', 'LOC']

# Crfsuite settings
CRFSUITE_ALGORITHM = 'l2sgd'
CRFSUITE_C2 = 0.001


# FeatureExtraction settings

# Default gazetteer file
GAZETTEER_FILE = os.path.join(NER_PACKAGE_PATH, 'gazetteer', 'gazetteer.txt')

# Feature templates
TEMPLATES = [
    # shape features
    (('iu', 0),),
    (('fsnt', 0),),
    (('p3', 0),),
    (('p4', 0),),
    (('s3', 0),),
    (('s4', 0),),
    (('bdash', 0),),
    (('adash', 0),),
    (('au', 0),),
    (('ad', 0),),
    (('ao', 0),),
    (('aan', 0),),
    (('cu', 0),),
    (('cd', 0),),
    (('cs', 0),),
    (('cp', 0),),
    (('cds', 0),),
    (('cdt', 0),),
    
    (('iu', -1),),
    (('au', -1),),
    (('au', -1),),
    (('ad', -1),),
    (('cu', -1),),
    (('cd', -1),),
    (('cs', -1),),
    (('cp', -1),),
    (('cds', -1),),
    (('cdt', -1),),
    (('adash', -1),),
    (('fsnt', -1),),
    
    (('iu', -2),),
    (('au', -2),),
    (('au', -2),),
    (('ad', -2),),
    (('cu', -2),),
    (('cd', -2),),
    (('cs', -2),),
    (('cp', -2),),
    (('cds', -2),),
    (('cdt', -2),),
    (('adash', -2),),
    (('fsnt', -2),),
    
    (('iu', 1),),
    (('au', 1),),
    (('au', 1),),
    (('ad', 1),),
    (('cu', 1),),
    (('cd', 1),),
    (('cs', 1),),
    (('cp', 1),),
    (('cds', 1),),
    (('cdt', 1),),
    (('adash', 1),),
    (('fsnt', 1),),
    
    (('iu', 2),),
    (('au', 2),),
    (('au', 2),),
    (('ad', 2),),
    (('cu', 2),),
    (('cd', 2),),
    (('cs', 2),),
    (('cp', 2),),
    (('cds', 2),),
    (('cdt', 2),),
    (('adash', 2),),
    (('fsnt', 2),),
    
    # morphological features
    (('lem', 0),),
    (('pos', 0),),
    (('pref', 0),),
    (('post', 0),),
    (('pun', 0),),
    (('case', 0),),
    (('ending', 0),),
    
    (('lem', -1),),
    (('prop', -1),),
    (('pos', -1),),
    (('pun', -1),),
    (('post', -1),),
    
    (('lem', -2),),
    (('prop', -2),),
    (('pos', -2),),
    (('pun', -2),),
    (('post', -2),),
    
    (('lem', 1),),
    (('prop', 1),),
    (('pos', 1),),
    (('pun', 1),),
    (('post', 1),),
    
    (('lem', 2),),
    (('prop', 2),),
    (('pos', 2),),
    (('pun', 2),),
    (('post', 2),),
    
    # global context aggregation
    (('iuoc', 0),),
    (('nprop', 0),),
    (('pprop', 0),),
    (('ngaz', 0),),
    (('pgaz', 0),),
    
    # gazeteers
    (('gaz', 0),),
    (('gaz', -1),),
    (('gaz', -2),),
    (('gaz', 1),),
    (('gaz', 2),),
    
    # composite features
    (('iu', 0),('fsnt', 0),),
    (('lem', 0),('lem', -1),),
    (('lem', 0),('lem', 1),),
    (('pos', 0),('pos', -1),),
    (('pos', 0),('pos', 1),),
    (('iu', 0),('iu', 1),),
    (('iu', 0),('iu', -1),),
    (('gaz', 0),('gaz', 1),),
    (('gaz', -1),('gaz', 0),),
]

FEATURE_EXTRACTORS = (
    "estnltk.taggers.estner.fex.NerMorphFeatureTagger",
    "estnltk.taggers.estner.fex.NerLocalFeatureTagger",
    "estnltk.taggers.estner.fex.NerSentenceFeatureTagger",
    "estnltk.taggers.estner.fex.NerGazetteerFeatureTagger",
    "estnltk.taggers.estner.fex.NerGlobalContextFeatureTagger"
 )

'''
FEATURE_EXTRACTORS = (
    "estnltk.taggers.estner.featureextraction.MorphFeatureExtractor",
    "estnltk.taggers.estner.featureextraction.LocalFeatureExtractor",
    "estnltk.taggers.estner.featureextraction.SentenceFeatureExtractor",
    "estnltk.taggers.estner.featureextraction.GazetteerFeatureExtractor",
    "estnltk.taggers.estner.featureextraction.GlobalContextFeatureExtractor"
)
'''