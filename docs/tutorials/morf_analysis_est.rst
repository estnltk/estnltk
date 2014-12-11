========================
Morfoloogiline analüüs
========================

Morfoloogilise analüüsi käigus määratakse kindlaks sõna struktuur (nt sõna algvorm (tüvi, liited) ja lõpud), sõnaliik ja kääne või pööre.
Algvorm ehk lemma on tüüpiliselt see sõnakuju, mida kasutatakse sõnastikus märksõnana.
Sõnaliik määrab selle, milliseid vorme sõnast moodustada saab (nt enamikku nimisõnadest saab käänata 14-nes käändes) ning millistes (süntaktilistes) rollides sõna lauses esineda võib (nt verbid võivad esineda lauses öeldisena). 
Lisaks selguvad morfoloogilise analüüsi käigus muud sõnavormi tasandil avalduvad grammatilised kategooriad, nt käändsõnade ainsus/mitmus, tegusõnade pöörded jms.

`Estnltk`-s võimaldab sõnesid morfoloogiliselt analüüsida funktsioon :class:`estnltk.morf.analyze`::

    from estnltk import analyze
    from pprint import pprint

    pprint(analyze('Tüünete öötööde allmaaraudteejaam'))

Tulemuseks on sisendteksti morfoloogilised analüüsid JSON-i laadses vormingus::

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

Tuleb täheldada, et eestikeelsed tekstid on sageli morfoloogiliselt *mitmesed*, st ühte sõna võib sageli mitut moodi analüüsida. Kuna morfoloogiliseks analüüsiks kasutatav teek `vabamorf`_ ei sisalda veel morfoloogilist *ühestamist* (st konteksti põhjal õigete analüüside väljavalimist), siis tagastab analüsaator  kõik võimalikud analüüsid. 
Ülevaate kasutatavatest morfoloogilistest märgenditest ja nende tähendustest leiab vabamorfi `dokumentatsioonist`_ ja `spetsifikatsioonist`_.

    .. _vabamorf: https://github.com/Filosoft/vabamorf/
    .. _spetsifikatsioonist:  https://www.keeletehnoloogia.ee/et/ekt-projektid/vabavaraline-morfoloogiatarkvara/tarkvara-nouete-spetsifikatsioon
    .. _dokumentatsioonist: https://github.com/Filosoft/vabamorf/blob/master/doc/tagset.html

Morfoloogilist analüsaatorit saab rakendada ka juba eeltükeldatud dokumendil (st dokumendil, mis on eelneval analüüsil jagatud paragrahvideks, lauseteks, sõnadeks).
Sellisel juhul on morfoloogilise analüüsi tulemuseks dokument, millel saab teha ka päringuid, nt võib leida järjendid, kus on toodud välja iga sõna sõnaliik, lemma vm morfoloogiline kategooria.
Kasutame selleks klassi :class:`estnltk.morf.PyVabamorfAnalyzer`::

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

    # jagame sisendteksti tükkideks ja rakendame morfoloogilist analüüsi
    morf_analyzed = analyzer(tokenizer(text))

    # väljastame tulemused: lemmad ja sõnaliigid
    print (morf_analyzed.lemmas)
    print (morf_analyzed.postags)
    
    # väljastame kogu informatsiooni koos
    pprint (list(zip(morf_analyzed.word_texts,
                     morf_analyzed.lemmas,
                     morf_analyzed.forms,
                     morf_analyzed.postags)))

Tulemusena väljastatakse järgmine sisendteksti sõnalemmade järjend::
    
    ['keeletehnoloogia', 'olema', 'arvutilingvistika', 'praktiline', 'pool', 'keeletehnoloog', 
    'kasutama', 'arvutilingvistika', 'väli', 'töötatud', 'teooria', ',', 'et', 'looma', 
    'rakendus', '(', 'nt', 'arvutiprogramm', ')', ',', 'mis', 'võimaldama', 'inimkeel', 
    'arvuti', 'abi', 'töötlema', 'ja', 'mõistma', 'tänapäev', 'olema', 'keeletehnoloogia', 
    'tuntum', 'valdkond', 'masintõlge', ',', 'arvutileksikoloogia', ',', 'dialoogisüsteem', 
    ',', 'kõneanalüüs', 'ja', 'kõnesüntees']

ja sõnaliikide järjend::

    ['S', 'V', 'S', 'A', 'S', 'S', 'A', 'S', 'S', 'A', 'S', 'Z', 'J', 'S', 'S', 'Z', 'Y', 
    'S', 'Z', 'Z', 'P', 'A', 'S', 'S', 'K', 'V', 'J', 'V', 'S', 'V', 'S', 'C', 'S', 'S', 
    'Z', 'S', 'Z', 'S', 'Z', 'S', 'J', 'S']

ning iga sõna erinevaid analüüse (sõna tekstikuju, lemma, vormitüüp ja sõnaliik) koondav järjend::

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

NB! Kuigi eelnev näide võib jätta mulje, et igal sõnal ongi ainult üks analüüs, siis tegelikult on mitmesed analüüsid lihtsalt peidetud, st ``morf_analyzed.lemmas``, ``morf_analyzed.forms`` ja  ``morf_analyzed.postags`` tagastavad iga sõna kohta vaid ühe analüüsi (mis ei pruugi ühestamata teksti korral olla õige analüüs). Sõna ülejäänud analüüsidele pääseb ligi klassi :class:`estnltk.corpus.Word` atribuutide kaudu. Näide:: 

    # Väljastame esimese sõna ('Keeletehnoloogia') kõik vormitüübid
    print (morf_analyzed.words[0].forms)

annab tulemuseks::

    ['sg g', 'sg n']


Morfoloogiline süntees
=======================

`Estnltk` pakub ka morfoloogilise sünteesi tuge, st võimaldab etteantud sõnalemmast ja morfoloogilistest kategooriatest lähtuvalt genereerida uusi sõnavorme. 
Selleks rakendame funktsiooni :class:`estnltk.morf.synthesize`::

    from estnltk import synthesize

    print(synthesize('pood', form='pl p', partofspeech='S'))
    print(synthesize('palk', form='sg kom'))

Tulemusena väljastatakse::

    ['poode', 'poodisid']
    ['palgaga', 'palgiga']

Vabamorfi `dokumentatsioon`_ pakub ülevaadet võimalikest kategooriates, mida saab sünteesil kasutada.

    .. _dokumentatsioon: https://github.com/Filosoft/vabamorf/blob/master/doc/tagset.html

