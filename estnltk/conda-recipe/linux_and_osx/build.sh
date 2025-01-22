#!/bin/bash
CC=${PREFIX}/bin/g++
CXX=${PREFIX}/bin/g++
$PYTHON -m build "-C--build-option=build_ext" .

