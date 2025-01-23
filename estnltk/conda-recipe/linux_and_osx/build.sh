#!/bin/bash
CC=${PREFIX}/bin/g++
CXX=${PREFIX}/bin/g++
$PYTHON -m pip install . -vv --no-deps --no-build-isolation "-C--build-option=build_ext" 
