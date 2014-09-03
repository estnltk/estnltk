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
    
    install_requires = ['pyvabamrof>=1.3', 'dpath>=1.3'],
    
    author       = "Timo Petmanson, Aleksandr Tkachenko, Siim Orasmaa, Raul Sirel, Karl-Oskar Masing, Tanel Pärnamaa, Dage Särg, Sven Laur, Tarmo Vaino, Heiki-Jaan Kaalep",
    author_email = "tpetmanson@gmail.com",
    description  = "API for performing natural language processing tasks in Estonian.",
    license      = "LGPL",
    url          = "https://github.com/brainscauseminds/estnltk",
    
    
    classifiers = ['Intended Audience :: Developers',
                   'Intended Audience :: Education',
                   'Intended Audience :: Science/Research',
                   'Intended Audience :: Information Technology',
                   'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
                   'Operating System :: OS Independent',
                   'Topic :: Scientific/Engineering',
                   'Topic :: Scientific/Engineering :: Artificial Intelligence',
                   'Topic :: Scientific/Engineering :: Information Analysis',
                   'Topic :: Text Processing',
                   'Topic :: Text Processing :: Linguistic']   
)
