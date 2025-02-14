# Change Log


All notable changes to this project will be documented in this file.

# [1.7.4] - 2025-01-22

## Changed

* Changed licensing: EstNLTK is now dual licensed: choose either [GNU General Public License v2.0](http://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html) or [Apache 2.0 License](http://www.apache.org/licenses/LICENSE-2.0). 
* Updated `resource_utils`: removed rudimentary version constraints checking; version constraints are now checked with the [packaging](https://packaging.pypa.io/) utility which is a new dependency of EstNLTK;
* Refactored `estnltk.vabamorf.morf` module:
	* Removed legacy `deconvert` function;
	* Removed legacy shortcut functions `analyze` and `disambiguate` (use `VabamorfInstance.analyze` and `VabamorfInstance.disambiguate`) instead;
* Changed `syllabify_word`: it now uses stem-based morph analysis for compound word splitting (removed rudimentary and error-prone compound word splitting heuristic);
* Changed `BertTokens2WordsRewriter`: it can now also create a sublayer of the words layer, mapping each word to corresponding Bert embeddings, and added a constructor parameter <code>ambiguous</code> to control whether the output layer is ambiguous or not. In case unambiguous output (the default setting), the decorator function is expected to assign a single annotation (dictionary) to each span of the output layer, otherwise, the decorator must return a list of annotations.
* Updated `EstBERTNERTagger`: added `device` argument for [switching between cpu and gpu in transformers pipeline](https://huggingface.co/transformers/v3.0.2/main_classes/pipelines.html#transformers.Pipeline);
* Remove `PropBankPreannotator`'s lexicon from the package and made it available as a downloadable resource; 
* Updated `PropBankPreannotator`: added flag `discard_overlapped_frames` for removing entirely overlapped frames; Note: this is a heuristic and not entirely unharmful. Removing overlapped frames can reduce redundant frames roughly 9 %pt, but with a cost of decreasing correct frame detection accuracy 0.3 %pt (based on measurements on EDT-UD corpus). For evaluation of `PropBankPreannotator`, see notebook [this repository](https://github.com/estnltk/estnltk-model-data/tree/main/propbank_sem_roles).

## Added

* Added stem-based morphological analysis (and disambiguation) option to Vabamorf instance. Modified `VabamorfTagger` & its sub-components: and added stem-based morph_analysis option (flag `stem`). See [this tutorial](https://github.com/estnltk/estnltk/blob/0886be3ecbc5548827e0a70e4cef0f1aa313798b/tutorials/nlp_pipeline/B_morphology/02_morphological_analysis_stem_based.ipynb) for details; 
	* Be aware that there is _no lemma_ in the output of stem-based morphological analysis. This is also hinders the usability of the stem-based analysis by other tools in EstNLTK, because most of the tools require lemma-based morphological analysis.
* Added `CompoundWordTagger` for tagging linguistic compound word/subword boundaries on words. Details in the [tutorial](https://github.com/estnltk/estnltk/blob/0886be3ecbc5548827e0a70e4cef0f1aa313798b/tutorials/nlp_pipeline/B_morphology/compound_word_detection.ipynb);
* Added [packaging](https://packaging.pypa.io/) dependency to `estnltk_core` & `estnltk` (this is required for checking versions of Python packages used by EstNLTK).
* Added `GrammarCorrectorWebTagger` which tags grammatical error correction suggestions via TartuNLP's ws, see details in [this tutorial](https://github.com/estnltk/estnltk/blob/179ea6865383a3a349195907fb85b1da01c96eba/tutorials/taggers/web_taggers/web_taggers.ipynb);
* Added `BertMorphTagger` which tags part-of-speech and morphological form features in Estonian texts using Vabamorf's tagset, leveraging a fine-tuned Bert model. The tagger can also be used as a disambiguator to resolve ambiguities of an existing morphological analysis layer that uses Vabamorf's tagset. For details, see [this tutorial](https://github.com/estnltk/estnltk/blob/752ec7276b891c5d754433286058f26f9c973e74/tutorials/nlp_pipeline/B_morphology/08_bert_based_morph_tagger.ipynb). Note that `BertMorphTagger` depends on [sentencepiece](https://pypi.org/project/sentencepiece/), which won't be installed automatically with `estnltk-neural`, but needs to be installed manually;
* Added `GliLemTagger` which enhances Vabamorf's lemmatizer with an external disambiguation module based on GliNER and can either improve the lemmatization accuracy or provide an alternative lemmatization. The tagger can also be used as a disambiguator to resolve lemma ambiguities of an existing morphological analysis layer. For details, see [this tutorial](https://github.com/estnltk/estnltk/blob/b074fefa6597df7d6981b7920ca19a3621afbc0d/tutorials/nlp_pipeline/B_morphology/08_glilem_lemmatizer_and_disambiguator.ipynb). Note that `GliLemTagger` depends on [gliner](https://pypi.org/project/gliner/), which won't be installed automatically with `estnltk-neural`, but needs to be installed manually;
* Added a tutorial about using [TimeLocTagger](https://github.com/estnltk/estnltk/blob/179ea6865383a3a349195907fb85b1da01c96eba/tutorials/nlp_pipeline/X_miscellaneous/03_time_and_location_adverbials.ipynb) -- an experimental tagger which can be used to classify oblique phrases into time and location adverbials;
* Added a tutorial about [PropBankPreannotator](https://github.com/estnltk/estnltk/blob/179ea6865383a3a349195907fb85b1da01c96eba/tutorials/nlp_pipeline/X_miscellaneous/04_propbank_semantic_roles_preannotation.ipynb), which tags Estonian PropBank semantic roles based on a (manually-crafted) lexicon; 
* Added `converters.label_studio` `PhraseTaggingTask` & `PhraseClassificationTask` for importing/exporting [Labelstudio](https://labelstud.io/) annotations. For usage details, see [this tutorial](https://github.com/estnltk/estnltk/blob/179ea6865383a3a349195907fb85b1da01c96eba/tutorials/converters/labelstudio_exporter_importer.ipynb).

## Fixed

* Bugfix in `conll_to_texts_list`;
* Fixed issue [#122](https://github.com/estnltk/estnltk/issues/122): `SentenceTokenizer`'s base tokenizer now uses resources from `"punkt_tab"` (so estnltk is now compatible with `nltk > 3.8.1`);
* Bugfix in `StanzaSyntaxTagger`: do not crash if the input is accidentially missing `'xpos'` (affects only `input_type='sentences'`);
* Fix in `resource_utils._normalize_resource_size`: resource sizes smaller than 1M will be normalized properly now; 


# [1.7.3] - 2024-06-10

## Changed

* Updated `BaseText`:
	* `BaseText.sorted_layers` covers both span layers and relation layers now. however, for backwards compatibility, it returns only sorted span layers by default. set flag `relation_layers=True` to include relation layers;
	* removed `BaseText.sorted_relation_layers`; 
	* updated `Text` import/export functions to take account of dependencies between span and relation layers;
* Updated `Layer` and `RelationLayer`:
	* `None` values will appear translucent by default in the HTML representation;
* Updated `json_to_layer`: added possibility to load a single layer instead of a list of layers. Examples in [tutorial](https://github.com/estnltk/estnltk/blob/caa53bc4cda8198a93fc07a8a3146a23287dab5f/tutorials/converters/json_exporter_importer.ipynb); 
* Removed deprecated module `estnltk.resolve_layer_dag` (use `estnltk.default_resolver` instead); 
* Updated `UserDictTagger`: made `add_word` & `add_words_from_csv_file` non-public methods, which should no longer be used directly. Instead, `UserDictTagger`'s constructor should be used for adding all words; 
* Added [deprecation warning](https://github.com/estnltk/estnltk/blob/caa53bc4cda8198a93fc07a8a3146a23287dab5f/tutorials/nlp_pipeline/B_morphology/syllabification.ipynb) about `Vabamorf`'s syllabifier. Instead of using `Vabamorf`'s syllabifier, please use [the finite state transducer based syllabifier](https://gitlab.com/tilluteenused/docker_elg_syllabifier) which provides a complete syllabification functionality of Estonian;
* Update `parse_enc`:
   * adapted to processing ENC 2023 .vert files;
   * added `add_document_index` option to parse_enc (saves document's original locations in the vert file) for processing ENC 2023;
   * added `focus_block` parameter to enable and control data parallelization;
   * added `extended_morph_form` parameter to enable importing of additional morphological form information in CG categories. This is possible only in ENC 2021 and ENC 2023 versions of the corpora which have both regular `morph_analysis` and `morph_extended` annotations available. 
   * details in [the tutorial](https://github.com/estnltk/estnltk/blob/592a1689b9e07822d821d5b7bfa18f5981ec8f6d/tutorials/corpus_processing/importing_text_objects_from_corpora.ipynb);
* Updated `PhraseTagger`, `RegexTagger`, `SpanTagger`, `SubstringTagger` with `get_decorator_inputs` method, which can be used for debugging while creating rules, see [this tutorial](https://github.com/estnltk/estnltk/blob/caa53bc4cda8198a93fc07a8a3146a23287dab5f/tutorials/taggers/rule_taggers/B_decorator_development.ipynb) for examples;
* Renamed `NerWebTagger`'s parameter `ner_output_layer` to `output_layer`;
* Renamed `SyntaxDependencyRetagger`'s parameter `conll_syntax_layer` to `syntax_layer`;
* Renamed `HfstClMorphAnalyser`'s method `lookup` to `analyze_token` and added corresponding implementation;
* Refactored & simplified `PhraseExtractor` interface;
* Removed `legacy.dict_taggers`;
* Updated `estnltk/setup.py`: customised build_py to build swig extensions before python modules;
* Updated `StanzaSyntaxEnsembleTagger`'s `majority_voting` algorithm: added Chu–Liu/Edmonds' post-processing to assure a valid tree structure;
* Updated `CoreferenceTagger`: added parameter `xgb_tree_method` which allows to set a `tree_method` training parameter in `xgboost` (since `xgboost` version 2.0, the default `tree_method` has been changed, so this parameter allows to roll back to the previous `tree_method` to restore the old behaviour of the model);
* Refactored `BertTagger` & `RobertaTagger`:
	* create unambiguous layers by default, avoid unnecessary nested lists in the output; Examples in [this tutorial](https://github.com/estnltk/estnltk/blob/caa53bc4cda8198a93fc07a8a3146a23287dab5f/tutorials/nlp_pipeline/E_embeddings/bert_embeddings_tagger.ipynb);
* Optimized `PgCollection` initialization: do not count all rows during the initialization. This should make initialization relatively fast even for large tables;
* Removed `PostgresStorage` from short import path `estnltk.storage`. Please use long import path: `from estnltk.storage.postgres import PostgresStorage`;
* Refactored `PgCollection`: moved `create_collection_table` to `CollectionStructureBase` as creating collection table now depends on the collection structure version; stand-alone function `create_collection_table` is deprecated;
* Renamed `CollectionStructureBase.create_table` -> `create_layer_info_table`;


## Added

* Updated `RelationLayer`:
	* added possibility to define enveloping `RelationLayer`; 
	* added `display_order`, which can be used for specifying the order of `span_names` & `attributes` in the HTML representation of the layer;
	* added `display()` method to `RelationLayer` for showing relation (named span) annotations in text;
	* added `relations_v1` serialization module for serializing updated version of the layer;
	* For examples about the updated relation layer, please see [this tutorial](https://github.com/estnltk/estnltk/blob/caa53bc4cda8198a93fc07a8a3146a23287dab5f/tutorials/system/relation_layer.ipynb);
* Added `DisplayNamedSpans` & `NamedSpanVisualiser` classes that support `RelationLayer` visualisation;
* Updated `Relation`: added HTML representation;
* Updated `NamedSpan`: added `resolve_attribute` method, which allows to get an access to foreign attributes; Examples in [this tutorial](https://github.com/estnltk/estnltk/blob/caa53bc4cda8198a93fc07a8a3146a23287dab5f/tutorials/system/relation_layer.ipynb);
* Updated `TokensTagger`: added quotation marks postfixes (flag `apply_quotes_postfixes`);
* Added `LocalTokenSplitter` that splits tokens into smaller tokens based on regular expression patterns and user-defined functions for determining the split point; For details, see [the tutorial](https://github.com/estnltk/estnltk/blob/caa53bc4cda8198a93fc07a8a3146a23287dab5f/tutorials/nlp_pipeline/A_text_segmentation/01_tokens.ipynb); 
* Updated `VabamorfAnalyzer`: added function `analyze_token` for analysing a single word; Usage details in [the tutorial](https://github.com/estnltk/estnltk/blob/caa53bc4cda8198a93fc07a8a3146a23287dab5f/tutorials/nlp_pipeline/B_morphology/01_morphological_analysis.ipynb);
* Added `TimeLocTagger` which tags time/location OBL phrases based on UD syntax layer;
* Added `PropBankPreannotator` which tags Estonian PropBank semantic roles based on a (manually-crafted) lexicon; Note that  this is a preliminary version of the tagger;
* Added `RegexElement`, `StringList` and `ChoiceGroup` classes that wrap around [regex library](https://pypi.org/project/regex/) and allow to systematically document and test regular expressions. For usage details, please see [this tutorial](https://github.com/estnltk/estnltk/blob/caa53bc4cda8198a93fc07a8a3146a23287dab5f/tutorials/taggers/rule_taggers/A_regex_development.ipynb);
* Added a [tutorial](https://github.com/estnltk/estnltk/blob/caa53bc4cda8198a93fc07a8a3146a23287dab5f/tutorials/taggers/rule_taggers/B_decorator_development.ipynb) about rule_tagger's decorator development (by swenlaur);
* Added `enc_layer_to_conll` for converting ENC morphosyntactic layer to CONLLU string. See details in the [tutorial](https://github.com/estnltk/estnltk/blob/38a50d30c938aed8c811b9ef0b296d0e4f01fcc0/tutorials/converters/conll_exporter.ipynb); 
* Added `syntax_phrases_v0` serialization module (used by `PhraseExtractor`);
* Updated `StanzaSyntaxEnsembleTagger`: added calculation of predictions' entropy (optional); For usage details, see [this tutorial](https://github.com/estnltk/estnltk/blob/caa53bc4cda8198a93fc07a8a3146a23287dab5f/tutorials/nlp_pipeline/C_syntax/03_syntactic_analysis_with_stanza.ipynb);
* Updated `PgCollection`'s create layer functions: if layer creation fails, document id-s will be logged;
* Updated `PgCollection` default version to V4:
	* Introduced new collection structure `postgres/structure/v40/collectionstructure.py`;
	* Added possibility to hide documents in pg collection. Note: a row-level security policy must be defined for the hiding to take effect;
	* Enable storing relation layers;
	* Added `pg_collection.is_relation_layer` method;

## Fixed

* Fixed `BaseLayer` `__getitem__` & `get` methods: preserve `serialisation_module` while extracting a sub-layer;
* Fixed `UserDictTagger`: `morph_layer`'s spans are now properly changed so that old values would not reappear after retagging;
* Fixed DeprecationWarning in NER `model_storage_util`;
* Fixed `syllabify_word`: do not crash on empty input;
* Fixed `RegexTagger` & `SpanTagger`: drop annotations if global decorator insists;
* Fixed `TimeLocDecorator`:
    * proper reading of lemmas list from file;
    * avoid circular wordnet import;
* Fixed matplotlib's imports (use internal imports to avoid occasional importing errors in Windows conda packages);
* Fixed `Wordnet.__del__` error (before closing database, assure it is open);
* Fixed `CoreferenceTagger`.`expand_mentions_to_named_entities`: remove any duplicate relations;
* Fixed `StanzaSyntaxTagger`/`StanzaSyntaxEnsembleTagger` a preprocessing bug introduced in stanza version update to 1.7.0+;
* Fixed `EstBERTNERTagger`: added proper input tokenization that does not fail on rare unicode symbols;
* Fixed `BertTagger` & `RobertaTagger`:
	* added proper tokenization processing that does not fail on rare unicode symbols;
	* do not use deprecated `tokenizer.encode_plus`;


# [1.7.2] - 2023-08-10

## Changed

* Renamed `PgCollection.meta` -> `meta_columns`;
* Deprecated `PgCollection.create()`. Use `PostgresStorage.add_collection` method to create new collections;
* Deprecated `PgCollection.delete()`, `PostgresStorage.delete(collection)` and `PostgresStorage.__delitem__(collection)`. Use `PostgresStorage.delete_collection` method to remove collections;
* Deprecated `PgCollection.select_fragment_raw()` (no longer relevant) and `continue_creating_layer` (use `create_layer(..., mode="append")` instead);
* Deprecated `PgCollection.has_fragment()`, `get_fragment_names()`, `get_fragment_tables()`. Use `collection.has_layer(name, layer_type="fragmented")` and `collection.get_layer_names_by_type(layer_type="fragmented")` instead;
* Merged `PgCollection.create_fragment` into `PgCollection.create_fragmented_layer`;
* Merged `PgCollection._create_layer_table` into `PgCollection.add_layer`;
* `StorageCollections.load()` removed legacy auto-insert behaviour;
* Refactored `PostgresStorage`: upon connecting to database, a new schema is now automatically created if the flag `create_schema_if_missing` has been set and the user has enough privileges. No need to manually call `create_schema` anymore;
* Refactored `StorageCollections` & `PostgresStorage`: relocated `storage_collections` table insertion and deletion logic to `PostgresStorage`;
* Refactored `PgCollection.add_layer`: added `layer_type` parameter, deprecated `fragmented_layer` paramater and added `'multi'` to layer types;
* Replaced function `conll_to_str` with `converters.conll.layer_to_conll`. For usage, see [this tutorial](https://github.com/estnltk/estnltk/blob/4ba6d9896b851d0a922a6a43bf2cc08a09667802/tutorials/nlp_pipeline/C_syntax/01_syntax_preprocessing.ipynb) ("CONLL exporter");
* Refactored `DateTagger`, `AddressPartTagger`, `SyntaxIgnoreTagger`, `CompoundTokenTagger`: use new RegexTagger instead of the legacy one;
* Refactored `AdjectivePhrasePartTagger`: use `rule_taggers` instead of legacy `dict_taggers`;
* Updated `StanzaSyntax(Ensemble)Tagger`: random picking of ambiguous analyses is no longer deterministic: you'll get different result on each run if the input is morphologically ambiguous. However, if needed, you can use seed values to ensure repeatability. For details, see [stanza parser tutorials](https://github.com/estnltk/estnltk/blob/4ba6d9896b851d0a922a6a43bf2cc08a09667802/tutorials/nlp_pipeline/C_syntax/03_syntactic_analysis_with_stanza.ipynb);
* Updated `StanzaSyntaxEnsembleTagger`: 
	* if user attempts to process sentences longer than 1000 words with GPU / CUDA, a guarding exception will be thrown. Pass parameter `gpu_max_words_in_sentence=None` to the tagger to disable the exception;
	* added `aggregation_algorithm` parameter, which defaults to `'las_coherence'` (the same algorithm that has been used in the previous versions);
	* added a new aggregation algorithm: `'majority_voting'`. With the majority voting, the input will be processed token-wise and head & deprel that gets most votes from models will be picked for each token. Note, however, that this method can produce invalid tree structures, as there is no  mechanism to ensure that majority-voting-picked tokens will make up a valid tree. 
* Renamed `SoftmaxEmbTagSumWebTagger` to `NeuralMorphDisambWebTagger` and made following updates:
	* `NeuralMorphDisambWebTagger` is now a `BatchProcessingWebTagger`;
	* `NeuralMorphDisambWebTagger` is now also a `Retagger` and can be used to disambiguate ambiguous `morph_analysis` layer. In the same vein, `NeuralMorphTagger` was also made `Retagger` and can be used for disambiguation. For details on the usage, see [the neural morph tutorial](https://github.com/estnltk/estnltk/blob/b67ca34ef0702bb7d7fbe1b55639327dfda55830/tutorials/nlp_pipeline/B_morphology/08_neural_morph_tagger_py37.ipynb); 
* `estnltk_neural` package requirements: removed explicit `tensorflow` requirement. 
	* Note, however, that `tensorflow <= 1.15.5` (along with Python `3.7`) is still required if you want to use `NeuralMorphTagger`;
* `Wordnet`: 
	* default database is no longer distributed with the package, wordnet now downloads the database automatically via `estnltk_resources`;
	* alternatively, a local database can now be imported via parameter `local_dir`;
	* updated wordnet database version to **2.6.0**;
* `HfstClMorphAnalyser`: 
	* the model is no longer distributed with the package, the analyser now downloads model automatically via `estnltk_resources`;
* Refactored `BatchProcessingWebTagger`:
	* renamed parameter `batch_layer_max_size` -> `batch_max_size`; 
	* the tagger has now 2 working modes: a) batch splitting guided by text size limit, b) batch splitting guided by layer size limit (the old behaviour);
* Updated `vabamorf`'s function `syllabify_word`: 
    * made compound word splitting heuristic more tolerant to mismatches, and as a result, we can now more properly syllabify words which root tokens do not match exactly with the surface form. Examples: `kolmekümne` (`kol-me-küm-ne`),  `paarisada` (`paa-ri-sa-da`), `ühesainsas` (`ü-hes-ain-sas`). However, if you need to use the old syllabification  behaviour, pass parameter `tolerance=0` to the function, e.g. `syllabify_word('ühesainsas', tolerance=0)`.

## Added

* `MultiLayerTagger` -- interface for taggers that create multiple layers at once;
* `NerWebTagger` that tags NER layers via [tartuNLP NER webservice](https://ner.tartunlp.ai/api) (uses EstBERTNER v1 model). See [this tutorial](https://github.com/estnltk/estnltk/blob/b970ea98532921a4e06022fff2cd3755fc181edf/tutorials/nlp_pipeline/D_information_extraction/02_named_entities.ipynb) for details;
* `EstBERTNERTagger` that tags NER layers using huggingface EstBERTNER models. See [this tutorial](https://github.com/estnltk/estnltk/blob/b970ea98532921a4e06022fff2cd3755fc181edf/tutorials/nlp_pipeline/D_information_extraction/02_named_entities.ipynb) for details;
* `RelationLayer` -- new type of layer for storing information about relations between entities mentioned in text, such as coreference relations between names and pronouns, or semantic roles/argument structures of verbs. However, `RelationLayer` has not yet completely integrated with EstNLTK's tools, and there are following limitations:
	* you cannot access attributes of foreign layers (such as `lemmas` from `morph_analysis`) via spans of a relation layer;
	* `estnltk_core.layer_operations` do not support `RelationLayer`;
	* `estnltk.storage.postgres` does not support `RelationLayer`;
	* `estnltk.visualisation` does not handle `RelationLayer`;

    For usage examples, see the [RelationLayer's tutorial](https://github.com/estnltk/estnltk/blob/b8ad0932a852daedb1e3eddeb02c944dd1f292ee/tutorials/system/relation_layer.ipynb).

* `RelationTagger` -- interface for taggers creating `RelationLayer`-s. Instructions on how to create a `RelationTagger` can be found in [this tutorial](https://github.com/estnltk/estnltk/blob/4ba6d9896b851d0a922a6a43bf2cc08a09667802/tutorials/taggers/base_tagger.ipynb);
* `WebRelationTagger` & `BatchProcessingWebRelationTagger`, which allow to create web-based `RelationTagger`-s;
* `CoreferenceTagger` which detects pronominal coreference relations. The tool is based on [Estonian Coreference System  v1.0.0](https://github.com/SoimulPatriei/EstonianCoreferenceSystem) and currently relies on stanza 'et' models for pre-processing the input text. In future, the tool also becomes available via a web service (by `CoreferenceV1WebTagger`). For details, see the [coreference tutorial](https://github.com/estnltk/estnltk/blob/28814a3fa9ff869cd4cfc88308f6ce7e29157889/tutorials/nlp_pipeline/D_information_extraction/04_pronominal_coreference.ipynb);
* Updated `VabamorfDisambiguator`, `VabamorfTagger` & `VabamorfCorpusTagger`: added possibility to preserve phonetic mark-up (even with disambiguation);
* `UDMorphConverter` -- tagger that converts Vabamorf's morphology categories to Universal Dependencies morphological categories. Note that the conversion can introduce additional ambiguities as there is no disambiguation included, and roughly 3% to 9% of words do not obtain correct UD labels with this conversion. More details in [tutorial](https://github.com/estnltk/estnltk/blob/4ba6d9896b851d0a922a6a43bf2cc08a09667802/tutorials/nlp_pipeline/B_morphology/06_morph_analysis_with_ud_categories.ipynb);
* `RobertaTagger` for tagging `EMBEDDIA/est-roberta` embeddings. The interface is analogous to that of `BertTagger`. [Tutorial](https://github.com/estnltk/estnltk/blob/e223a7e6245d29a6b1838335bfa3872a0aa92840/tutorials/nlp_pipeline/E_embeddings/bert_embeddings_tagger.ipynb).
* `BertTokens2WordsRewriter` -- tagger that rewrites BERT tokens layer to a layer enveloping EstNLTK's words layer. Can be useful for mapping Bert's output to EstNLTK's tokenization (currently used by `EstBERTNERTagger`). 
* `PhraseExtractor` -- tagger for removing phrases and specific dependency relations based on UD-syntax;
* `ConsistencyDecorator` -- decorator for PhraseExtractor. Calculates syntax conservation scores after removing phrase from text;
* `StanzaSyntaxTaggerWithIgnore` -- entity ignore tagger. Retags text with StanzaSyntaxTagger and excludes phrases found by PhraseExtractor;
* `estnltk.resource_utils.delete_all_resources`. Apply it before uninstalling EstNLTK to remove all resources;
* `clauses_and_syntax_consistency` module, which allows to 1) detect potential errors in clauses layer using information from the syntax layer, 2) fix clause errors with the help of syntactic information. [Tutorial](https://github.com/estnltk/estnltk/blob/4ba6d9896b851d0a922a6a43bf2cc08a09667802/tutorials/nlp_pipeline/F_annotation_consistency/clauses_and_syntax_consistency.ipynb);
* `PostgresStorage` methods:
	* `add_collection`
	* `refresh`
	* `delete_collection`
* `PgCollection` methods:
	* `refresh` 
	* `get_layer_names_by_type`
* `PgCollectionMeta` (provides views to `PgCollection`'s metadata, and allows to query metadata) and `PgCollectionMetaSelection` (read-only iterable selection over `PgCollection`'s metadata values); 
* Parameter `remove_empty_nodes` to `conll_to_text` importer -- if switched on (default), then empty / null nodes (ellipsis in the enhanced representation) will be discarded (left out from textual content and also from annotations) while importing from conllu files; 
* Added a simplified example about how to get whitespace tokenization for words to tutorial [`restoring_pretokenized_text.ipynb`](https://github.com/estnltk/estnltk/blob/4ba6d9896b851d0a922a6a43bf2cc08a09667802/tutorials/corpus_processing/restoring_pretokenized_text.ipynb);
* `pg_operations.drop_all`;

## Fixed

* `extract_(discontinuous_)sections`: should now also work on non-ambiguous layer that has a parent;
* `BaseText.topological_sort`: should now also work on layers with malformed/unknown dependencies;
* `CompoundTokenTagger`: 2nd level compounding rules now also work on detached layers;
* `TimexTagger`'s rules: disabled extraction of too long year values (which could break _Joda-Time_ integer limits);
* Bug that caused collection metadata to disappear when using `PgCollection.insert` (related to `PgCollection.column_names` not returning automatically correct metadata column names on a loaded collection; newly introduced `PgCollectionMeta` solved that problem);
* `StanzaSyntax(Ensemble)Tagger`: should now also work on detached layers;
* Fixed `BaseLayer.diff`: now also takes account of a difference in `secondary_attributes`;
* Fixed `downloader._download_and_install_hf_resource`: disabled default behaviour and `use_symlinks` option, because it fails under the Windows;
* Fixed `download`: made it more flexible on parsing (idiosyncratic) 'Content-Type' values;
* Fixed `BertTagger` tokenization: `BertTagger` can now better handle misalignments between bert tokens and word spans caused by emojiis, letters with diacritics, and the invisible token `\xad`;

# [1.7.1] - 2022-08-30

## Changed

* Stucture and organization of [EstNLTK's tutorials](https://github.com/estnltk/estnltk/tree/811978b24b9bacd4b53d301d379ffad2bd8b41e9/tutorials), including:
	* Relocated introductory tutorials into the folder ['basics'](https://github.com/estnltk/estnltk/tree/811978b24b9bacd4b53d301d379ffad2bd8b41e9/tutorials/basics);
	* Relocated 'estner_training' tutorials to 'nlp_pipeline/D_information_extraction';
	* Updated syntax tutorials and split into parser-wise sub tutorials:
		* [maltparser tutorial](https://github.com/estnltk/estnltk/blob/811978b24b9bacd4b53d301d379ffad2bd8b41e9/tutorials/nlp_pipeline/C_syntax/03_syntactic_analysis_with_maltparser.ipynb);
		* [stanza's parser tutorial](https://github.com/estnltk/estnltk/blob/811978b24b9bacd4b53d301d379ffad2bd8b41e9/tutorials/nlp_pipeline/C_syntax/03_syntactic_analysis_with_stanza.ipynb);
		* [udpipe's parser tutorial](https://github.com/estnltk/estnltk/blob/811978b24b9bacd4b53d301d379ffad2bd8b41e9/tutorials/nlp_pipeline/C_syntax/03_syntactic_analysis_with_udpipe.ipynb);
		* [vislcg3 tutorial](https://github.com/estnltk/estnltk/blob/811978b24b9bacd4b53d301d379ffad2bd8b41e9/tutorials/nlp_pipeline/C_syntax/03_syntactic_analysis_with_vislcg3.ipynb);  
* Updated `parse_enc` -- it can now be used for parsing [ENC 2021](https://metashare.ut.ee/repository/browse/eesti-keele-uhendkorpus-2021-vert/f176ccc0d05511eca6e4fa163e9d454794df2849e11048bb9fa104f1fec2d03f/). See the details from [the tutorial](https://github.com/estnltk/estnltk/blob/811978b24b9bacd4b53d301d379ffad2bd8b41e9/tutorials/corpus_processing/importing_text_objects_from_corpora.ipynb);
	* The function `parse_enc_file_iterator` now attempts to _automatically fix malformed paragraph annotations_ . As a result, more words and sentences can be imported from corpora, but the side effect is that there will be artificially created paragraph annotations -- even for documents that do not have paragraph annotations originally. The setting can be turned off, if needed;
* Updated `get_resource_paths` function: added EstNLTK version checking. A resource description can now contain version specifiers, which declare estnltk or estnltk_neural version required for using the resource. Using version constraints is optional, but if they are used and constraints are not satisfied, then `get_resource_paths` won't download the resource nor return its path;
* Relocated `estnltk.transformers` (`MorphAnalysisWebPipeline`) into `estnltk.web_taggers`;
* Refactoring: moved functions `_get_word_texts` & `_get_word_text` to `estnltk.common`;

## Added

* `ResourceView` class, which lists EstNLTK's resources as a table, and shows their download status. See the [resources tutorial](https://github.com/estnltk/estnltk/blob/811978b24b9bacd4b53d301d379ffad2bd8b41e9/tutorials/basics/estnltk_resources.ipynb) for details. 
* `SyntaxIgnoreCutter` class, which cuts the input Text object into a smaller Text by leaving out all spans from the syntax_ignore layer (produced by `SyntaxIgnoreTagger`). The resulting Text can then be analysed syntactically while skipping parts of a text may be difficult to analyse. For details, see the [tutorial](https://github.com/estnltk/estnltk/blob/811978b24b9bacd4b53d301d379ffad2bd8b41e9/tutorials/nlp_pipeline/C_syntax/02_syntax_preprocessing_with_ignoretagger.ipynb);
* function `add_syntax_layer_from_cut_text`, which can be used to carry over the syntactic analysis layer from the cut text (created by `SyntaxIgnoreCutter`) to the original text. The [tutorial](https://github.com/estnltk/estnltk/blob/811978b24b9bacd4b53d301d379ffad2bd8b41e9/tutorials/nlp_pipeline/C_syntax/02_syntax_preprocessing_with_ignoretagger.ipynb);

## Fixed

* Syntax preprocessing [tutorial](https://github.com/estnltk/estnltk/blob/811978b24b9bacd4b53d301d379ffad2bd8b41e9/tutorials/nlp_pipeline/C_syntax/01_syntax_preprocessing.ipynb) to describe the current state of preprocessing;

# [1.7.0] - 2022-06-17

## Changed

* EstNLTK's tools that require large resources (e.g. syntactic parsers and neural analysers) can now download resources automatically upon initialization. This stops the program flow with an interactive prompt asking
 for user's permission to download the resource. However, you can predownload the resource in order to avoid the interruption, see this [tutorial](https://github.com/estnltk/estnltk/blob/cad31cc63b583bbef56b5f5fbcc3218ba8f5461c/tutorials/estnltk_resources.ipynb) for details. 

* Stucture and organization of [EstNLTK's tutorials](https://github.com/estnltk/estnltk/tree/cad31cc63b583bbef56b5f5fbcc3218ba8f5461c/tutorials). However, the work on updating tutorials is still not complete.

* `PgCollection`: now uses `CollectionStructure.v30` by default.

* Disambiguator (a system tagger): it's now a Retagger, but can work either as a retagger or a tagger, depending on the inputs. [Tutorial](https://github.com/estnltk/estnltk/blob/cad31cc63b583bbef56b5f5fbcc3218ba8f5461c/tutorials/taggers/system/disambiguator.ipynb).

## Added

* `downloader` & `resources_utils` for downloading additional resources and handling paths of downloaded resources. [Tutorial](https://github.com/estnltk/estnltk/blob/cad31cc63b583bbef56b5f5fbcc3218ba8f5461c/tutorials/estnltk_resources.ipynb)

* Collocation net -- allows to find different connections between words based on the collocations each word was in. [Tutorial](https://github.com/estnltk/estnltk/blob/cad31cc63b583bbef56b5f5fbcc3218ba8f5461c/tutorials/collocation_net/tutorial.ipynb).

* `PgCollection`: added `CollectionStructure.v30` which allows to create sparse layer tables. Sparse layer tables do not store empty layers, which can save up the storage space and allow faster queries over tables & collection. The [main db tutorial](https://github.com/estnltk/estnltk/blob/cad31cc63b583bbef56b5f5fbcc3218ba8f5461c/tutorials/storage/storing_text_objects_in_postgres.ipynb) exemplfies the creation and usage of sparse layers.

	* `PgCollection.create_layer` & `PgCollection.add_layer` now take parameter `sparse=True` which turns layer into a sparse layer;
	
	* `PgCollection.select` now has a boolean parameter `keep_all_texts`: turning the parameter off yields only texts with non-empty sparse layers;  

	* `PgSubCollection` now has methods `create_layer` and `create_layer_block` which can be used to create a sparse layer from specific subcollection;

## Fixed

* `BaseText.__repr__` method using wrong variable name;

* `NeuralMorphTagger`'s configuration reading and handling: model locations can now be freely customized;

* `TimexTagger`'s rules on detecting dates with roman numeral months & dates with slashes.

# [1.7.0-rc0] - 2022-03-24

EstNLTK has gone through a major package restructuring and refactoring process.

# Package restructuring

 EstNLTK has been split into 3 Python packages:

* `estnltk-core` -- package containing core datastructures, interfaces and data conversion functions of the EstNLTK library;
* `estnltk` -- the standard package, which contains basic linguistic analysis (including Vabamorf morphological analysis, syntactic parsing and information extraction models), system taggers and Postgres database tools;
* `estnltk-neural` -- package containing linguistic analysis based on neural models (Bert embeddings tagger, Stanza syntax taggers and neural morphological tagger);

Normally, end users only need to install `estnltk` (as `estnltk-core` will be installed automatically). 

Tools in `estnltk-neural` require installation of deep learning frameworks (`tensorflow`, `pytorch`), and are demanding for computational resources; they also rely on large models (which need to be downloaded separately).

## Changed

* `Text`:

	* method `text.analyse` is deprecated and no longer functional. Use `text.tag_layer` to create layers. Calling `text.analyse` will display an error message with additional information on migrating from `analyse` to `tag_layer`;
	* added instance variable `text.layer_resolver` which uses EstNLTK's default pipeline to create layers. The following new layers were added to the pipeline: `'timexes'`,` 'address_parts`', `'addresses'`, `'ner'`, `'maltparser_conll_morph'`, `'gt_morph_analysis'`, `'maltparser_syntax'`,`'verb_chains'`, `'np_chunks'`
	* Shallow copying of a `Text` is no longer allowed. Only `deepcopy` can be used;
	* Renamed method: `text.list_layers` -> `text.sorted_layers`;
	* Renamed property: `text.attributes` -> `text.layer_attributes`;
	* `Text` is now a subclass of `BaseText` (from `estnltk-core`). `BaseText` stores raw text, metadata and layers, has methods for adding and removing layers, and provides layer access via indexing (square brackets). `Text` provides an alternative access to layers (layers as attributes), and allows to call for text analysers / NLP pipeline (`tag_layer`)

* `Layer`:
	* Removed `to_dict()` and `from_dict()` methods. Use `layer_to_dict` and `dict_to_layer` from `estnltk.converters` instead;
	* Shallow copying of a `Layer` is no longer allowed. Only `deepcopy` can be used;
	* Renamed `Layer.attribute_list()` to `Layer.attribute_values()`;
		* indexing attributes (`start`, `end`, `text`) should now be passed to the method via keyword argument `index_attributes`. They will be prepended to the selection of normal attributes;
	* Renamed `Layer.metadata()` to `Layer.get_overview_dataframe()`;
	* Method `Layer.add_annotation(base_span, annotations)`:
		* now allows to pass `annotations` as a dictionary (formerly, `annotations` could be passed only as keyword arguments);
		* `Annotation` object cannot be passed as a `base_span`; 
	* HTML representation: maximum length of a column is 100 characters and longer strings will be truncated; however, you can change the maximum length via `OUTPUT_CONFIG['html_str_max_len']` (a configuration dictionary in `estnltk_core.common`);
	* `Layer` is now a subclass of `BaseLayer` (from `estnltk-core`). `BaseLayer` stores text's annotations, attributes of annotations and metadata, has methods for adding and removing annotations, and provides span/attribute access via indexing (square brackets). `Layer` adds layer operations (such as finding descendant and ancestor layers, and grouping spans or annotations of the layer), provides an alternative access to local attributes (via dot operator), and adds possibility to access foreign attributes (e.g. attributes of a parent layer).  

* ` SpanList/Envelopingspan/Span/Annotation`:
	* Removed `to_records()`/`to_record()` methods. The same functionality is provided by function `span_to_records` (from `estnltk_core.converters`), but note that the conversion to records does not support all EstNLTK's data structures and may result in information loss. Therefore, we recommend converting via functions `layer_to_dict`/`text_to_dict` instead;
	* Method `Span.add_annotation(annotation)` now allows to pass `annotation` as a dictionary (formerly, `annotation` could be passed only as keyword arguments);
	* Constructor `Annotation(span, attributes)` now allows to pass `attributes` as a dictionary (formerly, `attributes` could be passed only as keyword arguments);

* `Tagger`:
	* trying to `copy` or `deepcopy` a tagger now raises `NotImplementedError`. Copying a tagger is a specific operation, requires handling of tagger's resources and therefore no copying should attempted by default. Instead, you should create a new tagger instance;

* `PgCollection`: Removed obsolete `create_layer_table` method. Use `add_layer` method instead.

* `estnltk.layer_operations`
	*  moved obsolete functions `compute_layer_intersection`, `apply_simple_filter`, `count_by_document`, `dict_to_df`, `group_by_spans`, `conflicts`, `iterate_conflicting_spans`, `combine`, `count_by`, `unique_texts`, `get_enclosing_spans`, `apply_filter`, `drop_annotations`, `keep_annotations`, `copy_layer` (former `Layer.copy()`) to `estnltk_core.legacy`;

* Renamed `Resolver` -> `LayerResolver` and changed:
	* `default_layers` (used by `Text.tag_layer`) are held at the `LayerResolver` and can be changed;
	* `DEFAULT_RESOLVER` is now available from `estnltk.default_resolver`. Former location `estnltk.resolve_layer_dag` was preserved for legacy purposes, but will be removed in future;
	* Renamed property `list_layers` -> `layers`;
	* HTML/string represenations now display default_layers and a table, which lists names of creatable layers, their prerequisite layers, names of taggers responsible for creating the layers and descriptions of corresponding taggers;  
	* Trying to `copy` or `deepcopy` a layer resolver results in an exception. You should only create new instances of `LayerResolver` -- use function `make_resolver()` from `estnltk.default_resolver` to create a new default resolver;

* Renamed `Taggers` -> `TaggersRegistry` and changed:
	* now retaggers can also be added to the registry. For every tagger creating a layer, there can be 1 or more retaggers modifying the layer. Also, retaggers of a layer can be removed via `clear_retaggers`;
	* taggers and retaggers can now be added as `TaggerLoader` objects: they declare input layers, output layer and importing path of a tagger, but do not load the tagger until explicitly demanded ( _lazy loading_ );

* Refactored `AnnotationRewriter`:
	* tagger should now clearly define whether it only changes attribute values (default) or modifies the set of attributes in the layer;
	* tagger should not add or delete annotations (this is job for `SpanAnnotationsRewriter`); 

* Restructured `estnltk.taggers` into 3 submodules:
	* `standard` -- tools for standard NLP tasks in Estonian, such as text segmentation, morphological processing, syntactic parsing, named entity recognition and temporal expression tagging;
	* `system` -- system level taggers for finding layer differences, flattening and merging layers, but also taggers for rule-based information extraction, such as phrase tagger and grammar parsing tagger;
	* `miscellaneous` -- taggers made for very specific analysis purposes (such as date extraction from medical records), and experimental taggers (verb chain detection, noun phrase chunking);
	* _Note_: this should not affect importing taggers: you can still import most of the taggers from `estnltk.taggers` (except neural ones, which are now in the separate package `estnltk-neural`);

* `serialisation_map` (in `estnltk.converters`) was replaced with `SERIALISATION_REGISTRY`:
	* `SERIALISATION_REGISTRY` is a common registry used by all serialisation functions (such as `text_to_json` and `json_to_text` in `estnltk_core.converters`). The registry is defined in the package `estnltk_core` (contains only the `default` serialization module), and augmented in `estnltk` package (with `legacy_v0` and `syntax_v0` serialization modules);

* Renamed `estnltk.taggers.dict_taggers` -> `estnltk.taggers.system.rule_taggers` and changed:
	* `Vocabulary` class is replaced by `Ruleset` and `AmbiguousRuleset` classes
	* All taggers now follow a common structure based on a pipeline of static rules, dynamic rules and a global decorator
	* Added new tagger `SubstringTagger` to tag occurences of substrings in text
	* Old versions of the taggers are moved to `estnltk.legacy` for backward compatibility

* Relocated TCF, CONLL and CG3 conversion utils to submodules in `estnltk.converters`;

* Relocated `estnltk.layer` to `estnltk_core.layer`;

* Relocated `estnltk.layer_operations` to `estnltk_core.layer_operations`;

* Moved functionality of `layer_operations.group_by_layer` into `GroupBy` class; 

* Relocated `TextaExporter` to `estnltk.legacy` (not actively developed);

* Renamed `TextSegmentsTagger` -> `HeaderBasedSegmenter`;
 
* Renamed `DisambiguatingTagger` -> `Disambiguator`;

* Rename `AttributeComparisonTagger` --> `AttributeComparator`;

* Relocated Vabamorf's default parameters from `estnltk.taggers.standard.morph_analysis.morf_common` to `estnltk.common`;

* Merged `EnvelopingGapTagger` into `GapTagger`:
	* `GapTagger` now has 2 working modes: 
		* Default mode: look for sequences of consecutive characters not covered by input layers;
		* EnvelopingGap mode: look for sequences of enveloped layer's spans not enveloped by input enveloping layers;

* Refactored `TimexTagger`: 
	* removed `TIMEXES_RESOLVER` and moved all necessary preprocessing (text segmentation and morphological analysis) inside `TimexTagger`;
	* `'timexes'` is now a flat layer by default. It can be made enveloping `'words'`, but this can result in broken timex phrases due to differences in `TimexTagger`'s tokenization and EstNLTK's default tokenization;

* `Vabamorf`'s optimization:
	* Disabled [Swig proxy classes](http://www.swig.org/Doc3.0/Python.html#Python_builtin_types). As a result, the morphological analysis is faster. However, this update is under testing and may not be permanent, because disabled proxy classes are known to cause conflicts with other Python Swig extensions compiled under different settings (for more details, see [here](https://stackoverflow.com/q/21103242) and [here](https://github.com/estnltk/estnltk/blob/b0d0ba6d943fb42b923fa6999c752fead927c992/dev_documentation/hfst_integration_problems/solving_stringvector_segfault.md));

* Dropped Python 3.6 support;


## Added

* `Layer.secondary_attributes`: a list of layer's attributes which will be skipped while comparing two layers. Usually this means that these attributes contain redundant information. Another reason for marking attribute as _secondary_ is the attribute being recursive, thus skipping the attribute avoids infinite recursion in comparison;

* `Layer.span_level` property: an integer conveying depth of enveloping structure of this layer; `span_level=0` indicates no enveloping structure: spans of the layer mark raw text positions `(start, end)`, and `span_level` > 0 indicates that spans of the layer envelop around smaller level spans (for details, see the `BaseSpan` docstring in `estnltk_core.layer.base_span`);

* `Layer.clear_spans()` method that removes all spans (and annotations) from the layer. Note that clearing does not change the `span_level` of the layer, so spans added after the clearing must have the same level as before clearing;

* `find_layer_dependencies` function to `estnltk_core.layer_operations` -- finds all layers that the given layer depends on. Can also be used for reverse search: find all layers depending on the given layer (e.g. enveloping layers and child layers);

* `SpanAnnotationsRewriter` (a replacement for legacy `SpanRewriter`) -- a tagger that applies a modifying function on each span's annotations.  The function takes span's annotations (a list of `Annotation` objects) as an input and is allowed to change, delete and add new annotations to the list. The function must return a list with modified annotations. Removing all annotations of a span is forbidden.  

## Fixed

* Property `Layer.end` giving wrong ending index;
* `Text` HTML representation: Fixed "FutureWarning: The frame.append method is deprecated /.../ Use pandas.concat instead";
* `Layer.ancestor_layers` and `Layer.descendant_layers` having their functionalities swaped (`ancestor_layers` returned descendants instead of ancestors), now they return what the function names insist;
* `Span.__repr__` now avoids overly long representations and renders fully only values of basic data types (such as `str`, `int`, `list`);
* `SyntaxDependencyRetagger` now marks `parent_span` and `children` as `secondary_attributes` in order to avoid infinite recursion in syntax layer comparison;
* `PgCollection`: `collection.layers` now returns `[]` in case of an empty collection;
* `PgCollection`: added proper exception throwing for cases where user wants to modify an empty collection;
 


# [1.6.9.1-beta] - 2021-09-20

This is an intermediate release of PyPI packages. The version 1.6.9b0  and 1.6.9.1b0 are equal considering the main functionalities, so no conda packages will be generated. The list of changes will be documented in the next release.

# [1.6.9-beta] - 2021-08-30

## Changed

* `Tagger` API: added methods `get_layer_template` (returns an empty detached layer that contains all the proper attribute initializations), and `_make_layer_template` (a concrete implementation of `get_layer_template` in a derived class). New taggers should now provide `_make_layer_template` implementations in addition to `_make_layer` implementations, and it is recommended that `_make_layer` also uses `_make_layer_template` whenever it needs to create a new layer. For details, see [this tutorial](https://github.com/estnltk/estnltk/blob/f45ca4b546703b8e069c398403d81e825be5c186/tutorials/taggers/base_tagger.ipynb)

	* Most `estnltk.taggers` were updated so that they have `_make_layer_template` implementations. However, in some system taggers (e.g. in `DiffTagger` and `DisambiguatingTagger`), the exact configuration of layer's  attributes is not known before `_make_layer()` has been called, and thus `_make_layer_template` functionality is not supported;
	
    * An important usage of layer templates is `PgCollection`'s new `add_layer` method, see [this tutorial](https://github.com/estnltk/estnltk/blob/3776a140b542855b5fef0b38a80828067e7b2022/tutorials/storage/storing_text_objects_in_postgres.ipynb);

* `PgCollection`'s method `create_layer_block`: an existing (unfinished) block can now be continued if  `mode='append'` is passed to the method. For details about using `create_layer_block`, see [this tutorial](https://github.com/estnltk/estnltk/blob/3776a140b542855b5fef0b38a80828067e7b2022/tutorials/storage/storing_text_objects_in_postgres.ipynb)

* `layer_operations` function `flatten`: added parameter `disambiguation_strategy`. If  `disambiguation_strategy='pick_first'` then the resulting layer will be disambiguated by preserving only the first annotation of every span. By default, the resulting layer will remain ambiguous.  
 

## Added

* method `add_layer` to `PgCollection` -- adds a new detached or fragmented layer to the collection. The method initializes a new empty layer before filling it with data. [Tutorial](https://github.com/estnltk/estnltk/blob/c7e093303566ce7691ffbf899841d741d654bc46/tutorials/storage/storing_text_objects_in_postgres.ipynb)

* new `layer_operations`: function `join_layers` concatenates a list of layers into one layer, and function `join_texts` concatenates a list of Text objects into a single Text object (roughly a reverse of `split_by` and `extract_sections` functionalities). Function `join_layers_while_reusing_spans` joins layers efficiently by reusing spans of the input layers (but as a result, the input layers will be broken). Details about `join_texts` are given in the [tutorial](https://github.com/estnltk/estnltk/blob/7256c8c692f7b718d7b6dee8504fcb705bd71997/tutorials/system/layer_operations.ipynb).

* `BatchProcessingWebTagger` -- a web tagger which processes the input via small batches ( splits large requests into smaller ones ). More detailed usage information [here](https://github.com/estnltk/estnltk/blob/7256c8c692f7b718d7b6dee8504fcb705bd71997/estnltk/taggers/web_taggers/v01/batch_processing_web_tagger.py).

	* `BertEmbeddingsWebTagger`, `StanzaSyntaxEnsembleWebTagger` and `StanzaSyntaxWebTagger` were refactored in a way that they no longer throw `WebTaggerRequestTooLargeError` upon large requests, but use batch processing instead;


## Fixed

* `MorphExtendedTagger`: now it is possible to customize input and output layer names. Also added unit tests for syntax preprocessing with customized layer names;

* `PostgresStorage` `collections` property: now collections list can be accessed even if it is empty;

* `MissingLayerQuery`: removed a major speed bottleneck;

* `BlockQuery`: added missing `required_layers` property and an unit test;

* `BufferedTableInsert`: buffer size limits are now checked before the insertion (to avoid large buffer limit exceedings);


# [1.6.8-beta] - 2021-05-31

## Changed

* `HfstEstMorphAnalyser` was renamed to `HfstClMorphAnalyser` and it's engine was changed. It is no longer dependent on the PyPI `hfst` package, but uses [HFST command line tools](https://github.com/hfst/hfst/wiki/Command-Line-Tools) instead. Both file-based and stream-based communication modes are supported. For details, see [this tutorial](https://github.com/estnltk/estnltk/blob/2b47a4ce8e3a08b85b23b73a281836a23e20ac68/tutorials/hfst/morph_analysis_with_hfst_analyser.ipynb);

* `UserDictTagger`: dictionary entries should now be passed only via the constructor. Using methods `add_word()` and `add_words_from_csv_file()` directly is deprecated. [Tutorial](https://github.com/estnltk/estnltk/blob/2b47a4ce8e3a08b85b23b73a281836a23e20ac68/tutorials/nlp_pipeline/B_07a_morph_analysis_with_user_dict.ipynb);

* `CorpusBasedMorphDisambiguator`: the interface was changed in a way that  the disambiguator now works with detached layers. The interface similar to  `Retagger`'s `_change_layer` is provided by methods `_predisambiguate_detached_layers` and ` _postdisambiguate_detached_layers`. For details, see [this tutorial](https://github.com/estnltk/estnltk/blob/2b47a4ce8e3a08b85b23b73a281836a23e20ac68/tutorials/nlp_pipeline/B_07b_morph_analysis_with_corpus-based_disambiguation.ipynb);

* Statistical syntactic parsers:
    * `MaltParserTagger` now uses a model trained on `morph_analysis` layer by default. This is also the only model that is distributed with the package, other models need to be downloaded from the [github](https://github.com/estnltk/estnltk/tree/ba471626227238b2b83ef7a3479b315407c44807/estnltk/taggers/syntax/maltparser_tagger/java-res/maltparser);
    * `UDPipeTagger`-s models now need to be downloaded separately from github. See [this tutorial](https://github.com/estnltk/estnltk/blob/ba471626227238b2b83ef7a3479b315407c44807/tutorials/syntax/syntax.ipynb) for details;

* Refactored `VabamorfTagger` & other morphology components: 
	* removed `re_sort_analyses` parameter, which is no longer relevant;
	* added `use_reorderer` parameter, which turns on applying [`MorphAnalysisReorderer`](https://github.com/estnltk/estnltk/blob/2b47a4ce8e3a08b85b23b73a281836a23e20ac68/tutorials/nlp_pipeline/B_07c_morph_analysis_reordering.ipynb) as the last correction step. Note: the parameter is switched on by default, so that ambiguous morphological analyses are now always reordered (by their corpus frequency);

* `Layer.groupby` now accepts a string argument if you need to group by a single attribute. So, instead of `text.morph_analysis.groupby(['partofspeech'])`, you can write `text.morph_analysis.groupby('partofspeech')`. In addition, an attached layer can be grouped by other layer of the `Text` object simply by giving the name of the layer, e.g. `text.morph_analysis.groupby('sentences')`.

* `TIMEXES_RESOLVER`, which provides a pipeline for `TimeTagger` along with required tokenization fixes (which improve the quality of timex detection). For details, see [this tutorial](https://github.com/estnltk/estnltk/blob/2b47a4ce8e3a08b85b23b73a281836a23e20ac68/tutorials/taggers/temporal_expression_tagger.ipynb);

* PostgreSQL interface was refactored:
	*  Removed `_select_by_key`, `get_layer_names` and `find_fingerprint` from `PgCollection`;
	*  Tabel insertion logic was moved from `PgCollection` to separate context manager classes: `BufferedTableInsert`, `CollectionTextObjectInserter` and `CollectionDetachedLayerInserter`;
	*  Refactored `Query.eval()` interface: `PgCollection` is now used as an input;
	* `JsonbTextQuery` and `JsonbLayerQuery` were replaced by **`LayerQuery`**, which now works both on attached and detached layers. [Tutorial](https://github.com/estnltk/estnltk/blob/7efc7a60eb15be5775c6790c0b8ca5a06259e2ae/tutorials/storage/storing_text_objects_in_postgres.ipynb);

* Dropped Python 3.5 support, and added Python 3.8 support. 

## Added

* Function `make_userdict()` for automatically creating `UserDictTagger` based on a dictionary of mappings from incorrect spellings to correct spellings. For details, see [this tutorial](https://github.com/estnltk/estnltk/blob/2b47a4ce8e3a08b85b23b73a281836a23e20ac68/tutorials/nlp_pipeline/B_07a_morph_analysis_with_user_dict.ipynb);

* Function `split_by_clauses`, which properly splits text into clauses,
  considering all the discontinuous spans (embedded clauses) of the clauses layer. For this, a supporting function `extract_discontinuous_sections` was implemented, which allows to extract discontinuous sections from the `Text`. The function `split_by` was updated in a way that it applies `split_by_clauses` on the clauses layer by default. For details, see [this tutorial](https://github.com/estnltk/estnltk/blob/2b47a4ce8e3a08b85b23b73a281836a23e20ac68/tutorials/system/layer_operations.ipynb);

* Added parameters `predisambiguate` and `postdisambiguate` to `VabamorfTagger`, which can be used to turn on _text-based morphological disambiguation_ provided by `CorpusBasedMorphDisambiguator`. Note: by default, the parameters are not turned on. For details, see [this tutorial](https://github.com/estnltk/estnltk/blob/2b47a4ce8e3a08b85b23b73a281836a23e20ac68/tutorials/nlp_pipeline/B_07b_morph_analysis_with_corpus-based_disambiguation.ipynb);

* Parameter `force_resolving_by_priority` to `GrammarParsingTagger`. This applies (experimental) post-resolving all conflicts by priority attributes of grammar rules. Details in [this tutorial](https://github.com/estnltk/estnltk/blob/2b47a4ce8e3a08b85b23b73a281836a23e20ac68/tutorials/finite_grammar/introduction_to_finite_grammar.ipynb); 

* `TokenSplitter` -- a retagger which can be used to make rule-based post-corrections to the tokens layer. Details are given in [this tutorial](https://github.com/estnltk/estnltk/blob/c5b30eb7b1c7eb6868ebda408a6c12a19f8dffa7/tutorials/nlp_pipeline/B_01_segmentation_tokens.ipynb);

* Added patterns for detecting hashtags and Twitter username mentions to `CompoundTokenTagger`. Can be switched on by the flag `tag_hashtags_and_usernames`. For details, see [this tutorial](https://github.com/estnltk/estnltk/blob/2b47a4ce8e3a08b85b23b73a281836a23e20ac68/tutorials/nlp_pipeline/B_02_segmentation_compound_tokens.ipynb). Also, `PostMorphAnalysisTagger` was updated to provide some post-corrections on  the corresponding tokens, see details [here](https://github.com/estnltk/estnltk/blob/2b47a4ce8e3a08b85b23b73a281836a23e20ac68/tutorials/nlp_pipeline/B_06_morphological_analysis.ipynb).

* The following new query types were added to PostgreSQL interface: 
   * `IndexQuery`, `SliceQuery` -- for querying `Text` objects by their collection indexes;
   * `MetadataQuery` -- for querying `Text` objects by their metadata (collection or text metadata, for details, see this [tutorial](https://github.com/estnltk/estnltk/blob/7efc7a60eb15be5775c6790c0b8ca5a06259e2ae/tutorials/storage/storing_text_objects_in_postgres.ipynb);
   * Updated `LayerNgramQuery`: added validation for the existence of `ngram_index` columns;

* Shuffling and sampling methods were added to `PgSubCollection`:
   * method `permutate()` -- iterates texts in random order;
   * method `sample()` -- selects a random sample of texts from the collection;
   * method `sample_from_layer()` -- selects a random sample of spans from a specific layer of the collection;
   * for details, see [this tutorial](https://github.com/estnltk/estnltk/blob/7efc7a60eb15be5775c6790c0b8ca5a06259e2ae/tutorials/storage/sampling_texts_and_layers_in_postgres.ipynb) 

* Proper implementations of `head` and `tail` methods were added to `PgSubCollection`. For details, see [this tutorial](https://github.com/estnltk/estnltk/blob/7efc7a60eb15be5775c6790c0b8ca5a06259e2ae/tutorials/storage/storing_text_objects_in_postgres.ipynb);

* Possibility to append to an existing table with `PgCollection`'s `export_layer` method. Use the parameter `mode='append'` to switch on the appending mode. Read also [docstring of the method](https://github.com/estnltk/estnltk/blob/aadf87855f07b2a465eecdaebac95aef1caffeda/estnltk/storage/postgres/collection.py#L960-L1007).

* `StanzaSyntaxTagger` and `StanzaSyntaxEnsembleTagger` -- the syntax taggers use models trained with [Stanza](https://stanfordnlp.github.io/stanza/). See [tutorial](https://github.com/estnltk/estnltk/blob/ba471626227238b2b83ef7a3479b315407c44807/tutorials/syntax/syntax.ipynb) for usage, performance scores and links to models;

* `UDValidationRetagger` and `DeprelAgreementRetagger` -- retaggers for marking errors in parsed syntax. These only work for layers that make use of UD syntactic relations.
See [tutorial](https://github.com/estnltk/estnltk/blob/ba471626227238b2b83ef7a3479b315407c44807/tutorials/syntax/syntax.ipynb) for details and usage.


* WebTaggers -- taggers which annotate texts via webservices. Currently implemented web taggers: `VabamorfWebTagger`, `BertEmbeddingsWebTagger`, `SoftmaxEmbTagSumWebTagger`, `StanzaSyntaxWebTagger`, `StanzaSyntaxEnsembleWebTagger`. For details, see [this tutorial](https://github.com/estnltk/estnltk/blob/c5b30eb7b1c7eb6868ebda408a6c12a19f8dffa7/tutorials/taggers/web_taggers.ipynb);

* Wordnet method `get_synset_by_name` which can be used to retrieve a synset by its name attribute, and method `all_relation_types` for retrieving all relation types. Details in [this tutorial](https://github.com/estnltk/estnltk/blob/c5b30eb7b1c7eb6868ebda408a6c12a19f8dffa7/tutorials/wordnet/wordnet.ipynb).

## Fixed

* `PostMorphAnalysisTagger`: added `input_words_layer` parameter, because it was required for checking `morph_analysis` parent;

* `Layer.display()` crashing on an empty layer;

* `extract_sections` crashing on discontinouos spans & `trim_overlapping=True`;

* estner `Trainer`: 
	* `trainer.train` is now called after features from all documents have been extracted (makes training much faster if the number of training documents is large);
	* `ModelStorageUtil` now allows to save a newly trained model to the directory from which the settings were loaded. An exception is the default model dir, which should not be used.


* PostgreSQL interface:
    * `pgpass_parsing`: reading password from the `pgpass_file` should work now;
	* Fixed `PgCollection.create_layer`: missing\_layer is now properly specified in the data\_iterator;
	* Fix in `SubstringQuery`: added missig `required_layers` property;
	* Fix in `WhereClause`: added missing `_required_layers` for conjunction of `WhereClauses`;
	* Fixes for `And` & `Or` queries: added missing `required_layers` properties;


# [1.6.7-beta] - 2020-09-02
## Changed

* The module `parse_enc2017` was renamed to `parse_enc`. Tools were updated so that they can also be used to read *.vert files of the [Estonian National Corpus 2019](https://metashare.ut.ee/repository/browse/eesti-keele-uhendkorpus-2019-vrt-vormingus/be71121e733b11eaa6e4005056b4002483e6e5cdf35343e595e6ba4576d839fb/). So, now both ENC 2017 corpus and ENC 2019 corpus files can be read. For details, see the renewed tutorial [here](https://github.com/estnltk/estnltk/blob/9535931e9ade45fe17d5bfd0f24e4411fac02999/tutorials/corpus_processing/importing_text_objects_from_corpora.ipynb).
* Updated `text.tag_layer(layer_names)` : `layer_names` can now also be a string. So, you can use `text.tag_layer('sentences')` or `text.tag_layer('morph_analysis')`;

## Added

* Experimental noun phrase chunker, which can be used to detect non-overlapping noun phrases from the text. The tool was ported from the version 1.4.1; the tutorial is available [here](https://github.com/estnltk/estnltk/blob/9535931e9ade45fe17d5bfd0f24e4411fac02999/tutorials/taggers/noun_phrase_chunker.ipynb);
* `WordNet` synset definitions and examples. Interfaces of `WordNet` queries and similarity finding functions were also changed, see [this tutorial](https://github.com/estnltk/estnltk/blob/ca4be5942c991c380dea330a177226c35aa7dbb8/tutorials/wordnet/wordnet.ipynb) for details;
* `delete_layer()` to Postgres collection (can only be used with detached layers);

## Fixed

* `CompoundTokenTagger`: removed a speed bottleneck that appeared while processing large texts;
* `CompoundTokenTagger`'s import of `EmptyDataError` (now it should work with pandas<=1.1.0)
* `VerbChainDetector`: removed legacy attributes;
* Postgres collection's `_repr_html_`: collections which names start with the same prefix are now displayed correctly; 
* Issues in `conll_importer` and `maltparser_tagger` caused by updating the conllu package to version 3.0;


# [1.6.6-beta] - 2020-05-22
## Changed

* Updated the C++ source code of EstNLTK's Vabamorf module to be compatible with [Vabamorf's commit 7a44b62dba](https://github.com/Filosoft/vabamorf/tree/7a44b62dba66cd39116edaad57db4f7c6afb34d9) (2020-01-22). The update also adds two new binary lexicons: `2020-01-22_nosp` and `2020-01-22_sp`. However, the old binary lexicons (`2015-05-06` and `2019-10-15`) can no longer be used with the new Vabamorf, so they were removed. For details about binary lexicons, see the section _"Changing Vabamorf's binary lexicons"_ in [this tutorial](https://github.com/estnltk/estnltk/blob/d4319cd65178fc1772c2873ee9b11d238f9745a6/tutorials/nlp_pipeline/B_06_morphological_analysis.ipynb);

* Improved `CorpusBasedMorphDisambiguator`'s `count_inside_compounds` heuristic: lemmas acquired from non-compound words are now also used for reducing ambiguities of last words of compound words. In addition, a user-definable lemma skip list (`ignore_lemmas_in_compounds`) was introduced to the heuristic in order to reduce erroneous disambiguation choices. The name of heuristic's flag was changed from `count_inside_compounds` to `disamb_compound_words`. For details on the usage, see [this tutorial](https://github.com/estnltk/estnltk/blob/45eb6536d36f77284c25a1d4c7c0852d5b033e63/tutorials/nlp_pipeline/B_07b_morph_analysis_with_corpus-based_disambiguation.ipynb).

* Changed Layer removing: in order to delete a layer from `Text` object, use `text.pop_layer( layer_name )`. Old ways of removing (via `del` and `delattr`) are no longer working;

* Reorganized tutorials (including cleaned up some old stuff):

	* Removed `brief_intro_to_text_layers_and_tools.ipynb` (became redundant after `basics_of_estnltk.ipynb` was introduced);
	* Removed `text_segmentation.ipynb` (it's content is covered by segmentation tutorials in `tutorials/nlp_pipeline`);
	* Relocated tutorials:
		* `importing_text_objects_from_corpora.ipynb` to `tutorials/corpus_processing`;
		* `restoring_pretokenized_text.ipynb` to `tutorials/corpus_processing`;
		* `estnltk_basic_concepts.ipynb` to `tutorials/system`;
		* `layer_operations.ipynb` to `tutorials/system`;
		* `low_level_layer_operations.ipynb` to `tutorials/system`;
		* `MorphAnalyzedToken`'s tutorial to `tutorials/system`;
	* Introduced `tutorials/miscellaneous` (currently contains tutorials about morphological synthesis and word syllabification):


## Added

* `SpellCheckRetagger`: a Vabamorf-based spelling normalization for the words layer. For details on the usage, see [this tutorial](https://github.com/estnltk/estnltk/blob/5c5ce3a810f7a5e41602156b7044edb63e83532d/tutorials/nlp_pipeline/B_03_segmentation_words_spelling_normalization.ipynb);
* `MaltParserTagger` which analyses Text with EstNLTK's MaltParser and produces `maltparser_syntax` layer. This should be the most straightforward way of using the MaltParser. [Usage tutorial](https://github.com/estnltk/estnltk/blob/84b12bc7ece6bde6906e8d4fa0d5831d3149fce5/tutorials/syntax/syntax.ipynb);
* `VabamorfEstCatConverter` -- a tagger which can be used to convert Vabamorf's category names to Estonian (for educational purposes). For details, see [this tutorial](https://github.com/estnltk/estnltk/blob/84b12bc7ece6bde6906e8d4fa0d5831d3149fce5/tutorials/nlp_pipeline/A_01_short_introduction_and_tutorial_for_linguists.ipynb);
* A heuristic that improves syllabification of compounds in the function `syllabify_word`. The heuristic (`split_compounds`) is switched on by default. For details, see [this tutorial](https://github.com/estnltk/estnltk/blob/5c5ce3a810f7a5e41602156b7044edb63e83532d/tutorials/miscellaneous/syllabification.ipynb);
* Flag `slang_lex` to `VabamorfTagger`. The flag switches on an extended version of Vabamorf's lexicon (namely, the lexicon `2020-01-22_nosp`), which contains extra entries for analysing most common spoken and slang words;
* Flag `overwrite_existing` to `UserDictTagger`: allows to turn off overwriting of existing analyses, so that only words with `None` analyses will obtain analyses from the user dictionary; 
* Tutorial `basics_of_estnltk.ipynb`, which provides an overview of the API of EstNLTK 1.6. The tutorial also provides links to more detailed/advanced tutorials. The tutorial should be a "getting started" point for new users of EstNLTK, as well as place for more advanced users to find pointers to further information;
* Tutorial about Vabamorf-based morphological synthesis ([here](https://github.com/estnltk/estnltk/blob/5c5ce3a810f7a5e41602156b7044edb63e83532d/tutorials/miscellaneous/morphological_synthesis.ipynb)). The interface of the synthesizer is basically the same as in v1.4;
* Tutorial about Vabamorf-based word syllabification ([here](https://github.com/estnltk/estnltk/blob/5c5ce3a810f7a5e41602156b7044edb63e83532d/tutorials/miscellaneous/syllabification.ipynb));
* Updated tutorial `importing_text_objects_from_corpora` on how to import texts from Estonian UD treebank;
* Updated neural morphological tagger's tutorial: added information about where the models can be downloaded;
* `WordNet`: API that provides means to query Estonian WordNet. Compared to v1.4 queries for definition and examples are missing and synsets can be queried by wn[lemma] as opposed to v1.4's wn.synsets(lemma). Other aspects are comparable to v1.4;
* `UDPipeTagger` which analyses Text with EstNLTK's UDPipe and produces `udpipe_syntax` layer. [Usage tutorial](https://github.com/estnltk/estnltk/blob/84b12bc7ece6bde6906e8d4fa0d5831d3149fce5/tutorials/syntax/syntax.ipynb)
* Flag `fix_selfreferences` to `VislTagger`: removes self-references.  
* `Named Entity Tagging`: Taggers for named entity recognition (NER). One tagger tags whole named entities and the other tagger tags each word separately. CRF model used is the same as in v1.4.

## Fixed

* Vabamorf's initialization bug on Linux: merged fixes from [#97](https://github.com/estnltk/estnltk/issues/97) and pull [#109](https://github.com/estnltk/estnltk/pull/109), and added some conditionals to keep the whole thing compiling and running under Windows (and macOS);
* Removed a major speed bottleneck from `CompoundTokenTagger`'s patterns (annotating `compound_tokens` should be much faster now);
* Rule customization in `CompoundTokenTagger`: 1st level and 2nd level patterns can now be updated via constructor parameters `patterns_1` and `patterns_2`;
* Rule customization in `SentenceTokenizer`: all merge patterns can now be updated via constructor parameter `patterns`;
* Rule prioritizing in `SyntaxIgnoreTagger` (the output no longer has fluctuations in rule types);
* Fix in `WordTagger`: 'words' layer can now be created from detached 'tokens' and 'compound_tokens' layers;
* `syllabify_word`: do not analyse dash and slash in order to avoid crash in Vabamorf's syllabifier;
* Bug related to setting `'display.max_colwidth'` in `pandas` (affects  `pandas` versions >= 1.0.0);
* `convert_cg3_to_conll.py`: handles input `'"<s>"'` with analysis correctly 

# [1.6.5.5-beta] - 2020-04-16
A pre-release only for developers. The list of changes will be documented in the next release.

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

