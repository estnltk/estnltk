#
# Docker file for Ubuntu 18.04 based EstNLTK 1.6 devel building, installing and testing
#
# ================================
#   Set up OS
# ================================
FROM ubuntu:18.04

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
# Get & install dependency: libhfst
#
RUN wget -nv http://apertium.projectjj.com/apt/release/pool/main/h/hfst/libhfst53_3.15.4-1~bionic1_amd64.deb
RUN apt install -y ./libhfst53_3.15.4-1~bionic1_amd64.deb
#
# Get & install hfst command line tools
#
RUN wget -nv http://apertium.projectjj.com/apt/release/pool/main/h/hfst/hfst_3.15.4-1~bionic1_amd64.deb
RUN apt install -y ./hfst_3.15.4-1~bionic1_amd64.deb
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
#   Get EstNLTK's devel source
# ================================
RUN git clone --depth=25 --branch=devel_1.6 https://github.com/estnltk/estnltk.git estnltk_devel

# ================================
#   Set paths to syntax models 
# ================================
ENV UDPIPE_SYNTAX_MODELS_PATH=/estnltk_devel/estnltk/taggers/syntax/udpipe_tagger/resources
ENV MALTPARSER_SYNTAX_MODELS_PATH=/estnltk_devel/estnltk/taggers/syntax/maltparser_tagger/java-res/maltparser

# ================================
#   Python 3.7
# ================================
RUN echo " Python 3.7 " | figlet 
RUN conda create -n py37 python=3.7
#
# Make RUN commands use the new environment (https://pythonspeed.com/articles/activate-conda-dockerfile/)
#
SHELL ["conda", "run", "-n", "py37", "/bin/bash", "-c"]
RUN python --version
#
# Install packages required for testing
#
RUN conda install pytest
RUN conda install -c conda-forge pytest-httpserver
#
# Build and install EstNLTK
#
WORKDIR /estnltk_devel
RUN python setup.py build_ext install
#
# Run estnltk's tests
#
WORKDIR /
RUN conda list estnltk
RUN pytest --pyargs estnltk.vabamorf
RUN pytest --pyargs estnltk.tests

#ENTRYPOINT ["/bin/bash"]
