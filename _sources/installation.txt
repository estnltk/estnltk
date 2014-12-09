============
Installation
============

We do not recommend building the library from source in Windows as it can be very time-consuming.
Instead, we provide binary installers that can be downloaded from project `repository`_.

.. _repository:: https://github.com/tpetmanson/estnltk

Installers for 32 and 64 bit versions of Python2.7 and Python3.4:

* installer1
* installer2
* installer3
* installer4

However, in order to get it working, you need to install these dependencies:
TODO: try to put them all in a single installer

* pyvabamorf
* nltk
* whatever else


Building from source
--------------------

To build the `estnltk` module from source, we recommend using Visual Studio 2008 for Python2.7 and Visual Studio 2010 for Python3.4.
Note that for 64-bit versions you need to have also 64-bit toolchains, which are not included in Express versions of the Visual Studio.
Please read the Linux section of required dependencies.

Linux
-----

Although much development of the library is done in Linux, there are no pre-built binaries.
Fortunately, building software from source in Linux is somewhat easier than in Windows, so we provide the necessary steps.

First, you need to have installed following dependencies (typically installable from the package manager of your distro):

* Python development files
* GCC C++ compiler
* SWIG wrapper generator
* list here dependencies of dependencies etc.


There are no pre-built binaries for Linux. For building, you need to have installed Python development files (headers and libraries), GCC C++ compiler and also SWIG wrapper generator ( http://swig.org/ ). Depending on your distribution, you might be able to simply install them from software repositories of your distribution.

After all dependencies are installed, the easiest way to build the pyvabamorf package is using the pip tool:

sudo pip install pyvabamorf
Another way is to clone the repository and execute the setup.py script inside:

sudo python setup.py install
Then run the tests and see if they all pass (NB! Do not run them from same directory you have cloned the source distribution):


Post-installation steps
-----------------------

Downloading NLTK tokenizers for Estonian::

    python -m nltk.downloader punkt

Building default named entity tagger for Estonian (optional, installation should already come with a pre-trained model)::

    python -m estnltk.ner train_default_model
