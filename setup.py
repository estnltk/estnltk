# -*- coding: utf-8 -*-
from setuptools import setup, find_packages, Extension
import os
import sys

setup(
    name="estnltk_light",
    version="1.6.7.7b0",
    packages=find_packages(),
    author="University of Tartu",
    author_email="siim.orasmaa@gmail.com, alex.tk.fb@gmail.com, tpetmanson@gmail.com, swen@math.ut.ee",
    description="EstNLTK light — core components of the EstNLTK v1.6 library",
    long_description=open('description.txt').read(),
    license="GPLv2",
    url="https://github.com/estnltk/estnltk",
    install_requires=[
        'networkx',  # building graphs: required for managing layer dependencies
    ],
    classifiers=['Intended Audience :: Developers',
                 'Intended Audience :: Education',
                 'Intended Audience :: Science/Research',
                 'Intended Audience :: Information Technology',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 3.6',
                 'Programming Language :: Python :: 3.7',
                 'Programming Language :: Python :: 3.8',
                 'Topic :: Scientific/Engineering',
                 'Topic :: Scientific/Engineering :: Artificial Intelligence',
                 'Topic :: Scientific/Engineering :: Information Analysis',
                 'Topic :: Text Processing',
                 'Topic :: Text Processing :: Linguistic']
)
