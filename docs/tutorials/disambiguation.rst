=========================================================
Morphological disambiguation on a collection of documents
=========================================================
.. highlight:: python

Estnltk does basic morphological disambiguation by using a probabilistic disambiguator which relies on the local (sentence) context. _[KA01]
This works well enough for any type of texts: news articles, comments, mixed content etc.

However, the quality of the disambiguation can be further improved if a broader context (e.g. the whole text, or a collection of texts) is considered in the process. If morphologically ambiguous words (for example: proper names) reoccur in other parts of the text or in other related texts, one can use the assumption "one lemma per discourse" (inspired by the observation "one sense per discourse" from Word Sense Disambiguation) and choose the right analysis based on the most frequently occurring lemma candidate. _[KA12]

.. [KA01] Kaalep, Heiki-Jaan, and Vaino, Tarmo. "Complete morphological analysis in the linguist's toolbox." Congressus Nonus Internationalis Fenno-Ugristarum Pars V (2001): 9-16.
.. [KA12] Kaalep, Heiki Jaan, Riin Kirt, and Kadri Muischnek. "A trivial method for choosing the right lemma." Baltic HLT. 2012.

Consider the following example of a text collection::

    corpus = ['Esimesele kohale tuleb Jänes, kuigi tema punktide summa pole kõrgeim.',\
              'Lõpparvestuses läks Konnale esimene koht. Teise koha sai seekord Jänes. Uus võistlus toimub 2. mail.', \
              'Konn paistis silma suurima punktide summaga. Uue võistluse toimumisajaks on 2. mai.']

After applying the default (local context) morphological disambiguation, some of the words will still be ambiguous, as can be revealed by executing the following scipt::

    from estnltk import Text
    from estnltk.names import TEXT, ANALYSIS, ROOT, POSTAG, FORM

    for text_str in corpus:
        text = Text(text_str)
        # Perform morphological analysis with default disambiguation
        text.tag_analysis()
        # Print out all words with ambiguous analyses
        for word in text.words:
            if len(word[ANALYSIS]) > 1:
                print( word[TEXT],[(a[ROOT],a[POSTAG],a[FORM]) for a in word[ANALYSIS]] )

which has the following output::

    kohale [('koht', 'S', 'sg all'), ('koha', 'S', 'sg all')]
    kuigi [('kuigi', 'D', ''), ('kuigi', 'J', '')]
    Teise [('teine', 'O', 'sg g'), ('teine', 'P', 'sg g')]
    koha [('koht', 'S', 'sg g'), ('koha', 'S', 'sg g')]
    mail [('maa', 'S', 'pl ad'), ('mai', 'S', 'sg ad')]
    summaga [('summ', 'S', 'sg kom'), ('summa', 'S', 'sg kom')]
    on [('ole', 'V', 'b'), ('ole', 'V', 'vad')]

Basic usage
===============

Estnltk's class :py:class:`~estnltk.disambiguator.Disambiguator` provides method :py:meth:`~estnltk.disambiguator.Disambiguator.disambiguate`, which takes a collection of texts (can be a list of strings or a list of :py:class:`~estnltk.text.Text` objects) as an input, and performs both local context morphological disambiguation and "one lemma per discourse" disambiguation on the collection::

    from estnltk import Disambiguator
    
    corpus = ['Esimesele kohale tuleb Jänes, kuigi tema punktide summa pole kõrgeim.',\
              'Lõpparvestuses läks Konnale esimene koht. Teise koha sai seekord Jänes. Uus võistlus toimub 2. mail.', \
              'Konn paistis silma suurima punktide summaga. Uue võistluse toimumisajaks on 2. mai.']

    disamb = Disambiguator()
    texts = disamb.disambiguate(corpus)

The method returns a list of :py:class:`~estnltk.text.Text` objects. We can use the following script to check for morphological ambiguities in this list::

    from estnltk.names import TEXT, ANALYSIS, ROOT, POSTAG, FORM
    
    for text in texts:
        # Print out all words with ambiguous analyses
        for word in text.words:
            if len(word[ANALYSIS]) > 1:
                print(word[TEXT],[(a[ROOT],a[POSTAG],a[FORM]) for a in word[ANALYSIS]])

The output shows that the ambiguities in the content words (nouns *kohale*, *koha*, *mail*, *summaga*) have been removed::

    kuigi [('kuigi', 'D', ''), ('kuigi', 'J', '')]
    Teise [('teine', 'O', 'sg g'), ('teine', 'P', 'sg g')]
    on [('ole', 'V', 'b'), ('ole', 'V', 'vad')]

Pre-disambiguation and post-disambiguation
===========================================
Under the hood, the disambiguation process implemented in :py:class:`~estnltk.disambiguator.Disambiguator` can be broken down into three steps:

1. **pre-disambiguation** during which the collection level disambiguation is applied for resolving proper noun vs common noun ambiguities;
2. **local context disambiguation** during which the sentence level disambiguation is performed;
3. **post-disambiguation** during which the collection level disambiguation is applied for resolving remaining ambiguities in content words;

By default, all three steps are performed on the input corpus. However, if needed, pre-disambiguation and post-disambiguation can also be disabled, passing ``pre_disambiguate=False`` and ``post_disambiguate=False`` as input arguments for the method :py:meth:`~estnltk.disambiguator.Disambiguator.disambiguate`.

In following example, disambiguation is applied both with pre-disambiguation enabled and   disabled, and the difference in results is printed out::

    corpus = ['Jänes oli parajasti põllu peal. Hunti nähes ta ehmus ja pani jooksu.',\
              'Talupidaja Jänes kommenteeris, et hunte on viimasel ajal liiga palju siginenud. Tema naaber, talunik Lammas, nõustus sellega.', \
              'Jänesele ja Lambale oli selge, et midagi tuleb ette võtta. Eile algatasid nad huntidevastase kampaania.']
    
    from estnltk.names import TEXT, ANALYSIS, ROOT, POSTAG, FORM      
    from estnltk import Disambiguator
    
    disamb = Disambiguator()
    texts_with_predisamb    = disamb.disambiguate(corpus)
    texts_without_predisamb = disamb.disambiguate(corpus, pre_disambiguate=False)

    for i in range(len(texts_with_predisamb)):
        with_predisamb    = texts_with_predisamb[i]
        without_predisamb = texts_without_predisamb[i]
        for j in range(len(with_predisamb.words)):
            word1 = with_predisamb.words[j]
            word2 = without_predisamb.words[j]
            if word1 != word2:
                print(word1[TEXT], \
                      [(a[ROOT],a[POSTAG],a[FORM]) for a in word1[ANALYSIS]], \
                      ' vs ', \
                      [(a[ROOT],a[POSTAG],a[FORM]) for a in word2[ANALYSIS]] )

The output of the script::

    Jänes [('Jänes', 'H', 'sg n')]  vs  [('jänes', 'S', 'sg n')]
    Hunti [('hunt', 'S', 'sg p')]  vs  [('Hunt', 'H', 'sg g'), ('Hunti', 'H', 'sg g')]
    Talupidaja [('talu_pidaja', 'S', 'sg n')]  vs  [('talu_pidaja', 'S', 'sg g')]
    Jänes [('Jänes', 'H', 'sg n')]  vs  [('jänes', 'S', 'sg n')]
    Lammas [('Lammas', 'H', 'sg n')]  vs  [('lammas', 'S', 'sg n')]
    Jänesele [('Jänes', 'H', 'sg all')]  vs  [('jänes', 'S', 'sg all')]
    Lambale [('Lammas', 'H', 'sg all')]  vs  [('lammas', 'S', 'sg all')]
                      
