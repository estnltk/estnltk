===================================
 Ajaväljendite tuvastamine
===================================

Ajaväljendite tuvastaja leiab tekstist ajaväljendid ning esitab (normaliseerib) nende nende semantika (nt väljenditele vastavad kuupäevad ja kellaajad) eeldefineeritud märgenduskeele raamides.
Programmi poolt kasutatav märgendusviis on sarnane TimeML raamistikus kasutatavale TIMEX3 märgendusele (märgendusviisi detailsema kirjelduse leiab `ajaväljendite märgendamise juhistest`_).

.. _ajaväljendite märgendamise juhistest: https://github.com/soras/EstTimeMLCorpus/blob/master/docs-et/ajav2ljendite_m2rgendamine_06.pdf?raw=true

TimeML järgi eristatakse nelja tüüpi ajaväljendeid:

* DATE - kalendrilised toimumisajad, nt *järgmisel kolmapäeval*
* TIME - kellaajalised toimumisajad, nt *kell 18.00*
* DURATION - ajalised kestvused, nt *viis päeva*
* SET - ajalised korduvused, nt *igal aastal*

Ajaväljendite tuvastamine nõuab, et sisendtekst on lausestatud ja sõnestatud (klassi :class:`estnltk.tokenize.Tokenizer` abil), morfoloogiliselt analüüsitud (klassi :class:`estnltk.morf.PyVabamorfAnalyzer` abil) ning morfoloogiliselt ühestatud (kuigi programm töötab ka morfoloogiliselt mitmesel tekstil, võib analüüsi kvaliteet olla madalam kui ühestatud tekstil).

Näide::

    from estnltk import Tokenizer
    from estnltk import PyVabamorfAnalyzer
    from estnltk import TimexTagger
    from pprint import pprint

    tokenizer = Tokenizer()
    analyzer = PyVabamorfAnalyzer()
    tagger = TimexTagger()

    text = ''''Potsataja ütles eile, et vaatavad nüüd Genaga viie aasta plaanid uuesti üle.'''
    tagged = tagger(analyzer(tokenizer(text)))

    pprint(tagged.timexes)

tulemusena väljastatakse ajaväljendid::

    [['Timex(eile, DATE, 2014-12-02, [timex_id=1])',
     'Timex(nüüd, DATE, PRESENT_REF, [timex_id=2])',
     'Timex(viie aasta, DURATION, P5Y, [timex_id=3])']

Eelmises näites kuupäevaks normaliseeritud väljendi *eile* kalendriline semantika sõltub kasutuskontekstist.
Selliste väljendite normaliseerimisel kasutatakse vaikimisi *dokumendi loomise ajana* (ehk siis "kõnehetkena") programmi käivitamise kuupäeva (eelmises näites oli selleks 3. detsember 2014).
Dokumendi loomise aja saab ka teksti analüüsil eraldi täpsustada, kasutades selleks argumendi `creation_date` määramist.
Nt võime eelneva näitelause analüüsil määrata "dokumendi loomise ajaks" 10. juuni 1995::

    import datetime

    # märgendame teise dokumendi loomise aja suhtes
    tagged = tagger(tagged, creation_date=datetime.datetime(1995, 6, 10))
    pprint(tagged.timexes)
    
    ['Timex(eile, DATE, 1995-06-09, [timex_id=1])',
     'Timex(nüüd, DATE, PRESENT_REF, [timex_id=2])',
     'Timex(viie aasta, DURATION, P5Y, [timex_id=3])']

Vaikimisi töötleb ajaväljendite tuvastaja kõiki sisendteksti lauseid eraldi, kuna selline töötlusviis on suhteliselt vähenõudlik mäluressurssi suhtes.
Samas seab see tulemustele ka teatud piirangud.
Esiteks, ajaväljendite identifikaatorid on unikaalsed ainult ühe lause piires, mitte kogu dokumendi piires, nagu nõuab TimeML raamistik.
Ja teiseks, teatud anafoorsete ajaväljendite (s.o ajaväljendite, mille semantika sõltub teistest ajaväljenditest) normaliseerimine jääb poolikuks, kuna selleks võib olla tarvis vaadata ka ajaväljendeid ümbritsevates lausetes.
Nende probleemide vältimiseks on võimalik kasutada lippu `process_as_whole`, mille sisselülitamisel analüüsitakse kogu sisendteksti tervikuna (mitte lause-lause haaval)::

    text = ''''3. detsembril 2014 oli näiteks ilus ilm. Aga kaks päeva varem jälle ei olnud.'''
    tagged = tagger(analyzer(tokenizer(text)), process_as_whole = True)
    
    pprint(tagged.timexes)
    
    ['Timex(3. detsembril 2014, DATE, 2014-12-03, [timex_id=t1])',
     'Timex(kaks päeva varem, DATE, 2014-12-01, [timex_id=t2])']

Suurte tekstide töötlemisel tasub silmas pidada, et selline töötlemisviis võib olla üsna nõudlik mäluressurssi suhtes.

Nagu eeltoodud näidetest võib näha, tuuakse vaikimisi ajaväljendi sõne-esituskujus välja neli väärtust: ajaväljendi fraas, tüüp (DATE, TIME, DURATION või SET), semantika esituskuju (TimeML-baseeruv *value*) ning ajaväljendi unikaalne identifikaator (*timex_id*).
Sõltuvalt ajaväljendi semantikast võib määratud olla teisigi atribuute, millele pääseb ligi *Timex* objekti väljade kaudu.
Näiteks, kui ajaväljendi semantika on arvutatud mingit teist ajaväljendit aluseks võttes (nagu eelmise näite anafoorne väljend *kaks päeva varem*), viitab atribuut `anchor_id` teise väljendi identifikaatorile::

    text = ''''3. detsembril 2014 oli näiteks ilus ilm. Aga kaks päeva varem jälle ei olnud.'''
    tagged = tagger(analyzer(tokenizer(text)), process_as_whole = True)

    for timex in tagged.timexes:
        print(timex, ' is anchored to timex:', timex.anchor_id )

tulemusena väljastatakse::

    'Timex(3. detsembril 2014, DATE, 2014-12-03, [timex_id=1])'  is anchored to timex: None
    'Timex(kaks päeva varem, DATE, 2014-12-01, [timex_id=2])'  is anchored to timex: 1

Rohkem informatsiooni kasutusel olevate atribuutide kohta leiab klassi :class:`estnltk.corpus.Timex` dokumentatsioonist.

Ajaväljendite tuvastaja leiab tekstist ka mõned sellised väljendid, mida on keeruline normaliseerida ning seetõttu jäävad ajaväljendi väljad *type* ja *value* määratlemata.
Vaikimisi selliseid ajaväljendid eemaldatakse väljundist, aga seda sätet on võimalik tühistada, käivitades tuvastaja argumendiga `remove_unnormalized_timexes=False`.
