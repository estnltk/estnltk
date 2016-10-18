#!/usr/bin/env bash

#script step follows the install step. Here we perform the build.

conda build -c conda-forge -c estnltk --py "$PYTHON_TARGET" conda-recipe
BUILT_FILE="conda build --py "$PYTHON_TARGET" conda-recipe --output"
export BUILT_FILE
anaconda logout #Otherwise consecutive builds might fail.

