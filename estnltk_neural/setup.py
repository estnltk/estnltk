# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="estnltk_neural",
    version="1.6.10b0",
    packages=find_packages(),
    author="University of Tartu",
    author_email="siim.orasmaa@gmail.com, alex.tk.fb@gmail.com, tpetmanson@gmail.com, swen@math.ut.ee",
    description="EstNLTK neural -- package containing linguistic analysis based on neural models",
    # TODO: long_description
    long_description="EstNLTK neural -- package containing linguistic analysis based on neural models",
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
        'estnltk',
        'tensorflow',
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