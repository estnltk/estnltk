# -*- coding: utf-8 -*-
#
#   Analyses JSON format data, adding layers of analyses up to the level 
#   of morphological analysis (incl).
#   Saves results as EstNLTK 1.6.0 JSON export files (recommended), or 
#   as pickle Text objects.
#   This script is for processing large corpora -- Koondkorpus and 
#   etTenTen -- with EstNLTK.
#
#   Developed and tested under Python's version:  3.5.4
#                              EstNLTK version:   1.6.0_beta
#
#

import re
import sys, codecs
import os, os.path
import json
import argparse
import pickle

from datetime import datetime 
from datetime import timedelta

from estnltk import Text
from estnltk.taggers import SentenceTokenizer
from estnltk.taggers.syntax_preprocessing.syntax_ignore_tagger import SyntaxIgnoreTagger
from estnltk.taggers.morph.gt_morf import GTMorphConverter

from estnltk.converters import export_json

skip_existing         = True   # skip existing files (continue analysis where it stopped previously)
skip_saving           = False  # skip saving (for debugging purposes)
record_sentence_fixes = True   # record types of sentence postcorrections (for debugging purposes)
add_metadata          = True   # add metadata to Text 
add_syntax_ignore     = True   # add layer 'syntax_ignore'
add_gt_morph_analysis = True   # add layer 'gt_morph_analysis'

input_ext     = '.txt'      # extension of input files
corpus_type   = 'ettenten'  # 'koond' or 'ettenten'
output_format = 'json'      # 'json' or 'pickle'

skip_list     = []          # files to be skipped (for debugging purposes)

# =======  Helpful utils

def write_error_log( fnm, err ):
    ''' Writes information about a processing error into
        file "__errors.txt".
    '''
    err_file = "__errors.txt"
    if not os.path.exists(err_file):
        with open(err_file, 'w', encoding='utf-8') as f:
            pass
    with open(err_file, 'a', encoding='utf-8') as f:
        f.write( '{} :'.format(datetime.now())+' '+str(fnm)+' : ' )
        f.write( "{0}".format(err)+'\n\n' )


def load_in_file_names( fnm ):
    ''' Loads names of the input files from a text file. 
        Each name should be on a separate line.
    '''
    filenames = []
    with open(fnm, 'r', encoding='utf-8') as f:
       for line in f:
           line = line.strip()
           if len( line ) > 0:
              filenames.append( line )
    return filenames


def get_text_type_for_koond( corpus_dir, corpus_file ):
    ''' Detects and assigns the type of text (in case of Koondkorpus files).
        In most cases, the type is determined by analysing the name of the 
        input file; in some cases, metadata inside the file also needs to be 
        checked.
    '''
    f_prefix  = re.sub('^([A-Za-z_\-]+)(\.|[0-9]+).*', '\\1', corpus_file)
    text_type = None
    if f_prefix.startswith('ilu_'):
        f_prefix  = 'ilu_'
        text_type = f_prefix
    if f_prefix.startswith('tea_'):
        f_prefix = 'tea_'
        text_type = f_prefix
    if f_prefix.startswith('agraar_'):
        f_prefix = 'tea_'
        text_type = f_prefix
    if f_prefix.startswith('horisont_'):
        f_prefix = 'tea_'
        text_type = f_prefix
    if f_prefix.startswith('sea_'):
        f_prefix = 'sea_'
        text_type = f_prefix
    if f_prefix.startswith('rkogu_'):
        f_prefix = 'rkogu_'
        text_type = f_prefix
    if f_prefix.startswith('aja_'):
        text_type = f_prefix
    # If text type cannot be determined from the name of the file, 
    # try to get it from metadata of the Text object
    if not text_type:
        fnm = os.path.join( corpus_dir, corpus_file )
        with codecs.open(fnm, 'rb', 'ascii') as f:
            t = json.loads(f.read())
        if t:
            if 'alamfoorum' in t.keys():
                text_type = 'netifoorum'
            elif 'type' in t.keys():
                if t['type'] == 'jututoavestlus':
                    text_type = t['type']
                elif t['type'] == 'uudisgrupi_salvestus':
                    text_type = t['type']
                elif t['type'] == 'kommentaarid':
                    text_type = 'neti'+t['type']
    return text_type


# =======  Parse input arguments

arg_parser = argparse.ArgumentParser(description=\
'''  Analyses JSON format text data with EstNLTK 1.6.0, adding layers of 
     analyses up to the level of morphological analysis (incl).
     Saves results as EstNLTK JSON export files (recommended), or 
     as pickle Text objects.
     This script is for processing large corpora -- Koondkorpus and 
     etTenTen -- with EstNLTK.
''')
arg_parser.add_argument('in_dir', default = None, \
                                  help='the directory containing input files; '+\
                                       'Input files should be JSON files, in binary '+\
                                       'format, containing only ASCII symbols (non-ASCII '+\
                                       'characters escaped). Analysable text should be '+\
                                       'under the key "text", and other keys may contain '+\
                                       'metadata about the text. Basically, the input files '+\
                                       'should be JSON files created by EstNLTK 1.4.1 method '+\
                                       'write_document (see '+\
                                       'https://github.com/estnltk/estnltk/blob/1.4.1/estnltk/corpus.py#L80'+\
                                       ' for details)'
)
arg_parser.add_argument('--in_files', default = None, \
                                      help='a text file containing names of the input '+\
                                           'files (files from in_dir) that should be '+\
                                           'analysed. File names should be separated by newlines. '+\
                                           'Use this argument to specify a subset of files to be '+\
                                           'analysed while parallelizing the analysis process. '+\
                                           'You can use the script "split_large_corpus_files_into_subsets.py" '+\
                                           'for splitting the input corpus into subsets of files.')
arg_parser.add_argument('out_dir', default = None, \
                                    help='the output directory where the results '+\
                                         'of analysis (one output file per each input file) '+\
                                         'will be written.')
arg_parser.add_argument('--koond', default = False,
                                    help='If set, then expects that the input files come '+\
                                         'from Koondkorpus (and applies Koondkorpus-specific meta-'+\
                                         'data acquisition methods). Otherwise, assumes that input '+\
                                         'files come from etTenTen.',\
                                         action='store_true')
arg_parser.add_argument('--pickle', default = False,
                                    help='If set, then changes the output format from json (which is '+\
                                         'default) to pickle. Note that pickle files take up more space '+\
                                         'and therefore the recommended format for processing large '+\
                                         'corpora is json.', \
                                         action='store_true')

args     = arg_parser.parse_args()
in_dir   = args.in_dir  if os.path.isdir(args.in_dir)  else None
out_dir  = args.out_dir if os.path.isdir(args.out_dir) else None
in_files = args.in_files if args.in_files and os.path.isfile(args.in_files) else None
if args.in_files and not os.path.isfile(args.in_files):
    print(' Unable to load input from',in_files,'...' )
output_format = 'pickle' if args.pickle==True else 'json'
corpus_type   = 'koond' if args.koond==True else 'ettenten'

if out_dir and in_dir:
    assert corpus_type and corpus_type.lower() in ['koond', 'ettenten']
    assert output_format and output_format.lower() in ['json', 'pickle']
    # =======  Collect input files
    print(' Type of the input corpus: ', corpus_type)
    if not in_files:
        all_files = os.listdir( in_dir )
    else:
        print(' Loading input from',in_files,'...' )
        all_files = load_in_file_names( in_files )
    print('*'*70)
    print(' Found',len(all_files),' files.')
    # =======  Initialize
    sentence_tokenizer   = SentenceTokenizer()
    syntax_ignore_tagger = SyntaxIgnoreTagger()
    gt_converter         = GTMorphConverter()
    startTime = datetime.now() 
    elapsed = 0
    errors  = 0
    skipped = 0
    processed = 0
    new_files = 0
    for in_file_name in all_files:
        fnm  = os.path.join( in_dir, in_file_name )
        # skip dirs and non-input files
        if os.path.isdir( fnm ):
            continue
        if not fnm.endswith( input_ext ):
            continue
        if in_file_name in skip_list:
            continue
        # construct output file, and check whether it already exists
        out_file_name_pckl = in_file_name.replace('.txt', '.pickle')
        out_file_name_json = in_file_name.replace('.txt', '.json')
        ofnm_pckl = os.path.join( out_dir, out_file_name_pckl )
        ofnm_json = os.path.join( out_dir, out_file_name_json )
        if skip_existing:
            if os.path.exists( ofnm_pckl ):
                print('(!) Skipping existing file:', ofnm_pckl)
                processed += 1
                skipped += 1
                continue
            if os.path.exists( ofnm_json ):
                print('(!) Skipping existing file:', ofnm_json)
                processed += 1
                skipped += 1
                continue
        # Load input text from JSON
        text_dict = None
        with codecs.open(fnm, 'rb', 'ascii') as f:
            text_dict = json.loads(f.read())
        if 'text' in text_dict:
            # Perform the analysis
            try:
                text = Text( text_dict['text'] )
                # 0) Add metadata
                if add_metadata:
                    for key in text_dict:
                        meta_value = text_dict[key]
                        if isinstance(meta_value, (str, int, float)) and key not in ['text']:
                            text.meta[key] = meta_value
                    if corpus_type.lower() == 'koond':
                        text_type = get_text_type_for_koond( in_dir, in_file_name )
                        text.meta['subcorpus'] = str(text_type)

                # 1) Add basic/tokenization annotations
                text.tag_layer(['words'])
                if record_sentence_fixes:
                    sentence_tokenizer.tag(text, record_fix_types=True)
                else:
                    sentence_tokenizer.tag(text)
                text.tag_layer(['paragraphs'])
                word_spans = text['words'].spans
                
                if output_format == 'pickle':
                    print(processed,'->',ofnm_pckl)
                else:
                    print(processed,'->',ofnm_json)

                # 2) Add morphological analysis
                text.tag_layer(['morph_analysis'])
                
                # 3) Convert morph analyses to GT format 
                if add_gt_morph_analysis:
                    gt_converter.tag( text )
                    
                # 4) Add syntax_ignore
                if add_syntax_ignore:
                    syntax_ignore_tagger.tag( text )
                # 5) Save results
                if not skip_saving:
                    if output_format == 'pickle':
                       with open( ofnm_pckl, 'wb' ) as fout:
                            pickle.dump(text, fout)
                    else:
                       export_json(text, file=ofnm_json)
                    new_files += 1
                    
            # X) Log errors
            except RuntimeError as err:
                write_error_log( in_file_name, err )
                errors += 1
            except Exception as err:
                write_error_log( in_file_name, err )
                errors += 1
            processed += 1

        else:
            err_msg = '(!) Error in input JSON file: key "text" is missing.'
            print(err_msg)
            pprint(text_dict)
            write_error_log( in_file_name, err_msg )
            errors += 1

        # Report processing status and time elapsed
        if processed % 500 == 0:
            print(processed)
        time_diff = datetime.now() - startTime 
        minutes = time_diff / timedelta(minutes=1)
        seconds = time_diff / timedelta(seconds=1)
        if (2 <= int(minutes) < 3 and elapsed == 0) or \
           (5 <= int(minutes) < 6 and elapsed == 1) or \
           (7 <= int(minutes) < 8 and elapsed == 2) or \
           (10 <= int(minutes) < 11 and elapsed == 3) or \
           (15 <= int(minutes) < 16 and elapsed == 4) or \
           (30 <= int(minutes) < 31 and elapsed == 5):
            print()
            print('Time elapsed (hh:mm:ss.ms) {}'.format(time_diff))
            print()
            elapsed += 1
    print()

    # Report final statistics about processing
    if in_files:
        print('  Finished processing subset listed in',in_files,'.')
    print(' ',errors,'processing errors.')
    print(' ',processed,'files processed (incl',skipped,'files skipped).')
    print(' ',new_files,'new files created.')
    time_diff = datetime.now() - startTime
    print(' Total processing time: {}'.format(time_diff))
else:
    arg_parser.print_help()



