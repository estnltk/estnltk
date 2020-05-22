#
# Docker file for CentOS based building of EstNLTK 1.6 manylinux wheels
# See also: https://github.com/pypa/manylinux 
#
# ================================
#   Set up OS
# ================================
FROM quay.io/pypa/manylinux2014_x86_64

RUN yum install swig -y && yum install -y git 

# Install figlet for ascii graphix messages (purely optional)
RUN yum install -y figlet 

# Check OS version (optional)
RUN cat /etc/os-release

# ================================
#   Get EstNLTK's source
# ================================
RUN git clone --depth=25 --branch=version_1.6_travis https://github.com/estnltk/estnltk.git estnltk_devel

# Directory for outputs
RUN mkdir output

# ================================
#   Python 3.5
# ================================
RUN echo " Python 3.5 " | figlet 
# (!) Important: run "build_ext"  before  creating  the  wheel,  because 
#     pip wheel runs "build_ext" as the last command and then the package 
#     will be missing auto-generated "vabamorf.py" ...
WORKDIR /estnltk_devel
RUN /opt/python/cp35-cp35m/bin/python setup.py build_ext
WORKDIR /
RUN /opt/python/cp35-cp35m/bin/pip wheel /estnltk_devel -w output
RUN auditwheel repair /output/estnltk-*-cp35-*-linux_*.whl -w /output

# Clean-up auto-generated source (optional)
#RM estnltk_devel\estnltk\vabamorf\vabamorf.py
#RM estnltk_devel\estnltk\vabamorf\vabamorf_wrap.cpp

# ================================
#   Python 3.6
# ================================
RUN echo " Python 3.6 " | figlet 
WORKDIR /estnltk_devel
RUN /opt/python/cp36-cp36m/bin/python setup.py build_ext
WORKDIR /
RUN /opt/python/cp36-cp36m/bin/pip wheel /estnltk_devel -w output
RUN auditwheel repair /output/estnltk-*-cp36-*-linux_*.whl -w /output

# Clean-up auto-generated source (optional)
#RM estnltk_devel\estnltk\vabamorf\vabamorf.py
#RM estnltk_devel\estnltk\vabamorf\vabamorf_wrap.cpp

# ================================
#   Python 3.7
# ================================
RUN echo " Python 3.7 " | figlet 
WORKDIR /estnltk_devel
RUN /opt/python/cp37-cp37m/bin/python setup.py build_ext
WORKDIR /
RUN /opt/python/cp37-cp37m/bin/pip wheel /estnltk_devel -w output
RUN auditwheel repair /output/estnltk-*-cp37-*-linux_*.whl -w /output

# Clean-up auto-generated source (optional)
#RM estnltk_devel\estnltk\vabamorf\vabamorf.py
#RM estnltk_devel\estnltk\vabamorf\vabamorf_wrap.cpp

# Inspect created wheels
RUN ls -lah /output/estnltk-*-manylinux*.whl

#ENTRYPOINT ["/bin/bash"]
