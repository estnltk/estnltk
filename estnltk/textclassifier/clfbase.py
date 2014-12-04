# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

from estnltk.textclassifier.featureextractor import FeatureExtractor

from sklearn.linear_model import LogisticRegression
from sklearn.cross_validation import StratifiedKFold

import numpy as np

class ClfBase(object):
    '''Base class for classification tasks.
    
    Provides funtions to perform basic evaluation of model building,
    '''
    
    def __init__(self, feat_extractor):
        '''Initialize.
        
        Parameters
        ----------
        feat_extractor: FeatureExtractor
        '''
        assert isinstance(feat_extractor, FeatureExtractor)
        self._fe = feat_extractor
        self._cache = {}

    def get_new_classifier(self):
        '''Returns
        -------
        new sklearn compatible classifier.
        '''
        return LogisticRegression(penalty='l1')

    @property
    def feature_extractor(self):
        return self._fe
    
    @property
    def cv_stats(self):
        '''Perform cross-validation for model evaluation.
        
        Returns
        -------
        (list[int], list[int], list[float])
            Tuple containing three lists of the same size:
                true labels
                predicted labels
                prediction probabilities
        '''
        if 'y_true' in self._cache:
            return self._cache['y_true'], self._cache['y_pred'], self._cache['y_prob'], self._cache['sigfeatures']
        
        X = self._fe.X
        y = self._fe.y
        
        kf = StratifiedKFold(y, n_folds=10, shuffle=True)
        y_true, y_pred, y_prob = [], [], []
        sigfeatures = []

        order_indices = []

        for train_index, test_index in kf:
            order_indices.extend(test_index)
			
            X_train, X_test = X[train_index], X[test_index]
            y_train, y_test = y[train_index], y[test_index]

            clf = self.get_new_classifier()
            clf.fit(X_train, y_train)

            pred = clf.predict(X_test)
            prob = clf.predict_proba(X_test)
            prob = np.choose(pred, prob.T)
            
            for predy in pred:
                sigfeatures.append(get_sig_features(predy, clf.coef_, 20))
            
            y_true.extend(y_test)
            y_pred.extend(pred)
            y_prob.extend(prob)
        # reorder the results so they match the order of original data
        y_true = [v for i, v in sorted(zip(order_indices, y_true))]
        y_pred = [v for i, v in sorted(zip(order_indices, y_pred))]
        y_prob = [v for i, v in sorted(zip(order_indices, y_prob))]
        assert list(y_true) == list(y)
        
        # cache the results
        self._cache['y_true'] = y_true
        self._cache['y_pred'] = y_pred
        self._cache['y_prob'] = y_prob
        self._cache['sigfeatures'] = sigfeatures
        
        return (y_true, y_pred, y_prob, sigfeatures) 

def get_sig_features(y, coef, n=10):
    if coef.shape[0] == 1:
        # our data only has two different categories
        # let's add coefficients to the second feature as opposite of first feature
        coef = np.vstack((-coef, coef))
    values = [(abs(v), i, v) for i, v in enumerate(coef[y]) if abs(v) > 0.001]
    values.sort(reverse=True)
    values = [(i, v) for a, i, v in values[:n]]
    values.sort()
    return values

    
