# Change Log


All notable changes to this project will be documented in this file.

# [1.6.5.5-beta] - 2020-04-16
A pre-release only for developers. The list of changes will be documented in the next full release.

# [1.6.5-beta] - 2019-12-06
## Changed

* Updated `Vabamorf`'s **binary lexicon** files: binary lexicons from Vabamorf's commit [7bed3f7
](https://github.com/Filosoft/vabamorf/tree/7bed3f743e3b505227e1413535d4d3407bee2bb5/dct/binary) (2019-10-15) are now used by default. The change improves lexical coverage of Vabamorf's analyser, and also adds proper analyses for some spoken language and slang words. However, the upgrade is not complete, as `Vabamorf` C++ source code in EstNLTK also needs to be updated. This remains a future work.

    * As `Vabamorf`'s source code was not upgraded along with  lexicons, there is a possibility that morphological analysis has a reduced quality in some situations. 
    If this hinders your work, you can also roll back to `Vabamorf`'s binary lexicons used in the previous version.
    Previous version's lexicons are also included inside EstNLTK's package and [this tutorial](https://github.com/estnltk/estnltk/blob/e0f5723e00017b8d964041c6fa01988f93fb08d4/tutorials/nlp_pipeline/B_06_morphological_analysis.ipynb) shows how to switch back to them (see the section _"Changing Vabamorf's binary lexicons"_);

    * Under the hood, the location and the loading logic of `Vabamorf`'s binary lexicons was also changed;

* Ambiguous analyses in the `morph_analysis` layer are no longer re-sorted. As a result, the ordering of ambiguous analyses should be the same as the ordering used in EstNLTK's versions prior 1.6.0_beta (e.g. ordering used in version 1.4.1). If required, `VabamorfTagger`'s the parameter `re_sort_analyses` can be used to switch re-sorting back on. **Note:** Regardless whether the re-sorting parameter is switched on or off, the ambiguous analyses in `VabamorfTagger`'s output **are not** ordered by likelihood / probability;

* Relocated tutorials `date_tagger.ipynb` and `MorphAnalyzedToken.ipynb`;
* Removed `MorphAnalysisRecordBasedRetagger` (this was a redundant branch of development, please use `AnnotationRewriter` or `SpanRewriter` instead);

* `PostMorphAnalysisTagger` no longer creates a pickle file (with number analysis fixes) on the run. Instead, the pickle file will be created during a newly introduced preinstall phase in `setup.py`;

## Added

* Attribute `normalized_text` to the `morph_analysis` layer. The attribute holds a string: the normalized word form or the surface word form that was used as a basis on generating the analysis. So, if there were  multiple normalized forms for a word in the `words` layer, you can examine, which of the normalized forms gave rise to which of the analysis. Related changes:

    * Layers `morph_extended` and `gt_morph_analysis` now also have the attribute `normalized_text`, because these layers are directly derived from the `morph_analysis` layer;

    * `PostMorphAnalysisTagger` now makes number analysis fixes and pronoun analysis removal only based on the `normalized_text` attribute of an  analysis. As a result, `PostMorphAnalysisTagger` no longer depends on the `words` and `sentences` layers.
    
    * `UserDictTagger` now overwrites analyses based on the  `normalized_text` attribute of an analysis. As a result, `UserDictTagger` no longer depends on the `words` layer. Note: if the user dictionary does not specify `normalized_text` values, then (by default) attribute's value will be `None` after overwriting. 

* `MorphAnalysisReorderer` -- a tool which can be used for re-ordering ambiguous analyses in `morph_analysis` layer in a way that the first analysis is more likely the correct one. The tool can be applied as a post-processer after applying `VabamorfTagger` or `VabamorfCorpusTagger`. See [this tutorial](https://github.com/estnltk/estnltk/blob/327bb7c06975df97f6362ca01d5768be40bc794b/tutorials/nlp_pipeline/B_07c_morph_analysis_reordering.ipynb) for details.

* Method `save_as_csv()` to `UserDictTagger` -- can be used for saving the content of the dictionary as a csv format file.

* `SubstringQuery`

## Fixed

 * `HfstEstMorphAnalyser`'s 'morphemes_lemmas' output format: fixed part-of-speech parsing for punctuation and abbreviations;
 * `estnltk.core.abs_path` is now used instead of `estnltk.core.rel_path` for defining paths to EstNLTK's resources. This should fix problems on the Windows platform where relative paths do not exist if the EstNLTK is installed on one drive, and the code using EstNLTK is executed from another drive; 
 * `ConllMorphTagger`: A Linux-specific hardcoded `vislcg_path` was removed so that `ConllMorphTagger` can also be used on Windows;
 * `CorpusBasedMorphDisambiguator`: the `predisambiguate` method should now be able to distinguish between sentence-initial and sentence-central proper name candidates even iff there is a quotation mark or an ordinal number before the proper name candidate at the beginning of the sentence;
 * `test_old_neural_morf_tagger.py` and `test_conll_exporter/importer.py` will skip gracefully if their requirement packages are not installed;



# [1.6.4-beta] - 2019-09-16
## Changed

* Removed AmbiguousSpan. Span and EnvelopingSpan act as ambiguous or not ambiguous spans depending on the `ambiguous` 
attribute value of the layer they belong to. Every span now has its base span whitch represents its location on the raw 
text and can be used as an index to retrive spans from layers. Also, every span has its own list of annotations where annotation data is stored. No annotation data is stored as an attribute value of a span.

* Resolving of layer/span attributes is rewritten and now works similarily but not exactly as before.

* The default dict representation of a layer is now independent of the layer type (ambiguous, enveloping, parent).

* The new dict representation is also used when storing texts in the PgStrorage collections. Old Postgres databases might not work.

* Converted `VabamorfAnalyzer` and `VabamorfTagger` from `TaggerOld` to `Tagger`. As a result, exact parameters of the morphological analysis (`propername`, `guess`, `compound`, `phonetic`) must be specified at the initialization of `VabamorfAnalyzer`, and cannot be changed afterwards while running `VabamorfAnalyzer`. Also, `VabamorfAnalyzer` and `VabamorfTagger` no longer accept unspecified set of parameters (`**kwargs`) in their constructors;

* Relocated `RobustDateNumberTagger`, `AddressPartTagger`, `AddressGrammarTagger`, `AdjectivePhraseTagger`, `SentenceFleschScoreRetagger` from `estnltk.taggers.standard_taggers` to `estnltk.taggers.miscellaneous`;

* Relocated `MorphAnalyzedToken` from `estnltk.rewriting.helpers` to `estnltk.taggers.morph_analysis.proxy`;

* Removed `VabamorfCorrectionRewriter`, and carried over its functionalities to `PostMorphAnalysisTagger`. Flags `fix_number_analyses_using_rules` and `remove_broken_pronoun_analyses` can now be used in `PostMorphAnalysisTagger` to switch the functionalities on/off;


* Made the `'words'` layer ambiguous. `VabamorfAnalyzer` and `HfstEstMorphAnalyser` now provide analyses for every normalized word form in the `'words'` layer. `PostMorphAnalysisTagger` and `UserDictTagger` can overwrite analyses in the context of word normalization ambiguities. However, `VabamorfDisambiguator` has not been fully tested on multiple normalized word forms, and its performance is not guaranteed in such settings. So, we suggest to use multiple normalized forms only with the morphological analyzer, and keep ambiguities minimal if (Vabamorf's) disambiguation needs to be applied. For more details, see [this tutorial](https://github.com/estnltk/estnltk/blob/5541c1a18a4277debdc50f50a997d1e555de6c20/tutorials/nlp_pipeline/B_03_segmentation_words.ipynb );
	 * Ambiguity of  `'words'` also affects `TimexTagger` and `ClauseSegmenter`, which now always pick the first normalized form in  every word (if normalized forms exist) for their input. This behaviour can be switched off by the parameter `use_normalized_word_form`;



## Removed 
* `TaggerOld`
* Layer rewriting functionality.
* `PhraseListTagger`
* `PronounTypeTagger`
* `LambdaAttribute`

## Added

 * Class `CorpusBasedMorphDisambiguator`, which provides text-based and corpus-based disambiguation for Vabamorf's morphological analysis. For details, see [this tutorial](https://github.com/estnltk/estnltk/blob/5541c1a18a4277debdc50f50a997d1e555de6c20/tutorials/nlp_pipeline/B_07b_morph_analysis_with_corpus-based_disambiguation.ipynb);
 	* added experimental parameters to `CorpusBasedMorphDisambiguator`:
	 	* `count_position_duplicates_once` -- if set, then lemma duplicates  appearing in analyses of a word will be only counted once during the post-           disambiguation;
	 	* `count_inside_compounds` -- if set, then additional lemma counts will be obtained from the last words of compound words during the post-disambiguation;

 * `VabamorfCorpusTagger` -- a tool that combines functionalities of `VabamorfTagger` and `CorpusBasedMorphDisambiguator`, and provides full  morphological analysis and disambiguation for a collection of `Text` objects. For usage details, see [this tutorial](https://github.com/estnltk/estnltk/blob/5541c1a18a4277debdc50f50a997d1e555de6c20/tutorials/nlp_pipeline/B_07b_morph_analysis_with_corpus-based_disambiguation.ipynb);
 * Updated `VabamorfTagger`: added parameter `vm_instance`, which can be used to change the instance of `Vabamorf` used by the tagger. This can be useful when you need to change `Vabamorf`'s binary lexicons inside the `VabamorfTagger`. See [this tutorial](https://github.com/estnltk/estnltk/blob/5541c1a18a4277debdc50f50a997d1e555de6c20/tutorials/nlp_pipeline/B_06_morphological_analysis.ipynb) f0r details;

 * `VerbChainDetector` -- a tagger which identifies main verbs and their extensions (verb chains) in clauses. The implementation uses the source code ported from the EstNLTK version 1.4.1.1. For usage details, see [this tutorial](https://github.com/estnltk/estnltk/blob/5541c1a18a4277debdc50f50a997d1e555de6c20/tutorials/taggers/verb_chain_detector.ipynb);

 * Updated `SentenceTokenizer`: added sentence boundary corrections that are based on counting quotation marks in the whole text. Note that these corrections are switched off by default, but they can be switched on with the flag `fix_double_quotes_based_on_counts`. For details, see [this tutorial](https://github.com/estnltk/estnltk/blob/5541c1a18a4277debdc50f50a997d1e555de6c20/tutorials/nlp_pipeline/B_04_segmentation_sentences.ipynb);

 * Function `conll_to_texts_list` which can be used to import a list of `Text` objects from a single `.conllu` file. This can be useful if you need to load documents separately from `.conllu` files of [the UD Estonian corpus](https://github.com/UniversalDependencies/UD_Estonian-EDT); 

## Fixed

 * `CompoundTokenTagger`'s rules: 
   * improved detection of short web addresses;
   * improved normalization of numbers containing a period;
 * `CompoundTokenTagger`'s logic: 
   * abbreviations that overlap with hyphenations can be detected without running into an error;
   * tokens consisting of repeated hyphens will be compounded to words; 
 * `SentenceTokenizer`'s rules: improved detection of sentence endings after prolonged punctuation;
 * `PostMorphAnalysisTagger`'s rules for fixing number analyses: preserve hyphens at the start and end of a lemma; 
 * `MorphAnalyzedToken`: a hyphen at the end of a word will not be removed during token normalization (to preserve marker of a halved word);



# [1.6.3-beta] - 2019-05-10
## Changed
 * EstNLTK core classes `Span`, `AmbiguousSpan`, `EnvelopingSpan`, `Layer`, `Text`, `SpanList`, `Annotation` are under reconstruction. The easiest and recommended way of adding spans and annotations to layers is the `Layer.add_annotation` method.
 * Major refactoring in Koondkorpus processing module (`parse_koondkorpus.py`): A) during the reconstruction of text strings, you can now change the default paragraph and sentence separators, B) reconstruction of the tokenization layers can now be made independently of the concrete paragraph and sentence separators present in the text string; C) `reconstruct_text` now also creates layers 'tokens' and 'compound_tokens' (to enable morph analysis); D) a custom prefix can now be added to names of original tokenization layers, E) XML content can be loaded from the zipped files, F) Text objects can be reconstructed from a string content;
 * Improved `Tagger`, the abstract base class for taggers.
 * Made `Retagger` as a subclass of `Tagger`, and introduced span consistency checks that take place after retagging of a layer;
 * Converted the following taggers to `Retagger`: `UserDictTagger`, `PostMorphAnalysisTagger`, `VabamorfDisambiguator`;
 * Converted the following taggers from `TaggerOld` to `Tagger`: `TokensTagger`, `WordTagger`, `SentenceTokenizer`, `ClauseSegmenter`, `GTMorphConverter`, `SyntaxIgnoreTagger`, `TimexTagger`. Also, input layer  names are now changeable in `CompoundTokenTagger`, `WordTagger`, `ParagraphTokenizer`, `SentenceTokenizer`, `PostMorphAnalysisTagger`, `PostMorphAnalysisTagger`, `UserDictTagger`, `VabamorfTagger` (and in its subtaggers), `ClauseSegmenter`, `GTMorphConverter`, `SyntaxIgnoreTagger`, `TimexTagger`;
 * Java-based taggers (`ClauseSegmenter` and `TimexTagger`) can now be used as context managers, which ensures that the corresponding Java processes will be properly terminated after the `with` statement. Alternatively,  now they also have the `close()` method, which can be used for manually terminating the process if the tagger is no longer needed; 
 * EstNLTK's `Vabamorf` extension now uses Python proxy classes in order to avoid a [conflict](https://github.com/estnltk/estnltk/blob/eca541f64d29a633ef0dcefbba3ca445bde0d4e3/dev_documentation/hfst_integration_problems/solving_stringvector_segfault.md) with the [hfst](https://pypi.org/project/hfst) package. This has a small effect on processing speed, see [this evaluation report](https://github.com/estnltk/estnltk/blob/0aaf0b43d10ea5fcf4888618a6dafeb4f3e9fae2/dev_documentation/vabamorf_benchmarking/vabamorf_speed_benchmarking.md) for details;
 * Taggers: `SpanTagger`, `PhraseTagger`, `RegexTagger`, `GrammarParsingTagger`, `AddressTagger`, `AddressPartTagger`, `DiffTagger`, `GapsTagger`, `CombinedTagger`, `VabamorphTagger`, `SentenceTokenizer`
 * `Vocabulary` class for dict taggers.
 * Improved storage of EstNLTK objects in PostgreSQL database.

## Added
 * `TimexTagger` -- a tool which can be used to detect and normalize time expressions. Initial source of the `TimexTagger` was ported from the version 1.4.1. For details on the usage, see [this tutorial](https://github.com/estnltk/estnltk/blob/0aaf0b43d10ea5fcf4888618a6dafeb4f3e9fae2/tutorials/taggers/temporal_expression_tagger.ipynb). _Note_: in order to run the tool with EstNLTK, Java SE Runtime Environment must be installed into the system and available from the PATH environment variable. Improvements in `TimexTagger` (compared to the version 1.4.1):
 	* added a possibility to use custom rules. Upon the initialization of `TimexTagger`, user can now specify from which XML file the tagging rules will be loaded;
 	* document creation time can now also be specified as an ISO date string, and there can be gaps in the creation time (an experimental feature);
 	* improved `TimexTagger`'s default rules: rules for absolute date detection now take account the tokenization specifics of EstNLTK v1.6;
 	* changed annotation format: implicit timexes ("timexes without textual content") were removed from the layer `timexes`, and attributes `begin_point`, `end_point` and (a newly introduced attribute) `part_of_interval` now contain these timexes (represented as `OrderedDict`-s);     

 * `WhiteSpaceTokensTagger` (can be used for restoring the original tokenization of a pretokenized corpus);
 * `PretokenizedTextCompoundTokensTagger` (can be used for restoring the original tokenization of a pretokenized corpus);
 * `parse_ettenten.py` module  that encapsulates the logic of importing Texts from the [etTenTen 2013](https://metashare.ut.ee/repository/browse/ettenten-korpus-toortekst/b564ca760de111e6a6e4005056b4002419cacec839ad4b7a93c3f7c45a97c55f) corpus. In addition to importing the whole corpus, you can now also load specific documents by their `id`-s;
 * `parse_enc2017.py` module  that can be used for importing Texts from files of the [Estonian National Corpus 2017](https://metashare.ut.ee/repository/browse/estonian-national-corpus-2017/b616ceda30ce11e8a6e4005056b40024880158b577154c01bd3d3fcfc9b762b3/). Texts can loaded with original tokenization or with estnltk's tokenization; original morphological analyses from the file can also be restored as a layer. Importing Texts can be restricted to documents with specific ids, documents from specific sources (e.g. a Web Corpus, or Estonian Wikipedia), and documents in specific language. See [this tutorial](https://github.com/estnltk/estnltk/blob/0aaf0b43d10ea5fcf4888618a6dafeb4f3e9fae2/tutorials/importing_text_objects_from_corpora.ipynb) for further details;
 * `HfstEstMorphAnalyser` which can be used to perform morphological analysis with the help of [HFST-based analyser of Estonian](https://victorio.uit.no/langtech/trunk/experiment-langs/est/). This also introduces a new dependency: the library [hfst](https://pypi.org/project/hfst) must be installed before the analyser can be used. See [this tutorial](https://github.com/estnltk/estnltk/blob/0aaf0b43d10ea5fcf4888618a6dafeb4f3e9fae2/tutorials/hfst/morph_analysis_with_hfst_analyser.ipynb) for further details;
 * `SyntaxLasTagger`
 * `SyntaxDependencyRetagger`
 * `ConllMorphTagger`
 * `SegmentTagger`
 * `VislTagger`
 * `NeuralMorphTagger`
 * `SentenceFleschScoreRetagger`
 * `FlattenTagger`
 * `TextaExporter`
 * importers from `conll` fromat: `conll_to_text`, `add_layer_from_conll`
 * visulisation module for colorful dispaly of layers and attributes
 * `DiffSampler` class for iterating over diff layer (the output layer of `DiffTagger`)

Fixed
-----
 * Fixes in `CompoundTokenTagger`'s rules regarding to normalization of numbers ending with periods;
 * Fix in `CompoundTokenTagger`: compound tokens overlapping with paragraphs boundaries (`\n\n`) are now discarded by default. A new argument `do_not_join_on_strings` was added, specifying contexts, in which  compound tokens should not be created;
 * Fix in `SentenceTokenizer`: paragraph ending fixes now have priority over sentence merging fixes (so that sentences won't be mistakenly joined in places of paragraph boundaries);
 * More informative error message for situations when the Java is missing from the system and user attempts to use a Java-based tagger;



[1.6.2-beta] - 2018-04-16
=========================
Changed
-------
 * Moved command line scripts for processing etTenTen and koondkorpus from `estnltk/corpus_processing` to `corpus_processing`;
 * The command line scripts for processing etTenTen and koondkorpus were remade in a way that they both use the JSON format of the version 1.6 for storing intermediate results;
 * Restructured tutorials: `basic_nlp_toolchain.ipynb` was split into 7 separate tutorials and moved to `tutorials/nlp_pipeline`. Morphology and syntax-related tutorials were also move to `tutorials/nlp_pipeline`;
 * Indexing of `Text` and `Layer` objects.
 * Banned equal spans in not ambiguous layers.

Added
-----
* Functionality to store and query text objects in the Postgres database.
* Tagger `AddressGrammarTagger` to extract address information from text.
* Tutorial demonstrating how to extract addresses from text using `AddressGrammarTagger` and store results in the Postgres database (tutorials/postgres/storing_text_objects_in_postgres.ipynb).
* Module `parse_koondkorpus.py`, which can be used for loading texts from XML TEI files of the Estonian Reference Corpus as EstNLTK Text objects. The module was ported from the version 1.4.1.1 and improved upon. Improvements: default encoding is now 'utf-8', and there is a working option to preserve the original sentence and paragraph tokenization from the XML files;
* Tutorial about loading XML TEI files with EstNLTK;
* Added more helpful scripts for processing large corpora (a script for random selection and clean-up of files);
* Added AdjectivePhraseTagger (ported from version 1.4.1.1);
* DisambiguatingTagger to disambiguate ambiguous layers.
* EnvelopingSpan to replace SpanList in enveloping layers.
* Attribute lists to hold and represent attribute values extracted from layers.


[1.6.1-beta] - 2018-03-27
=========================
Changed
-------
* Redesigned Tagger base class. The deprecated TaggerOld is also in use so far.
* Moved morphology-related modules from `estnltk/taggers/` to `estnltk/taggers/morph/`;
* Moved functions that convert between Vabamorf dicts and EstNLTK's Spans to `estnltk/taggers/morph/morf_common.py`;
* Updated _make\_resolver_: default parameters for morphological analysis are now taken from `morf_common.py`;
* Updated SentenceTokenizer: _base\_sentence\_tokenizer_ is now customizable (e.g. [LineTokenizer](http://www.nltk.org/api/nltk.tokenize.html#nltk.tokenize.simple.LineTokenizer) can be used to split into sentences by newlines);


Added
-----
* Finite grammar module and GrammarParsingTagger.
* New taggers GapTagger, EnvelopingGapTagger, PhraseTagger, SpanTagger and vocabulary reading methods for PhraseTagger and SpanTagger.
* Added command line scripts that can be used for processing etTenTen and Koondkorpus;
* Added JavaProcess (ported from version 1.4.1.1);
* Added ClauseSegmenter (ported from version 1.4.1.1). Layer 'clauses' can now be added to the Text object. _Note_: this adds Java dependency to the EstNLTK: Java SE Runtime Environment (version >= 1.8) must be installed into the system and available from the PATH environment variable;
* Added UserDictTagger, which can be used to provide dictionary-based post-corrections to morphological analyses;

Fixed
-----
* Bugfix in PostMorphAnalysisTagger: postcorrections are no longer applied to empty spans;
* Bugfix in VabamorfTagger: _layer\_name_ can now be changed without running into errors;
* Fix in GTMorphConverter: added the missing disambiguation step. Clause annotations are now used to resolve the ambiguities related to conversion of _sid_, _ksid_, _nuksid_ forms;
* SyntaxIgnoreTagger: improved detection of parenthesized acronyms;
* CompoundTokenTagger: improved detection of numbers with percentages;


[1.6.0-beta] - 2017-12-23
=========================
EstNLTK has gone through a major redesign of the interface.
Changes include re-designing the interface of a basic data structure (the Text class), re-designing interfaces of analysis tools, up to the level of morphological analysis, and improving quality of basic text operations (such as sentence and word segmentation).

Changed
-------
* EstNLTK no longer supports Python 2.7. 
Recommended Python's version is 3.5;
* Text class has been redesigned. 
Text annotations are now decomposed into Span-s, SpanList-s and Layer-s;
* A common class for text annotators -- Tagger class -- has been introduced;
* Word segmentation has been redesigned. 
It is now a three-step process, which includes basic tokenization (layer 'tokens'), creation of compound tokens (layer 'compound\_tokens'), and creation of words (layer 'words') based on 'tokens' and 'compound\_tokens'.
Token compounding rules that are aware of text units containing punctuation (such as abbreviations, emoticons, web addresses) have been implemented;
* The segmentation order has been changed: word segmentation now comes before the sentence segmentation, and the paragraph segmentation comes after the sentence segmentation; 
* Sentence segmentation has been redesigned. 
Sentence segmenter is now aware of the compound tokens (fixing compound tokens can improve sentence segmentation results), and special post-correction steps are applied to improve quality of sentence segmentation;
* Morphological analysis interface has been redesigned.
Morphological analyses are no longer attached to the layer 'words' (although they can be easily accessed through the words, if needed), but are contained in a separate layer named 'morph_analysis'.
* Morphological analysis process can now more easily decomposed into analysis and disambiguation (using special taggers VabamorfAnalyzer and VabamorfDisambiguator).
Also, a tagger responsible for post-corrections of morphological analysis (PostMorphAnalysisTagger) has been introduced, and post-corrections for improving quality of part of speech, and quality of analysis of numbers and pronouns have been implemented;
* Rules for converting morphological analysis categories from Vabamorf's format to GT (giellatekno) format have been ported from the previous version of EstNLTK.
Note, however, that the porting is not complete: full functionality requires 'clauses' annotation (which is currently not available);
* ...
* Other components of EstNLTK (such as the temporal expression tagger, and the named entity recognizer) are yet to be ported to the new version in the future;

Added
-----
* SyntaxIgnoreTagger, which can be used for detecting parts of text that should be ignored by the syntactic analyser.
Note: it is yet to be integrated with the pre-processing module of syntactic analysis;



[1.4.0] - 2016-04-25
====================

Added
-----

* Support for parsing EstNLTK texts with Java-based Maltparser; Maltparser can be used for obtaining syntactic dependencies between words
* Experimental NP chunker for Estonian; The chunker picks up NP chunks from the output of Maltparser
* Disambiguator: added checking for input parameters;

Changed
-------

* VerbChainDetector: intervening punctuation is now ignored during the construction of regular verb chains. See "test_verbchain_3" in "test_verbchains.py" for a detailed example.
* Improved EstWordTokenizer: made it more aware of utf8 minus, dash and other hyphen-like symbols used instead of the regular hyphen symbol;

Fixed
-----

* Fix on https://github.com/estnltk/estnltk/issues/28 : unit-testing of Java components (with estnltk.run_tests) should now also work under Windows (tested on Windows 10 and with Python 3.4);
* Fix on https://github.com/estnltk/estnltk/issues/56 : improved word_tokenizer: now it should be more aware of mistakenly conjoined sentence endings and beginnings;
* Fix on https://github.com/estnltk/estnltk/issues/39 : verb chains are now annotated as multi-regions;
* Fix on https://github.com/estnltk/estnltk/issues/46 : added a hack solution which allows do to sentence tokenization based on the existing word tokenization;
*  Fixed a bug that caused some timex annotations to disappear after splitting the text into sentences;

