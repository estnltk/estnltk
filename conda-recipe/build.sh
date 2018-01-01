#!/bin/bash
CC=${PREFIX}/bin/g++
CXX=${PREFIX}/bin/g++
export PYTHONNOUSERSITE=1
$PYTHON setup.py build
$PYTHON setup.py install
#$PYTHON setup.py install --single-version-externally-managed --record=record.txt
