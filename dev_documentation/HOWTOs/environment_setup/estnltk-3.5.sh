#!/bin/bash

conda create --name estnltk-3.5 python=3.5
conda install -n estnltk-3.5 jupyter
conda install -n estnltk-3.5 -c estnltk -c conda-forge estnltk
conda install -n estnltk-3.5 -c conda-forge conllu
conda install -n estnltk-3.5 psycopg2
conda install -n estnltk-3.5 pytest
conda install -n estnltk-3.5 -c conda-forge rise
conda install -n estnltk-3.5 -c conda-forge nbval
conda install -n estnltk-3.5 pydot
