#
# Docker file for Ubuntu 22.04 based EstNLTK 1.7 devel building, installing and testing
#
# ================================
#   Set up OS
# ================================
FROM ubuntu:22.04

RUN apt-get update && apt-get upgrade -y && apt-get install -y wget && \
    apt-get install -y g++ libpcre3 libpcre3-dev swig && \
    apt-get install -y default-jre && \
    apt-get install -y git && apt-get install -y unzip
RUN apt-get install -y cg3

# Install figlet for ascii graphix messages (purely optional)
RUN apt-get install -y figlet 

# Check Ubuntu version (optional)
RUN cat /etc/os-release

# ================================
#   Get UDPipe (1.2.0) binary
# ================================
RUN wget -nv https://github.com/ufal/udpipe/releases/download/v1.2.0/udpipe-1.2.0-bin.zip
RUN unzip udpipe-1.2.0-bin
ENV PATH=/udpipe-1.2.0-bin/bin-linux64:${PATH}

# ================================
#   Get HFST command line tool    
# ================================
#
# https://github.com/hfst/hfst/wiki/Download-And-Install#download-and-install-hfst
# https://github.com/hfst/hfst/wiki/Download-And-Install#installing-hfst-to-linux
#

RUN wget https://apertium.projectjj.com/apt/install-nightly.sh
RUN chmod ug+x install-nightly.sh
RUN ./install-nightly.sh
RUN apt-get install -y hfst

#
# Check general hfst into
#
RUN hfst-info

#
# Check that command line tool is available
#
RUN hfst-lookup --version

# ================================
#   Set up conda
# ================================
# Download and install miniconda
RUN wget -nv https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
RUN bash miniconda.sh -b -p /miniconda
RUN rm -r miniconda.sh
ENV PATH=/miniconda/bin:${PATH}

# Configure and update conda
RUN conda config --set always_yes yes && \
    conda update -q conda && \
    conda info -a

# ================================
#   Python 3.10
# ================================
RUN echo " Python 3.10 " | figlet 
RUN conda create -n py310 python=3.10
#
# Make RUN commands to use the new environment (https://pythonspeed.com/articles/activate-conda-dockerfile/)
#
SHELL ["conda", "run", "-n", "py310", "/bin/bash", "-c"]
RUN python --version

# ================================
#   Tools required for building 
#   Python package
# ================================
# 
# Updgrade pip, setuptools, and install build
# 
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir --upgrade setuptools
RUN pip install --no-cache-dir build

#
# Install packages required for testing
#
RUN conda install pytest
RUN conda install -c conda-forge pytest-httpserver

# ================================
#   Get EstNLTK's devel source
# ================================
RUN echo "Load devel 1.7" | figlet 
RUN git clone --depth=25 --branch=devel_1.7 https://github.com/estnltk/estnltk.git estnltk_devel

# ================================
#   Estnltk-core
# ================================
RUN echo " EstNLTK-core " | figlet 
WORKDIR /estnltk_devel/estnltk_core
#
# Build EstNLTK-core
#
RUN python -m build --sdist --wheel --outdir dist/ .
#
# Install EstNLTK-core
#
WORKDIR /estnltk_devel/estnltk_core/dist
RUN ls -lah
RUN pip install $(ls -1 estnltk_core*.whl)

#
# Run estnltk-core's tests
#
WORKDIR /
RUN conda list estnltk
RUN pytest --pyargs estnltk_core.tests

# ================================
#   Estnltk (default package)
# ================================
RUN echo " EstNLTK " | figlet 
WORKDIR /estnltk_devel/estnltk

#
# Build EstNLTK
#
RUN python -m build --sdist --wheel --outdir dist/ .
#
# Install EstNLTK
#
WORKDIR /estnltk_devel/estnltk/dist
RUN ls -lah
RUN pip install $(ls -1 estnltk*.whl)

WORKDIR /
RUN conda list estnltk

#
# Download wordnet resources (optional)
#
RUN python -c "import estnltk; estnltk.download('wordnet')"
#
# Download syntax resources (optional)
#
RUN python -c "import estnltk; estnltk.download('udpipetagger')"
RUN python -c "import estnltk; estnltk.download('maltparsertagger')"

#
# Enable testing of EstNLTK's downloader (optional)
#
ENV TEST_ESTNLTK_DOWNLOADER=1

#
# Run estnltk's tests
#
RUN pytest --pyargs estnltk.vabamorf
RUN pytest --pyargs estnltk.tests

#
# Clean-up: Delete downloaded the resources
#
RUN python -c "from estnltk.resource_utils import delete_all_resources; delete_all_resources()"

#
# Clean-up: Delete installed package
#
#SHELL ["/bin/bash", "-c"]
#WORKDIR /estnltk_devel/estnltk
#RUN rm -r estnltk.egg-info
#RUN rm -r build
#RUN rm -r dist
#WORKDIR /
# Remove the environment
#RUN conda remove --name py310 --all

#ENTRYPOINT ["/bin/bash"]
