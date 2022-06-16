EstNLTK -- Open source tools for Estonian natural language processing
=====================================================================

EstNLTK provides common natural language processing functionality such as paragraph, sentence and word tokenization,
morphological analysis, named entity recognition, etc. for the Estonian language.

The project is funded by EKT ([Eesti Keeletehnoloogia Riiklik Programm](https://www.keeletehnoloogia.ee/)).

This package contains EstNLTK's basic linguistic analysis, system and database tools:

* `Text` class with the Estonian NLP pipeline;
* tokenization tools: word, sentence and paragraph tokenization; clause segmentation; 
* morphology tools: morphological analysis and disambiguation, spelling correction, morphological synthesis and syllabification, HFST based analyser and GT converter;
* information extraction tools: addresses tagger, named entity recognizer, temporal expression tagger; tools for rule based and grammar based fact extraction;
* experimental taggers: verb chain detector, noun phrase chunker, adjective phrase tagger;
* syntactic analysis tools: preprocessing for syntactic analysis, VislCG3 and Maltparser based syntactic parsers;
* Estonian Wordnet;
* web taggers -- such as bert embeddings web tagger, stanza syntax web tagger and stanza ensemble syntax web tagger;
* corpus importing tools -- tools for importing data from large Estonian corpora, such as the Reference Corpus or the National Corpus of Estonia;
* system taggers -- regex tagger, disambiguator, atomizer, merge tagger etc;
* resource utils for downloading additional resources (e.g. model files required by taggers); 
* Postgres database tools;

## Version 1.7

### Installation

EstNLTK is available for osx, windows-64, and linux-64, and for python versions 3.7 to 3.10. 
You can install the latest version via PyPI:

```
pip install estnltk==1.7.0
```

Alternatively, you can install EstNLTK via [Anaconda](https://www.anaconda.com/download). Installation steps with conda:

1. [create a conda environment](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-with-commands) with python 3.8, for instance:
```
conda create -n py38 python=3.8
```

2. [activate the environment](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#activating-an-environment), for instance:
```
conda activate py38
```

3. install EstNLTK with the command:
```
conda install -c estnltk -c conda-forge estnltk=1.7.0
```

_Note_: for using some of the tools in estnltk, you also need to have Java installed in your system. We recommend using Oracle Java http://www.oracle.com/technetwork/java/javase/downloads/index.html, although alternatives such as OpenJDK (http://openjdk.java.net/) should also work.

### Using on Google Colab

You can install EstNLTK on [Google Colab](https://colab.research.google.com) environment via command:

```
!pip install estnltk==1.7.0
```

### Documentation

EstNLTK's tutorials come in the form of [jupyter notebooks](http://jupyter.org). However, updating tutorials is currently work-in-progress.

  * [Starting point of tutorials](https://github.com/estnltk/estnltk/tree/main/tutorials/README.md) (via [nbviewer](https://nbviewer.org/github/estnltk/estnltk/tree/main/tutorials/README.md))
  * [Tutorials root folder](https://github.com/estnltk/estnltk/tree/main/tutorials) (via [nbviewer](https://nbviewer.org/github/estnltk/estnltk/tree/main/tutorials/)) 
  
Additional educational materials on EstNLTK are available on web pages of an NLP course taught at the University of Tartu:

  * [https://github.com/d009/EstNLP](https://github.com/d009/EstNLP) (in Estonian)  

Note: if you have trouble viewing jupyter notebooks in github (you get an error message _Sorry, something went wrong. Reload?_ at loading a notebook), then try to open notebooks with the help of [https://nbviewer.jupyter.org](https://nbviewer.jupyter.org)

### Source

The source of the last release is available at the [main branch](https://github.com/estnltk/estnltk/tree/main/estnltk).

Changelog is available [here](https://github.com/estnltk/estnltk/blob/main/CHANGELOG.md).

## Citation

In case you use EstNLTK in your work, please cite us as follows:

    @InProceedings{laur-EtAl:2020:LREC,
      author    = {Laur, Sven  and  Orasmaa, Siim  and  Särg, Dage  and  Tammo, Paul},
      title     = {EstNLTK 1.6: Remastered Estonian NLP Pipeline},
      booktitle = {Proceedings of The 12th Language Resources and Evaluation Conference},
      month     = {May},
      year      = {2020},
      address   = {Marseille, France},
      publisher = {European Language Resources Association},
      pages     = {7154--7162},
      url       = {https://www.aclweb.org/anthology/2020.lrec-1.884}
    }

If you use EstNLTK v1.4.1 (or older), please cite:

    @InProceedings{ORASMAA16.332,
    author = {Siim Orasmaa and Timo Petmanson and Alexander Tkachenko and Sven Laur and Heiki-Jaan Kaalep},
    title = {EstNLTK - NLP Toolkit for Estonian},
    booktitle = {Proceedings of the Tenth International Conference on Language Resources and Evaluation (LREC 2016)},
    year = {2016},
    month = {may},
    date = {23-28},
    location = {Portorož, Slovenia},
    editor = {Nicoletta Calzolari (Conference Chair) and Khalid Choukri and Thierry Declerck and Marko Grobelnik and Bente Maegaard and Joseph Mariani and Asuncion Moreno and Jan Odijk and Stelios Piperidis},
    publisher = {European Language Resources Association (ELRA)},
    address = {Paris, France},
    isbn = {978-2-9517408-9-1},
    language = {english}
    }

---

License: GNU General Public License v2.0

(C) University of Tartu  