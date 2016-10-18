#!/usr/bin/env bash

#run tests here
x=`cat $HOME/outfile.txt`
conda install -y -c conda-forge -c estnltk $x
python -m estnltk.run_tests