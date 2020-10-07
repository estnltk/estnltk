## Solving the conflict between `estnltk.vabamorf` and `hfst`

### Description of the conflict

Once you have [installed HFST via PyPI](https://pypi.org/project/hfst/#installation-via-pypi), and attempt to use it along with `estnltk.vabamorf`, you will get a strange import conflict between the two modules.

If you import `hfst` as a first thing in the program, everything works fine:

	import hfst
    from estnltk.vabamorf.vabamorf import StringVector
    from estnltk.vabamorf.morf import Vabamorf
    
    sv = StringVector(1)
    sv[0] = 'Tere'

    vm_instance = Vabamorf.instance()
    results = vm_instance.analyze(words=sv)
	print(results)

But if you change the import order, like in this example:

    from estnltk.vabamorf.vabamorf import StringVector
    from estnltk.vabamorf.morf import Vabamorf
	import hfst
    
    sv = StringVector(1)
    sv[0] = 'Tere'

    vm_instance = Vabamorf.instance()
    results = vm_instance.analyze(words=sv)
	print(results)

then the program will crash with a _"Segmentation Fault"_, both on Windows and Linux systems. A closer examination showed that the crash occurred at the line `sv[0] = 'Tere'`.

Both `estnltk.vabamorf` and `hfst` use [**Swig**](http://www.swig.org/) for interfacing Python with C and C++ code, and they both also use the `StringVector` Python class, which wraps around the corresponding STL class. 
So, it seemed that something was wrong in the interface between Python's `StringVector` class and the underlying C++ datastructure. 
There were some notable differences in how the Swig interface was defined in two modules. 
Firstly, `hfst` used [Python proxy classes](http://www.swig.org/Doc3.0/Python.html#Python_nn28), but `estnltk.vabamorf` was compiled to support high-performance processing, without any Python proxy classes.
Secondly, the `hfst` extension defined the `StringVector` inside a namespace `hfst` (`hfst::StringVector *`), but `estnltk.vabamorf` extension kept it inside the standard namespace `std` (`StringVector *`). 
And, finally, the latest `hfst` PyPI package for Linux-64 (`hfst 3.15.0.0b0`) was compiled under Swig 3.0.8, while `estnltk.vabamorf`'s latest extension for Linux-64 was compiled under Swig 3.0.12. (`win-32` versions of the both packages were compiled under the Swig 3.0.12)

While at first it seemed that the issue was likely related to `hfst` and `estnltk.vabamorf` using different C++ namespaces for the `StringVector` class, changing namespaces did not help to avoid the crashes. 
The situation improved, however, when `estnltk.vabamorf` was recompiled with Python proxy classes switched on. Then crashes disappeared from the `win-32` platform entirely, and "moved to other place" on the Linux-64 platform. On the Linux, crashes now occurred at script's exit: at releasing the memory, `Error in 'python': free(): invalid pointer` occurred.
And, finally, if [`hfst` Python module](https://github.com/hfst/hfst/tree/master/python) was recompiled with Swig 3.0.12 under Linux-64 (so that both modules were now compiled with the same version of Swig), then the crashes disappeared entirely. 
 
In the following, I'll present the step by step solutions for different platforms.

---

### Solution for win-32

1. Change estnltk's [`setup.py`](https://github.com/estnltk/estnltk/blob/version_1.6/setup.py#L33): remove the argument `'-builtin'` from the list `swig_opts`. This will generate wrapper classes `SwigPyIterator`, `StringVector`, `AnalysisVector` etc inside the file `estnltk/vabamorf/vabamorf.py` during the compilation of the `estnltk.vabamorf` extension;

2. Recompile the `estnltk.vabamorf` extension's binaries with the Swig version 3.0.12. Use either `python setup.py build` (for local build) or `python setup.py install` (for local build and global installation). 

3. Because both `hfst 3.15.0.0b0` and `estnltk.vabamorf` have been generated with the same settings (both use Swig version 3.0.12 and no `'-builtin'` option), they should now run smoothly together. Case closed.

    _Notes on installation_: for Windows platform, only 32-bit binary wheels are currently available for the latest `hfst` (version 3.15.0.0b0). If you are using an Anaconda environment with 64-bit Python on Windows, you need to create an environment with a 32-bit Python, and install `hfst` into it:

		REM force using 32-bit Python in conda
		set CONDA_FORCE_32BIT=1
		
		REM create a new environment that uses 32bit Python
		conda create -n py3.5_32bit python=3.5.5
		
		REM activate the environment and install hfst
		...

    Also, you need to build and install `estnltk` package correspondingly. You can either build and install `estnltk` locally from the source (`python setup.py build_ext install`) in the 32-bit Python environment, or build the conda package for 32-bit Python (as described [here](https://github.com/estnltk/estnltk/tree/b4252b7e80cb8edefaa697b17947c83696933abd/conda-recipe), see the section "Building for Windows") and install it into the environment.

### Solution for linux-64

**2019-04-02**

1. Change estnltk's [`setup.py`](https://github.com/estnltk/estnltk/blob/version_1.6/setup.py#L33): remove the argument `'-builtin'` from the list `swig_opts`. This will generate wrapper classes `SwigPyIterator`, `StringVector`, `AnalysisVector` etc inside the file `estnltk/vabamorf/vabamorf.py` during the compilation of the `estnltk.vabamorf` extension;

2. Two options:
    
    2.1. First, recompile the `estnltk.vabamorf` extension's binaries with Swig version 3.0.12. Use either `python setup.py build` (for local build) or `python setup.py install` (for local build and global installation). Second, download [`hfst` source](https://github.com/hfst/hfst/tree/master/python) and build the Python module. Again, it is important that you use the same Swig version (3.0.12) for building. Third, overwrite the `so` file of the `pip`-installed `hfst` (located in your Anaconda `envs` dir, e.g. `'.../envs/{my_env}/lib/python3.5/site-packages/_libhfst.cpython-35m-x86_64-linux-gnu.so'`) with the newly compiled `so` file (with the same name). Now, both  `pip`-installed `hfst 3.15.0.0b0` and `estnltk.vabamorf` should run smoothly together. Case closed. **(This worked in practice with estnltk v1.6.3beta source, but has not been tried with newer versions)**

	2.2. Recompile the `estnltk.vabamorf` extension's binaries with Swig version 3.0.8. Use either `python setup.py build` (for local build) or `python setup.py install` (for local build and global installation). Now, both  `pip`-installed `hfst 3.15.0.0b0` and `estnltk.vabamorf` should run smoothly together, because Linux wrapper files for `hfst 3.15.0.0b0` were also created with Swig version 3.0.8. Case closed. **(This worked in practice for estnltk v1.6.3beta release, but segmentation faults reappeared in newer estnltk's releases)**

**2020-10-07**

   * _Update:_ It seems that the conflict on Linux can be solved if both `hfst` and `estnltk` are installed from [manylinux wheels](https://github.com/pypa/manylinux), as `hfst` and `estnltk` work smoothly together in Google Colab environment. How to achieve that? `hfst`'s PyPI package already is a manylinux wheel, so nothing to be done there. For `estnltk`, you can build a manylinux wheel using a Dockerfile (see [this document](https://github.com/estnltk/estnltk/blob/b4ff68f9165335caa8ab5c0269157e0e62aadc45/dev_documentation/PyPi_package_for_Google_Colab/readme.md) for details).