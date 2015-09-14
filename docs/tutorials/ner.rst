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

Default models that come with Estnltk are good enough for basic tasks.
However, for more serious tasks, a custom NER model is crucial to guarantee better accuracy.

... content ...
