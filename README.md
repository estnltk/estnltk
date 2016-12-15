Estnltk -- Open source tools for Estonian natural language processing
=====================================================================

Estnltk provides common natural language processing functionality such as paragraph, sentence and word tokenization,
morphological analysis, named entity recognition, etc. for the Estonian language.

The project is funded by EKT (Eesti Keeletehnoloogia Riiklik Programm, https://www.keeletehnoloogia.ee/).


## Installation
The recommended way of installing estnltk is by using the [anaconda python distribution](https://www.continuum.io/downloads) and python 3.5+.

We have installable packages built for osx, windows-64, and linux-64.

The command for installing estnltk is:
```
conda install -c estnltk -c conda-forge estnltk
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

Find more details in the [installation tutorial](http://estnltk.github.io/estnltk/1.4/tutorials/installation.html).

## Documentation

Release 1.4.1 documentation is available at http://estnltk.github.io/estnltk/1.4.1/index.html.
For previous versions refer to http://estnltk.github.io/estnltk.
For more tools see http://estnltk.github.io.

Additional educational materials on estnltk are available on the web page of the NLP course taught at the University of Tartu: https://courses.cs.ut.ee/2015/pynlp/fall.

## Citation

Once you use Estnltk in your work, plase cite us as follows:

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
