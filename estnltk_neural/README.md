EstNLTK neural -- EstNLTK's linguistic analysis based on neural models
===========================================================================

This package contains EstNLTK's linguistic analysis tools that use neural models:

* neural morphological tagger ( disambiguator );
* bert embeddings tagger;
* bert NER tagger;
* stanza syntax tagger and stanza ensemble syntax tagger;
* pronominal coreference tagger v1 (relies on stanza for input preprocessing);

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

Supported Python versions: 3.8+

### Neural models

Models required by neural tools are large, and therefore cannot be distributed with this package. 
However, our tagger classes are implemented in a way that once you create an instance of a neural tagger, you'll be asked  for a permission to download missing models, and if you give the permission, the model will be downloaded (and installed in a proper location) automatically. 
If needed, you can also change the default location where downloaded models will be placed, see [this tutorial](https://github.com/estnltk/estnltk/blob/44de136c5fa046b1050fd5006ce1bb9b2225100c/tutorials/basics/estnltk_resources.ipynb) for details.

### Documentation

EstNLTK's [NLP component tutorials](https://github.com/estnltk/estnltk/tree/main/tutorials/nlp_pipeline) also cover information about neural taggers. 

### Source

The source of the last release is available at the [main branch](https://github.com/estnltk/estnltk/tree/main/estnltk_neural).

---

License: GNU General Public License v2.0

(C) University of Tartu  