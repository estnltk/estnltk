@ECHO OFF
SET PYTHONPATH=%PYTHONPATH%;C:\Users\kittask\Documents\estnltk\
CALL conda activate estnltk-3.6
CALL jupyter notebook
CALL conda deactivate
