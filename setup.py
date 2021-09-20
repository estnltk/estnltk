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

# Check command line args: are we making a source distribution?
is_source_dist = 'sdist' in sys.argv
# If we are making a source distribution, then include "preinstall";
# otherwise: exclude it.
exclude_package_dirs=["preinstall"] if not is_source_dist else []

# Create necessary cached files
from preinstall import create_caches
create_caches()


setup(
    name="estnltk",
    version="1.6.9.1b0",

    packages=find_packages(exclude=exclude_package_dirs),
    include_package_data=True,
    # TODO: package_data duplicates MANIFEST.in; if there is no need for package_data, remove it
    package_data={
        'estnltk.java': [ 'res/*.*'],
        'estnltk.taggers.estner': ['gazetteer/*', 'models/py3_default/*'],
        'estnltk.taggers.miscellaneous':  ['*.csv'],
        'estnltk.taggers.morph_analysis': ['hfst/models/*.*', 
                                           'number_fixes/*.*', 
                                           'reorderings/*.*'],
        'estnltk.taggers.syntax': ['files/*.*', 
                                   'files/LICENSE', 
                                   'maltparser_tagger/java-res/maltparser/maltparser-1.9.0.jar', 
                                   'maltparser_tagger/java-res/maltparser/MaltParser_LICENSE.txt', 
                                   'maltparser_tagger/java-res/maltparser/morph_analysis_conllu.mco', 
                                   'maltparser_tagger/java-res/maltparser/lib/*.*', 
                                   'stanza_tagger/stanza_resources/*.*',
                                   'ud_validation/agreement_resources/*.*',
                                   'ud_validation/data/*.*'],
        'estnltk.taggers.syntax_preprocessing': ['rules_files/*.*'], 
        'estnltk.taggers.text_segmentation': ['*.csv'], 
        'estnltk.taggers.verb_chains': ['v1_4_1/res/*.*'],
        'estnltk.tests.test_converters': ['*.conll'], 
        'estnltk.tests.test_corpus_processing': ['*.vert'], 
        'estnltk.tests.test_morph': ['*.csv'], 
        'estnltk.tests.test_syntax_preprocessing': ['*.txt'], 
        'estnltk.tests.test_taggers': ['*.txt', 
                                       'test_dict_taggers/*.csv', 
                                       'miscellaneous/*.json',
                                       'test_standard_taggers/*.json',], 
        'estnltk.tests.test_visualisation': ['expected_outputs/direct_plain_span_visualiser_outputs/*.txt',
                                             'expected_outputs/indirect_plain_span_visualiser_outputs/*.txt',
                                             'expected_outputs/attribute_visualiser_outputs/*.txt'], 
        'estnltk.vabamorf': ['dct/2020-01-22_nosp/*.dct', 
                             'dct/2020-01-22_sp/*.dct'],
        'estnltk.wordnet': ['data/estwn-et-2.3.2/*.*'],
        'estnltk.visualisation': ['attribute_visualiser/*.css', 
                                  'attribute_visualiser/*.js', 
                                  'span_visualiser/*.css', 
                                  'span_visualiser/*.js']
    },

    author="University of Tartu",
    author_email="siim.orasmaa@gmail.com, alex.tk.fb@gmail.com, tpetmanson@gmail.com, swen@math.ut.ee",
    description="Estnltk — open source tools for Estonian natural language processing",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
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
        'nltk>=3.4.1 ; python_version >= "3.6"', # NLTK mainly required for tokenization
        'regex>=2015.07.19',       # improved Python regular expressions
        'python-crfsuite>=0.8.3',  # Conditional random fields library
        'cached-property>=1.2.0',  # Simple property for caching results
        'bs4', # BeautifulSoup: for processing XML files of the Estonian Reference Corpus
        'html5lib',      # for processing XML files of the Estonian Reference Corpus
        'lxml',          # required for importing/exporting TCF format data
        'networkx ; python_version >  "3.6"',      # building graphs: required for layers, WordNet and grammars (> py36)
        'networkx==2.5 ; python_version == "3.6"', # building graphs: required for layers, WordNet and grammars (= py36)
        'matplotlib ; python_version >  "3.6"',        # required for visualizing layer graph (> py36)
        'matplotlib==3.3.4 ; python_version == "3.6"', # required for visualizing layer graph (= py36)
        'requests',   # required for TextA export and WebTagger
        'tqdm',       # progressbar: for showing progress on time-hungry operations
        'ipython ; python_version >  "3.6"',         # required for integration with Jupyter Notebook-s (> py36)
        'ipython< 7.17.0 ; python_version == "3.6"', # required for integration with Jupyter Notebook-s (= py36)
        'conllu>=3.1.1 ; python_version >= "3.6"', # CONLLU for syntax
        'numpy==1.19.4 ; python_version == "3.6"', # This is the last numpy version that supports py36
        'pandas>=1.1.5 ; python_version >  "3.6"', # Panel Data Analysis library for Python (> py36)
        'pandas<=1.1.5 ; python_version == "3.6"', # Panel Data Analysis library for Python (= py36)
    ],
    #
    #  Note: if you need to build and install for Python 3.5, you need 
    #  the following fixed package versions:
    #     parso==0.7.0 
    #     matplotlib==3.0.3 
    #     pandas==0.25.3 
    #     regex==2018.08.29 
    #     networkx==2.4 
    #     ipython==7.9.0
    #     conllu==3.1.1
    #  ( tested on Ubuntu 18.04 )
    #
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
