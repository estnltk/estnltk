## Solving the import conflict between `estnltk.vabamorf` and `hfst`

### Description of the conflict

Once you have [installed HFST via PyPI](https://pypi.org/project/hfst/#installation-via-pypi), and attempt to use it along with `estnltk.vabamorf`, you will get a strange import conflict between the two modules.

If you import `hfst` as a first thing in the program, everything works fine:

	import hfst
    from estnltk.vabamorf.vabamorf import Vabamorf, StringVector
    
    sv = StringVector(2)
    sv[0] = 'Tere'

    vm_instance = Vabamorf.instance()
    results = vm_instance.analyze(words=sv)
	print(results)

But if you change the import order, like in this example:

    from estnltk.vabamorf.vabamorf import Vabamorf, StringVector
	import hfst
    
    sv = StringVector(2)
    sv[0] = 'Tere'

    vm_instance = Vabamorf.instance()
    results = vm_instance.analyze(words=sv)
	print(results)

then the program will crash with a _"Segmentation Fault"_, both on Windows and Linux systems.

---

A closer examination showed that the problem is related to the `StringVector` Python class that wraps around the STL corresponding classes, and that is used by both `estnltk.vabamorf` and `hfst` in their swig interface.

---

### Solution for win-32

1. Change [`setup.py`](https://github.com/estnltk/estnltk/blob/version_1.6/setup.py#L33): remove the argument `'-builtin'` from the list `swig_opts`. This will generate wrapper classes `SwigPyIterator`, `StringVector`, `AnalysisVector` etc inside the file `estnltk/vabamorf/vabamorf.py` during the compilation of the `estnltk.vabamorf` extension;

2. Recompile the `estnltk.vabamorf` extension's binaries with the Swig version 3.0.12. Use either `python setup.py build` (for local build) or `python setup.py install` (for local build and global installation). 

3. Because both `hfst 3.15.0.0b0` and `estnltk.vabamorf` have been generated with the same settings (both use Swig version 3.0.12 and no `'-builtin'` option), the should now run smoothly together. Case closed.

### Solution for linux-64

1. Change [`setup.py`](https://github.com/estnltk/estnltk/blob/version_1.6/setup.py#L33): remove the argument `'-builtin'` from the list `swig_opts`. This will generate wrapper classes `SwigPyIterator`, `StringVector`, `AnalysisVector` etc inside the file `estnltk/vabamorf/vabamorf.py` during the compilation of the `estnltk.vabamorf` extension;

2. Two options:
    
    2.1. First, recompile the `estnltk.vabamorf` extension's binaries with Swig version 3.0.12. Use either `python setup.py build` (for local build) or `python setup.py install` (for local build and global installation). Second, download [`hfst` source](https://github.com/hfst/hfst) and build the module `hfst/python/`. Again, it is important that you use the same Swig version (3.0.12) for building. Third, overwrite the `so` file of the `pip`-installed `hfst` (located in your Anaconda `envs` dir: `'.../envs/{my_env}/lib/python3.5/site-packages/_libhfst.cpython-35m-x86_64-linux-gnu.so'`) with the newly compiled `so` file (with the same name). Now, both  `pip`-installed `hfst 3.15.0.0b0` and `estnltk.vabamorf` should run smoothly together. Case closed. **(This worked in practice)**

	2.2. Recompile the `estnltk.vabamorf` extension's binaries with Swig version 3.0.8. Use either `python setup.py build` (for local build) or `python setup.py install` (for local build and global installation). Now, both  `pip`-installed `hfst 3.15.0.0b0` and `estnltk.vabamorf` should run smoothly together, because Linux wrapper files for `hfst 3.15.0.0b0` were also created with Swig version 3.0.8. Case closed. **(This hasn't been tried out in practice yet)**