==================================
Experimental NP chunking
==================================

Estnltk includes an experimental noun phrase chunker, which can be used to detect non-overlapping noun phrases from the text.

Basic usage
=============

The class :py:class:`~estnltk.np_chunker.NounPhraseChunker` provides method :py:meth:`~estnltk.np_chunker.NounPhraseChunker.analyze_text`, which takes a :py:class:`~estnltk.text.Text` object as an input, detects potential noun phrases, and stores in the layer ``NOUN_CHUNKS``::

    from estnltk import Text
    from estnltk.np_chunker import NounPhraseChunker
    from estnltk.names import TEXT, NOUN_CHUNKS
    from pprint import pprint

    # initialise the chunker
    chunker = NounPhraseChunker()

    text = Text('Suur karvane kass nurrus punasel diivanil, väike hiir aga hiilis temast mööda.')
    # chunk the input text
    text = chunker.analyze_text( text )
    
    # output the results (found phrases)
    pprint( text[NOUN_CHUNKS] )

::

    [{'end': 17, 'start': 0, 'text': 'Suur karvane kass'},
     {'end': 41, 'start': 25, 'text': 'punasel diivanil'},
     {'end': 53, 'start': 43, 'text': 'väike hiir'},
     {'end': 71, 'start': 65, 'text': 'temast'}]

By default, the method :py:meth:`~estnltk.np_chunker.NounPhraseChunker.analyze_text` returns the input text. 
The keyword argument ``return_type`` can be used to change the type of data returned. If ``return_type='labels'``, the method returns results of chunking in a BIO annotation scheme::

    from estnltk import Text
    from estnltk.np_chunker import NounPhraseChunker
    from estnltk.names import TEXT

    # initialise the chunker
    chunker = NounPhraseChunker()

    text = Text('Suur karvane kass nurrus punasel diivanil, väike hiir aga hiilis temast mööda.')
    
    # chunk the input text, get the results in BIO annotation format
    np_labels = chunker.analyze_text( text, return_type='labels' )

    # output results of the chunking in BIO annotation format
    for word, np_label in zip(text.words, np_labels):
        print( word[TEXT]+'  '+str(np_label) )

In the above example, the resulting list ``np_labels`` contains a label for each word in the input text, indicating word's position in phrase: ``"B"`` denotes that the word begins a phrase, ``"I"`` indicates that the word is inside a phrase, and ``"O"`` indicates that the word does not belong to any noun phrase.
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
    from estnltk.names import TEXT, ANALYSIS, LEMMA

    # initialise the chunker
    chunker = NounPhraseChunker()

    text = Text('Autojuhi lapitekk pälvis linna koduleheküljel paljude kodanike tähelepanu.')
    # chunk the input text
    phrases = chunker.analyze_text( text, return_type="tokens" )
    # output phrases word by word
    for phrase in phrases:
        print()
        for token in phrase:
            # output text and first lemma
            print( token[TEXT], token[ANALYSIS][0][LEMMA] )

The output::

    Autojuhi autojuht
    lapitekk lapitekk
    
    linna linn
    koduleheküljel kodulehekülg
    
    paljude palju
    kodanike kodanik
    tähelepanu tähelepanu

Note that, regardless the ``return_type``, the layer ``NOUN_CHUNKS`` will always be added to the input Text.

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

Using a custom syntactic parser
================================

By default, the MaltParser is used for obtaining the syntactic annotation, which is used as a basis in the chunking. 
Using the keyword argument ``parser`` in the initialization of the :py:class:`~estnltk.np_chunker.NounPhraseChunker` , you can specify a custom parser to be used during the preprocessing::

    from estnltk import Text
    from estnltk.np_chunker import NounPhraseChunker
    from estnltk.syntax.parsers import VISLCG3Parser

    # initialise the chunker using VISLCG3Parser instead of MaltParser
    chunker = NounPhraseChunker( parser = VISLCG3Parser() )
    
    text = Text('Maril oli väike tall.')
    # chunk the input text
    text = chunker.analyze_text( text )
    
    # output the results (found phrases)
    pprint( text[NOUN_CHUNKS] )
    
::

    [{'end': 5, 'start': 0, 'text': 'Maril'},
     {'end': 20, 'start': 10, 'text': 'väike tall'}]


.. rubric:: Notes

.. [#] An automatic analysis of the Balanced Corpus of Estonian suggests that only 3% of all NP chunks are longer than 3 words.