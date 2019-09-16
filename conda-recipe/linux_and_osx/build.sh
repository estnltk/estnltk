#!/bin/bash
CC=${PREFIX}/bin/g++
CXX=${PREFIX}/bin/g++
$PYTHON setup.py build
$PYTHON setup.py install --single-version-externally-managed --record=record.txt
