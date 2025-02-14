NLP components
============

This folder contains tutorials about EstNLTK's natural language processing (NLP) components. 
While many of the components are part of the default pipeline (callable via _default resolver_), some components are also stand-alone and need to be imported from specific paths.

* [introduction_to_nlp_pipeline.ipynb](../basics/introduction_to_nlp_pipeline.ipynb) gives an overview about how to use EstNLTK for basic text analysis: splitting text into tokens, words, sentences, and performing morphological analysis (including lemmatisation and part-of-speech tagging).

* [A_text_segmentation](A_text_segmentation/) tutorials give details about segmenting texts into tokens, compound tokens, words, sentences, paragraphs and clauses.

* [B_morphology](B_morphology/) tutorials describe morphological analysis tools (Vabamorf, text-based and corpus-based disambiguator, user dictionary tagger, UD and GT converters; HFST-based analyser; Bert-based morphological tagger and GliLem lemmatizer/disambiguator), morphological synthesis, spelling correction, stemming, compound word detection and syllabification.

* [C_syntax](C_syntax/) tutorials give information about preprocessing for syntactic analysis and syntactic analysers, available models and utilities for comparing and validating syntactic annotations.

* [D_information_extraction](D_information_extraction/) tutorials describe how to extract addresses, named entities, temporal expressions from texts, and how to resolve pronominal coreference.

* [E_embeddings](E_embeddings/) tutorials describe pre-trained language models / embeddings available for Estonian.

* [F_annotation_consistency](F_annotation_consistency/) tutorials describe tools for detecting inconsistencies between different linguistic annotations and for repairing annotations;

* [X_miscellaneous](X_miscellaneous/) and experimental language analysers: verb chain detector, noun phrase chunker, classifying oblique phrases into times and locations, lexicon-based tagging of PropBank semantic roles, date and number taggers for medical texts, adjective phrase tagger and Flesch reading ease score tagger.


