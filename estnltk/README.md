EstNLTK -- Open source tools for Estonian natural language processing
=====================================================================

EstNLTK provides common natural language processing functionality such as paragraph, sentence and word tokenization,
morphological analysis, named entity recognition, etc. for the Estonian language.

The project is funded by EKT ([Eesti Keeletehnoloogia Riiklik Programm](https://www.keeletehnoloogia.ee/)).

Currently, there are two branches of EstNLTK:

* version **1.6** -- the new branch, which is in a beta status and under development. The version 1.6.9beta is available from [Anaconda package repository](https://anaconda.org/estnltk/estnltk). More recently, [PyPI wheels](https://pypi.org/project/estnltk/#history) have also been created and made available under the version 1.6.9.1beta. Due to the beta status, some of the tools are limited or incomplete. Supported Python versions are 3.6, 3.7 and 3.8. The source of the latest release is available at the branch [version_1.6](https://github.com/estnltk/estnltk/tree/version_1.6), and the development source can be found at [devel_1.6](https://github.com/estnltk/estnltk/tree/devel_1.6). 
  
* version **1.4.1** -- the old branch, which contains full functionality of different analysis tools. Available via [Anaconda package repository](https://anaconda.org/estnltk/estnltk/files) for Python 3.5. PyPI packages are also available for Python 3.4, 3.5 and 2.7. Python versions 3.6, 3.7 and beyond are not supported;

## Version 1.6

### Installation
The recommended way of installing EstNLTK is by using the [anaconda python distribution](https://www.anaconda.com/download) and python 3.6+.

Installable packages have been built for osx, windows-64, and linux-64.

Installation steps with conda:

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
conda install -c estnltk -c conda-forge estnltk=1.6.9b
```

Alternatively, you can install EstNLTK via PyPI wheel.  
Wheels are available for windows-64, linux-64 and osx_64, covering Python versions 3.6 - 3.9. 
The corresponding version is 1.6.9.1beta, and it can be installed with command:

```
pip install estnltk==1.6.9.1b0
```

_Note_: The version 1.6.9b0 (conda) and 1.6.9.1b0 (PyPI) are equal considering the main functionalities. 
While the version 1.6.9b0 (and earlier EstNLTK's versions) are also  available in PyPI, the support for different platforms and Python versions is very limited in earlier PyPI releases.
If you need to use earlier versions of EstNLTK, please use our Anaconda packages. 

_Note_: for using some of the tools in estnltk, you also need to have Java installed in your system. We recommend using Oracle Java http://www.oracle.com/technetwork/java/javase/downloads/index.html, although alternatives such as OpenJDK (http://openjdk.java.net/) should also work.

### Using on Google Colab

You can install EstNLTK on [Google Colab](https://colab.research.google.com) environment via command:

```
!pip install estnltk==1.6.9.1b0
```

### Neural models

Neural models of EstNLTK are not distributed with the package, but must be downloaded separately from the repository [https://entu.keeleressursid.ee/entity/folder/7510](https://entu.keeleressursid.ee/entity/folder/7510). Neural models for syntactic parsing can be downloaded from [https://entu.keeleressursid.ee/entity/folder/9785](https://entu.keeleressursid.ee/entity/folder/9785) (see also the [tutorial](https://github.com/estnltk/estnltk/blob/version_1.6/tutorials/syntax/syntax.ipynb) of syntactic parsers).

### Documentation

Documentation for 1.6 currently comes in the form of [jupyter notebooks](http://jupyter.org), which are available here: https://github.com/estnltk/estnltk/tree/version_1.6/tutorials

Additional educational materials on EstNLTK version 1.6 are available on web pages of an NLP course taught at the University of Tartu:

  * [https://github.com/d009/EstNLP](https://github.com/d009/EstNLP) (in Estonian)

Note: if you have trouble viewing jupyter notebooks in github (you get an error message _Sorry, something went wrong. Reload?_ at loading a notebook), then try to open notebooks with the help of [https://nbviewer.jupyter.org](https://nbviewer.jupyter.org)

### Source

The source of the latest release is available at the branch [version_1.6](https://github.com/estnltk/estnltk/tree/version_1.6), and the development source can be found at [devel_1.6](https://github.com/estnltk/estnltk/tree/devel_1.6). 

## Version 1.4.1

### Installation
The recommended way of installing estnltk v1.4 is by using the [anaconda python distribution](https://www.anaconda.com/download) and python 3.5.

We have installable packages built for osx, windows-64, and linux-64. Installation steps:

1. [create a conda environment](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-with-commands) with python 3.5, for instance:
```
conda create -n py35 python=3.5
```

2. [activate the environment](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#activating-an-environment), for instance:
```
conda activate py35
```

3. install estnltk with the command:
```
conda install -c estnltk -c conda-forge nltk=3.4.4 estnltk=1.4.1
```

_Note_: for using some of the tools in estnltk, you also need to have Java installed in your system. We recommend using Oracle Java http://www.oracle.com/technetwork/java/javase/downloads/index.html, although alternatives such as OpenJDK (http://openjdk.java.net/) should also work.

If you have [jupyter notebook installed](https://test-jupyter.readthedocs.io/en/rtd-theme/install.html#using-anaconda-and-conda-recommended), you can use EstNLTK in an interactive web application. For that, type the command:

```
jupyter notebook
```

To run our tutorials, [download them as a zip file](https://github.com/estnltk/tutorials/archive/master.zip), unpack them to a directory and run the command `jupyter notebook` in that directory.  

---------

The alternative way for installing if you are unable to use the anaconda distribution is:

`python -m pip install estnltk==1.4.1.1`

This is slower, more error-prone and requires you to have the appropriate compilers for building the scientific computation packages for your platform. 

Find more details in the [installation tutorial for version 1.4](https://estnltk.github.io/estnltk/1.4/tutorials/installation.html).

### Documentation

Release 1.4.1 documentation is available at https://estnltk.github.io/estnltk/1.4.1/index.html.
For previous versions refer to https://estnltk.github.io/estnltk.
For more tools see https://estnltk.github.io.

Additional educational materials on EstNLTK version 1.4 are available on web pages of the NLP courses taught at the University of Tartu:

  * [https://github.com/d009/EstNLP/tree/v1.0\_estnltk\_v1.4](https://github.com/d009/EstNLP/tree/v1.0\_estnltk\_v1.4)
  * https://courses.cs.ut.ee/2015/pynlp/fall

### Source

The source of the latest v1.4 release is available at the [master branch](https://github.com/estnltk/estnltk/tree/master).

## Citation

In case you use EstNLTK 1.6 in your work, please cite us as follows:

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

If you use EstNLTK 1.4.1 (or older), please cite:

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
