import wordnet as wn

#print wn.synsets('korraldama')

synset = wn.synset('korraldama.v.01')

print len(synset._raw_synset.internalLinks)
