# EstNLTK's tutorials 

---

Updating and reorganizing tutorials is currently work-in-progress. There can be broken or misleading links in tutorials, and some cross-references may be incorrect. Some of the tutorials may be reorganized and relocated. We hope to finish the updating as soon as possible. 

---


* Basics of EstNLTK:
    * Introduction to the basic NLP pipeline and morphological tagging:  [introduction_to_nlp_pipeline.ipynb](nlp_pipeline/introduction_to_nlp_pipeline.ipynb)

    * Introduction to EstNLTK's programming interface and data structures: [basics_of_estnltk.ipynb](basics_of_estnltk.ipynb)
     
    * EstNLTK's resources (downloading models required by taggers): [estnltk_resources.ipynb](estnltk_resources.ipynb) 

* NLP components:
    
    * [text_segmentation](nlp_pipeline/A_text_segmentation) -- taggers for splitting text into tokens, words, sentences, paragraphs and clauses;
    
    * [morphological processing](nlp_pipeline/B_morphology) -- morphological analysis, disambiguation and synthesis; spelling correction and syllabification;

    * [syntactic analysis](nlp_pipeline/C_syntax) -- preprocessing for syntax and syntactic analysers; available models; utilities for comparing and validating syntactic annotations;

    * [information extraction](nlp_pipeline/D_information_extraction): tools for extracting addresses, named entities and temporal expressions from texts;
   
    * [embeddings](nlp_pipeline/E_embeddings): EstNLTK's pretrained language models. 

    * [web taggers](taggers/web_taggers/web_taggers.ipynb): EstNLTK's taggers that are available (or can be made available) as web services.

    * [miscellaneous language analysers and experimental tools](nlp_pipeline/X_miscellaneous): verb chain detector, noun phrase chunker, date and number taggers for medical texts,  adjective phrase tagger and Flesch reading ease score tagger.

    * [Estonian WordNet API](wordnet/wordnet.ipynb)
 
    * [Collocation-Net](collocation_net/tutorial.ipynb) 
  
* Importing texts from large Estonian corpora: [importing_text_objects_from_corpora.ipynb](corpus_processing/importing_text_objects_from_corpora.ipynb)
    
    * Importing pretokenized text while keeping the original tokenization: [restoring_pretokenized_text.ipynb](corpus_processing/restoring_pretokenized_text.ipynb).

* Working with different input/output formats:

    * [converters](converters) -- functions for converting between EstNLTK's data structures and other data formats (such as JSON or CONLL); saving and loading annotated texts.

* Using Postgres database for storing/retrieving texts: ( [storage](storage) )

    * Basics of database access and storage: [storage/storing_text_objects_in_postgres.ipynb](storage/storing_text_objects_in_postgres.ipynb)

* System taggers and tools for rule-based language engineering:

    * [rule_taggers](taggers/rule_taggers) -- Rule based taggers for text annotation using regular experssions, word listings and phrase patterns;

    * [finite_grammar](taggers/finite_grammar) -- grammar based fact extraction taggers;

    * [system taggers](taggers/system) for comparing, manipulating and merging annotation layers, and for testing taggers;

* Making your own taggers and retaggers:

    * How to create annotation layers: [low_level_layer_operations.ipynb](system/low_level_layer_operations.ipynb)
    
    * How to create a tagger / retagger: [base_tagger.ipynb](taggers/base_tagger.ipynb)

* [layer_operations](system/layer_operations.ipynb) -- extract, split or join layers; flatten layer; group spans or annotations of a layer;

* How to visualise annotations: ( [visualisation](visualisation) )