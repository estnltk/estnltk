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

Põhikasutus
------------

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
        print(' peaverbi polaarsus: ', chain.polarity )
        print(' peaverbi kõneviis: ', chain.mood )
        print(' peaverbi aeg:      ', chain.tense )
        print(' peaverbi tegumood: ', chain.voice )
        print(' kontekstis on teisi verbe?: ', chain.other_verbs )
        print()  

Tulemusena väljastatakse::

     tekst:  oleks pidanud minema
     üldine muster:  ['ole', 'verb', 'verb']
     algvormid:  ['ole', 'pida', 'mine']
     morf:  ['V_ks', 'V_nud', 'V_ma']
     peaverbi polaarsus:  POS
     peaverbi kõneviis:  condit
     peaverbi aeg:       past
     peaverbi tegumood:  personal
     kontekstis on teisi verbe?:  False

     tekst:  ei läinud.
     üldine muster:  ['ei', 'verb']
     algvormid:  ['ei', 'mine']
     morf:  ['V_neg', 'V_nud']
     peaverbi polaarsus:  NEG
     peaverbi kõneviis:  indic
     peaverbi aeg:       imperfect
     peaverbi tegumood:  personal
     kontekstis on teisi verbe?:  False

Järgneb atribuutide lühikirjeldus:
   
    * ``pattern_tokens`` - üldine muster: järjend, mis sisaldab iga ahelasse kuuluva sõna üldist kirjeldust. Märgitakse, kas sõna on *'ega'*, *'ei'*, *'ära'*, *'pole'*, *'ole'*, *'&'* (sidesõna: ja/ning/ega/või), *'verb'* (mitte-*'olema'* verb) või *'nom/adv'* (käändsõna/adverb); 
    * ``roots`` - järjend, mis sisaldab iga ahelasse kuuluva sõna 'root' väärtust morfoloogilisest analüüsist;
    * ``morph`` - järjend, mis sisaldab iga ahelasse kuuluva sõna morfoloogilisi tunnuseid: sõnaliik ja vormitüüp (ühe sõnena, sõnaliigi ja vormitüübi vahel on eraldajaks '_'; kui tunnused on jäänud mitmeseks, on erinevate variantide vahel eraldajaks '/');
    * ``polarity`` - ahela peaverbi grammatiline polaarsus. Võimalikud väärtused: *'POS'*, *'NEG'* või *'??'*. *'NEG'* märgib seda, et verbiahela alguses on eitusesõna (*ei/pole/ega/ära*); *'??'* on reserveeritud juhtudeks, kui pole kindel, kas *ära* on kasutusel eitusesõnana või mitte;
    * ``mood`` - ahela peaverbi kõneviis. Võimalikud väärtused: *'indic'* (indikatiiv ehk kindel kv), *'imper'* (imperatiiv ehk käskiv kv), *'condit'* (konditsionaal ehk tingiv kv), *'quotat'* (kvotatiiv ehk kaudne kv) või *'??'* (määramata);
    * ``tense`` - ahela peaverbi aeg. Võimalikud väärtused sõltuvad kõneviisist. Kindla kõneviisi ajad: *'present'* (olevik), *'imperfect'* (lihtminevik), *'perfect'* (täisminevik), *'pluperfect'* (enneminevik); käskiva kõneviisi aeg: *'present'*; tingiva ja kaudse kõneviisi ajad: *'present'* (olevik) ja *'past'* (minevik). Lisaks võib aeg jääda määramata (*'??'*).
    * ``voice`` - ahela peaverbi tegumood. Võimalikud väärtused: *'personal'* (isikuline), *'impersonal'* (umbisikuline), *'??'* (määramata).
    * ``other_verbs`` - kahendmuutuja, mis märgib, kas verbiahela kontekstis on veel verbe, mis võivad  kuuluda verbiahela koosseisu. Kui väärtus on ``True``, pole kindel, kas ahel on terviklik või mitte;

Verbiahelates on sõnad järjestatud grammatiliste seoste järgi (järjestus, mis võib, aga ei pruugi, langeda kokku sõnade tegeliku järjekorraga lauses). 
Ahela esimene sõna (või sõnapaar, nt eituse korral) on tüüpiliselt osalauses kesksel kohal olev verb (peaverb) ning iga järgnev sõna ahelas on eelmise sõna alluv.
Mõneti erandlikud on juhud, kus verbiahela lõpus on kahe infiniitverbi konjunktsioon (üldise mustri lõpus on *verb & verb*) - sellistel juhtudel peaksid mõlemad infiniitverbid alluma ahelas eelnevale sõnale.

.. Note that the words in the verb chain are ordered not as they appear in the text, but by the order of the grammatical relations: first words are mostly grammatical (such as auxiliary negation words *ei/ega/ära*) or otherwise abstract (e.g. modal words like *tohtima*, *võima*, aspectual words like *hakkama*), and only the last words carry most of the semantic/concrete meaning.

Näiteid üldistest mustritest
-------------------------------
Üks viis saada ülevaade programmi praeguse versiooni poolt leitavatest verbiahelatest on jooksutada seda suurel korpusel ning uurida tulemusi.
Failis :download:`tasak_verb_chain_examples <_static/tasak_verb_chain_examples.html>` ongi toodud Tasakaalus korpusest (http://www.cl.ut.ee/korpused/grammatikakorpus/index.php?lang=et) programmi poolt eraldatud verbiahelate statistika ning näited.
Verbiahelad on grupeeritud üldiste mustrite järgi (täpsemalt: üldiste mustrite esimeste sõnade järgi) ning iga grupi sisu on omakorda sorteeritud esinemissageduse järgi.
Iga üldise mustri juures on toodud välja selle esinemissagedus, suhteline sagedus kõigi mustrite seas ning üks näitelause (kus ahelasse kuuluvad sõnad on allajoonitud).
Viimane muster ( *...+??* ) tähistab kõiki potentsiaalselt poolikuks jäänud verbiahelaid (st ahelaid, mille puhul ``other_verbs == True``).


.. rubric:: Märkused

.. [#] Mõistet *verbiahel* ei kasutata siin mitte ranges lingvistilises tähenduses (mõiste *ahelverb* sünonüümina), vaid üldisemas tähenduses, mis peaks hõlmama nii süntaktilisse predikaati kuuluvaid verbiühendeid (liitajad, ahelverbid) kui ka mõningaid semantilise predikaadi moodustavaid verbiühendeid (teatud tugiverbiühendid/ühendverbid koos nende laiendustega);