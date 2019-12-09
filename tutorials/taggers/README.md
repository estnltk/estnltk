Taggers
=======

Tagger is a class that creates a layer and attaches it to the text object.

* [Tagger](base_tagger.ipynb) is a base class for taggers.
* [make_tagger_test](tagger_test_maker.ipynb) method helps to create test files for taggers.

* [Vocabulary](vocabulary.ipynb) is an input data object for SpanTagger, PhraseTagger, RegexTagger.
* [PhraseTagger](phrase_tagger.ipynb) tags sequencial attribute values of a layer.
* [RegexTagger](regex_tagger.ipynb) tags matches of regular expressions on the text.
* [SpanTagger](span_tagger.ipynb) tags spans on a pre-annotated layer of the Text object

* [RobustDateNumberTagger](measurement_tagging.ipynb) wraps RegexTagger to tag dates and numbers.
* [DateTagger](date_tagger.ipynb) yet another tagger for dates. 
* [TimexTagger](temporal_expression_tagger.ipynb) provides most complete tagging for dates and other temporal expressions (such as times, durations and recurrences). Its analysis output is based on the TIMEX3 tag from [TimeML](http://www.timeml.org/).

* [AddressTagger](address_tagging.ipynb) tags addresses on a text and extracts the street name, house number, zip code, town, and county from the text.
* [AdjectivePhraseTagger](adjective_phrase_tagger.ipynb) tags simple adjective phrases on the text.
* [VerbChainDetector](verb_chain_detector.ipynb) tags main verbs and their extensions (verb chains) in clauses.


* [Atomizer](atomizer.ipynb) forgets the parent of the input layer.
* [CombinedTagger](combined_tagger.ipynb) runs input taggers in parallel and resolves conflicts.
* [MergeTagger](merge_tagger.ipynb) merges input layers.
* [DisambiguatingTagger](disambiguator.ipynb) disambiguates ambiguous layer.
* [GapTagger and EnvelopingGapTagger](gaps_tagging.ipynb) tag gaps in input layers.

