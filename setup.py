# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

setup(
    name = "estnltk",
    version = "1.0",
    packages = find_packages(),
    package_data = {
        'estnltk': ['corpora/*.json.bz2', 'java-res/*'],
        'estnltk.estner': ['models/*.bin', 'gazetteer/*.txt']
    },
    
    install_requires = ['nltk>=3.0.0',
                        'pyvabamorf>=1.5',
                        'python-crfsuite>=0.8.1',
                        'jsonpath-rw>=1.3.0',
                        'six>=1.7.3',
                        'tempdir>=0.6',
                        'xmltodict>=0.9.0',
                        'beautifulsoup4>=4.3.2'],
    
    author       = "Timo Petmanson, Aleksandr Tkachenko, Siim Orasmaa, Raul Sirel, Karl-Oskar Masing, Tanel Pärnamaa, Dage Särg, Neeme Kahusk, Sven Laur, Tarmo Vaino, Heiki-Jaan Kaalep",
    author_email = "tpetmanson@gmail.com",
    description  = "API for performing common natural language processing tasks in Estonian.",
    license      = "GPL",
    url          = "https://github.com/tpetmanson/estnltk",
    
    classifiers = ['Intended Audience :: Developers',
                   'Intended Audience :: Education',
                   'Intended Audience :: Science/Research',
                   'Intended Audience :: Information Technology',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3.4',
                   'Topic :: Scientific/Engineering',
                   'Topic :: Scientific/Engineering :: Artificial Intelligence',
                   'Topic :: Scientific/Engineering :: Information Analysis',
                   'Topic :: Text Processing',
                   'Topic :: Text Processing :: Linguistic']   
)
