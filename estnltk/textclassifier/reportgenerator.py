# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

from estnltk.textclassifier.featureextractor import FeatureExtractor
from estnltk.textclassifier.clfbase import ClfBase, get_sig_features
from estnltk import analyze

from sklearn.cluster import Ward
from sklearn.feature_selection import chi2
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support, precision_score, recall_score, f1_score
from sklearn.base import TransformerMixin

import numpy as np
import pandas
import matplotlib
matplotlib.use('svg')
import matplotlib.pyplot as plt
import six

import tempfile
try:
    from html import escape as htmlescape
except ImportError:
    from cgi import escape as htmlescape
from collections import defaultdict
from copy import copy
 
class Renumberer(TransformerMixin):
    '''Class for renumbering integers so that they are consequent.
    
    As we reorder the labels in computations, it is necessary to make sure they are consequent as otherwise
    scikit learn metrics functions complain.'''
    
    def __init__(self, **kwargs):
        self._map = {}
        self._next = 0
    
    def fit(self, X, y=None):
        for value in set(X):
            if value not in self._map.keys():
                self._map[value] = self._next
                self._next += 1
    
    def transform(self, X):
        return [self._map[v] for v in X]

    
class ReportGeneratorData(dict):
    '''Dictionary containing report generator data.'''
    
    def __init__(self, clfbase, coef):
        dict.__init__(self)
        self['y_true'], self['y_pred'], self['y_prob'], self['sigfeatures'] = clfbase.cv_stats
        self['feature_names'] = clfbase._fe.feature_names
        self['labels'] = clfbase.feature_extractor.labels
        self['sentences'] = clfbase.feature_extractor.strings
        self['coverages'], self['f1s'], self['cutoffs'] = self.coverage_curve
        self['dataframe'] = clfbase._fe.dataframe
        self['settings'] = clfbase._fe.settings
        self['coef'] = coef

    @property
    def coverage_curve(self):
        '''Compute coverage statistics.
        
        Returns
        -------
        (list[float], list[float], list[float])
            Three related lists containing:
                Coverage percentages
                F1-scores
                Cutoff values
        '''
        data = list(zip(self['y_true'], self['y_pred'], self['y_prob']))
        data.sort(key=lambda x: x[2], reverse=True)
        run_true, run_pred = [], []
        coverages, f1s, cutoffs = [], [], []
        
        renumberer = Renumberer()
        for idx, (true, pred, prob) in enumerate(data):
            renumberer.fit([true, pred])
            run_true.extend(renumberer.transform([true]))
            run_pred.extend(renumberer.transform([pred]))
            
            coverages.append(float(idx) / len(data))
            f1s.append(f1_score(run_true, run_pred))
            cutoffs.append(prob)
        return coverages, f1s, cutoffs

        
class TextAnnotator(object):

    def __init__(self, unifier):
        self._unifier = unifier
    
    def trim_feature_prefixes(self, features):
        result = []
        for feat, value in features:
            if feat.startswith('word__'):
                feat = feat[6:]
            elif feat.startswith('lemma__'):
                feat= feat[7:]
            else:
                raise ValueError('Can only handle features with word__ and lemma__ prefixes.')
            result.append((feat, value))
        return result

    def does_match(self, variants, features):
        for variant in variants:
            for feat, value in features:
                feattoks = feat.split()
                for feattok in feattoks:
                    if variant.startswith(feattok):
                        return value

    def annotate_color(self, f, v):
            color = 'black'
            if v < 0:
                return '<span style="color:red">{0}</span>'.format(htmlescape(f))
            else:
                return '<b>{0}</b>'.format(htmlescape(f))
                    
    def annotate_important_features(self, text, features):
        toks = text.split()    
        features = self.trim_feature_prefixes(features)
        result = []
        for tok in toks:
            variants = [tok] + [an['lemma'] for an in analyze([tok])[0]['analysis']]
            variants = [self._unifier.unify(v.lower()) for v in variants]
            match = self.does_match(variants, features)
            if match is not None:
                tok = self.annotate_color(tok, match)
            result.append(tok)
        return ' '.join(result)


class ReportGenerator(object):
    '''Class for generating HTML raports.
    
    Raports containg statistics and evaluation data for estimating the model performance
    and providing clues to improve the performance.
    '''
    
    def __init__(self, data):
        assert isinstance(data, ReportGeneratorData)
        self._data = data
        pandas.set_option('display.max_colwidth', -1)

    def classification_report_total(self, prec, rec, f1):
        html  = '<table><tr><th>Precision</th><th>Recall</th><th>F1-score</th></tr>'
        html += '<tr><td>{0:.1f}</td><td>{1:.1f}</td><td>{2:.1f}</tr>'.format(prec*100, rec*100, f1*100)
        html += '</table>'
        return html

    def classification_report_list(self, title, data):
        html = ('<table>'
                    '<tr><th colspan="5">{0}</th></tr>'
                    '<tr><th>Class</th><th>Precision</th><th>Recall</th><th>F1</th><th>Support/Count</th>'
                '</tr>').format(title)
        for l, p, r, f, s in data:
            row = '<tr><td>{0}</td><td>{1:.1f}</td><td>{2:.1f}</td><td>{3:.1f}</td><td>{4}</td></tr>'
            row = row.format(htmlescape(l), p*100, r*100, f*100, s)
            html += row
        return html + '</table>'
    
    @property
    def classification_report(self):
        '''Returns
        -------
        unicode
            HTML containing the classification report.
        '''
        y_true, y_pred = self._data['y_true'], self._data['y_pred']
        labels = self._data['labels']
        # compute total p, r, f1, s
        html = '<h3>Classification report</h3>'
        prec = precision_score(y_true, y_pred)
        rec  = recall_score(y_true, y_pred)
        f1   = f1_score(y_true, y_pred)
        html += self.classification_report_total(prec, rec, f1)
        # compute metrics for each label
        
        # compute metrics
        precs, recs, fs, supps = precision_recall_fscore_support(y_true, y_pred)
        assert len(precs) == len(labels)
        # order data by support and by F1
        data_supp = list(zip(labels, precs, recs, fs, supps))
        data_supp.sort(key=lambda x: x[4], reverse=True)
        data_f1 = copy(data_supp)
        data_f1.sort(key=lambda x: x[3], reverse=True)
        # construct HTML display of metrics for each label
        html += self.classification_report_list('Ordered by F1', data_f1)
        html += self.classification_report_list('Ordered by support', data_supp)
        
        return html

    @property
    def coverage_f1_fig(self):
        return self._as_blob(self._plot_curve(self._data['coverages'], self._data['f1s'], 'Data coverage', 'Accuracy (weighted F1)'))
    
    @property
    def cutoff_f1_fig(self):
        return self._as_blob(self._plot_curve(self._data['cutoffs'], self._data['f1s'], 'Confidence cutoff', 'Accuracy (weighted F1)'))

    def _plot_curve(self, xs, ys, xlabel, ylabel):
        ticks = np.array(range(0, 105, 5))/100.0
        ticklabels = ['{0:.0f}%'.format(v*100) for v in ticks]
        fig, ax = plt.subplots()
        ax.plot(xs, ys)
        ax.axhline(y=0.9, color='r')
        ax.axhline(y=0.95, color='g')
        ax.set_xticks(ticks)
        ax.set_xticklabels(ticklabels, rotation=45)
        ax.set_xlabel(xlabel)
        ax.set_yticks(ticks)
        ax.set_yticklabels(ticklabels)
        ax.set_ylabel(ylabel)
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0.5, 1)
        ax.grid()
        return fig
    
    def _as_blob(self, fig):
        '''Get the figure as binary blob.'''
        f = tempfile.NamedTemporaryFile(suffix='.svg')
        fig.savefig(f, format='svg', transparent=True, bbox_inches='tight', pad_inches=1)
        f.seek(0)
        blob = f.read()
        f.close()
        return blob.decode('ascii')
    
    @property
    def sentence_report(self):
        '''Returns
        -------
        unicode
            HTML containing misclassified sentences.
        '''
        y_true, y_pred, sentences = self._data['y_true'], self._data['y_pred'], self._data['sentences']
        labels = self._data['labels']
        D = defaultdict(list)
        # divide sentences / 
        for i, (t, p) in enumerate(zip(y_true, y_pred)):
            if t != p:
                D[(t, p)].append(sentences[i])
        html = '<h3>Misclassified sentences</h3>'
        for s, s_label in enumerate(labels):
            for d, d_label in enumerate(labels):
                if s == d:
                    continue
                sents = D[(s, d)]
                if len(sents) > 0:
                    html += '<table><tr><th>{0} &#8594; {1}. Count: {2}.</th></tr>'.format(htmlescape(s_label),
                                                                                           htmlescape(d_label),
                                                                                           len(sents))
                    for sent in sents:
                        html += '<tr><td>{0}</td></tr>'.format(htmlescape(sent))
                    html += '</table>'
        return html

    @property
    def significant_features(self):
        settings = self._data['settings']
        feature_names = self._data['feature_names']
        coef = self._data['coef']
        ta = TextAnnotator(settings.unifier)
        labels = self._data['labels']
        html = '<h3>Significant features by labels</h3>\n'
        html += '<p>Below is a list with at most 100 most significant features for each label, that are used in the classification process.</p>'
        html += '<p>Features written in <b>black</b> and <span style="color:red">red</span> denote features that are respectively contributing'
        html += ' towards and against assigning the particular class label. '
        html += 'Both are equally important, but they should be interpreted differently, when debugging the classifier.</p>'
        html += '<table style="border: 1px solid black">'
        
        for idx, label in enumerate(labels):
            features = get_sig_features(idx, coef, 100)
            features = [(feature_names[featidx], value) for featidx, value in features]
            features = ta.trim_feature_prefixes(features)
            features = ', '.join([ta.annotate_color(f, v) for f, v in features])
            html += '<tr><td style="border-bottom: 1px solid black">{0}</td><td style="border-bottom: 1px solid black">{1}</td></tr>'.format(htmlescape(label), features)
        html += '</table>'
        return html

    @property
    def main_report(self):
        html = '''<!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Classification report</title>
            </head>

            <body>'''
        html += self.classification_report + '\n'
        html += '<h3>Confidence cutoff / F1 curve</h3>'
        html += '<p>Each classified data point has a confidence score -- the higher the score, the lower the probability of '
        html += 'making an error. In other words, it describes how hard it is to classify the data point.'
        html += 'The plot shows how the overall accuracy changes by including only data points where '
        html += 'the confidence is greater or equal to the confidence cutoff treshold.</p>'
        html += self.cutoff_f1_fig
        
        html += '<h3>Coverage / F1 curve</h3>'
        html += '<p>The coverage plot shows how the overall accuracy changes by removing data that is harder to classify. '
        html += 'Typically, by removing the harder examples, we obtain better overall accuracy.</p>'
        html += self.coverage_f1_fig
        
        html += self.significant_features + '\n'
        html += '</body></html>'
        return html

    @property
    def misclassified_data(self):
        y_true, y_pred = self._data['y_true'], self._data['y_pred']
        sentences = self._data['sentences']
        df = self._data['dataframe']
        labels = self._data['labels']
        sigfeatures = self._data['sigfeatures']
        settings = self._data['settings']
        feature_names = self._data['feature_names']
        ta = TextAnnotator(settings.unifier)
        
        D = defaultdict(list)
        # divide sentences /
        for i, (t, p) in enumerate(zip(y_true, y_pred)):
            if t != p:
                D[(t, p)].append(i)
                assert labels[t] == df[settings.label][i]
        html = '''<!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Classification report</title>
            </head>

            <body>'''
        html += '<h3>Misclassified data</h3>'
        for s, s_label in enumerate(labels):
            for d, d_label in enumerate(labels):
                if s == d:
                    continue
                idxs = D[(s, d)]
                if len(idxs) > 0:
                    html += '<br/><br/><br/><b>True label:</b> {0}<br/><b>Predicted label:</b> {1}<br/><b>Count:</b> {2}<br/>\n'.format(s_label, d_label, len(idxs))
                    subdf = df.iloc[idxs].fillna('')
                    for idx in idxs:
                        features = [(feature_names[featidx], value) for featidx, value in sigfeatures[idx]]
                        for col in settings.features:
                            subdf[col][idx] = ta.annotate_important_features(htmlescape(subdf[col][idx]), features)
                    html += subdf.to_html(index=False, escape=False)
        return html + '</body></html>'

