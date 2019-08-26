## How to build EstNLTK with conda

_A brief overview_. [Recipes](https://docs.conda.io/projects/conda-build/en/latest/concepts/recipe.html) for building EstNLTK's _conda_ packages are in the subdirectories `linux_and_osx` and `windows`. 
These have been tested on linux-64, osx-64, win-64 and win32 with Python 3.5 and 3.6.
We depend on the _conda-forge_ project for most of our dependencies and publish our own versions to the `estnltk` channel as needed. To build, use the command:

`conda build -c estnltk -c conda-forge <recipe-directory>`

## Details

### Before making the build

All developments and fixes should be made on the [`devel_1.6`](https://github.com/estnltk/estnltk/tree/devel_1.6)  branch.
Before making the build, make sure that:
 
 1. all source code directories (packages) that should be distributed with EstNLTK have [`__init__.py`](https://python-packaging-tutorial.readthedocs.io/en/latest/setup_py.html#packages) files;
 2. all the resource files (files without the `py` extension) required by EstNLTK are included `package_data` in [`setup.py`](https://github.com/estnltk/estnltk/blob/devel_1.6/setup.py); 
 3. package requirements in [`linux_and_osx/meta.yaml`](
https://github.com/estnltk/estnltk/blob/devel_1.6/conda-recipe/linux_and_osx/meta.yaml) and [`windows/meta.yaml`](
https://github.com/estnltk/estnltk/blob/devel_1.6/conda-recipe/windows/meta.yaml) are up to date;
 
After you have updated `setup.py` and `meta.yaml` files in the `devel_1.6` branch, merge the `devel_1.6` branch into the `version_1.6` breach. 
This branch should always maintain the source of the most recent release.

### Building for Linux and MacOSX

Building for these platforms has been fully automated with the help of [Travis CI](https://travis-ci.org). 
Detailed building instructions are in the file [.travis.yml](https://github.com/estnltk/estnltk/blob/version_1.6_travis/.travis.yml). 
After you have merged the `devel_1.6` branch into the `version_1.6`, merge the `version_1.6` branch into the `version_1.6_travis` branch. 
This will launch an [automated building process](https://travis-ci.org/estnltk/estnltk/requests) in Travis.
If the build is successful (✓), then created packages will also be uploaded into [estnltk's anaconda channel](https://anaconda.org/estnltk/estnltk).

Notes:

  * A build will not start if `.travis.yml` has invalid format. If you change the file, you can use [http://www.yamllint.com](http://www.yamllint.com) to validate the format of the file;

  * By default, built packages will be uploaded to _anaconda_ under the label `dev`. To test out if the package was build successfully, you should try to install and use it in a new conda environment. For instance:
          
        conda create -n test_35 python=3.5 -y
		conda activate test_35
		conda install -c estnltk/label/dev estnltk -y
		python -c "import estnltk; print(estnltk.Text('Tere, maailm\!').analyse('all'))"
			
		conda deactivate
		conda env remove -n test_35

  
    Once you have tested out the packages, you should change the label to `main`. Just log in to _anaconda.org_ and change labels of the corresponding files.

### Building for Windows

#### Building in a local machine

This instruction assumes that you have already completed a Travis CI build for Linux and MacOSX, and the source required for the build is in the branch  `version_1.6_travis`.

1. Download the source from github: 

        git clone --depth=50 --branch=version_1.6_travis https://github.com/estnltk/estnltk.git

2. Create and set up a conda environment for the build, for instance:

        conda create -n py3.5_conda_build python=3.5
        conda activate py3.5_conda_build
        conda install conda-build conda-verify swig cython

    Note: If you are using win-64, and you want to build for win-32, you can call `set CONDA_FORCE_32BIT=1` before creating the new environment. This will force conda to use 32-bit Python in the new environment. 

3. In order to compile estnltk's _Vabamorf_ extension, you'll need to have [Microsoft Visual Studio](https://visualstudio.microsoft.com) installed in the system. Note: which Visual C++ compiler you need depends on the specific Python version (see [this document](https://wiki.python.org/moin/WindowsCompilers) for details). In the following, _Microsoft Visual Studio Community Edition 2017_ (Visual C++ 14.0) was used.

	3.1. Locate `vcvarsall.bat` in the Visual Studio installation directory, and use it to initialize compiling environment for `x64` (win-64) or `x86` (win-32). For instance:

        call "c:\Program Files (x86)\Microsoft Visual Studio Community 2017\VC\Auxiliary\Build\vcvarsall.bat" x64
    
    3.2. (Optional) Set `VS140COMNTOOLS` and `VS100COMNTOOLS` environment variables, for instance:

        SET %VS140COMNTOOLS%="C:\Program Files (x86)\Microsoft Visual Studio Community 2017\Common7\Tools"
        SET VS100COMNTOOLS=%VS140COMNTOOLS%

    Note: setting `VS140COMNTOOLS` / `VS100COMNTOOLS` can help to resolve error messages like

        ...\vcvarsall.bat is not recognized as an internal or external command, operable program or batch file.

    during the building process in step 4.


4. Navigate into the windows recipe directory and launch the build, for instance:

        cd conda-recipe\windows
        conda build -c conda-forge --py 3.5  .

    If the build was successful, you should also see an upload instruction in the output, for instance:

        # If you want to upload package(s) to anaconda.org later, type:
 
        anaconda upload C:\Miniconda3\envs\py3.5_conda_build\conda-bld\win-64\estnltk-1.6.Xbeta-3.5.tar.bz2

5. Install _anaconda-client_, login and upload the package to _anaconda.org_:

        conda install anaconda-client
        anaconda login
        anaconda upload -l dev C:\Miniconda3\envs\py3.5_conda_build\conda-bld\win-64\estnltk-1.6.Xbeta-3.5.tar.bz2
        anaconda logout

     Note: if you previously used `set CONDA_FORCE_32BIT=1`, you should now use `set CONDA_FORCE_32BIT=` before installing `anaconda-client`;

6. Finally, test the installation in a new conda environment:

        conda create -n test_35 python=3.5 -y
		conda activate test_35
		conda install -c estnltk/label/dev estnltk -y
		python -c "import estnltk; print(estnltk.Text('Tere, maailm!').analyse('all'))"
			
		conda deactivate
		conda env remove -n test_35


#### Building with Travis

While Travis CI also has [a Windows support](https://blog.travis-ci.com/2018-10-11-windows-early-release), it is still in early stages.
We [tried it out](https://github.com/estnltk/estnltk/blob/dff24a6c943fd5285be3bced6bd8247191cb7c7b/.travis.yml), and stumbled upon a problem with `choco install`: it hanged because a secured environment variable was used in `.travis.yml` (see [this issue](https://travis-ci.community/t/current-known-issues-please-read-this-before-posting-a-new-topic/264/10) for details).
Better luck next time!