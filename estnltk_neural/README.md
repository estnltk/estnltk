EstNLTK neural -- EstNLTK's linguistic analysis based on neural models
===========================================================================

This package contains EstNLTK's linguistic analysis tools that use neural models:

* neural morphological tagger (disambiguator);
* bert embeddings tagger;
* stanza syntax tagger and stanza ensemble syntax tagger;

The EstNLTK project is funded by EKT ([Eesti Keeletehnoloogia Riiklik Programm](https://www.keeletehnoloogia.ee/)).

### Installation

EstNLTK-neural is available as a PyPI wheel:  

```
pip install estnltk_neural==1.7.0
```

And as an Anaconda package:

```
conda install -c estnltk -c conda-forge estnltk_neural=1.7.0
```

Supported Python versions: 3.7+

### Neural models

Models required by neural tools are large, and therefore cannot be distributed with this package. 
However, our tagger classes are implemented in a way that once you create an instance of a neural tagger, you'll be asked  for a permission to download missing models, and if you give the permission, the model will be downloaded (and installed in a proper location) automatically. 
If needed, you can also change the default location where downloaded models will be placed, see [this tutorial](https://github.com/estnltk/estnltk/blob/main/tutorials/estnltk_resources.ipynb) for details.

### Documentation

You can find tutorials of neural morph disambiguator and bert embeddings tagger [here](https://github.com/estnltk/estnltk/tree/main/tutorials/estnltk_neural).

Tutorials about stanza syntactic analysers are currently in [this file](https://github.com/estnltk/estnltk/blob/fc796f8383e190d2fbaa0957b1b2240def126b3f/tutorials/nlp_pipeline/C_syntax/04_syntactic_analysers_and_utils.ipynb) (but this location is about to change in future releases).

### Source

The source of the last release is available at the [main branch](https://github.com/estnltk/estnltk/tree/main/estnltk_neural).

---

License: GNU General Public License v2.0

(C) University of Tartu  