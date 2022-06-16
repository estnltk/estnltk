EstNLTK-core -- core components of the EstNLTK library
===========================================================================

This package contains core components of the EstNLTK library:

* data structures: `BaseText`, `BaseLayer`, `Layer`, `Span`, `EnvelopingSpan`, `SpanList`, `Annotation`;
* tagger component interfaces: `Tagger`, `Retagger`;
* basic layer operations: flatten, merge, rebase, split layers etc.
* basic visualization and Jupyter Notebook support (HTML representations);
* functions for converting between EstNLTK's data structures and JSON / dict representations;
* skeleton for NLP pipeline (components for resolving layer dependencies and tagging layers sequentially);

Note: this package does not include linguistic analysis tools / Estonian NLP pipeline. Please use the `estnltk` package for the pipeline.

The EstNLTK project is funded by EKT ([Eesti Keeletehnoloogia Riiklik Programm](https://www.keeletehnoloogia.ee/)).

### Installation

EstNLTK-core is available as a PyPI wheel:  

```
pip install estnltk_core==1.7.0
```

And as an Anaconda package:

```
conda install -c estnltk -c conda-forge estnltk_core=1.7.0
```

Supported Python versions: 3.7+

### Documentation

Information about EstNLTK-core's API is provided in docstrings of classes and methods. Browse the source for details.  

### Source

The source of the package can be found at [main branch](https://github.com/estnltk/estnltk/tree/main/estnltk_core).

---

License: GNU General Public License v2.0

(C) University of Tartu  