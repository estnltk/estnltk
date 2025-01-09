EstNLTK neural -- EstNLTK's linguistic analysis based on neural models
===========================================================================

This package contains EstNLTK's linguistic analysis tools that use neural models:

* bert embeddings tagger;
* bert-based named entity recognition;
* bert-based morphological features tagger and disambiguator;
* stanza syntax tagger and stanza ensemble syntax tagger;
* pronominal coreference tagger v1 (relies on stanza for input preprocessing);
* [legacy] tensorflow-based neural morphological features tagger ( disambiguator );

Note: these tools require installation of deep learning frameworks (`tensorflow`, `pytorch`), and are demanding for computational resources; they also rely on large models which need to be downloaded separately. 

The EstNLTK project is funded by EKT ([Eesti Keeletehnoloogia Riiklik Programm](https://www.keeletehnoloogia.ee/)).

### Installation

EstNLTK-neural is available as a PyPI wheel:  

```
pip install estnltk_neural
```

And as an Anaconda package:

```
conda install -c estnltk -c conda-forge estnltk_neural
```

Supported Python versions: 3.9+

### Neural models

Models required by neural tools are large, and therefore cannot be distributed with this package. 
However, our tagger classes are implemented in a way that once you create an instance of a neural tagger, you'll be asked  for a permission to download missing models, and if you give the permission, the model will be downloaded (and installed in a proper location) automatically. 
If needed, you can also change the default location where downloaded models will be placed, see [this tutorial](https://github.com/estnltk/estnltk/blob/ce224214244bd903d71283a2f1db2e4697f20e84/tutorials/basics/estnltk_resources.ipynb) for details.

### Documentation

EstNLTK's [NLP component tutorials](https://github.com/estnltk/estnltk/tree/main/tutorials/nlp_pipeline) also cover information about neural taggers:

* [bert embeddings tagger](https://github.com/estnltk/estnltk/blob/main/tutorials/nlp_pipeline/E_embeddings/bert_embeddings_tagger.ipynb);
* [named entity recognition (incl bert-based approaches)](https://github.com/estnltk/estnltk/blob/main/tutorials/nlp_pipeline/D_information_extraction/02_named_entities.ipynb);
* [bert-based morphological features tagger and disambiguator](https://github.com/estnltk/estnltk/blob/devel_1.7/tutorials/nlp_pipeline/B_morphology/08_bert_based_morph_tagger.ipynb);
* GliLem lemmatizer and morphological disambiguator;
* [stanza-based syntax taggers](https://github.com/estnltk/estnltk/blob/main/tutorials/nlp_pipeline/C_syntax/03_syntactic_analysis_with_stanza.ipynb);
* [pronominal coreference tagger v1](https://github.com/estnltk/estnltk/blob/main/tutorials/nlp_pipeline/D_information_extraction/04_pronominal_coreference.ipynb);
* [\[legacy\] tensorflow-based neural morphological features tagger ( disambiguator )](https://github.com/estnltk/estnltk/blob/main/tutorials/nlp_pipeline/B_morphology/08_neural_morph_tagger_py37.ipynb)


### Source

The source of the last release is available at the [main branch](https://github.com/estnltk/estnltk/tree/main/estnltk_neural).

## License

EstNLTK-neural is released under dual license - either GNU General Public License v2.0 or Apache 2.0 License. 
EstNLTK-neural's GliLem lemmatizer and morphological disambiguator contains code that is licensed under Mozilla Public License 2.0 (MPL 2.0).

(C) University of Tartu  