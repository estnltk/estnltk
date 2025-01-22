$PYTHON -m build "-C--build-option=build_ext" .
if errorlevel 1 exit 1
