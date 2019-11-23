# How to set up development environment

To set up development environment:

1. install `conda` 
2. create separate environment `estnltk-3.5`
3. clone `devel_1.6` branch to a directory `estnltk`
4. create shell file that modifies `PYTHONPATH` so that cloned repo wins
5. compile the cloned estnltk package to get dynamical libraries for `vabamorf`

The last step is hardest as you might get random C++ compiling and linking errors due to differences in your system and reference system. It is impossible to cover every flavour of Linux and Windows


## Vabamorf hack as a solution

**Problem:** EstNLTK needs dynamical libraries that execute vabamorf functions. 

**Solution:** 

* These are prebuilt in `conda` packages. 
* You only need to locate them and copy into right place in the cloned repo

**Instructions:**

1. Go to the root directory of anaconda distribution 
   * `/opt/anaconda3` for Linux and macOS
2. Go to the package directory `pkgs/estnltk-1.6xxx-3.y/lib/pyhton3.y/site-packages/estnltk/vabamorf`
3. Locate the dynamic library `_vabamorf.cpyhton-3yzz.zz`
4. Copy the dynamic library to the cloned repo in the path `estnltk/vabamorph`      
 

## Additonal suppot files files

* `estnltk-3.5.sh`: creates `estnltk-3.5` environment for Pyhton 3.5
* `estnltk-3.6.sh`: creates `estnltk-3.6` environment for Pyhton 3.6
* `jupyter-notebook-3.5.sh`: activates `estnltk-3.5` and launces Jupyter shell
* `jupyter-notebook-3.6.sh`: activates `estnltk-3.6` and launces Jupyter shell
