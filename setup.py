# -*- coding: utf-8 -*-
from setuptools import setup, find_packages, Extension
import os
import sys

def get_sources(src_dir='src', ending='.cpp'):
    '''Function to get a list of files ending with `ending` in `src_dir`.'''
    return [os.path.join(src_dir, fnm) for fnm in os.listdir(src_dir) if fnm.endswith(ending)]

# define directories for vabamorf source directories
dirs = ['fsc', 'proof', 'etana', 'json']
src_dirs = [os.path.join('src', d) for d in dirs]

# define a list of C++ source files
lib_sources = []
for d in src_dirs:
    lib_sources.extend(get_sources(d))

# define directories for vabamorf include directories
dirs.append(os.path.join('fsc', 'fsjni'))
include_dirs = [os.path.join('include', d) for d in dirs]

# define the vabamorf SWIG wrapper generator interface file
swig_interface = os.path.join('estnltk', 'pyvabamorf', 'vabamorf.i')
swig_opts = []

# Python 3 specific configuration
extra = {}
if sys.version_info[0] == 3: 
    swig_opts.append('-py3')
swig_opts.append('-c++')

setup(
    name = "estnltk",
    version = "1.0",
    packages = find_packages(),
    package_data = {
        'estnltk': ['corpora/*.json.bz2', 'java-res/*'],
        'estnltk.estner': ['models/*.bin', 'gazetteer/*.txt'],
        'estnltk.mw_verbs': ['res/*.txt'],
        'estnltk.pyvabamorf': ['dct/*.dct'],
        'estnltk.wordnet': ['*.cnf', 'data/*.cnf', 'data/*.soi', 'data/*.txt', 'data/scripts/*.py'],
        'estnltk.textclassifier.tests': ['*.def', '*.xlsx', '*.csv', '*.txt'],
    },
    
    install_requires = ['nltk>=3.0.0',
                        'python-crfsuite>=0.8.1',
                        'jsonpath-rw>=1.3.0',
                        'six>=1.7.3',
                        'tempdir>=0.6',
                        'xmltodict>=0.9.0',
                        'beautifulsoup4>=4.3.2',
                        
                        'pandas>=0.14.1', # text classifier related + some needed in future
                        'scikit-learn>=0.15.1',
                        'xlrd>=0.9.2',
                        'xlsxwriter>=0.5.7',
                        'numpy>=1.8.2',
                        'scipy>=0.11.0',
                        'pytz>=2014.4',
                        'python-dateutil>=2.2',
                        'nose>=1.3.3',
                        'pyparsing>=2.0.2',
                        'matplotlib>=1.2.1',
                        'xlwt-future>=0.7.5'],
    
    author       = "Timo Petmanson, Aleksandr Tkachenko, Siim Orasmaa, Raul Sirel, Karl-Oskar Masing, Tanel Pärnamaa, Dage Särg, Neeme Kahusk, Sven Laur, Tarmo Vaino, Heiki-Jaan Kaalep",
    author_email = "tpetmanson@gmail.com",
    description  = "Open source tools for Estonian natural language processing",
    license      = "GPL",
    url          = "https://github.com/tpetmanson/estnltk",
    
    ext_modules = [
        Extension('estnltk.pyvabamorf._vabamorf',
                  [swig_interface] + lib_sources,
                  swig_opts = swig_opts,
                  include_dirs=include_dirs)
        ],
    
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
