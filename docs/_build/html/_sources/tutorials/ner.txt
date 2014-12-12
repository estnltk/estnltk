========================
Named entity recognition
========================

Named-entity recognition (NER) (also known as entity identification, entity chunking and entity extraction) is a subtask of information extraction that seeks to locate
and classify elements in text into pre-defined categories such as the names of persons, organizations, locations.

The `estnltk` package should contain pretrained models for NE tagging with Python 2.7/Python 3.4.
However, if required, the model can also trained (or retrained) by invoking the command::

    python -m estnltk.ner train_default_model

This will build the default model tuned for named entity recognition in news articles.

In order to use named entity tagging, the input text needs to be tokenized and morphologically analyzed first.
A quick example, how to do it::

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

    # tag the documents
    ner_tagged = tagger(analyzer(tokenizer(text)))

    # print the words and their explicit labels in BIO notation
    pprint(list(zip(ner_tagged.word_texts, ner_tagged.labels)))
    

As a result, we see the list of words with annotated labels::

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

Named entity tags are encoded using a widely accepted BIO annotation scheme, where each label is prefixed with B or I, or the entire label is given as O.
**B-** denotes the *beginning* and **I-** *inside* of an entity, while **O** means *omitted*.
This can be used to detect entities that consist of more than a single word as can be seen in above example.

It is also possible to query directly :class:`estnltk.corpus.NamedEntity` objects from tagged corpora.
This makes it easy to see all words that are grouped into a named entity::

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

See :class:`estnltk.corpus.NamedEntity` documentation for information on available properties.
