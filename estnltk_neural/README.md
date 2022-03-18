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
pip install estnltk_neural==1.7.0rc0
```

And as an Anaconda package:

```
conda install -c estnltk -c conda-forge estnltk_neural=1.7.0rc0
```

Supported Python versions: 3.7+

### Neural models

Neural models are not distributed with the package, and must be downloaded separately from the repository [https://entu.keeleressursid.ee/entity/folder/7510](https://entu.keeleressursid.ee/entity/folder/7510). 
Neural models for syntactic parsing can be downloaded from [https://entu.keeleressursid.ee/entity/folder/9785](https://entu.keeleressursid.ee/entity/folder/9785) (see also the [tutorial](https://github.com/estnltk/estnltk/blob/version_1.6/tutorials/syntax/syntax.ipynb) of syntactic parsers).

### Documentation

Updating tutorials is currently work-in-progress. 
The information is provided in docstrings of classes and methods.
You can find old tutorials [here](https://github.com/estnltk/estnltk/tree/version_1.6/tutorials).

### Source

The source of the package can be found at branch [devel\_1.6\_split](https://github.com/estnltk/estnltk/tree/devel_1.6_split/estnltk_neural).
The main repository is  https://github.com/estnltk/estnltk

---

License: GNU General Public License v2.0

(C) University of Tartu  