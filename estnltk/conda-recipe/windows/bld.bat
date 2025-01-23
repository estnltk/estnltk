$PYTHON -m pip install . -vv --no-deps --no-build-isolation "-C--build-option=build_ext" 
if errorlevel 1 exit 1
