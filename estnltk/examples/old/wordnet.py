from estnltk.wordnet import wn
from pprint import pprint

print (len(wn.all_synsets()))

pprint(wn.synsets("koer",pos=wn.VERB))
pprint(wn.synsets('koer'))


synset = wn.synset("king.n.01")
pprint(synset.name)
pprint(synset.pos)
pprint(synset.definition())
pprint(synset.examples())

pprint(synset.hypernyms())
pprint(synset.hyponyms())
pprint(synset.meronyms())
pprint(synset.holonyms())

pprint(synset.get_related_synsets('fuzzynym'))


target_synset = wn.synset('kinnas.n.01')
pprint(synset.path_similarity(target_synset))
pprint(synset.lch_similarity(target_synset))
pprint(synset.wup_similarity(target_synset))
pprint(synset.lowest_common_hypernyms(target_synset))

