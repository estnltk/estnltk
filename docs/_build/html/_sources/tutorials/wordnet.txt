=============================
Estonian Wordnet
=============================

Estonian WordNet API provides means to query Estonian WordNet.
WordNet is a network of synsets, in which synsets are collections of synonymous words and are connected to other synsets via relations.
For example, the synset which contains the word "koer" ("dog") has a generalisation via hypernymy relation in the form of synset which contains the word "koerlane" ("canine").

Estonian WordNet contains synsets with different types of part-of-speech: adverbs, adjectives, verbs and nouns.


Resemblance
-----------

Given API is on most parts in conformance with NLTK WordNet's API (http://www.nltk.org/howto/wordnet.html).
However, there are some differences due to different structure of the WordNets.

* Lemma classes' relations return empty sets.
  - Reason: In Estonian WordNet relations are only between synsets.
* No verb frames
  - Reason: No information on verb frames.
* Only path, Leacock-Chodorow and Wu-Palmer similarities
  - No information on Information Content

  
Side notes
----------

Existing types of part of speech:

===============  ===============
Part of speech   API equivalent
===============  ===============
Adverb           wn.ADV
Adjective        wn.ADJ
Noun             wn.NOUN
Verb             wn.VERB
===============  ===============

Existing relations:

'antonym', 'be_in_state', 'belongs_to_class', 'causes', 'fuzzynym', 'has_holo_location', 'has_holo_madeof', 'has_holo_member', 'has_holo_part', 'has_holo_portion', 'has_holonym', 'has_hyperonym', 'has_hyponym', 'has_instance', 'has_mero_location', 'has_mero_madeof', 'has_mero_member', 'has_mero_part', 'has_mero_portion', 'has_meronym', 'has_subevent', 'has_xpos_hyperonym', 'has_xpos_hyponym', 'involved', 'involved_agent', 'involved_instrument', 'involved_location', 'involved_patient', 'involved_target_direction', 'is_caused_by', 'is_subevent_of', 'near_antonym', 'near_synonym', 'role', 'role_agent', 'role_instrument', 'role_location', 'role_patient', 'role_target_direction', 'state_of', 'xpos_fuzzynym', 'xpos_near_antonym', 'xpos_near_synonym'


Usage
-----

