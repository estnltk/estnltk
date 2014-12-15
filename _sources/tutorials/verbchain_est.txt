==========================
Verbiahelate tuvastamine
==========================

Verbiahelate [#]_ tuvastaja leiab tekstist mitmesõnalised verbiüksused. Praegune versioon programmist tegeleb järgmiste verbiüksustega:

* osalauses kesksel kohal olevad verbid:

  * eitus: *ei/ära/pole/ega* + verb (nt, Helistasin korraks Carmenile, kuid ta **ei vastanud.**);
  * (jaatav) *olema* üksiku peaverbina (nt, Raha **on** alati vähe) ja *olema* kahesõnalise verbiahela kooseisus (nt, **Oleme** sellist kino ennegi **näinud**);
  * (jaatav) mitte-*olema* verb peaverbina (nt, Pidevalt **uurivad** asjade seisu ka hollandlased);

* laiendatud verbiahelad:

  * verb + verb : ahela viimast verbi laiendatakse sellest sõltuva infiniitverbiga, nt verbi *kutsuma* laiendatakse *ma*-infinitiivse argumendiga (Kevadpäike **kutsub** mind **suusatama**) ning verbi *püüdma* laiendatakse *da*-infinitiivse argumendiga (Aita **ei püüdnudki** Leenat **mõista**);
  * verb + nom/adv + verb : ahela viimast verbi laiendatakse sellest sõltuva käändsõna/adverbiga, kui viimasest sõltub omakorda mõni infiniitverb, nt verb *otsima* moodustab mitmesõnalise üksuse käändsõnaga *võimalust*, mis omakorda võtab *da*-infinitiivi argumendiks (Seepärast **otsisimegi võimalust** kusagilt mõned ilvesed **hankida**);

Verbiahelate tuvastamine nõuab, et sisendtekst on lausestatud ja sõnestatud (klassi :class:`estnltk.tokenize.Tokenizer` abil), morfoloogiliselt analüüsitud (klassi :class:`estnltk.morf.PyVabamorfAnalyzer` abil), morfoloogiliselt ühestatud ning jagatud osalauseteks.
Meenutagem, et teksti on võimalik jagada osalauseteks klassi :class:`estnltk.clausesegmenter.ClauseSegmenter` abil.

Näide::

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

    # väljastame leitud verbiahelad
    pprint(processed.verb_chains)

Väli :class:`estnltk.corpus.Corpus.verb_chains` annab järjendi kõigist leitud verbiahelatest, mis on esitatud   :class:`estnltk.corpus.VerbChain` objektide kujul.
Eelmise koodilõigu käivitamisel väljastatakse järgmised verbiahelad::

    ['VerbChain(on, ole, ole, POS)',
     'VerbChain(korraldus, verb, korraldu, POS)',
     'VerbChain(jätkuda ei saa., ei+verb+verb, ei_saa_jätku, NEG)']

Kuna programm käivitati morfoloogiliselt ühestamata tekstil, siis tuvastati sõna *korraldus* ekslikult kui osalause peaverb (ehk siis kui verbi *korralduma* minevikuvorm).
Verbiahelate tuvastaja töökvaliteet sõltub üsnagi palju sellest, kas sisendiks olev tekst on morfoloogiliselt ühestatud ning ühestamata teksti korral on oodata ka rohkem vigu.

Nagu eelmisest näitest näha võib, tuuakse iga verbiahela sõnekuju-esituses vaikimisi välja nelja atribuudi väärtused: verbiahela tekst, üldine muster, verbiahela lemmad ning verbiahela grammatiline polaarsus.
Neile ja muudele väärtustele pääseb ligi ka otse, verbiahel-objekti atribuutide kaudu::

    text = ''' Ta oleks pidanud sinna minema, aga ei läinud. '''
    processed = detector(segmenter(analyzer(tokenizer(text))))

    # väljastame atribuutide väärtused
    for chain in processed.verb_chains:
        print(' tekst: ', chain.text )
        print(' üldine muster: ', chain.pattern_tokens )
        print(' algvormid: ', chain.roots )
        print(' morf: ', chain.morph )
        print(' polaarsus: ', chain.polarity )
        print(' kontekstis on teisi verbe?: ', chain.other_verbs )
        print()  

Tulemusena väljastatakse::

     tekst:  oleks pidanud minema
     üldine muster:  ['ole', 'verb', 'verb']
     algvormid:  ['ole', 'pida', 'mine']
     morf:  ['V_ks', 'V_nud', 'V_ma']
     polaarsus:  POS
     kontekstis on teisi verbe?:  False

     tekst:  ei läinud.
     üldine muster:  ['ei', 'verb']
     algvormid:  ['ei', 'mine']
     morf:  ['V_neg', 'V_nud']
     polaarsus:  NEG
     kontekstis on teisi verbe?:  False

Järgneb atribuutide lühikirjeldus:
   
    * ``pattern_tokens`` - üldine muster: järjend, mis sisaldab iga ahelasse kuuluva sõna üldist kirjeldust. Märgitakse, kas sõna on *'ega'*, *'ei'*, *'ära'*, *'pole'*, *'ole'*, *'&'* (sidesõna: ja/ning/ega/või), *'verb'* (mitte-*'olema'* verb) või *'nom/adv'* (käändsõna/adverb); 
    * ``roots`` - järjend, mis sisaldab iga ahelasse kuuluva sõna 'root' väärtust morfoloogilisest analüüsist;
    * ``morph`` - järjend, mis sisaldab iga ahelasse kuuluva sõna morfoloogilisi tunnuseid: sõnaliik ja vormitüüp (ühe sõnena, sõnaliigi ja vormitüübi vahel on eraldajaks '_'; kui tunnused on jäänud mitmeseks, on erinevate variantide vahel eraldajaks '/');
    * ``polarity`` - verbiahela grammatiline polaarsus: *'POS'*, *'NEG'* või *'??'*. *'NEG'* märgib seda, et verbiahela alguses on eitusesõna (*ei/pole/ega/ära*); *'??'* on reserveeritud juhtudeks, kui pole kindel, kas *ära* on kasutusel eitusesõnana või mitte;
    * ``other_verbs`` - kahendmuutuja märkimaks, kas verbiahela kontekstis on veel verbe, mis võivad  kuuluda verbiahela koosseisu. Kui väärtus on ``True``, pole kindel, kas ahel on terviklik või mitte;
  
.. Note that the words in the verb chain are ordered not as they appear in the text, but by the order of the grammatical relations: first words are mostly grammatical (such as auxiliary negation words *ei/ega/ära*) or otherwise abstract (e.g. modal words like *tohtima*, *võima*, aspectual words like *hakkama*), and only the last words carry most of the semantic/concrete meaning.


.. rubric:: Märkused

.. [#] Mõistet *verbiahel* ei kasutata siin mitte ranges lingvistilises tähenduses (mõiste *ahelverb* sünonüümina), vaid üldisemas tähenduses, mis peaks hõlmama nii süntaktilisse predikaati kuuluvaid verbiühendeid (liitajad, ahelverbid) kui ka mõningaid semantilise predikaadi moodustavaid verbiühendeid (teatud tugiverbiühendid/ühendverbid koos nende laiendustega);