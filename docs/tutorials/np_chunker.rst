==================================
Experimental NP chunking
==================================

Estnltk includes an experimental noun phrase chunker, which can be used to detect non-overlapping noun phrases from the text.

Basic usage
=============

The class :py:class:`~estnltk.np_chunker.NounPhraseChunker` provides method :py:meth:`~estnltk.np_chunker.NounPhraseChunker.analyze_text`, which takes a :py:class:`~estnltk.text.Text` object as an input, and provides a tagging of phrases in a BIO annotation scheme::

    from estnltk import Text
    from estnltk.np_chunker import NounPhraseChunker
    from estnltk.names import NP_LABEL, TEXT

    # initialise the chunker
    chunker = NounPhraseChunker()

    text = Text('Suur karvane kass nurrus punasel diivanil, väike hiir aga hiilis temast mööda.')
    # chunk the input text
    chunker.analyze_text( text )

    # output results of the chunking in BIO annotation scheme
    for word in text.words:
        print( word[TEXT]+'  '+str(word[NP_LABEL]) )

As a result of chunking, attribute ``NP_LABEL`` will be added to every word in the input text. 
Attribute's value indicates word's position in phrase: ``"B"`` denotes that the word begins a phrase, ``"I"`` indicates that the word is inside a phrase, and ``"O"`` indicates that the word does not belong to any noun phrase.
Running the above example will produce following output::

    Suur  B
    karvane  I
    kass  I
    nurrus  O
    punasel  B
    diivanil  I
    ,  O
    väike  B
    hiir  I
    aga  O
    hiilis  O
    temast  B
    mööda  O
    .  O

By default, the method :py:meth:`~estnltk.np_chunker.NounPhraseChunker.analyze_text` returns the input text. 
If the input argument ``return_type="strings"`` is passed to the method, the method returns only results of the chunking as a list of phrase strings::

    from estnltk import Text
    from estnltk.np_chunker import NounPhraseChunker

    # initialise the chunker
    chunker = NounPhraseChunker()

    text = Text('Autojuhi lapitekk pälvis linna koduleheküljel paljude kodanike tähelepanu.')
    # chunk the input text
    phrase_strings = chunker.analyze_text( text, return_type="strings" )
    # output phrases
    print( phrase_strings )

The above example produces following output::

    ['Autojuhi lapitekk', 'linna koduleheküljel', 'paljude kodanike tähelepanu']

If ``return_type="tokens"`` is set, the chunker returns a list of lists of tokens, where each token is given as a dictonary containing analyses of the word::

    from estnltk import Text
    from estnltk.np_chunker import NounPhraseChunker
    from estnltk.names import NP_LABEL, TEXT, ANALYSIS, LEMMA

    # initialise the chunker
    chunker = NounPhraseChunker()

    text = Text('Autojuhi lapitekk pälvis linna koduleheküljel paljude kodanike tähelepanu.')
    # chunk the input text
    phrases = chunker.analyze_text( text, return_type="tokens" )
    # output phrases word by word
    for phrase in phrases:
        print()
        for token in phrase:
            # output text, first lemma, and NP label
            print( token[TEXT], token[ANALYSIS][0][LEMMA], token[NP_LABEL] )

The output::

    Autojuhi autojuht B
    lapitekk lapitekk I
    
    linna linn B
    koduleheküljel kodulehekülg I
    
    paljude palju B
    kodanike kodanik I
    tähelepanu tähelepanu I


Cutting phrases
=================

By default, the chunker does not allow tagging phrases longer than 3 words, as the quality of tagging longer phrases is likely suboptimal, and the coverage of these phrases is also likely  low [#]_ .
So, phrases longer than 3 words will be cut into one word phrases.
This default setting can be turned off by specifying ``cutPhrases=False`` as an input argument for the method :py:meth:`~estnltk.np_chunker.NounPhraseChunker.analyze_text`::

    from estnltk import Text
    from estnltk.np_chunker import NounPhraseChunker

    # initialise the chunker
    chunker = NounPhraseChunker()

    text = Text('Kõige väiksemate tassidega serviis toodi kusagilt vanast tolmusest kapist välja.')
    
    # chunk the input text while allowing phrases longer than 3 words
    phrase_strings = chunker.analyze_text( text, cutPhrases=False, return_type="strings" )
    # output phrases
    print( phrase_strings )

The output is following::

    ['Kõige väiksemate tassidega serviis', 'vanast tolmusest kapist']



.. rubric:: Notes

.. [#] An automatic analysis of the Balanced Corpus of Estonian suggests that only 3% of all NP chunks are longer than 3 words.