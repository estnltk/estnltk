@ECHO OFF
CALL conda create --name estnltk-3.6 python=3.6
CALL conda install -n estnltk-3.6 jupyter
CALL conda install -n estnltk-3.6 numpy
CALL conda install -n estnltk-3.6 pandas
CALL conda install -n estnltk-3.6 -c estnltk -c conda-forge estnltk
CALL conda install -n estnltk-3.6 -c conda-forge conllu
CALL conda install -n estnltk-3.6 psycopg2
CALL conda install -n estnltk-3.6 pytest
CALL conda install -n estnltk-3.6 -c conda-forge rise
CALL conda install -n estnltk-3.6 -c conda-forge nbval
CALL conda install -n estnltk-3.6 pydot
