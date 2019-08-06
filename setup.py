# -*- coding: utf-8 -*-
from setuptools import setup, find_packages, Extension
import os
import sys

os.environ['CC'] = 'g++'
os.environ['CXX'] = 'g++'


def get_sources(src_dir='src', ending='.cpp'):
    """Function to get a list of files ending with `ending` in `src_dir`."""
    return [os.path.join(src_dir, fnm) for fnm in os.listdir(src_dir) if fnm.endswith(ending)]


# define directories for vabamorf source directories
dirs = ['etana', 'etyhh', 'fsc', 'json', 'proof', 'estnltk']
src_dirs = [os.path.join('src', d) for d in dirs]

# define a list of C++ source files
lib_sources = []
vabamorf_src = os.path.join('src', 'estnltk', 'vabamorf.cpp')
for d in src_dirs:
    lib_sources.extend(get_sources(d))
lib_sources.remove(vabamorf_src)  # we add it later as the first file to compile
# less time to wait, when working with vabamorf wrapper

# define directories for vabamorf include directories
dirs.append(os.path.join('fsc', 'fsjni'))
include_dirs = [os.path.join('include', d) for d in dirs]

# define the vabamorf SWIG wrapper generator interface file
swig_interface = os.path.join('estnltk', 'vabamorf', 'vabamorf.i')

#swig_opts = ['-builtin']  # Disable proxy classes
swig_opts = []             # Enable proxy classes 

# How enabling proxy classes affects vabamorf's speed:
#  https://github.com/estnltk/estnltk/blob/devel_1.6/dev_documentation/vabamorf_benchmarking/vabamorf_speed_benchmarking.md


# Python 3 specific configuration
extra = {}
if sys.version_info[0] == 3:
    swig_opts.append('-py3')
swig_opts.append('-c++')

setup(
    name="estnltk",
    version="1.6.3beta",

    packages=find_packages(),
    include_package_data=True,
    package_data={
        'estnltk': ['corpora/arvutustehnika_ja_andmetootlus/*.xml', 'corpora/*.json', 'java/res/*.*'],
        'estnltk.taggers': ['miscellaneous/*.csv', 'syntax/files/*.*', 'syntax/files/LICENSE', 'morph_analysis/hfst/models/*.*', 'verb_chains/v1_4_1/res/*.*'],
        'estnltk.tests': ['test_morph/*.csv', 'test_corpus_processing/*.vert', 'test_taggers/test_dict_taggers/*.csv', 'test_taggers/miscellaneous/*.json', 'test_taggers/standard_taggers/*.json', 'test_visualisation/expected_outputs/direct_plain_span_visualiser_outputs/*.txt', 'test_visualisation/expected_outputs/indirect_plain_span_visualiser_outputs/*.txt', 'test_converters/*.conll'],
        'estnltk.vabamorf': ['dct/*.dct'],
        'estnltk.estner': ['gazetteer/*', 'models/py2_default/*', 'models/py3_default/*'],
        'estnltk.wordnet': ['*.cnf', 'data/*.txt', 'data/*.soi', 'data/*.cnf', 'data/scripts/*.py'],
        'estnltk.mw_verbs': ['res/*'],
        'estnltk.converters': ['*.mrf'],
        'estnltk.syntax': ['files/*'],
        'estnltk.visualisation': ['attribute_visualiser/*.css', 'attribute_visualiser/*.js', 'span_visualiser/*.css', 'span_visualiser/*.js']
    },

    author="University of Tartu",
    author_email="siim.orasmaa@gmail.com, alex.tk.fb@gmail.com, tpetmanson@gmail.com, swen@math.ut.ee",
    description="Estnltk — open source tools for Estonian natural language processing",
    long_description=open('README.md').read(),
    license="GPLv2",
    url="https://github.com/estnltk/estnltk",
    ext_modules=[
        Extension('estnltk.vabamorf._vabamorf',
                  [swig_interface, vabamorf_src] + lib_sources,
                  swig_opts=swig_opts,
                  include_dirs=include_dirs)
    ],

    # we have fixed dependency versions to guarantee, what works
    # however, you can probably safely install newer versions of the dependencies
    install_requires=[
        'nltk>=3.0.4',  # NLTK mainly used for English
        'regex>=2015.07.19',  # improved Python regular expressions
        'pandas>=0.16.2',  # Panel Data Analysis library for Python
        'python-crfsuite>=0.8.3',  # Conditional random fields library
        'cached-property>=1.2.0',  # Simple property for caching results
        'bs4', # BeautifulSoup: for processing XML files of the Estonian Reference Corpus
        'html5lib', # for processing XML files of the Estonian Reference Corpus
        'lxml',
        'networkx',
    ],

    classifiers=['Intended Audience :: Developers',
                 'Intended Audience :: Education',
                 'Intended Audience :: Science/Research',
                 'Intended Audience :: Information Technology',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 3.5',
                 'Topic :: Scientific/Engineering',
                 'Topic :: Scientific/Engineering :: Artificial Intelligence',
                 'Topic :: Scientific/Engineering :: Information Analysis',
                 'Topic :: Text Processing',
                 'Topic :: Text Processing :: Linguistic']
)
