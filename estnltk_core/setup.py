# -*- coding: utf-8 -*-
from setuptools import setup
from setuptools import find_namespace_packages

import os.path, re

# Get version number from __init__.py
# Based on: 
#  https://milkr.io/kfei/5-common-patterns-to-version-your-Python-package/3
def get_version():
    VERSIONFILE = os.path.join('estnltk_core', '__init__.py')
    initfile_lines = open(VERSIONFILE, 'rt', errors='ignore').readlines()
    VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
    for line in initfile_lines:
        mo = re.search(VSRE, line, re.M)
        if mo:
            return mo.group(1)
    raise RuntimeError('Unable to find version string in {!r}.'.format(VERSIONFILE))

setup(
    name="estnltk_core",
    version=get_version(),
    packages=find_namespace_packages(),
    author="University of Tartu",
    author_email="siim.orasmaa@gmail.com, alex.tk.fb@gmail.com, tpetmanson@gmail.com, swen@math.ut.ee",
    description="EstNLTK core - basic data structures and components of the EstNLTK library",
    long_description=open('README.md', errors='replace').read(),
    long_description_content_type='text/markdown',
    license="Dual License: GPLv2 or Apache-2.0",
    url="https://github.com/estnltk/estnltk",
    install_requires=[
        'regex>=2015.07.19', # improved Python regular expressions
        'networkx',          # building graphs: required for layers
        'pandas',            # Panel Data Analysis library for Python
        'packaging'          # Required for version checking
    ],
    classifiers=['Intended Audience :: Developers',
                 'Intended Audience :: Education',
                 'Intended Audience :: Science/Research',
                 'Intended Audience :: Information Technology',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 3.9',
                 'Programming Language :: Python :: 3.10',
                 'Programming Language :: Python :: 3.11',
                 'Programming Language :: Python :: 3.12',
                 'Programming Language :: Python :: 3.13',
                 'Topic :: Scientific/Engineering',
                 'Topic :: Scientific/Engineering :: Artificial Intelligence',
                 'Topic :: Scientific/Engineering :: Information Analysis',
                 'Topic :: Text Processing',
                 'Topic :: Text Processing :: Linguistic']
)