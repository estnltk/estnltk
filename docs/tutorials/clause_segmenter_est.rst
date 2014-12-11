================
Osalausestamine
================

Lihtlause on lause, mis tüüpiliselt sisaldab ühte pöördelist verbivormi ning väljendab ühte tegevust, seisundit või olukorda.
Loomuliku keele tekstides tuleb aga sageli ette ka keerukama struktuuriga *liitlauseid*, kus mitu väiksemat lauset (osalauset) on ühendatud üheks lauseks.
Selliste lausete töötlemisele lisab keerukust veel asjaolu, et osalaused võivad olla sisestatud teiste lausete sisse, jagades need kiiluna kaheks osaks.

Osalausestaja võimaldab jagada liitlaused väiksemateks osadeks - osalauseteks ja kiiludeks - ning töödelda iga osa eraldiseisva tekstiüksusena. Enne teksti osalausestamist on tarvis see lausestada ja sõnestada (klassi :class:`estnltk.tokenize.Tokenizer` abil) ning sooritada tekstil morfoloogiline analüüs (klass :class:`estnltk.morf.PyVabamorfAnalyzer`) ja morfoloogiline ühestamine (kuigi osalausestaja töötab ka morfoloogiliselt mitmesel tekstil, võib analüüsi kvaliteet olla madalam kui ühestatud tekstil).

Näide::

    from estnltk import Tokenizer, PyVabamorfAnalyzer, ClauseSegmenter
    from pprint import pprint

    tokenizer = Tokenizer()
    analyzer = PyVabamorfAnalyzer()
    segmenter = ClauseSegmenter()

    text = '''Mees, keda seal kohtasime, oli tuttav ja teretas meid.'''

    segmented = segmenter(analyzer(tokenizer(text)))



Osalausestaja märgib tekstis osalausepiirid (milliste sõnade järelt jookseb osalausepiir) ning kiilude algus- ja lõpp-positsioonid. 
Selle märgenduse põhjal genereeritakse igale lause sõnale arvuline indeks, mis märgib, millisesse osalausesse sõna kuulub.
Sõnadele omistatud osalausemärgendid on saadaval järjendina dokumendi välja ``clause_indices`` kaudu ning osalauseindeksid ``clause_annotations`` kaudu.
Järgnevas näites väljastatakse sõnad koos osalauseindeksite ja -märgenditega::

    pprint(list(zip(segmented.words, segmented.clause_indices, segmented.clause_annotations)))

    [('Word(Mees)', 0, None),
     ('Word(,)', 1, 'embedded_clause_start'),
     ('Word(keda)', 1, None),
     ('Word(seal)', 1, None),
     ('Word(kohtasime)', 1, None),
     ('Word(,)', 1, 'embedded_clause_end'),
     ('Word(oli)', 0, None),
     ('Word(tuttav)', 0, None),
     ('Word(ja)', 0, 'clause_boundary'),
     ('Word(teretas)', 2, None),
     ('Word(meid.)', 2, None)]

Osalausestamise tulemus on ka esitatud :class:`estnltk.corpus.Clause` objektidena, mis koondavad endas kõiki osalausesse kuuluvaid sõnu. Seega on võimalik lihtsa päringuga saada kätte kõik tekstist tuvastatud osalaused::

    # väljastame osalaused
    pprint(segmented.clauses)
    
    ['Clause(Mees oli tuttav ja [clause_index=0])',
     'Clause(, keda seal kohtasime , [clause_index=1])',
     'Clause(teretas meid. [clause_index=2])']

Järgnev näide demonstreerib, kuidas saada tekstist osalausete kaupa grupeeritud sõnade järjendeid::

    # Osalausete kaupa grupeeritud sõnad
    for clause in segmented.clauses:
        pprint(clause.words)
        
    ['Word(Mees)', 'Word(oli)', 'Word(tuttav)', 'Word(ja)']
    ['Word(,)', 'Word(keda)', 'Word(seal)', 'Word(kohtasime)', 'Word(,)']
    ['Word(teretas)', 'Word(meid.)']
