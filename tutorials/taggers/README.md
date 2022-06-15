Taggers
=======

Tagger is a generic class that creates a layer and attaches it to the text object.

🛠️ [This tutorial](base_tagger.ipynb) gives basics about using the Tagger interface and creating your own taggers and retaggers.

🛠️ System taggers:

* [Generic taggers](system/) for comparing, manipulating and merging annotation layers, and for testing taggers.

* [Rule taggers](rule_taggers/) for text annotation using regular experssions, word listings and phrase patterns.

* [GrammarParsingTagger](finite_grammar/) for finite grammar based text annotation.

⚙️ Application taggers:

* [HfstClMorphAnalyser](hfst/) provides alternative morphological analysis via HFST tools.

* [Web taggers tutorial](web_taggers.ipynb) introduces EstNLTK's taggers that are available as a web service.

* [MorphAnalysisWebPipeline](web_pipeline_morph_analysis.ipynb) provides text segmentation and morph analysis via webservice (currently not available).

⚙️ [miscellaneous taggers](miscellaneous/) include tagging simple adjective phrases or detecting measurements and dates from medical texts.

