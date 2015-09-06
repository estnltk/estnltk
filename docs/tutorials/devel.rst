=======================
Estnltk developer guide
=======================

This document is for everyone who is working on Estnltk project (or wishes to work), but do not know how to get started.


Version control and branches
============================



Setting up development environment
==================================


Unit testing
============

Writing documentation
=====================

Documentation resides under `docs` folder of estnltk and is generated using `Sphinx`_ document generator.

.. _Sphinx: http://sphinx-doc.org/

Setting up Sphinx
-----------------

To install Sphinx on your system, issue following commands::

    sudo pip3 install Sphinx
    sudo pip3 install numpydoc

Next, open file ``docs/conf.py`` and find the line::

    sys.path.insert(0, '/home/timo/projects/estnltk')

Add a second line there, which tells where estnltk is installed on your system.
For example, if your user name is ``estnltkdeveloper`` and estnltk is in your home folder, add::

    sys.path.insert(0, '/home/estnltkdeveloper/estnltk')


After that, move to the docs folder and run::

    make html

Now Sphinx builds the documentation and stores it in ``docs/build/html`` subfolder.


Distributing the documentation to Github pages
----------------------------------------------

If you type ``git branch -a``, you should see a remote branch ``remotes/github/gh-pages``
containing content that is served at http://estnltk.github.io/estnltk/ .
This branch does not contain any code, so check it out into another directory in order to work with it.
Then, create a subfolder with the appropriate estnltk version and copy the new documentation there.


Creating releases
=================


