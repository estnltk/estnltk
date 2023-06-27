# -*- coding: utf-8 -*-
from setuptools import setup, Extension
from setuptools import find_namespace_packages
import os, os.path
import sys

# Required for extraction of version info
import re

# Required for creating caches for number_analysis_rules
from collections import defaultdict
import pickle
import csv

# Get version number from __init__.py
# Based on: 
#  https://milkr.io/kfei/5-common-patterns-to-version-your-Python-package/3
def get_version():
    VERSIONFILE = os.path.join('estnltk', '__init__.py')
    initfile_lines = open(VERSIONFILE, 'rt', errors='ignore').readlines()
    VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
    for line in initfile_lines:
        mo = re.search(VSRE, line, re.M)
        if mo:
            return mo.group(1)
    raise RuntimeError('Unable to find version string in {!r}.'.format(VERSIONFILE))


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

swig_opts = ['-builtin']  # Disable proxy classes
#swig_opts = []             # Enable proxy classes 

# How enabling proxy classes affects vabamorf's speed:
#  https://github.com/estnltk/estnltk/blob/devel_1.6/dev_documentation/vabamorf_benchmarking/vabamorf_speed_benchmarking.md


# Python 3 specific configuration
extra = {}
if sys.version_info[0] == 3:
    swig_opts.append('-py3')
swig_opts.append('-c++')

# Check command line args: are we making a source distribution?
is_source_dist = 'sdist' in sys.argv

exclude_package_dirs = ["scribbles*", "venv*"]
# If we are making a source distribution, then include 
# "src" and "include"; otherwise: exclude them.
if not is_source_dist:
    exclude_package_dirs.append("src*")
    exclude_package_dirs.append("include*")

#
# Create necessary cached files
#
# Note: this was done in a separate "preinstall" module previously, 
# but now we have to do it here, inside setup.py, because the new 
# build system defined in "pyproject.toml" currently does not allow 
# to import local modules while building. 
#
def load_number_analysis_rules_csv( csv_file:str, encoding='utf-8' ):
    '''Loads number analysis corrections from an input CSV file.
       Works with the csv module, no pandas package dependency.
    '''
    rules = defaultdict(dict)
    with open(csv_file, 'r', newline='', encoding=encoding) as csvfile_in:
        fle_reader = csv.reader(csvfile_in, delimiter=',')
        header = next(fle_reader)
        # Collect and validate header
        missing = []
        for attr in ('number','suffix','pos','form','ending'):
            if attr not in header:
                missing.append(attr)
        assert not missing, \
            '(!) CSV file header misses the following key(s): '+str(missing)
        # Collect and aggregate analyses
        for row in fle_reader:
            assert len(row) == len(header), \
                   '(!) Unexpected number of elements in a row: {!r}'.format(row)
            r = {}
            for kid, key in enumerate(header):
                r[key] = row[kid]
            # Collect rule
            if r['suffix'] not in rules[r['number']]:
                rules[r['number']][r['suffix']] = []
            rules[r['number']][r['suffix']].append( {'partofspeech': r['pos'], \
                                                     'form': r['form'], \
                                                     'ending':r['ending']} )
    return rules


def create_number_analysis_rules_cache( csv_file:str=None, force=False, verbose=False ):
    '''Creates a pickled version of the number analysis corrections CSV file.
       This cache file is used by PostMorphAnalysisTagger to speed up the 
       processing. 
       Note: the new pickled version is only created iff: 1) the pickle file 
       does not exist, 2) the pickle file is outdated, or 3) force==True;
    '''
    if csv_file is None:
        # Default path for NUMBER_ANALYSIS_RULES
        csv_file = \
            os.path.join(os.getcwd(),'estnltk','taggers','standard','morph_analysis',
                                     'number_fixes','number_analysis_rules.csv')
    if not os.path.exists(csv_file):
        raise FileNotFoundError('(!) Missing number analysis corrections csv file: {!r}'.format(csv_file))
    cache = csv_file + '.pickle'
    if not os.path.exists(cache) or os.stat(cache).st_mtime < os.stat(csv_file).st_mtime or force==True:
        rules = load_number_analysis_rules_csv( csv_file )
        with open(cache, 'wb') as out_file:
            pickle.dump(rules, out_file)
        if verbose:
            print('> cache file {!r} created.'.format(os.path.split(cache)[1]) )

# create number_analysis_rules_cache for PostMorphAnalysisTagger
if not is_source_dist:
    create_number_analysis_rules_cache()


setup(
    name="estnltk",
    version=get_version(),
    packages=find_namespace_packages(exclude=exclude_package_dirs),
    # the list of package data used by "build", "bdist" and "install"
    include_package_data=True,
    package_data={
        'estnltk.java': [ 'res/*.*'],
        'estnltk.storage': ['postgres/tests/*.conll'],
        'estnltk.taggers.standard.ner': ['gazetteer/*', 'models/py3_default/*'],
        'estnltk.taggers.standard.morph_analysis': ['number_fixes/*.*', 
                                                    'reorderings/*.*',
                                                    'ud_conv_rules/*.*'],
        'estnltk.taggers.standard.syntax': ['files/*.*', 
                                            'files/LICENSE', 
                                            'maltparser_tagger/java-res/maltparser/maltparser-1.9.0.jar', 
                                            'maltparser_tagger/java-res/maltparser/MaltParser_LICENSE.txt', 
                                            'maltparser_tagger/java-res/maltparser/morph_analysis_conllu.mco', 
                                            'maltparser_tagger/java-res/maltparser/lib/*.*', 
                                            'preprocessing/rules_files/*.*',
                                            'ud_validation/agreement_resources/*.*',
                                            'ud_validation/data/*.*'],
        'estnltk.taggers.standard.text_segmentation': ['*.csv'], 
        'estnltk.taggers.miscellaneous':  ['*.csv', 
                                           'verb_chains/v1_4_1/res/*.*'],
        'estnltk.tests.converters': ['*.conll'], 
        'estnltk.tests.corpus_processing': ['*.vert'], 
        'estnltk.tests.taggers': ['standard/morph_analysis/*.csv',
                                  'standard/syntax/preprocessing/*.txt',
                                  'miscellaneous/*.json',
                                  'system/*.json',
                                  'system/dict_taggers/*.csv'],
        'estnltk.tests.visualisation': ['expected_outputs/direct_plain_span_visualiser_outputs/*.txt',
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
    long_description=open('README.md', errors='replace').read(),
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
        'estnltk-core >= 1.7.1',   # EstNLTK's basic datastructures and conversion methods
        'nltk>=3.4.1',             # NLTK mainly required for tokenization
        'regex>=2015.07.19',       # improved Python regular expressions
        'python-crfsuite>=0.8.3',  # Conditional random fields library
        'cached-property>=1.2.0',  # Simple property for caching results
        'bs4',                     # BeautifulSoup: for processing XML files of the Estonian Reference Corpus
        'html5lib',                # for processing XML files of the Estonian Reference Corpus
        'lxml',                    # required for importing/exporting TCF format data
        'networkx',                # building graphs: required for layers, WordNet and grammars
        'matplotlib',              # required for visualizing layer graph
        'requests',                # required for TextA export and WebTagger
        'tqdm',                    # progressbar: for showing progress on time-hungry operations
        'ipython',                 # required for integration with Jupyter Notebook-s
        'conllu',                  # CONLLU for syntax
        'pandas',                  # Panel Data Analysis library for Python
        'pyahocorasick',           # Fast multi-pattern string search 
    ],
    classifiers=['Intended Audience :: Developers',
                 'Intended Audience :: Education',
                 'Intended Audience :: Science/Research',
                 'Intended Audience :: Information Technology',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 3.7',
                 'Programming Language :: Python :: 3.8',
                 'Programming Language :: Python :: 3.9',
                 'Programming Language :: Python :: 3.10',
                 'Topic :: Scientific/Engineering',
                 'Topic :: Scientific/Engineering :: Artificial Intelligence',
                 'Topic :: Scientific/Engineering :: Information Analysis',
                 'Topic :: Text Processing',
                 'Topic :: Text Processing :: Linguistic']
)
