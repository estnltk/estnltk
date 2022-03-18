# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

import os, os.path, re

# Get version number from __init__.py
# Based on: 
#  https://milkr.io/kfei/5-common-patterns-to-version-your-Python-package/3
def get_version():
    VERSIONFILE = os.path.join('estnltk_neural', '__init__.py')
    initfile_lines = open(VERSIONFILE, 'rt', errors='ignore').readlines()
    VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
    for line in initfile_lines:
        mo = re.search(VSRE, line, re.M)
        if mo:
            return mo.group(1)
    raise RuntimeError('Unable to find version string in {!r}.'.format(VERSIONFILE))

setup(
    name="estnltk_neural",
    version=get_version(),
    packages=find_packages(),
    author="University of Tartu",
    author_email="siim.orasmaa@gmail.com, alex.tk.fb@gmail.com, tpetmanson@gmail.com, swen@math.ut.ee",
    description="EstNLTK neural -- EstNLTK's linguistic analysis based on neural models",
    long_description=open('README.md', errors='replace').read(),
    long_description_content_type='text/markdown',
    license="GPLv2",
    # the list of package data used by "build", "bdist" and "install"
    include_package_data=True,
    package_data={
        'license_headers' : ['*.*'],
        'estnltk_neural.tests.taggers.neural_morph': ['*.txt'],
    },
    url="https://github.com/estnltk/estnltk",
    install_requires=[
        'estnltk-core',    # EstNLTK's basic datastructures and conversion methods
        'estnltk',         # EstNLTK's NLP pipelines and database tools
        'tensorflow',      
        'torch',
        'transformers',
        'stanza',
        'packaging'
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