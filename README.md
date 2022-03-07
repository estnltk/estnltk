## EstNLTK v1.6 packages

* [estnltk-core](estnltk_core) -- package containing core components of the EstNLTK v1.6 library:
	* data structures: BaseText, BaseLayer, Layer, Span, EnvelopingSpan, SpanList, Annotation;
	* tagger component interfaces: Tagger, Retagger;
	* basic layer operations: flatten, merge, rebase, split layers etc.
	* basic visualization and Jupyter Notebook support (HTML representations);
	* functions for converting between EstNLTK's data structures and JSON/dict representations;
	* Skeleton for NLP pipeline (components for resolving layer dependencies and tagging layers sequentially);
* [estnltk](estnltk) -- package containing basic linguistic analysis, system and database tools:
	* Text class with the Estonian NLP pipeline;   
	* tokenization tools: word, sentence and paragraph tokenization; clause segmentation; 
	* morphology tools: morphological analysis and disambiguation, spelling correction, morphological synthesis and syllabification, HFST based analyser and GT converter;
	* information extraction tools: named entity recognizer, temporal expression tagger, verb chain detector, address tagger, adjective phrase tagger, phrase tagger and grammar based fact extraction;
	* syntactic analysis tools: preprocessing for syntactic analysis, VislCG3 and Maltparser based syntactic parsers;
	* Estonian Wordnet;
    * web taggers -- such as bert embeddings web tagger, stanza syntax web tagger and stanza ensemble syntax web tagger;
	* corpus importing tools -- tools for importing data from large Estonian corpora, such as the Reference Corpus or  the National Corpus of Estonia; 
	* system taggers -- regex tagger, disambiguator, atomizer, merge tagger etc;
	* Postgres database tools;
* [estnltk-neural](estnltk_neural) -- package containing linguistic analysis based on neural models:
	* neural morphological tagger, bert embeddings tagger, stanza syntax tagger and stanza ensemble syntax tagger;

