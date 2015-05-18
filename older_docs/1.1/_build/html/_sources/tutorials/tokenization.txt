=========================================
Paragraph, sentence and word tokenization
=========================================

The first step in most text processing tasks is to tokenize the input into smaller pieces, typically paragraphs, sentences and words.
In lexical analysis, tokenization is the process of breaking a stream of text up into words, phrases, symbols, or other meaningful elements called tokens.
The list of tokens becomes input for further processing such as parsing or text mining.
Tokenization is useful both in linguistics (where it is a form of text segmentation), and in computer science, where it forms part of lexical analysis.


Estnltk provides the :class:`estnltk.tokenize.Tokenizer` class that does this.
In the next example, we define some text, then import and initialize a :class:`estnltk.tokenize.Tokenizer` instance and use to create a :class:`estnltk.corpus.Document` instance::

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

    
This will print out the tokenized words::

    ['Keeletehnoloogia', 'on', 'arvutilingvistika', 'praktiline', 'pool.', 'Keeletehnoloogid', 
    'kasutavad', 'arvutilingvistikas', 'välja', 'töötatud', 'teooriaid', ',', 'et', 'luua', 
    'rakendusi', '(', 'nt', 'arvutiprogramme', ')', ',', 'mis', 'võimaldavad', 'inimkeelt', 
    'arvuti', 'abil', 'töödelda', 'ja', 'mõista.', 'Tänapäeval', 'on', 'keeletehnoloogia', 
    'tuntumateks', 'valdkondadeks', 'masintõlge', ',', 'arvutileksikoloogia', ',', 'dialoogisüsteemid', 
    ',', 'kõneanalüüs', 'ja', 'kõnesüntees.']
    
and tokenized sentences::

    ['Keeletehnoloogia on arvutilingvistika praktiline pool.', 
     'Keeletehnoloogid kasutavad arvutilingvistikas välja töötatud \nteooriaid, 
        et luua rakendusi (nt arvutiprogramme), \nmis võimaldavad inimkeelt 
        arvuti abil töödelda ja mõista. ', 
     'Tänapäeval on keeletehnoloogia tuntumateks valdkondadeks \nmasintõlge, 
        arvutileksikoloogia, dialoogisüsteemid, \nkõneanalüüs ja kõnesüntees.\n']

and tokenized paragraphs::

    ['Keeletehnoloogia on arvutilingvistika praktiline pool.\nKeeletehnoloogid 
        kasutavad arvutilingvistikas välja töötatud \nteooriaid, et luua 
        rakendusi (nt arvutiprogramme), \nmis võimaldavad inimkeelt arvuti 
        abil töödelda ja mõista.',
     'Tänapäeval on keeletehnoloogia tuntumateks valdkondadeks \nmasintõlge, 
        arvutileksikoloogia, dialoogisüsteemid, \nkõneanalüüs ja kõnesüntees.\n']

and also the original full text can be accessed using ``text`` property of :class:`estnltk.corpus.Document`.
In case you get an error during tokenization, something like::

    LookupError: 
    **********************************************************************
      Resource u'tokenizers/punkt/estonian.pickle' not found.  Please
      use the NLTK Downloader to obtain the resource:  >>>
      nltk.download()

Then you have forgot post-installation step of downloading NLTK tokenizers. This can be done by invoking command::

    python -m nltk.downloader punkt

Token spans -- start and end positions
--------------------------------------

In addition to tokenization, it is often necessary to know where the tokens reside in the original document.
For example, you might want to inspect the context of a particular word.
For this purpose, estnltk provide ``word_spans``, ``sentence_spans`` and ``paragraph_spans`` methods.
Following the previous example, we can group together words and their start and end positions 
in the document using the following::

    zip(document.word_texts, document.word_spans)
    
This will create a list of tuples, where the first element is the tokenized word and the second element is a tuple
containing the start and end positions::

    [('Keeletehnoloogia', (0, 16)),
     ('on', (17, 19)),
     ('arvutilingvistika', (20, 37)),
     ('praktiline', (38, 48)),
     ('pool.', (49, 54)),
     ...
     ('kõneanalüüs', (340, 351)),
     ('ja', (352, 354)),
     ('kõnesüntees.', (355, 367))]

For other possible options, please check :class:`estnltk.corpus.Corpus`, :class:`estnltk.corpus.Document`, :class:`estnltk.corpus.Paragraph`, :class:`estnltk.corpus.Sentence` and :class:`estnltk.corpus.Word` classes.
