Named entity recognition
========================

Named-entity recognition (NER) (also known as entity identification, entity chunking and entity extraction) is a subtask of information extraction that seeks to locate and classify elements in text into pre-defined categories such as the names of persons, organizations, locations.

The `estnltk` package comes with the pre-trained NER-models for Python 2.7/Python 3.4.

A quick example below demonstrates how to extract named entities from the raw text::

  from estnltk import Text
  
  text = Text('''Eesti Vabariik on riik Põhja-Euroopas. 
      Eesti piirneb põhjas üle Soome lahe Soome Vabariigiga.
      Riigikogu on Eesti Vabariigi parlament. Riigikogule kuulub Eestis seadusandlik võim.
      2005. aastal sai peaministriks Andrus Ansip, kes püsis sellel kohal 2014. aastani.
      2006. aastal valiti presidendiks Toomas Hendrik Ilves.
      ''')

  # Extract named entities
  pprint(text.named_entities)
  ['Eesti vabariik',
   'põhi',
   'Euroopa',
   'Eesti',
   'Soome laht',
   'Soome Vabariik',
   'Riigikogu',
   'Eesti vabariik',
   'riigikogu',
   'Eesti',
   'Andrus Ansip',
   'Toomas Hendrik Ilves']
  

When calling a property `text.named_entities`, `estnltk` executes on the background the whole text processing pipeline, including tokenization, morphological analysis and named entity extraction.

A class :class:`estnltk.text.Text` additionally provides a number of useful methods to get more information on the extracted entities::
  
  pprint(list(zip(text.named_entities, text.named_entity_labels, text.named_entity_spans)))
  [('Eesti vabariik', 'LOC', (0, 14)),
   ('Põhi Euroopa', 'LOC', (25, 37)),
   ('Eesti', 'LOC', (46, 51)),
   ('Soome laht', 'LOC', (71, 81)),
   ('Soome Vabariik', 'LOC', (82, 99)),
   ('Riigikogu', 'ORG', (107, 116)),
   ('Eesti vabariik', 'LOC', (120, 135)),
   ('riigikogu', 'ORG', (147, 158)),
   ('Eesti', 'LOC', (166, 172)),
   ('Andrus Ansip', 'PER', (229, 241)),
   ('Toomas Hendrik Ilves', 'PER', (320, 340))]


Advanced NER
============

Tagging scheme
--------------

The default models use tags PER, ORG and LOC to denote person names, organizations and locations respectively. Entity tags are encoded using a widely accepted BIO annotation scheme, where each label is prefixed with B or I, or the entire label is given as O. B- denotes the beginning and I- inside of an entity, while O means omitted. This can be used to detect multiword entities, as shown in the example example above. The raw labels are accessible via a property `labels` in a class :class:`estnltk.text.Text`::

  pprint(list(zip(text.word_texts, text.labels)))
  [('Eesti', 'B-LOC'),
   ('Vabariik', 'I-LOC'),
   ('on', 'O'),
   ('riik', 'O'),
   ('Põhja', 'B-ORG'),
   ('-', 'O'),
   ('Euroopas', 'B-LOC'),
   ('.', 'O'),
   ('Eesti', 'B-LOC'),
   ('piirneb', 'O'),
   ('põhjas', 'O'),
   ('üle', 'O'),
   ('Soome', 'B-LOC'),
   ('lahe', 'I-LOC'),
   ('Soome', 'B-LOC'),
   ('Vabariigiga', 'I-LOC'),
   ('.', 'O'),
   ('Riigikogu', 'B-ORG'),
   ('on', 'O'),
   ('Eesti', 'B-LOC'),
   ('Vabariigi', 'I-LOC'),
   ('parlament', 'O'),
   ('.', 'O'),
   ('Riigikogule', 'B-ORG'),
   ('kuulub', 'O'),
   ('Eestis', 'B-LOC'),
   ('seadusandlik', 'O'),
   ('võim', 'O'),
   ('.', 'O'),
   ('2005', 'O'),
   ('.', 'O'),
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
   ('2014', 'O'),
   ('.', 'O'),
   ('aastani', 'O'),
   ('.', 'O'),
   ('2006', 'O'),
   ('.', 'O'),
   ('aastal', 'O'),
   ('valiti', 'O'),
   ('presidendiks', 'O'),
   ('Toomas', 'B-PER'),
   ('Hendrik', 'I-PER'),
   ('Ilves', 'I-PER'),
   ('.', 'O')]



Training custom models
----------------------

Default models that come with `estnltk` are good enough for basic tasks. However, for some specific tasks, a custom NER model might be needed. To train a new model, you need to provide a training corpus and custom configuration settings. Training is done using a class :class:`estnltk.ner.NerTrainer`. The following example demonstrates how to train a model using a default training dataset `/home/projects/estnltk/estnltk/corpora/estner.json` and a settings module :mod:`estnltk.estner.settings`::

  from estnltk.corpus import read_json_corpus 
  from estnltk.ner import NerTrainer
  
  # Read the corpus
  corpus = read_json_corpus('/home/projects/estnltk/estnltk/corpora/estner.json')
  
  # Read ner settings
  ner_settings = estnltk.estner.settings
  
  # Direcrory to save the model
  model_dir = '<output model directory>'
  
  # Train and save the model
  trainer = NerTrainer(ner_settings)
  trainer.train(corpus, model_dir)
  

The specified output directory will contain the resulting model file `model.bin` and a copy of a settings module used for training. Now, this model can be used to ne-tag text using a class :class:`estnltk.ner.NerTagger`::

  from estnltk.ner import NerTagger
  
  document = Text(u'Eesti koeraspordiliidu ( EKL ) presidendi Piret Laanetu intervjuu Eesti Päevalehele.')
  
  # Load the model and settings
  tagger = NerTagger(model_dir)
  
  # ne-tag the document
  tagger.tag_document(document)
  
  pprint(list(zip(document.word_texts, document.labels)))
  [('Eesti', 'B-ORG'),
     ('koeraspordiliidu', 'I-ORG'),
     ('(', 'O'),
     ('EKL', 'B-ORG'),
     (')', 'O'),
     ('presidendi', 'O'),
     ('Piret', 'B-PER'),
     ('Laanetu', 'I-PER'),
     ('intervjuu', 'O'),
     ('Eesti', 'B-ORG'),
     ('Päevalehele', 'I-ORG'),
     ('.', 'O')]
  
  
Training dataset
--------------------
`Estnltk` includes a training dataset used to train original models in `estnltk/estnltk/corpora/estner.json`.


Ner settings
-------------
By default, `estnltk` uses configuration from a module :mod:`estnltk.estner.settings`. A settings module defines training algorithm parameters, entity categories, feature extractors and feature templates. The simplest way to create a custom configuration is to make a new settings module, e.g. `custom_settings.py`, import the default settings and override necessary parts. For example, a custom minimalistic configuration module could look like this::

    from estnltk.estner.settings import *

    # Override feature templates
    TEMPLATES = [
        (('lem', 0),),
    ]
    
    # Override feature extractors
    FEATURE_EXTRACTORS = (
        "estnltk.estner.featureextraction.MorphFeatureExtractor",
    )

Now, the :class:`estnltk.ner.NerTrainer` instance can be initialized using `custom_settings` module (make sure `custom_settings.py` is on python path)::

  trainer = NerTrainer(custom_settings)  
