========================
Nimeüksuste tuvastamine
========================

Nimeüksuste tuvastamine on info ekstraheerimise alamülesanne, mille käigus tuvastatakse ja klassifitseeritakse tekstis leiduvad nimed, näiteks isikunimed, organisatsiooninimed, asukohanimed.

`Estnltk`-ga peaks tulema kaasa eeltreenitud nimeüksuste tuvastamise mudelid Python 2.7 ja Python 3 jaoks. 
Aga vajadusel on võimalik mudelid ka ise välja treenida, kasutades süsteemi käsurea käsku::

    python -m estnltk.ner train_default_model

Eeltoodud käsu täitmisel luuakse nn vaikemudel, mis on kohandatud nimeüksuste tuvastamiseks ajaleheartiklites.

Nimeüksuste tuvastamine eeldab, et sisendtekst on lausestatud ja sõnestatud (:class:`estnltk.tokenize.Tokenizer` abil) ning tekstil on sooritatud morfoloogiline analüüs (:class:`estnltk.morf.PyVabamorfAnalyzer` abil).
Näide nimeüksuste tuvastaja kasutamise kohta::

    from estnltk import Tokenizer, PyVabamorfAnalyzer, NerTagger
    from pprint import pprint

    tokenizer = Tokenizer()
    analyzer = PyVabamorfAnalyzer()
    tagger = NerTagger()

    text = '''Eesti Vabariik on riik Põhja-Euroopas. 
    Eesti piirneb põhjas üle Soome lahe Soome Vabariigiga.

    Riigikogu on Eesti Vabariigi parlament. Riigikogule kuulub Eestis seadusandlik võim.

    2005. aastal sai peaministriks Andrus Ansip, kes püsis sellel kohal 2014. aastani.
    2006. aastal valiti presidendiks Toomas Hendrik Ilves.
    '''

    # tuvastame nimeüksused
    ner_tagged = tagger(analyzer(tokenizer(text)))

    # väljastame sõnad ning nende BIO-märgendid
    pprint(list(zip(ner_tagged.word_texts, ner_tagged.labels)))
    

Tulemusena väljastatakse sõnad koos nimeüksuste märgendusega::

    [('Eesti', 'B-LOC'),
     ('Vabariik', 'I-LOC'),
     ('on', 'O'),
     ('riik', 'O'),
     ('Põhja-Euroopas.', 'B-LOC'),
     ('Eesti', 'B-LOC'),
     ('piirneb', 'O'),
     ('põhjas', 'O'),
     ('üle', 'O'),
     ('Soome', 'B-LOC'),
     ('lahe', 'I-LOC'),
     ('Soome', 'B-LOC'),
     ('Vabariigiga.', 'O'),
     ('Riigikogu', 'B-ORG'),
     ('on', 'O'),
     ('Eesti', 'B-LOC'),
     ('Vabariigi', 'I-LOC'),
     ('parlament.', 'O'),
     ('Riigikogule', 'B-ORG'),
     ('kuulub', 'O'),
     ('Eestis', 'B-LOC'),
     ('seadusandlik', 'O'),
     ('võim.', 'O'),
     ('2005.', 'O'),
     ('aastal', 'O'),
     ('sai', 'O'),
     ('peaministriks', 'O'),
     ('Andrus', 'B-PER'),
     ('Ansip', 'I-PER'),
     (',', 'O'),
     ('kes', 'O'),
     ('püsis', 'O'),
     ('sellel', 'O'),
     ('kohal', 'O'),
     ('2014.', 'O'),
     ('aastani.', 'O'),
     ('2006.', 'O'),
     ('aastal', 'O'),
     ('valiti', 'O'),
     ('presidendiks', 'O'),
     ('Toomas', 'B-PER'),
     ('Hendrik', 'I-PER'),
     ('Ilves.', 'I-PER')]

Nimeüksuste märgendus järgib BIO-märgendusviisi, mille järgi kodeeritakse fraaside tekstis esinemine/ mitteesinemine märgenditega B, I ja O.
**B-** tähistab nimeüksuse fraasi alguses paiknevat sõna (ingl *beginning*), **I-** fraasi sees paiknevat sõna  (ingl *inside*) ning **O** tähistab fraasist väljajäävat sõna (ingl *omitted*).

Lisaks on võimalik tuvastatud nimeüksustele (:class:`estnltk.corpus.NamedEntity` objektidele) ka otse ligi pääseda, kasutades märgendatud dokumendi küljes olevat välja ``named_entities``.
See võimaldab nimeüksusi käsitleda terviklike fraasidena::

    pprint (ner_tagged.named_entities)
    
    ['NamedEntity(eesti vabariik, LOC)',
     'NamedEntity(põhja-euroopa, LOC)',
     'NamedEntity(eesti, LOC)',
     'NamedEntity(soome lahe, LOC)',
     'NamedEntity(soome, LOC)',
     'NamedEntity(riigikogu, ORG)',
     'NamedEntity(eesti vabariik, LOC)',
     'NamedEntity(riigikogu, ORG)',
     'NamedEntity(eesti, LOC)',
     'NamedEntity(andrus ansip, PER)',
     'NamedEntity(toomas hendrik ilves, PER)']

Klassi :class:`estnltk.corpus.NamedEntity` dokumentatsioonist leiab täpsemat informatsiooni selle väljade kohta.
