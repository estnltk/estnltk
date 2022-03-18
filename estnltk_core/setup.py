# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

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
    packages=find_packages(),
    author="University of Tartu",
    author_email="siim.orasmaa@gmail.com, alex.tk.fb@gmail.com, tpetmanson@gmail.com, swen@math.ut.ee",
    description="EstNLTK core - basic data structures and components of the EstNLTK library",
    long_description=open('README.md', errors='replace').read(),
    long_description_content_type='text/markdown',
    license="GPLv2",
    # the list of package data used by "build", "bdist" and "install"
    include_package_data=True,
    package_data={
        'license_headers' : ['*.*'],
    },
    url="https://github.com/estnltk/estnltk",
    install_requires=[
        'regex>=2015.07.19',       # improved Python regular expressions
        'networkx ; python_version >  "3.6"',      # building graphs: required for layers, WordNet and grammars (> py36)
        'networkx==2.5 ; python_version == "3.6"', # building graphs: required for layers, WordNet and grammars (= py36)
        'pandas<=1.3.5 ; python_version == "3.7"', # Panel Data Analysis library for Python (= py37)
        'pandas<=1.1.5 ; python_version == "3.6"', # Panel Data Analysis library for Python (= py36)
        'pandas ; python_version > "3.7"',         # Panel Data Analysis library for Python (> py37)
        'numpy==1.19.4 ; python_version == "3.6"', # This is the last numpy version that supports py36
        'numpy==1.21.5 ; python_version == "3.7"', # This is the last numpy version that supports py37
    ],
    classifiers=['Intended Audience :: Developers',
                 'Intended Audience :: Education',
                 'Intended Audience :: Science/Research',
                 'Intended Audience :: Information Technology',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 3.7',
                 'Programming Language :: Python :: 3.8',
                 'Programming Language :: Python :: 3.9',
                 'Topic :: Scientific/Engineering',
                 'Topic :: Scientific/Engineering :: Artificial Intelligence',
                 'Topic :: Scientific/Engineering :: Information Analysis',
                 'Topic :: Text Processing',
                 'Topic :: Text Processing :: Linguistic']
)