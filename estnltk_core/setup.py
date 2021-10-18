# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="estnltk_core",
    version="1.6.10b0",
    packages=find_packages(),
    author="University of Tartu",
    author_email="siim.orasmaa@gmail.com, alex.tk.fb@gmail.com, tpetmanson@gmail.com, swen@math.ut.ee",
    description="EstNLTK core — basic components of the EstNLTK v1.6 library",
    # TODO: long_description
    long_description="EstNLTK core — basic components of the EstNLTK v1.6 library",
    #long_description=open('description.txt').read(),
    license="GPLv2",
    # the list of package data used by "build", "bdist" and "install"
    include_package_data=True,
    package_data={
        'license_headers' : ['*.*'],
        'estnltk.visualisation': ['span_visualiser/*.css', 
                                  'span_visualiser/*.js']
    },
    url="https://github.com/estnltk/estnltk",
    install_requires=[
        'regex>=2015.07.19',       # improved Python regular expressions
        'networkx ; python_version >  "3.6"',      # building graphs: required for layers, WordNet and grammars (> py36)
        'networkx==2.5 ; python_version == "3.6"', # building graphs: required for layers, WordNet and grammars (= py36)
        'ipython ; python_version >  "3.6"',         # required for integration with Jupyter Notebook-s (> py36)
        'ipython< 7.17.0 ; python_version == "3.6"', # required for integration with Jupyter Notebook-s (= py36)
        'pandas>=1.1.5 ; python_version >  "3.6"', # Panel Data Analysis library for Python (> py36)
        'pandas<=1.1.5 ; python_version == "3.6"', # Panel Data Analysis library for Python (= py36)
        'numpy==1.19.4 ; python_version == "3.6"', # This is the last numpy version that supports py36
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