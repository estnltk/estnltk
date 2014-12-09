======================
Morphological analysis
======================

In linguistics, morphology is the identification, analysis, and description of the structure of a given language's morphemes and other linguistic units,
such as root words, lemmas, affixes/endings, parts of speech.

In morphology and lexicography, a lemma (plural lemmas or lemmata) is the canonical form, dictionary form, or citation form of a set of words (headword).
In grammar, a part of speech (also a word class, a lexical class, or a lexical category) is a linguistic category of words (or more precisely lexical items),
which is generally defined by the syntactic or morphological behaviour of the lexical item in question.
Common linguistic categories include noun and verb, among others.
Word forms define additional grammatical information such as cases, plurality etc.


Estnltk contains :class:`estnltk.morf.analyze` function for performing morphological analysis::

    from estnltk import analyze
    from pprint import pprint

    pprint(analyze('Tüünete öötööde allmaaraudteejaam'))

The result will be JSON-style data::

    [{'analysis': [{'clitic': '',
                    'ending': 'te',
                    'form': 'pl g',
                    'lemma': 'tüüne',
                    'partofspeech': 'A',
                    'root': 'tüüne',
                    'root_tokens': ['tüüne']}],
      'text': 'Tüünete'},
     {'analysis': [{'clitic': '',
                    'ending': 'de',
                    'form': 'pl g',
                    'lemma': 'öötöö',
                    'partofspeech': 'S',
                    'root': 'öö_töö',
                    'root_tokens': ['öö', 'töö']}],
      'text': 'öötööde'},
     {'analysis': [{'clitic': '',
                    'ending': '0',
                    'form': 'sg n',
                    'lemma': 'allmaaraudteejaam',
                    'partofspeech': 'S',
                    'root': 'all_maa_raud_tee_jaam',
                    'root_tokens': ['all', 'maa', 'raud', 'tee', 'jaam']}],
      'text': 'allmaaraudteejaam'}]

Note that the underlying `vabamorf`_ library does not yet include disambiguation, so all possible analysis will be returned.
The tags are documented in vabamorf tagset `documentation`_.

    .. _vabamorf: https://github.com/Filosoft/vabamorf/
    .. _documentation: https://github.com/Filosoft/vabamorf/blob/master/doc/tagset.html


The morphological analysis can also be applied on pretokenized data, so it will be possible to more easily list all lemmas, pos tags etc.
To do that, one needs to use :class:`estnltk.morf.PyVabamorfAnalyzer` class::

    from estnltk import Tokenizer
    from estnltk import PyVabamorfAnalyzer

    tokenizer = Tokenizer()
    analyzer = PyVabamorfAnalyzer()

    text = '''Keeletehnoloogia on arvutilingvistika praktiline pool.
    Keeletehnoloogid kasutavad arvutilingvistikas välja töötatud 
    teooriaid, et luua rakendusi (nt arvutiprogramme), 
    mis võimaldavad inimkeelt arvuti abil töödelda ja mõista. 

    Tänapäeval on keeletehnoloogia tuntumateks valdkondadeks 
    masintõlge, arvutileksikoloogia, dialoogisüsteemid, 
    kõneanalüüs ja kõnesüntees.
    '''

    # first tokenize and then morphologically analyze
    morf_analyzed = analyzer(tokenizer(text))

    # print some results
    print (morf_analyzed.lemmas)
    print (morf_analyzed.postags)
    
    # print more information together
    pprint (list(zip(morf_analyzed.word_texts,
                     morf_analyzed.lemmas,
                     morf_analyzed.forms,
                     morf_analyzed.postags)))


The lemmas / stemmed words::
    
    ['keeletehnoloogia', 'olema', 'arvutilingvistika', 'praktiline', 'pool', 'keeletehnoloog', 
    'kasutama', 'arvutilingvistika', 'väli', 'töötatud', 'teooria', ',', 'et', 'looma', 
    'rakendus', '(', 'nt', 'arvutiprogramm', ')', ',', 'mis', 'võimaldama', 'inimkeel', 
    'arvuti', 'abi', 'töötlema', 'ja', 'mõistma', 'tänapäev', 'olema', 'keeletehnoloogia', 
    'tuntum', 'valdkond', 'masintõlge', ',', 'arvutileksikoloogia', ',', 'dialoogisüsteem', 
    ',', 'kõneanalüüs', 'ja', 'kõnesüntees']

The pos tags::

    ['S', 'V', 'S', 'A', 'S', 'S', 'A', 'S', 'S', 'A', 'S', 'Z', 'J', 'S', 'S', 'Z', 'Y', 
    'S', 'Z', 'Z', 'P', 'A', 'S', 'S', 'K', 'V', 'J', 'V', 'S', 'V', 'S', 'C', 'S', 'S', 
    'Z', 'S', 'Z', 'S', 'Z', 'S', 'J', 'S']

More information put together::

    [('Keeletehnoloogia', 'keeletehnoloogia', 'sg g', 'S'),
     ('on', 'olema', 'b', 'V'),
     ('arvutilingvistika', 'arvutilingvistika', 'sg g', 'S'),
     ('praktiline', 'praktiline', 'sg n', 'A'),
     ('pool.', 'pool', 'sg n', 'S'),
     ('Keeletehnoloogid', 'keeletehnoloog', 'pl n', 'S'),
     ('kasutavad', 'kasutama', 'pl n', 'A'),
     ('arvutilingvistikas', 'arvutilingvistika', 'sg in', 'S'),
     ('välja', 'väli', '', 'S'),
     ('töötatud', 'töötatud', 'pl n', 'A'),
     ('teooriaid', 'teooria', 'pl p', 'S'),
     (',', ',', '', 'Z'),
     ('et', 'et', '', 'J'),
     ('luua', 'looma', 'da', 'S'),
     ('rakendusi', 'rakendus', 'pl p', 'S'),
     ('(', '(', '', 'Z'),
     ('nt', 'nt', '?', 'Y'),
     ('arvutiprogramme', 'arvutiprogramm', 'pl p', 'S'),
     (')', ')', '', 'Z'),
     (',', ',', '', 'Z'),
     ('mis', 'mis', 'pl n', 'P'),
     ('võimaldavad', 'võimaldama', 'pl n', 'A'),
     ('inimkeelt', 'inimkeel', 'sg p', 'S'),
     ('arvuti', 'arvuti', 'sg g', 'S'),
     ('abil', 'abi', '', 'K'),
     ('töödelda', 'töötlema', 'da', 'V'),
     ('ja', 'ja', '', 'J'),
     ('mõista.', 'mõistma', 'da', 'V'),
     ('Tänapäeval', 'tänapäev', 'sg ad', 'S'),
     ('on', 'olema', 'b', 'V'),
     ('keeletehnoloogia', 'keeletehnoloogia', 'sg g', 'S'),
     ('tuntumateks', 'tuntum', 'pl tr', 'C'),
     ('valdkondadeks', 'valdkond', 'pl tr', 'S'),
     ('masintõlge', 'masintõlge', 'sg n', 'S'),
     (',', ',', '', 'Z'),
     ('arvutileksikoloogia', 'arvutileksikoloogia', 'sg g', 'S'),
     (',', ',', '', 'Z'),
     ('dialoogisüsteemid', 'dialoogisüsteem', 'pl n', 'S'),
     (',', ',', '', 'Z'),
     ('kõneanalüüs', 'kõneanalüüs', 'sg n', 'S'),
     ('ja', 'ja', '', 'J'),
     ('kõnesüntees.', 'kõnesüntees', 'sg n', 'S')]


Morphological synthesis
=======================

Estnltk can also do morphological synthesis using :class:`estnltk.morf.synthesize` function::

    from estnltk import synthesize

    print(synthesize('pood', form='pl p', partofspeech='S'))
    print(synthesize('palk', form='sg kom'))

That will print::

    ['poode', 'poodisid']
    ['palgaga', 'palgiga']

See `documentation`_ for possible parameters.

    .. _documentation: https://github.com/Filosoft/vabamorf/blob/master/doc/tagset.html

