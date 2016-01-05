#!/bin/bash
CC=${PREFIX}/bin/g++
CXX=${PREFIX}/bin/g++

#lazy and quick workaround for https://github.com/estnltk/estnltk/issues/47
#better would be to just copy the two files we need copied
#even better would be to fix the setup.py
#hoping for a fix from upstream
$PYTHON setup.py install --single-version-externally-managed --record=record.txt
$PYTHON setup.py install --single-version-externally-managed --record=record.txt
