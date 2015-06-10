============
Installation
============

Quick installation with pip
===========================

The easiest way to install Estnltk is using the standard ``pip`` tool, which downloads
the latest Estnltk version from PyPi repository, builds it and installs it::

    pip install estnltk

However, in order the command to succeed, you need to have the necessary dependencies installed your system,
regardless of the OS you run.

**NB! Check section about post-installation steps as well.**

Dependencies
============

**Python with development headers.** https://www.python.org/ .
The most obvious dependency of course is Python itself.
Estnltk currently supports *versions 2.7 and 3.4*.
Other versions may work as well, but are not tested.
Python installer for Windows includes the development headers that are saved to the Python folder.
In Linux, depending on the flavor and distribution, you usually have to install the headers separately.
Either by building the Python from source or using a package manager. The package is typically named
``python-dev`` for Python 2 and ``python3-dev`` for Python3.

**SWIG wrapper generator**, http://swig.org/ .
SWIG is a software development tool that connects programs written in C and C++ with a variety of high-level programming languages.
SWIG is used with different types of target languages including common scripting languages such as Javascript, Perl, PHP, Python, Tcl and Ruby.
Estnltk contains C++ code that uses SWIG to extend Python.
In Linux, this package is usually named ``swig`` and can be installed with a package manager.

**C++ compiler**.
In *Linux* systems, Estnltk can be built using GNU C++ compiler which can be installed with a package manager.
Typically the package is named ``g++``.
It is also possible to manually download the compiler from https://gcc.gnu.org/ .

In *Windows*, we recommend using Visual Studio 2008 for Python2.7 and Visual Studio 2010 for Python3.4.
Note that for 64-bit versions you need to have also 64-bit toolchains, which are not included in Express versions of the Visual Studio.
We recommend downloading the full Visual Studio SDK and performing the building process through the Visual studio command prompt interface.

**Java VM**.
Several Estnltk components are written in Java and interfaced with Python.
Therefore, you also need latest Java Runtime installed on your system.
The ``java`` virtual machine must be in the system ``PATH``.
We recommend using Oracle Java http://www.oracle.com/technetwork/java/javase/downloads/index.html,
although alternatives such as OpenJDK (http://openjdk.java.net/) should also work.

**setuptools**. https://pypi.python.org/pypi/setuptools .
A popular toolchain to build Python packages. In Linux package managers, typically called ``python-setuptools`` .

**Numpy/Scipy stack**. http://www.scipy.org/install.html
We include numpy/scipy in this list as it is quite difficult to build it from scratch
due to ATLAS/BLAS dependencies. Thus, we recommend installing a pre-built binaries (see http://www.scipy.org/install.html).

**python-crfsuite (version 0.8.1)**. Conditional random field library. There should be no problems building it automatically,
but just in case we have included pre-built binaries in our repository:
https://github.com/estnltk/estnltk/tree/master/dist/python-crfsuite .

**Other dependencies**

The rest of the dependencies should be easy to build, but just in case they wont,
here is the list of their names and precise version required by Estnltk.

Windows users should check out Christoph Gohlke's website: http://www.lfd.uci.edu/~gohlke/pythonlibs/ ,
that contains an marvellous list of pre-built binaries, including the ones required by Estnltk.

* **regex (version 2015.03.18)**
* **six (version 1.9.0)**
* **nltk (version 3.0.2)**
* **pandas (version 0.15.2)**
* **cached-property (version 1.2.0)**
* **beautifulsoup4 (version 4.3.2)**


Running the tests
=================

After you have installed the library, you should run the unit tests::

    python -m unittest discover estnltk.tests

Note that when you built directly from cloned Estnltk repository, navigate away from it as
running the command in the same directory can cause problems.

When unit tests pass, you know you have installed all necessary dependencies of the library.

Building from source
====================

First thing after installing the dependencies is to get the source.
One option is cloing the repository using latest code::

    git clone https://github.com/estnltk/estnltk estnltk
    
or from mirror repository::

    git clone https://estnltk.cs.ut.ee/timo/estnltk.git estnltk

or download it as a compressed zip::    

    https://estnltk.cs.ut.ee/estnltk/estnltk/repository/archive.zip
    
Then, extract the sources and issue following commands in the downloaded/cloned folder to build and install::

    python setup.py build
    sudo python setup.py install
    
Note that ``python`` usually refers to default Python version installed with the system.
Usually, you can also use more specific versions by replacing ``python`` with ``python2.7`` or ``python3.4``.
Note that the same commands work when building in Windows, but you need to execute them in Visual Studio SDK command prompt.


Windows installers
==================

You can use pre-built windows installers for Estnltk.
Note that you still need to install the dependencies separately.

32-bit:

* https://github.com/estnltk/estnltk/blob/master/dist/estnltk-1.2.win32-py2.7.msi
* https://github.com/estnltk/estnltk/blob/master/dist/estnltk-1.2.win32-py3.4.msi

64-bit:

* https://github.com/estnltk/estnltk/blob/master/dist/estnltk-1.2.win-amd64-py2.7.msi
* https://github.com/estnltk/estnltk/blob/master/dist/estnltk-1.2.win-amd64-py3.4.msi
    


Post-installation steps
=======================

Downloading NLTK tokenizers for Estonian. These are necessary for tokenization::

    python -m nltk.downloader punkt

Estnltk comes with pre-built named entity taggers, but you can optionally rebuild them if you have lost them for some reason.
The command to build the default named entity tagger for Estonian::

    python -m estnltk.tools.train_default_ner_model

