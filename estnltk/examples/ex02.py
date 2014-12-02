# -*- coding: utf-8 -*-
'''Morphological analysis example.'''
from __future__ import unicode_literals, print_function

from estnltk import analyze
from pprint import pprint

pprint(analyze('Tüünete öötööde allmaaraudteejaam'))


from estnltk import Tokenizer
from estnltk import PyVabamorfAnalyzer

tokenizer = Tokenizer()
analyzer = PyVabamorfAnalyzer()

text = '''Keeletehnoloogia on arvutilingvistika praktiline pool.
Keeletehnoloogid kasutavad arvutilingvistikas välja töötatud 
teooriaid, et luua rakendusi (nt arvutiprogramme), 
mis võimaldavad inimkeelt arvuti abil töödelda ja mõista. 

Tänapäeval on keeletehnoloogia tuntumateks valdkondadeks 
masintõlge, arvutileksikoloogia, dialoogisüsteemid, 
kõneanalüüs ja kõnesüntees.
'''

# first tokenize and then morphologically analyze
morf_analyzed = analyzer(tokenizer(text))

# print some results
print (morf_analyzed.lemmas)
print (morf_analyzed.postags)

# print more information together
pprint (list(zip(morf_analyzed.word_texts,
                 morf_analyzed.lemmas,
                 morf_analyzed.forms,
                 morf_analyzed.postags)))


# synthesis example

from estnltk import synthesize

print (synthesize('pood', form='pl p', partofspeech='S'))
print (synthesize('palk', form='sg kom'))
