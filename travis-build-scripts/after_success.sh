#!/usr/bin/env bash

#run tests here
filename=`cat $HOME/outfile.txt`


echo "Starting install from $filename"
conda install -y -c conda-forge -c estnltk $filename
echo "install done"



echo "running tests"
python -m estnltk.run_tests
echo "tests ran"