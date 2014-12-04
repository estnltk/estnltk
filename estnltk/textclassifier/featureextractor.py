# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

from estnltk.textclassifier.settings import Settings, NUM_CORES
from estnltk.textclassifier.analyzer import SimpleTextAnalyzer

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.pipeline import FeatureUnion
from sklearn import preprocessing

import numpy as np
import base64

try:
    import cPickle as pickle
except ImportError:
    import pickle


class FeatureExtractor(object):
    '''Class for exracting features from dataframe object.
    
    Attributes
    ----------
    
    _transform_only: bool
        True, if extractor was initiated from previously serialized vectorizer and labelencoder.
    
    '''
    
    def __init__(self, settings, dataframe, vectorizer=None, labelencoder=None):
        '''Initiate a featureextractor.
        
        Parameters
        ----------
        settings: Settings
            Settings instance of the classification task.
        dataframe: Dataframe
            Pandas Dataframe object containing the data compatible with the settings.

        Keyword parameters
        ------------------
        vectorizer: str
            Pickled and base64-encoded vectorizer from previous serialization.
        labelencoder: str
            Pickled and base64-encoded labelencoder from previous serialization.
        '''
        assert isinstance(settings, Settings)
        
        self._settings = settings
        self._dataframe = dataframe
        self._cache = {}
        self._transform_only = False
        
        if vectorizer is None:
            self._vectorizer = FeatureUnion([
                ('lemma', CountVectorizer(
                    analyzer=SimpleTextAnalyzer(settings.unifier),
                    binary=True,
                    min_df=5)),
                ('word', TfidfVectorizer(analyzer='word',
                    min_df=5,
                    use_idf=False,
                    ngram_range=(2, 3)))
                ], n_jobs=NUM_CORES)
        else:
            self._vectorizer = pickle.loads(base64.b64decode(vectorizer))
            self._transform_only = True
            
        if labelencoder is None:
            self._labelencoder = preprocessing.LabelEncoder()
        else:
            self._labelencoder = pickle.loads(base64.b64decode(labelencoder))
            self._transform_only = True

    def export(self):
        return {'settings': self.settings.export(),
                'vectorizer': base64.b64encode(pickle.dumps(self._vectorizer)).decode('ascii'),
                'labelencoder': base64.b64encode(pickle.dumps(self._labelencoder)).decode('ascii')}

    @property
    def settings(self):
        return self._settings

    @property
    def vectorizer(self):
        return self._vectorizer
    
    @property
    def dataframe(self):
        return self._dataframe
    
    @property
    def settings(self):
        return self._settings
    
    @property
    def labelencoder(self):
        return self._labelencoder

    @property
    def strings(self):
        '''Get feature strings.
        
        Returns
        -------
        list[unicode]
            Dataframe columns concatenated to a single string.
        '''
        if 'strings' not in self._cache:
            self._cache['strings'] = [' '.join(row) for row in self._dataframe[self._settings.features].fillna('').values]
        return self._cache['strings']

    @property
    def X(self):
        '''Returns
        -------
        scipy.sparse
            Sparse matrix containing textual features for classification.
        '''
        if 'X' not in self._cache:
            X = self.strings
            if self._transform_only:
                self._cache['X'] = self._vectorizer.transform(X)
            else:
                self._cache['X'] = self._vectorizer.fit_transform(X)
        return self._cache['X']

    @property
    def y(self):
        '''Returns
        -------
        numpy.array
            Labels encoded as integer values. Use get_labels() for mapping them back to strings.
        '''
        if 'y' not in self._cache:
            y = list(self._dataframe[self._settings.label].fillna(''))
            if self._transform_only:
                self._cache['y'] = np.array(self._labelencoder.transform(y))
            else:
                self._cache['y'] = np.array(self._labelencoder.fit_transform(y))
        return self._cache['y']
    
    @property
    def feature_names(self):
        '''Returns
        -------
        list[unicode]
            Meaningful feature names for vectorized feature matrix columns.
        '''
        return self._vectorizer.get_feature_names()
    
    @property
    def labels(self):
        '''Returns
        -------
        list[unicode]
            Labels for for encoded labels (y).
        '''
        self.y
        return [l for l in self._labelencoder.classes_] 
