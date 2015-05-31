# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

from estnltk.textclassifier.featureextractor import FeatureExtractor
from estnltk.textclassifier.settings import Settings
from estnltk.textclassifier.reportgenerator import ReportGenerator, ReportGeneratorData
from estnltk.textclassifier.clfbase import ClfBase
from sklearn.metrics import precision_recall_fscore_support, precision_score, recall_score, f1_score
from sklearn import preprocessing
from copy import copy

import numpy as np
import json
import logging
import base64
import time
import pandas

try:
    import cPickle as pickle
except ImportError:
    import pickle


logger = logging.getLogger('clf')

class Clf(ClfBase):
    '''estnltk.textclassifier classifier.
    
    Attributes
    ----------
    _settings: estnltk.textclassifier.settings.Settings
        Settings containing technical synonyms, feature labels etc.
    _clf: sklearn.base.BaseEstimator
        The internal representation of the classifier model.
    _fe_serialized: str
        Serialized version of the feature extractor used in training.
    _report: str
        The HTML report of training results.
    _misclassified_data: str
        Misclassified data report of training results.
    _train_dataframe: pandas.DataFrame
        Original data used for training. It is needed for active learning.
    '''

    def __init__(self, settings):
        '''Initialize the classifier.'''
        
        assert isinstance(settings, Settings)
        self._settings = settings
        self._clf = None
        self._fe_serialized = None
        self._report = None
        self._misclassified_data = None
        self._train_dataframe = None

    def train(self, dataframe, report=True):
        '''Train the classifier.
        
        Parameters
        ----------
        dataframe: pandas DataFrame object
            The dataframe containing feature columns and label column for training task.
        report: True
            Should we create a training report (default True).

        Returns
        -------
        Clf
            return self.
        '''
        starttime = time.time()
        logger.info('Training new model with settings{0} and dataframe with {1} rows'.format(self._settings,
                                                                                             dataframe.shape[0]))
        fe = FeatureExtractor(self._settings, dataframe)
        base = ClfBase(fe)
        classifier = base.get_new_classifier()
        
        info = 'Fitting classifier with {0} features and {1} examples and {2} disctinctive labels'
        logger.debug(info.format(fe.X.shape[1], fe.X.shape[0], len(fe.labels)))
        classifier.fit(fe.X, fe.y)
        self._clf = classifier
        self._fe_serialized = fe.export()
        
        if report:
            logger.info('Generating report.')
            rdata = ReportGeneratorData(base, classifier.coef_)
            repgen = ReportGenerator(rdata)
            self._report = repgen.main_report
            self._misclassified_data = repgen.misclassified_data
        else:
            logger.info('Skipping report generation.')
        endtime = time.time()
        self._train_dataframe = copy(dataframe)
        logger.info('Training finished. Took total of {0:.1f} seconds.'.format(endtime - starttime))
        return self
    
    def classify(self, dataframe):
        '''Classify the dataframe.
        
        Raises
        ------
        ValueError
            In case the classifier is not yet trained.

        Returns
        -------
        DataFrame
            The original dataframe with additional label and confidence columns.
        '''
        logger.info('Starting classification task.')
        starttime = time.time()
        if self._clf is None:
            raise ValueError('No classifier trained!')
        fe = FeatureExtractor(self._settings,
                              dataframe,
                              vectorizer = self._fe_serialized['vectorizer'],
                              labelencoder = self._fe_serialized['labelencoder'])
        pred = self._clf.predict(fe.X)
        prob = self._clf.predict_proba(fe.X)
        prob = np.choose(pred, prob.T)
        
        dataframe[self._settings.label] = fe._labelencoder.inverse_transform(pred)
        dataframe[self._settings.confidence] = prob
        
        endtime = time.time()
        logger.info('Classification completed. Took total of {0:.1f} seconds.'.format(endtime - starttime))
        
        return dataframe
        
    def test(self, dataframe):
        '''Test the classifier using given annotated dataframe.
        
        Parameters
        ----------
        dataframe: pandas.DataFrame
            The testing dataframe. Must contain same columns as the dataset used to train the classifier.
            
        Returns
        -------
        dict
            Dictionary containing the overall performance characterstics and also by each class.
        '''
        logger.info('Starting testing task')
        starttime = time.time()
        true = list(dataframe[self._settings.label])
        classified = self.classify(dataframe)
        pred = list(classified[self._settings.label])
        le = preprocessing.LabelEncoder()
        le.fit(true + pred)
        true = le.transform(true)
        pred = le.transform(pred)
        # overall scores
        prec = precision_score(true, pred)
        rec = recall_score(true, pred)
        f1 = f1_score(true, pred)
        # scores by classes
        precs, recs, fs, supps = precision_recall_fscore_support(true, pred)
        data_f1 = list(zip(le.classes_, precs, recs, fs, supps))
        data_f1.sort(key=lambda x: x[3], reverse=True)
        
        endtime = time.time()
        logger.info('Testing completed. Took total of {0:.1f} seconds.'.format(endtime - starttime))
        
        return {'precision': prec,
                'recall': rec,
                'f1_score': f1,
                'labels': [{'label': d[0], 'precision': d[1], 'recall': d[2], 'f1_score': d[3], 'count': d[4]} for d in data_f1]}
        
    def retrain(self, dataframe, conf_treshold=0.0, report=True):
        '''Retrain the classifier using extra data.
        
        Parameters
        ----------
        
        dataframe: pandas.DataFrame
            Dataframe of extra data.
            Should be unlabelled as we automatically label it during retraining.
            In case of labelled data, merge it instead with the original dataset and then train using that.
        conf_treshold: float
            The confidence treshold to filter_containing out the rows that will be excluded in the extended training dataset.
        report: bool
            Should we regenerate the training report based on new extended dataset (default True).
            
        Returns
        -------
        Clf
            self
        '''
            
        logger.info('Starting retraining task with conf_treshold={0}'.format(conf_treshold))
        starttime = time.time()
        dataframe = self.classify(dataframe)
        new_dataframe = merge_datasets(self._settings,
                                       self._train_dataframe,
                                       dataframe,
                                       conf_treshold)
        logger.info('Merged orignal dataset with {0} rows and extra dataset with {1} rows, after filtering, got {2} rows.'.format(
            self._train_dataframe.shape[0], dataframe.shape[0], new_dataframe.shape[0]))
        self.train(new_dataframe, report=report)
        endtime = time.time()
        logger.info('Retraining completed. Took total of {0:.1f} seconds.'.format(endtime - starttime))
        return self
    
    def export_json(self):
        '''Export the classifier as a JSON string.
        
        Returns
        -------
        str
            JSON encoded data
        '''
        data = {'clf': base64.b64encode(pickle.dumps(self._clf)).decode('ascii'),
                'featureextractor': self._fe_serialized,
                'train_dataframe': str(self._train_dataframe.to_json()),
                'report': self._report,
                'misclassified_data': self._misclassified_data,
                'settings': self._settings.export()}
        return json.dumps(data)
    
    @staticmethod
    def from_json(json_data):
        '''Import previously exported classifier from a JSON string.
        
        Parameters
        ----------
        json: str
            JSON encoded classifier.
        '''
        data = json.loads(json_data)
        settings = Settings(**data['settings'])
        classifier = pickle.loads(base64.b64decode(data['clf'].encode('ascii')))
        fe_serialized = data['featureextractor']
        train_dataframe = pandas.read_json(data['train_dataframe'])
        clf = Clf(settings)
        clf._clf = classifier
        clf._fe_serialized = fe_serialized
        clf._train_dataframe = train_dataframe
        return clf

    @property
    def settings(self):
        return copy(self._settings)

    @property
    def report(self):
        '''Obtain the main part of training report created during training.
        
        Returns
        -------
        str
            HTML containing the report
        None
            If there is no report, either because the model is not yet trained or was trained without report generation.
        '''
        return copy(self._report)
    
    @property
    def misclassified_data(self):
        '''Obtain misclassified data report creating during training.
        
        Returns
        -------
        str
            HTML containing the report
        None
            If there is no report, either because the model is not yet trained or was trained without report generation.
        '''
        return copy(self._misclassified_data)

    @property
    def train_dataframe(self):
        return copy(self._train_dataframe)


def merge_datasets(settings, indata, extradata, conf_treshold):
    '''Merge original dataset with extra data by keeping only
       best examples.
    
    Parameters
    ----------
    settings: estnltk.textclassifier.settings.Settings
        The settings including column information.
    indata: pandas.DataFrame
        The original dataset.
    extradata: pandas.DataFrame
        The extra dataset.
    conf_treshold: float
        The confidence treshold, which determines the split between
        bad and good examples.

    Returns
    -------
    pandas.DataFrame
        original data + extradata, where confidence >= conf_treshold.
    '''
    
    B = extradata[extradata[settings.confidence] >= conf_treshold]
    columns = indata.columns
    indata = indata.append(B)[columns].reset_index().drop('index', 1)
    print (indata.columns)
    return indata
