========================
Named entity recognition
========================

Named-entity recognition (NER) (also known as entity identification, entity chunking and entity extraction) is a subtask of information extraction that seeks to locate and classify elements in text into pre-defined categories such as the names of persons, organizations, locations.

The `estnltk` package comes with the pretrained NER-models for Python 2.7/Python 3.4.

A quick example of how to extract named entities from the raw text::

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
  

When calling `text.named_entities`, `estnltk` runs the whole text processing pileline on the background, including  tokenization, morphological analysis and named entity extraction.

The `Text` instance provides a number of useful methods to get more information on the extracted entities::
  
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


============
Advanced NER
============

--------------
Tagging scheme
--------------

The default models are trained to recognize names on people, organizations and locations respecivelly tagged as PER, ORG and LOC. Named entity tags are encoded using a widely accepted BIO annotation scheme, where each label is prefixed with B or I, or the entire label is given as O. B- denotes the beginning and I- inside of an entity, while O means omitted. 
  
Tokens with named entity labels::

  
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
======================


Default models that come with Estnltk are good enough for basic tasks.
However, for more serious tasks, a custom NER model is crucial to guarantee better accuracy.
::

  from estnltk.corpus import read_json_corpus 
  from estnltk.ner import NerTrainer
  
  # Read the corpus
  ds = read_json_corpus('projects/estnltk/estnltk/corpora/estner.json')
  
  # Read ner settings and initialize the trainer
  trainer = NerTrainer(estnltk.estner.settings)
  trainer.train(ds, '<output directory>')

Evaluation
==========
asdf

Serialization
=============

asdf
