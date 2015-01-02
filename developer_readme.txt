Building releases
=================

When creating pip source packages with `python setup.py sdist upload`, make sure you create them using Python2.7 by first calling

clean.sh
python2.7 setup.py build

This makes sure that SWIG generates code that works with both Python2.7 and Python3.4.
SWIG with Python3 uses function annotations that do not work with 2.7.
Also, run `build` and `sdist` in separate commands, because otherwise the generated wrapper is not included in the source distribution (?).

When building Windows installers, also run clean, build and bdist as separate commands.
Always test the installer.
Do not forget to uninstall the previous version.
Some unit tests with Python2.7 do not work in Windows due to Python multiprocessing bugs (this can be fixed by optionally excluding the tests for 2.7).


Working with GIT repositories
=============================

Here is a tip how to work with both Github and estnltk.cs.ut.ee repositories in a dual setup.

First, modify your .git/setup configuration to look like following:

[core]
	repositoryformatversion = 0
	filemode = true
	bare = false
	logallrefupdates = true
[remote "github"]
	url = git@github.com:tpetmanson/estnltk.git
	fetch = +refs/heads/*:refs/remotes/github/*
[remote "ut"]
	url = git@estnltk.cs.ut.ee:timo/estnltk.git
	fetch = +refs/heads/*:refs/remotes/ut/*
[remote "origin"]
	url = git@github.com:tpetmanson/estnltk.git
	url = git@estnltk.cs.ut.ee:timo/estnltk.git
[branch "master"]
	remote = ut
	merge = refs/heads/master
[gui]
	wmstate = normal
	geometry = 844x391+0+0 189 177


Second, use commands

git push origin master
git pull origin master

to perform pulls and pushes to both repositories without no extra hassel.

Third, your're done! ;)

