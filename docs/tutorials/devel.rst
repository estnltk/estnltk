=======================
Estnltk developer guide
=======================

This document is for everyone who is working on Estnltk project (or wishes to work), but do not know how to get started.

Version control and branches
============================

We have three repositories where we store Estnltk code: you should push/pull every time from all of them
 to make them synced.

First, modify your ``.git/setup`` configuration to look like following::

    [core]
        repositoryformatversion = 0
        filemode = true
        bare = false
        logallrefupdates = true
    [remote "github"]
        url = git@github.com:estnltk/estnltk.git
        fetch = +refs/heads/*:refs/remotes/github/*
    [remote "ut"]
        url = git@estnltk.cs.ut.ee:timo/estnltk.git
        fetch = +refs/heads/*:refs/remotes/ut/*
    [remote "keeleressursid"]
        url = git@gitlab.keeleressursid.ee:timo-petmanson/estnltk.git
        fetch = +refs/heads/*:refs/remotes/keeleressursid/*
    [remote "origin"]
        url = git@github.com:estnltk/estnltk.git
        url = git@estnltk.cs.ut.ee:timo/estnltk.git
        url = git@gitlab.keeleressursid.ee:timo-petmanson/estnltk.git
    [branch "master"]
        remote = origin
        merge = refs/heads/master
    [branch "devel"]
        remote = origin
        merge = refs/heads/devel

Second, use commands

git push origin master
git pull origin master

to perform pulls and pushes to both repositories without no extra hassel.

Third, your're done! ;)


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

TODO