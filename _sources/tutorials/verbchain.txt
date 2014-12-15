====================
Verb chain detection
====================

Verb chain detector identifies multiword verb units from text. 
The current version of the program aims to detect following verb chain constructions:

* basic main verbs:

  * negated main verbs: *ei/ära/pole/ega* + verb (e.g. Helistasin korraks Carmenile, kuid ta **ei vastanud.**);
  * (affirmative) single *olema* main verbs (e.g. Raha **on** alati vähe) and *olema* verb chains (**Oleme** sellist kino ennegi **näinud**);
  * (affirmative) single non-*olema* main verbs (example: Pidevalt **uurivad** asjade seisu ka hollandlased);

* verb chain extensions:

  * verb + verb : the chain is extended with an infinite verb if the last verb of the chain subcategorizes for it, e.g. the verb *kutsuma* is extended with *ma*-verb arguments (for example: Kevadpäike **kutsub** mind **suusatama**) and the verb *püüdma* is extended with *da*-verb arguments (Aita **ei püüdnudki** Leenat **mõista**);
  * verb + nom/adv + verb : the last verb of the chain is extended with nominal/adverb arguments which subcategorize for an infinite verb, e.g. the verb *otsima* forms a multiword unit with the nominal *võimalust* which, in turn, takes infinite *da*-verb as an argument (for example: Seepärast **otsisimegi võimalust** kusagilt mõned ilvesed **hankida**);

Verb chain detector requires that the input text has been tokenized (split into sentences and words), morphologically analyzed, morphologically disambiguated, and segmented into clauses. 
Recall that the text can be segmented into clauses with :class:`estnltk.clausesegmenter.ClauseSegmenter`.

Example::

    from estnltk import Tokenizer
    from estnltk import PyVabamorfAnalyzer
    from estnltk import ClauseSegmenter
    from estnltk import VerbChainDetector
    from pprint import pprint

    tokenizer = Tokenizer()
    analyzer = PyVabamorfAnalyzer()
    segmenter = ClauseSegmenter()
    detector = VerbChainDetector()

    text = ''''Samas on selge, et senine korraldus jätkuda ei saa.'''
    processed = detector(segmenter(analyzer(tokenizer(text))))

    # print verb chain objects
    pprint(processed.verb_chains)

Property :class:`estnltk.corpus.Corpus.verb_chains` lists all found :class:`estnltk.corpus.VerbChain` objects.
The previous example prints out following found verb chains::

    ['VerbChain(on, ole, ole, POS)',
     'VerbChain(korraldus, verb, korraldu, POS)',
     'VerbChain(jätkuda ei saa., ei+verb+verb, ei_saa_jätku, NEG)']

Note that because the program was ran on morphologically ambiguous text, the word *korraldus* was mistakenly detected as a main verb (past form of the verb *korralduma*).
In general, morphological disambiguation of the input is an important requirement for verb chain detector, and the quality of the analysis suffers quite much without it.

The default string representation of the verb chain (as can be seen from the previous example) contains four attribute values: text of the verb chain, the general pattern of the verb chain, concanated lemmas of the verb chain words, and grammatical polarity of the chain.
These and other attributes can also be directly accessed in the verb chain object::

    text = ''' Ta oleks pidanud sinna minema, aga ei läinud. '''
    processed = detector(segmenter(analyzer(tokenizer(text))))

    # print attributes of each verb chain object
    for chain in processed.verb_chains:
        print('text: ', chain.text )
        print('general pattern: ', chain.pattern_tokens )
        print('roots: ', chain.roots )
        print('morph: ', chain.morph )
        print('polarity: ', chain.polarity )
        print('other verbs: ', chain.other_verbs )
        print()    

The previous example outputs::

     text:  oleks pidanud minema
     general pattern:  ['ole', 'verb', 'verb']
     roots:  ['ole', 'pida', 'mine']
     morph:  ['V_ks', 'V_nud', 'V_ma']
     polarity:  POS
     other verbs:  False

     text:  ei läinud.
     general pattern:  ['ei', 'verb']
     roots:  ['ei', 'mine']
     morph:  ['V_neg', 'V_nud']
     polarity:  NEG
     other verbs:  False

Following is a brief description of the attributes:
   
    * ``pattern_tokens`` - the general pattern of the chain: for each word in the chain, lists whether it is *'ega'*, *'ei'*, *'ära'*, *'pole'*, *'ole'*, *'&'* (conjunction: ja/ning/ega/või), *'verb'* (verb different than *'ole'*) or *'nom/adv'* (nominal/adverb); 
    * ``roots`` - for each word in the chain, lists its corresponding 'root' value from the morphological analysis;
    * ``morph`` - for each word in the chain, lists its morphological features: part of speech tag and form (in one string, separated by '_', and multiple variants of the pos/form are separated by '/');
    * ``polarity`` - grammatical polarity of the chain: *'POS'*, *'NEG'* or *'??'*. *'NEG'* simply means that the chain begins with a negation word *ei/pole/ega/ära*; *'??'* is reserved for cases where it is uncertain whether *ära* forms a negated verb chain or not;
    * ``other_verbs`` - boolean, marks whether there are other verbs in the context, which can be potentially added to the verb chain; if ``True``,then it is uncertain whether the chain is complete or not;
  
.. Note that the words in the verb chain are ordered not as they appear in the text, but by the order of the grammatical relations: first words are mostly grammatical (such as auxiliary negation words *ei/ega/ära*) or otherwise abstract (e.g. modal words like *tohtima*, *võima*, aspectual words like *hakkama*), and only the last words carry most of the semantic/concrete meaning.
  
