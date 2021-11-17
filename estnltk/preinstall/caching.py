from collections import defaultdict
import os, os.path
import pickle
import csv

# Root directory of estnltk
ROOT_DIR = os.getcwd()
#ROOT_DIR = os.path.split(os.getcwd())[0]

# ========================================================================
#   Corrections for number analyses (used in PostMorphAnalysisTagger)
# ========================================================================

DEFAULT_NUMBER_ANALYSIS_RULES = \
        os.path.join(ROOT_DIR,'estnltk','taggers','standard','morph_analysis','number_fixes','number_analysis_rules.csv')

def load_number_analysis_rules_csv_with_pandas( csv_file:str ):
    '''Loads number analysis corrections from an input CSV file.
       Requires pandas package.
    '''
    import pandas
    df = pandas.read_csv(csv_file, na_filter=False, index_col=False)
    rules = defaultdict(dict)
    for _, r in df.iterrows():
        if r.suffix not in rules[r.number]:
            rules[r.number][r.suffix] = []
        rules[r.number][r.suffix].append({'partofspeech': r.pos, 'form': r.form, 'ending':r.ending})
    return rules


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


def create_number_analysis_rules_cache( csv_file:str=DEFAULT_NUMBER_ANALYSIS_RULES, force=False, verbose=False ):
    '''Creates a pickled version of the number analysis corrections CSV file.
       Note: the new pickled version is only created iff: 1) the pickle file 
       does not exist, 2) the pickle file is outdated, or 3) force==True;
    '''
    if not os.path.exists(csv_file):
        raise FileNotFoundError('(!) Missing number analysis corrections csv file: {!r}'.format(csv_file))
    cache = csv_file + '.pickle'
    if not os.path.exists(cache) or os.stat(cache).st_mtime < os.stat(csv_file).st_mtime or force==True:
        rules = load_number_analysis_rules_csv( csv_file )
        with open(cache, 'wb') as out_file:
            pickle.dump(rules, out_file)
        if verbose:
            print('> cache file {!r} created.'.format(os.path.split(cache)[1]) )


# ========================================================================
#   Main function
# ========================================================================

def create_caches():
    create_number_analysis_rules_cache( force=False, verbose=False )


#rules1 = load_number_analysis_rules_csv( DEFAULT_NUMBER_ANALYSIS_RULES )
#rules2 = load_number_analysis_rules_csv_with_pandas( DEFAULT_NUMBER_ANALYSIS_RULES )
#assert rules1 == rules2