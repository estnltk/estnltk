# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

setup(
    name = "estnltk",
    version = "1.0",
    packages = find_packages(),
    package_data = {
        'estnltk': ['corpora/pm_news/*.txt']
    },
    
    install_requires = ['nltk>=3.0.0',
                        'pyvabamorf>=1.5',
                        'python-crfsuite>=0.8.1',
                        'jsonpath-rw>=1.3.0',
                        'six>=1.7.3',
                        'tempdir>=0.6'],
    
    author       = "Timo Petmanson, Aleksandr Tkachenko, Siim Orasmaa, Raul Sirel, Karl-Oskar Masing, Tanel Pärnamaa, Dage Särg, Neeme Kahusk, Sven Laur, Tarmo Vaino, Heiki-Jaan Kaalep",
    author_email = "tpetmanson@gmail.com",
    description  = "API for performing natural language processing tasks in Estonian.",
    license      = "GPL",
    url          = "https://github.com/tpetmanson/estnltk",
    
    
    classifiers = ['Intended Audience :: Developers',
                   'Intended Audience :: Education',
                   'Intended Audience :: Science/Research',
                   'Intended Audience :: Information Technology',
                   'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3.4',
                   'Topic :: Scientific/Engineering',
                   'Topic :: Scientific/Engineering :: Artificial Intelligence',
                   'Topic :: Scientific/Engineering :: Information Analysis',
                   'Topic :: Text Processing',
                   'Topic :: Text Processing :: Linguistic']   
)
