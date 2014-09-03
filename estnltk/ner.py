# -*- coding: utf-8 -*-

class NamedEntityRecognition(object):
    
    def __call__(self, corpus):
        '''Apply NER annotations to given corpus'''
        for words in JsonPaths.words.find(corpus):
            for word in words.value:
                word['ne'] = u'PER'
        return corpus
