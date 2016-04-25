.. _installation_tutorial:

============
Installation
============

Estnltk works with Python versions 2.7 and 3.4 on Windows and Linux.

Installation on Linux Mint 17.2
===============================

In Linux, install dependences, install estnltk and test the installation::

    sudo apt-get install g++ python3-dev python3-pip python3-wheel python3-numpy swig
    sudo pip3 install estnltk

As a first test, try to run this line of code in your terminal::

    python3 -c "import estnltk; print( estnltk.Text('Tere estnltk').lemmas )"

It should print::

    [nltk_data] Downloading package punkt to /home/user/nltk_data...
    [nltk_data]   Unzipping tokenizers/punkt.zip.
    ['tere', 'estnltk']

You see that NLTK data is being dowloaded on first use of the library.
Then, run the unittest suite::

    python3 -m estnltk.run_tests

This should report the number of tests run and the status. If it is "OK", then you are good to go::

    Ran 157 tests in 35.207s

    OK

Although this is Linux Mint 17.2 specific, it should also work in Ubuntu.


(Optional) You might want to use Oracle JDK instead of OpenJDK, because Estnltk uses Java for some tasks.
These tutorials will help you install it: http://community.linuxmint.com/tutorial/view/1372 ,
http://community.linuxmint.com/tutorial/view/1091 .


Installation on Windows
=======================
The process involves installation of the pre-compiled version of estnltk and its dependencies so that no compiler is required. We assume you have python 3.4 installed and run a 64-bit Windows OS. Installation on a 32-bit platform is identical.

First, obtain the required packages:

* numpy-1.10.0b1+mkl-cp34-none-win_amd64.whl from http://www.lfd.uci.edu/~gohlke/pythonlibs/ 
* python_crfsuite-0.8.3-cp34-none-win_amd64.whl from https://github.com/estnltk/estnltk/blob/version1.4/dist/python-crfsuite
* estnltk-1.4-cp34-cp34m-win_amd64.whl from https://github.com/estnltk/estnltk/releases

Next, install the dependencies and estnltk::

    python.exe -m pip install numpy-1.10.0b1+mkl-cp34-none-win_amd64.whl
    python.exe -m pip install python_crfsuite-0.8.3-cp34-none-win_amd64.whl
    python.exe -m pip install estnltk-1.4-cp34-cp34m-win_amd64.whl
    
Make sure the installation was successfull by running::

    python.exe -c "import estnltk; print( estnltk.Text('Tere estnltk').lemmas )"

which should output::

    [nltk_data] Downloading package punkt to /home/user/nltk_data...
    [nltk_data] Unzipping tokenizers/punkt.zip.
    ['tere', 'estnltk']

Finally, run the unittests::

    python.exe -m estnltk.run_tests

This should report the number of tests run and the status. If the status is "OK", then you are good to go::

    Ran 157 tests in 35.207s

    OK

Full list of dependencies
=========================

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

**Elasticsearch server**.
Estnltk database module has a wrapper around Elastic database.
In order to use Elastic, see https://www.elastic.co/products/elasticsearch .

**setuptools**. https://pypi.python.org/pypi/setuptools .
A popular toolchain to build Python packages. In Linux package managers, typically called ``python-setuptools`` .

**Numpy/Scipy stack**. http://www.scipy.org/install.html
We include numpy/scipy in this list as it is quite difficult to build it from scratch
due to ATLAS/BLAS dependencies. Thus, we recommend installing a pre-built binaries (see http://www.scipy.org/install.html).

**python-crfsuite (version 0.8.3)**. Conditional random field library. There should be no problems building it automatically,
but just in case we have included pre-built binaries in our repository:
https://github.com/estnltk/estnltk/tree/master/dist/python-crfsuite .

**Other dependencies**

The rest of the dependencies should be easy to build, but just in case they wont,
here is the list of their names and precise version required by Estnltk.

Windows users should check out Christoph Gohlke's website: http://www.lfd.uci.edu/~gohlke/pythonlibs/ ,
that contains an marvellous list of pre-built binaries, including the ones required by Estnltk.

* **regex (version 2015.07.19)**
* **six (version 1.9.0)**
* **nltk (version 3.0.4)**
* **pandas (version 0.16.2)**
* **cached-property (version 1.2.0)**
* **beautifulsoup4 (version 4.4.0)**
* **elasticsearch (1.6.0)**
* **html5lib (0.9999999)**


Building from source
====================

First thing after installing the dependencies is to get the source.
One option is cloing the repository using latest code::

    git clone https://github.com/estnltk/estnltk estnltk

    
Then, issue following commands in the cloned folder to build and install::

    python3 setup.py build
    sudo python3 setup.py install
    
Note that ``python`` usually refers to default Python version installed with the system.
Usually, you can also use more specific versions by replacing ``python`` with ``python2.7`` or ``python3.4``.
Note that the same commands work when building in Windows, but you need to execute them in Visual Studio SDK command prompt.

If you want to set up estnltk for development, see :ref:`developer_guide`.


Post-installation steps
=======================

Downloading NLTK tokenizers for Estonian. These are necessary for tokenization.
This should happen automatically, but if it does not, use this command to download them::

    python3 -m nltk.downloader punkt

Estnltk comes with pre-built named entity taggers, but you can optionally rebuild them if you have lost them for some reason.
The command to build the default named entity tagger for Estonian::

    python3 -m estnltk.tools.train_default_ner_model

