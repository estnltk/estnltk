========================
Named entity recognition
========================

Named-entity recognition (NER) (also known as entity identification, entity chunking and entity extraction) is a subtask of information extraction that seeks to locate and classify elements in text into pre-defined categories such as the names of persons, organizations, locations.

In this tutorial you will learn how to use `estnltk`'s out of the box NER utilities and how to build your own ner-models from scratch.


Getting started with NER
========================

The `estnltk` package comes with the pre-trained NER-models for Python 2.7/Python 3.4. The models distinguish 3 types of entities: person names, organizations and locations.

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
  
::

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
  

When accessing the property :py:attr:`~estnltk.text.Text.named_entities` of the :py:class:`~estnltk.text.Text` instance, `estnltk` executes on the background the whole text processing pipeline, including tokenization, morphological analysis and named entity extraction.

The class :class:`~estnltk.text.Text` additionally provides a number of useful methods to get more information on the extracted entities::
  
  pprint(list(zip(text.named_entities, text.named_entity_labels, text.named_entity_spans)))
  
::

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


The default models use tags PER, ORG and LOC to denote person names, organizations and locations respectively. Entity tags are encoded using a BIO annotation scheme, where each entity label is prefixed with either B or I letter. B- denotes the beginning and I- inside of an entity. The prefixes are used to detect multiword entities, as shown in the example example above. All other words, which don't refer to entities of interest, are labelled with the O tag. 

The raw labels are accessible via the property :py:attr:`~estnltk.text.Text.labels` of the :py:attr:`~estnltk.text.Text` instance::

  pprint(list(zip(text.word_texts, text.labels)))

::

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


Advanced NER
============

Training custom models
----------------------

Default models that come with `estnltk` are good enough for basic tasks. However, for some specific tasks, a custom NER model might be needed. To train your own model, you need to provide a training corpus and custom configuration settings.  The following example demonstrates how to train a ner-model using the default training dataset and settings::

  from estnltk.corpus import read_json_corpus 
  from estnltk.ner import NerTrainer
  
  # Read the default training corpus
  corpus = read_json_corpus('/home/projects/estnltk/estnltk/corpora/estner.json')
  
  # Read the default settings
  ner_settings = estnltk.estner.settings
  
  # Directory to save the model
  model_dir = '<output model directory>'
  
  # Train and save the model
  trainer = NerTrainer(ner_settings)
  trainer.train(corpus, model_dir)
  

The specified output directory will contain a resulting model file `model.bin` and a copy of a settings module used for training. Now we can load the model and tag some text using :py:class:`~estnltk.ner.NerTagger`::

  from estnltk.ner import NerTagger
  
  document = Text(u'Eesti koeraspordiliidu ( EKL ) presidendi Piret Laanetu intervjuu Eesti Päevalehele.')
  
  # Load the model and settings
  tagger = NerTagger(model_dir)
  
  # ne-tag the document
  tagger.tag_document(document)
  
  pprint(list(zip(document.word_texts, document.labels)))
  
::

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
----------------
To train a model with `estnltk`, you need to provide your training data in a certain format (see the default dataset `estnltk/estnltk/corpora/estner.json` for example). The training file contains one document per line along with ne-labels. Let's create a simple document::
  
  text = Text('''Eesti Vabariik on riik Põhja-Euroopas.''')
  text.tokenize_words()
  pprint(text)

::

  {'paragraphs': [{'end': 38, 'start': 0}],
  'sentences': [{'end': 38, 'start': 0}],
  'text': 'Eesti Vabariik on riik Põhja-Euroopas.',
  'words': [{'end': 5, 'start': 0,  'text': 'Eesti'},
           {'end': 14, 'start': 6,  'text': 'Vabariik'},
           {'end': 17, 'start': 15, 'text': 'on'},
           {'end': 22, 'start': 18, 'text': 'riik'},
           {'end': 28, 'start': 23, 'text': 'Põhja'},
           {'end': 29, 'start': 28, 'text': '-'},
           {'end': 37, 'start': 29, 'text': 'Euroopas'},
           {'end': 38, 'start': 37, 'text': '.'}]}

Next, let's add named entity tags to each word in the document::
   
  words = text.words
  
  # label each word as "other":
  for word in words:
    word['label'] = 'O'
    
  # label words "Eesti Vabariik" as a location
  words[0]['label'] = 'B-LOC'
  words[1]['label'] = 'I-LOC'
  
  # label words "Põhja-Euroopas" as a location
  words[4]['label'] = 'B-LOC'
  words[5]['label'] = 'I-LOC'
  words[6]['label'] = 'I-LOC'
  
  pprint(text.words)

::

    [{'end': 5, 'label': 'B-LOC', 'start': 0, 'text': 'Eesti'},
     {'end': 14, 'label': 'I-LOC', 'start': 6, 'text': 'Vabariik'},
     {'end': 17, 'label': 'O', 'start': 15, 'text': 'on'},
     {'end': 22, 'label': 'O', 'start': 18, 'text': 'riik'},
     {'end': 28, 'label': 'B-LOC', 'start': 23, 'text': 'Põhja'},
     {'end': 29, 'label': 'I-LOc', 'start': 28, 'text': '-'},
     {'end': 37, 'label': 'I-LOc', 'start': 29, 'text': 'Euroopas'},
     {'end': 38, 'label': 'O', 'start': 37, 'text': '.'}]


Once we have a collection of labelled documents, we can save it to disc using the function :py:func:`estnltk.corpus.write_json_corpus`::

  from estnltk.corpus import write_json_corpus
  
  documents = [text]
  write_json_corpus(documents, '<output file name>')

  
This serializes each document object into a json string and saves to the specified file line by line. The resulting training file can be used with the :py:class:`~estnltk.ner.NerTrainer` as shown above. 


Ner settings
-------------
By default, `estnltk` uses configuration module :mod:`estnltk.estner.settings`. A settings module defines training algorithm parameters, entity categories, feature extractors and feature templates. The simplest way to create a custom configuration is to make a new settings module, e.g. `custom_settings.py`, import the default settings and override necessary parts. For example, a custom minimalistic configuration module could look like this::

    from estnltk.estner.settings import *

    # Override feature templates
    TEMPLATES = [
        (('lem', 0),),
    ]
    
    # Override feature extractors
    FEATURE_EXTRACTORS = (
        "estnltk.estner.featureextraction.MorphFeatureExtractor",
    )

Now, the :class:`estnltk.ner.NerTrainer` instance can be initialized using the `custom_settings` module (make sure `custom_settings.py` is on your python path)::

  trainer = NerTrainer(custom_settings)  
