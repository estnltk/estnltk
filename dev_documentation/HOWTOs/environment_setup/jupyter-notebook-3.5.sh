#!/bin/bash
export PYTHONPATH=/Users/swen/Documents/GIT/estnltk/:$PYTHONPATH
conda activate estnltk-3.5
jupyter notebook
conda deactivate
