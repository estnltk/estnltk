========================
Estnltk kasutusjuhised
========================

Järgnevalt tutvustame kõiki `estnltk` poolt pakutavaid keeletöötluse vahendeid.
Tööriistade paremaks tundmaõppimiseks on soovitav need juhised läbi lugeda ning näited kaasa teha.
Kasutatud koodinäited on pandud ka paketiga kaasa ning need leiab kataloogist `estnltk/examples`.

Teksti tükeldamine paragrahvideks, lauseteks ja sõnadeks
==========================================================

Enamikus keele automaattöötluse rakendustes on esimeseks sammuks sisendteksti jagamine väiksemateks tükkideks: paragrahvideks, lauseteks ja sõnadeks.

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

ning tükeldus paragrahvideks::

    ['Keeletehnoloogia on arvutilingvistika praktiline pool.\nKeeletehnoloogid 
        kasutavad arvutilingvistikas välja töötatud \nteooriaid, et luua 
        rakendusi (nt arvutiprogramme), \nmis võimaldavad inimkeelt arvuti 
        abil töödelda ja mõista.',
     'Tänapäeval on keeletehnoloogia tuntumateks valdkondadeks \nmasintõlge, 
        arvutileksikoloogia, dialoogisüsteemid, \nkõneanalüüs ja kõnesüntees.\n']

Teksti esialgne (sõnekuju) on endiselt kättesaadav klassi :class:`estnltk.corpus.Document` atribuudi ``text`` kaudu.

Kui teksti tükeldamisel peaks ilmuma järgnev veateade::

    LookupError: 
    **********************************************************************
      Resource u'tokenizers/punkt/estonian.pickle' not found.  Please
      use the NLTK Downloader to obtain the resource:  >>>
      nltk.download()

siis on tõenäoliselt ununenud täitmata installeerimisjärgne samm: NLTK eesti keele tükeldamisvahendite paigaldamine. Selle vea saab parandada (süsteemi käsurea) käsuga::

    python -m nltk.downloader punkt

