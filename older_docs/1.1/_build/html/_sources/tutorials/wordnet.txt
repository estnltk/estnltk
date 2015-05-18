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

* Lemma classes' relations return empty sets. Reason: In Estonian WordNet relations are only between synsets.
* No verb frames. Reason: No information on verb frames.
* Only path, Leacock-Chodorow and Wu-Palmer similarities. No information on Information Content.

  
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

antonym, be_in_state, belongs_to_class, causes, fuzzynym, has_holo_location, has_holo_madeof, has_holo_member, 
has_holo_part, has_holo_portion, has_holonym, has_hyperonym, has_hyponym, has_instance, has_mero_location, 
has_mero_madeof, has_mero_member, has_mero_part, has_mero_portion, has_meronym, has_subevent, has_xpos_hyperonym, 
has_xpos_hyponym, involved, involved_agent, involved_instrument, involved_location, involved_patient, involved_target_direction, 
is_caused_by, is_subevent_of, near_antonym, near_synonym, role, role_agent, role_instrument, role_location, role_patient, 
role_target_direction, state_of, xpos_fuzzynym, xpos_near_antonym, xpos_near_synonym .


Usage
=====

Before anything else, let's import the module::

    from estnltk.wordnet import wn
    
Synsets
-------

The most common use for the API is to query synsets.
Synsets can be queried in several ways.
The easiest way is to query all the synsets which match some conditions.
For that we can either use::

    wn.all_synsets()
    
which returns all the synsets there are or::

    wn.all_synsets(pos=wn.ADV)
    
which returns all the synset of which part of speech is "adverb".
We can also query synsets by providing a lemma and a part of speech using::

    >>> wn.synsets("koer",pos=wn.VERB)
    []
    
By neglecting "pos", it matches once again all the synsets with "koer" as lemma.

    >>> wn.synsets("koer")
    [Synset('koer.n.01'), Synset('kaak.n.01')]
    

Details
-------
The API allows to query synset's details. For example, we can retrieve name and pos::

    >>> synset = wn.synset("king.n.01")
    >>> synset.name
    'king.n.01'
    >>> synset.pos
    'n'
    
We can also query definition and examples::

    >>> synset.definition()
    'jalalaba kattev kontsaga jalats, mis ei ulatu pahkluust kõrgemale'
    >>> synset.examples()
    [u'Jalad hakkasid katkistes kingades k\xfclmetama.']
    

Relations
---------
We can also query related synsets.
There are relations, for which there are specific methods::

    >>> synset.hypernyms()
    [Synset('jalats.n.01')]
    >>> synset.hyponyms()
    [Synset('peoking.n.01'), Synset('rihmking.n.01'), Synset('lapseking.n.01')]
    >>> synset.meronyms()
    []
    >>> synset.holonyms()
    []
    
More specific relations can be queried with a universal method::

    >>> synset.get_related_synsets('fuzzynym')
    [Synset('jäätisemüüja.n.01'), Synset('jäätisekauplus.n.01'), Synset('jäätisekampaania.n.01'), Synset('jäätisekohvik.n.01')]
    
Similarities
------------

We can measure distance or similarity between two synsets in several ways.
For calculating similarity, we provide path, Leacock-Chodorow and Wu-Palmer similarities::

    >> target_synset = wn.synset('kinnas.n.01')
    >>> synset.path_similarity(target_synset)
    0.25
    >>> synset.lch_similarity(target_synset)
    1.8718021769
    >>> synset.wup_similarity(target_synset)
    0.8
    
In addition, we can also find the closest common ancestor via hypernyms.

    >>> synset.lowest_common_hypernyms(target_synset)
    [Synset('kehakate.n.01')]

There are 4 different part of speeches available in the Estonian WordNet: `wn.ADJ, wn.ADV, wn.VERB, wn.NOUN`.

