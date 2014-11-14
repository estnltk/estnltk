from itertools import izip
import sys

import pycrfsuite

from estner.featureextraction import FeatureExtractor
from estner import settings, nlputil


class CrfsuiteTagger(object):
    
    def __init__(self, model_file):
        self.tagger = pycrfsuite.Tagger()
        self.tagger.open(model_file)
        self.fex = FeatureExtractor(settings.FEATURE_EXTRACTORS,
                                    settings.TEMPLATES, settings.PATH)
    
    def process(self, text):
        doc = nlputil.lemmatise(text)
        nlputil.set_token_positions(doc.tokens, text)
        self.fex.process([doc])
        self.tag_document(doc)
        nes = nlputil.collect_person_names_in_doc(doc)
        output = nlputil.annotate_person_names_in_text(text, nes)
        return output, doc, nes
    
    def annotate_text(self, text):
        annotated_text, doc, nes = self.process(text)
        return annotated_text
    
    def tag_document(self, doc):
        for snt in doc.snts:
            xseq = [t.feature_list() for t in snt]
            ys = self.tagger.tag(xseq)
            for token, y in izip(snt, ys):
                token.predicted_label = y


def train(docs, model_file):
    print 'Extracting features...'
    fex = FeatureExtractor(settings.FEATURE_EXTRACTORS,
                           settings.TEMPLATES, settings.PATH)
    fex.prepare(docs)
    fex.process(docs)
    
    trainer = pycrfsuite.Trainer()
    for doc in docs:
        for snt in doc.snts:
            xseq = [t.feature_list() for t in snt]
            yseq = [t.label for t in snt]  
            trainer.append(xseq, yseq)
    
    trainer.select('l2sgd', 'crf1d')
#    trainer.select('lbfgs', 'crf1d')
    for name in trainer.params():
        print name, trainer.get(name), trainer.help(name)
    trainer.set('c2', '0.001')
#    trainer.set('feature.minfreq', 3)
    trainer.train(model_file)

    print "Done! Saved model to '%s'" % model_file
    
def tag(docs, model_file):
    '''
    Sets token's 'predicted_label' attribute. For convenience, 
    returns a list of predicted labels for each token.
    '''
    fex = FeatureExtractor(settings.FEATURE_EXTRACTORS,
                           settings.TEMPLATES, settings.PATH)
    
    fex.process(docs)
    
    tagger = pycrfsuite.Tagger()
    tagger.open(model_file)
#    tagger.dump(model_file+'.dump')
    
    predicted_labels = []
    
    for doc in docs:
        for snt in doc.snts:
            xseq = [t.feature_list() for t in snt]
            ys = tagger.tag(xseq)
            for token, y in izip(snt, ys):
                token.predicted_label = y
            predicted_labels.extend(ys)
    return predicted_labels
    
