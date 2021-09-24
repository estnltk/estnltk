# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="estnltk_core",
    version="1.7.0b0",
    packages=find_packages(),
    author="University of Tartu",
    author_email="siim.orasmaa@gmail.com, alex.tk.fb@gmail.com, tpetmanson@gmail.com, swen@math.ut.ee",
    description="EstNLTK core — basic components of the EstNLTK v1.7 library",
    # TODO: long_description
    long_description="EstNLTK core — basic components of the EstNLTK v1.7 library",
    #long_description=open('description.txt').read(),
    license="GPLv2",
    url="https://github.com/estnltk/estnltk",
    install_requires=[
        'regex>=2015.07.19',       # improved Python regular expressions
        'networkx ; python_version >  "3.6"',      # building graphs: required for layers, WordNet and grammars (> py36)
        'networkx==2.5 ; python_version == "3.6"', # building graphs: required for layers, WordNet and grammars (= py36)
        'pandas>=1.1.5 ; python_version >  "3.6"', # Panel Data Analysis library for Python (> py36)
        'pandas<=1.1.5 ; python_version == "3.6"', # Panel Data Analysis library for Python (= py36)
    ],
    classifiers=['Intended Audience :: Developers',
                 'Intended Audience :: Education',
                 'Intended Audience :: Science/Research',
                 'Intended Audience :: Information Technology',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 3.6',
                 'Programming Language :: Python :: 3.7',
                 'Programming Language :: Python :: 3.8',
                 'Programming Language :: Python :: 3.9',
                 'Topic :: Scientific/Engineering',
                 'Topic :: Scientific/Engineering :: Artificial Intelligence',
                 'Topic :: Scientific/Engineering :: Information Analysis',
                 'Topic :: Text Processing',
                 'Topic :: Text Processing :: Linguistic']
)