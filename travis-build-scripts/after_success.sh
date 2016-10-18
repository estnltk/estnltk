#!/usr/bin/env bash

#run tests here
x=`cat /outfile.txt`
conda install -y -c conda-forge -c estnltk $x
python -m estnltk.run_tests