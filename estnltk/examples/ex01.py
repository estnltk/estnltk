# -*- coding: utf-8 -*-
'''Tokenization example.'''
from __future__ import unicode_literals, print_function

# Let's define a sample document
text = '''Keeletehnoloogia on arvutilingvistika praktiline pool.
Keeletehnoloogid kasutavad arvutilingvistikas välja töötatud 
teooriaid, et luua rakendusi (nt arvutiprogramme), 
mis võimaldavad inimkeelt arvuti abil töödelda ja mõista. 

Tänapäeval on keeletehnoloogia tuntumateks valdkondadeks 
masintõlge, arvutileksikoloogia, dialoogisüsteemid, 
kõneanalüüs ja kõnesüntees.
'''

# tokenize it using default tokenizer
from estnltk import Tokenizer
tokenizer = Tokenizer()
document = tokenizer.tokenize(text)

# tokenized results
print (document.word_texts)
print (document.sentence_texts)
print (document.paragraph_texts)
print (document.text)

# start and end positions of words, sentences and paragraphs
from pprint import pprint
pprint (list(zip(document.word_texts, document.word_spans)))
