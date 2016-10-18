#!/usr/bin/env bash

#Here we perform the build.
conda build -c conda-forge -c estnltk --py "$PYTHON_TARGET" conda-recipe
conda build -c conda-forge -c estnltk --py "$PYTHON_TARGET" conda-recipe --output > $HOME/outfile.txt

