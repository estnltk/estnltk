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

