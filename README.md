EstNLTK -- Open source tools for Estonian natural language processing
=====================================================================

EstNLTK provides common natural language processing functionality such as paragraph, sentence and word tokenization,
morphological analysis, named entity recognition, etc. for the Estonian language.

The project is funded by EKT ([Eesti Keeletehnoloogia Riiklik Programm](https://www.keeletehnoloogia.ee/)).


***
(!) This is branch contains an old version of EstNLTK that is no longer supported. 
Please use a newer version from the main branch: [https://github.com/estnltk/estnltk](https://github.com/estnltk/estnltk)
***

## Version 1.4.1(.1)

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

The source of the last v1.4 release is available at the [version_1.4.1.1 branch](https://github.com/estnltk/estnltk/tree/version_1.4.1.1).

## Citation

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

