## How to create EstNTLK package that installs and runs in Google Colab

In order to get EstNTLK installing and running in [Google Colab](https://colab.research.google.com), you need to create a [manylinux](https://github.com/pypa/manylinux) Python wheel and upload it to to [PyPi](https://pypi.org/). ( Note: If you are trying to use some older version of EstNLTK, you also need to make some fixes in Vabamorf's source -- for details, see [this comment](https://github.com/estnltk/estnltk/issues/107#issuecomment-582839466) )


Easiest way to build EstNLTK's manulinux package is with the help of [Docker](www.docker.com). If you have Docker installed, use [this `Dockerfile`](Dockerfile) to build the wheels for Python 3.5, 3.6 and 3.7.

Once you have obtained estnltk `.whl` file for Python 3.6, follow the instructions [here](https://packaging.python.org/tutorials/packaging-projects/#uploading-the-distribution-archives) on uploading the wheel. A good practice would be to first upload the test wheel to [https://test.pypi.org/project/estnltk](https://test.pypi.org/project/estnltk) , test it out in Google Colab, and then upload the final version to [https://pypi.org/project/estnltk](https://pypi.org/project/estnltk) .


