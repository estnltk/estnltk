EstNLTK -- Open source tools for Estonian natural language processing
=====================================================================

EstNLTK provides common natural language processing functionality such as paragraph, sentence and word tokenization,
morphological analysis, named entity recognition, etc. for the Estonian language.

The project is funded by EKT (Eesti Keeletehnoloogia Riiklik Programm, https://www.keeletehnoloogia.ee/).

Currently, there are two branches of EstNLTK:

* version **1.6** -- the new branch, which is in a beta status and under development. The version 1.6.0-beta is available from [Anaconda package repository](https://anaconda.org/estnltk/estnltk). It contains analysis tools up to the level of morphological analysis, but it does not contain all the functionalities available in **1.4.1**. Supported Python versions: 3.5+;
  
* version **1.4.1** -- the old branch, which contains full functionality of different analysis tools. Also available via [Anaconda package repository](https://anaconda.org/estnltk/estnltk). Available for Python 3.4+ and Python 2.7, although recommended version is Python 3.5.*. Python 3.6 is not supported;

## Version 1.6

### Installation
The recommended way of installing estnltk is by using the [anaconda python distribution](https://www.continuum.io/downloads) and python 3.5+.

Installable packages have been built for osx, windows-64, and linux-64.

The command for installing is:
```
conda install -c estnltk -c conda-forge estnltk
```

The alternative way for installing if you are unable to use the anaconda distribution is:
```
python -m pip install estnltk
```

This is slower, more error-prone and requires you to have the appropriate compilers for building the scientific computation packages for your platform.

### Documentation

Documentation for 1.6 currently comes in the form of [jupyter notebooks](http://jupyter.org), which are available here: https://github.com/estnltk/estnltk/tree/version_1.6/tutorials

## Version 1.4.1

### Installation
The recommended way of installing estnltk is by using the [anaconda python distribution](https://www.continuum.io/downloads) and python 3.5+.

We have installable packages built for osx, windows-64, and linux-64.

The command for installing is:
```
conda install -c estnltk -c conda-forge estnltk=1.4.1
```

If you want to use EstNLTK in an interactive web application, type the command

```
jupyter notebook
```
To run our tutorials, [download them as a zip file](https://github.com/estnltk/tutorials/archive/master.zip), unpack them to a directory and run the command `jupyter notebook` in that directory.  

---------

The alternative way for installing if you are unable to use the anaconda distribution is:

`python -m pip install estnltk`

This is slower, more error-prone and requires you to have the appropriate compilers for building the scientific computation packages for your platform. 

Find more details in the [installation tutorial for version 1.4](http://estnltk.github.io/estnltk/1.4/tutorials/installation.html).

### Documentation

Release 1.4.1 documentation is available at http://estnltk.github.io/estnltk/1.4.1/index.html.
For previous versions refer to http://estnltk.github.io/estnltk.
For more tools see http://estnltk.github.io.

Additional educational materials on EstNLTK version 1.4 are available on web pages of the NLP courses taught at the University of Tartu:

  * https://github.com/d009/EstNLP
  * https://courses.cs.ut.ee/2015/pynlp/fall

## Citation

Once you use Estnltk in your work, please cite us as follows:

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
