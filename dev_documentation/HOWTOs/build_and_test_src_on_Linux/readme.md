## How to build and test EstNTLK's development code on Linux

You can use [Docker](https://docker.com) for building and testing EstNLTK's development source on Linux. [This `Dockerfile`](Dockerfile) provides an example of the process.

**Note**: In order to build and install EstNLTK with older Python versions, you'll need to pre-install exact versions of dependency packages. The following dockerfiles show building and installation steps required for specific Python versions:   

* [`Dockerfile.py39`](Dockerfile.py39)
* [`Dockerfile.py38`](Dockerfile.py38)
* [`Dockerfile.py37`](Dockerfile.py37)

**Example building command**:

```
docker build -t estnltk_devel -f Dockerfile --progress=plain .
```
