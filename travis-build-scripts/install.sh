#!/usr/bin/env bash

#In the install step we install the dependencies for building esntltk.

sudo apt-get update
sudo apt-get -y remove swig

wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh;
bash miniconda.sh -b -p "$HOME/miniconda"
export PATH="$HOME/miniconda/bin:$PATH"

conda config --set always_yes yes O

#do not change the bash prompt
conda config --set changeps1 no
conda update -q conda


  - conda install conda-build anaconda-client
  o
#Useful for debugging any issues with conda
conda info -a
conda install conda-build anaconda-client
anaconda login --hostname "$TRAVIS_BUILD_NUMBER"_"$PYTHON_TARGET" --username estnltk --password "$ESTNLTK_ANACONDA_PASSWORD"
