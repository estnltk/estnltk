Building releases
=================

When creating pip source packages with `python setup.py sdist upload`, make sure you create them using Python2.7 by first calling

clean.sh
python2.7 setup.py build

This makes sure that SWIG generates code that works with both Python2.7 and Python3.4.
SWIG with Python3 uses function annotations that do not work with 2.7.
Also, run `build` and `sdist` in separate commands, because otherwise the generated wrapper is not included in the source distribution (?).

When building Windows installers, also run clean, build and bdist as separate commands.
Always test the installer.
Do not forget to uninstall the previous version.
Some unit tests with Python2.7 do not work in Windows due to Python multiprocessing bugs (this can be fixed by optionally excluding the tests for 2.7)