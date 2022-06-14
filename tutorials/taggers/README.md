Taggers
=======

Tagger is a class that creates a layer and attaches it to the text object.
EstNLTK has both application taggers (directly providing an application such as date extraction), and system taggers (providing highly customizable  building blocks for language analysis).  

⚙️ Application taggers:

* [NerTagger](ner_tagger.ipynb) provides named entity recognition for Estonian; 
* [TimexTagger](temporal_expression_tagger.ipynb) provides tagging for dates and other temporal expressions (such as times, durations and recurrences) in general domain texts. Its analysis output is based on the TIMEX3 tag from [TimeML](https://en.wikipedia.org/wiki/TimeML).
* [RobustDateNumberTagger](measurement_tagging.ipynb) wraps RegexTagger to tag dates and numbers. For medical domain texts.
* [DateTagger](date_tagger.ipynb) yet another tagger for dates. For analysing medical domain texts. 
* [AddressTagger](address_tagging.ipynb) tags addresses on a text and extracts the street name, house number, zip code, town, and county from the text.
* [AdjectivePhraseTagger](adjective_phrase_tagger.ipynb) tags simple adjective phrases on the text.
* [VerbChainDetector](verb_chain_detector.ipynb) tags main verbs and their extensions (verb chains) in clauses.

🛠️ System taggers:

* [This tutorial](base_tagger.ipynb) gives basics about using Tagger interface and creating your own taggers.
* [make_tagger_test](tagger_test_maker.ipynb) method helps to create test files for taggers.
* [RegexTagger](regex_tagger.ipynb) tags matches of regular expressions on the text.
* [PhraseTagger](phrase_tagger.ipynb) tags sequencial attribute values of a layer.
* [SpanTagger](span_tagger.ipynb) tags spans on a pre-annotated layer of the Text object
* [Vocabulary](vocabulary.ipynb) is an input data object for SpanTagger, PhraseTagger, RegexTagger.
* [Atomizer](atomizer.ipynb) forgets the parent of the input layer.
* [CombinedTagger](combined_tagger.ipynb) runs input taggers in parallel and resolves conflicts.
* [MergeTagger](merge_tagger.ipynb) merges input layers.
* [DisambiguatingTagger](disambiguator.ipynb) disambiguates ambiguous layer.
* [GapTagger and EnvelopingGapTagger](gaps_tagging.ipynb) tag gaps in input layers.

