==========================================================
Teksti tükeldamine lõikudeks, lauseteks ja sõnadeks
==========================================================

Enamikus keele automaattöötluse rakendustes on esimeseks sammuks sisendteksti jagamine väiksemateks tükkideks: paragrahvideks, lauseteks ja sõnadeks. Keele automaatanalüüsi seisukohalt polegi see alati triviaalne ülesanne, näiteks ei saa eeldada, et punkt sõna lõpus tähistab alati lauselõppu (see võib olla ka nt kuupäeva ja aastarvu lõpus, vanemates tekstides ka lühendite lõpus). Seetõttu sisaldavad keele automaattöötluse rakendused sageli eraldi mooduleid, mis tegelevad teksti tükeldamise probleemidega.

Estnltk-s pakub teksti tükeldamise tuge klass :class:`estnltk.tokenize.Tokenizer`. Järgnevas näites loome sisendteksti (sõne ``text``), seejärel impordime ja initsialiseerime teksti tükeldaja (``tokenizer``, isendi klassist :class:`estnltk.tokenize.Tokenizer`) ning kasutame seda, et luua tükeldatud kujul sisendteksti sisaldav dokument (``document``, :class:`estnltk.corpus.Document` klassi isend)::

    # Loome näiteteksti
    text = '''Keeletehnoloogia on arvutilingvistika praktiline pool.
    Keeletehnoloogid kasutavad arvutilingvistikas välja töötatud 
    teooriaid, et luua rakendusi (nt arvutiprogramme), 
    mis võimaldavad inimkeelt arvuti abil töödelda ja mõista. 

    Tänapäeval on keeletehnoloogia tuntumateks valdkondadeks 
    masintõlge, arvutileksikoloogia, dialoogisüsteemid, 
    kõneanalüüs ja kõnesüntees.
    '''

    # Tükeldame teksti Tokenizer'i abil
    from estnltk import Tokenizer
    tokenizer = Tokenizer()
    document = tokenizer.tokenize(text)

    # Väljastame tükeldamise tulemused
    print (document.word_texts)
    print (document.sentence_texts)
    print (document.paragraph_texts)
    print (document.text)

    
Tulemusena väljastatakse teksti tükeldus sõnadeks (ehk teksti *sõnestus*)::

    ['Keeletehnoloogia', 'on', 'arvutilingvistika', 'praktiline', 'pool.', 'Keeletehnoloogid', 
    'kasutavad', 'arvutilingvistikas', 'välja', 'töötatud', 'teooriaid', ',', 'et', 'luua', 
    'rakendusi', '(', 'nt', 'arvutiprogramme', ')', ',', 'mis', 'võimaldavad', 'inimkeelt', 
    'arvuti', 'abil', 'töödelda', 'ja', 'mõista.', 'Tänapäeval', 'on', 'keeletehnoloogia', 
    'tuntumateks', 'valdkondadeks', 'masintõlge', ',', 'arvutileksikoloogia', ',', 'dialoogisüsteemid', 
    ',', 'kõneanalüüs', 'ja', 'kõnesüntees.']
    
ja tükeldus lauseteks (ehk teksti *lausestus*)::

    ['Keeletehnoloogia on arvutilingvistika praktiline pool.', 
     'Keeletehnoloogid kasutavad arvutilingvistikas välja töötatud \nteooriaid, 
        et luua rakendusi (nt arvutiprogramme), \nmis võimaldavad inimkeelt 
        arvuti abil töödelda ja mõista. ', 
     'Tänapäeval on keeletehnoloogia tuntumateks valdkondadeks \nmasintõlge, 
        arvutileksikoloogia, dialoogisüsteemid, \nkõneanalüüs ja kõnesüntees.\n']

ning tükeldus lõikudeks::

    ['Keeletehnoloogia on arvutilingvistika praktiline pool.\nKeeletehnoloogid 
        kasutavad arvutilingvistikas välja töötatud \nteooriaid, et luua 
        rakendusi (nt arvutiprogramme), \nmis võimaldavad inimkeelt arvuti 
        abil töödelda ja mõista.',
     'Tänapäeval on keeletehnoloogia tuntumateks valdkondadeks \nmasintõlge, 
        arvutileksikoloogia, dialoogisüsteemid, \nkõneanalüüs ja kõnesüntees.\n']

Teksti esialgne (sõnekuju) on endiselt kättesaadav klassi :class:`estnltk.corpus.Document` atribuudi ``text`` kaudu.

Kui teksti tükeldamisel peaks ilmuma järgnev (või sarnane) veateade::

    LookupError: 
    **********************************************************************
      Resource u'tokenizers/punkt/estonian.pickle' not found.  Please
      use the NLTK Downloader to obtain the resource:  >>>
      nltk.download()

siis on tõenäoliselt ununenud täitmata installeerimisjärgne samm: NLTK eesti keele tükeldamisvahendite paigaldamine. Selle vea saab parandada (süsteemi käsurea) käsuga::

    python -m nltk.downloader punkt


Tükkide asukoht algses tekstis
---------------------------------------

Pärast teksti tükeldamist on sageli tarvis teada, millistel positsioonidel saadud tükk (nt lause, sõna) algses tekstis paiknes.
Seda informatsiooni väljastavad `estnltk` meetodid ``word_spans``, ``sentence_spans`` and ``paragraph_spans``.

Võttes aluseks eelmise näite, grupeerime sõnad nende algus- ja lõpp-positsioonidega algses tekstis::

    zip(document.word_texts, document.word_spans)

tulemusena luuakse ennikute list, kus esimeseks elemendiks on tükeldamisel saadud sõna ning teiseks elemendiks on ennik, mis sisaldab sõna algus ja lõpp-positsiooni algses tekstis::

    [('Keeletehnoloogia', (0, 16)),
     ('on', (17, 19)),
     ('arvutilingvistika', (20, 37)),
     ('praktiline', (38, 48)),
     ('pool.', (49, 54)),
     ...
     ('kõneanalüüs', (340, 351)),
     ('ja', (352, 354)),
     ('kõnesüntees.', (355, 367))]

Muude tekstiüksuste positsioonide leidmise kohta palun vt täpsemalt klasside :class:`estnltk.corpus.Corpus`, :class:`estnltk.corpus.Document`, :class:`estnltk.corpus.Paragraph`, :class:`estnltk.corpus.Sentence` ja :class:`estnltk.corpus.Word` dokumentatsioonist.
