#!/bin/bash

conda create --name estnltk-3.6 python=3.6
conda install -n estnltk-3.6 jupyter
conda install -n estnltk-3.6 numpy
conda install -n estnltk-3.6 pandas
conda install -n estnltk-3.6 -c estnltk -c conda-forge estnltk
conda install -n estnltk-3.6 -c conda-forge conllu
conda install -n estnltk-3.6 psycopg2
conda install -n estnltk-3.6 pytest
conda install -n estnltk-3.6 -c conda-forge rise
conda install -n estnltk-3.6 -c conda-forge nbval
conda install -n estnltk-3.6 pydot
