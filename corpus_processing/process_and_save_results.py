#
#   Analyses JSON format data, adding layers of analyses up to the level 
#   of morphological analysis (incl).
#   Saves results as EstNLTK 1.6.x JSON export files (recommended), or 
#   as pickle Text objects.
#   This script is for processing large corpora -- Koondkorpus and 
#   etTenTen -- with EstNLTK.
#
#   Developed and tested under Python's version:  3.5.4
#                              EstNLTK version:   1.6.1_beta
#

import os, os.path
import argparse
import pickle

from datetime import datetime 
from datetime import timedelta

from estnltk import Text
from estnltk.taggers import SentenceTokenizer
from estnltk.taggers.morph_analysis.gt_morf import GTMorphConverter
from estnltk.taggers.syntax_preprocessing.syntax_ignore_tagger import SyntaxIgnoreTagger

from estnltk.converters import text_to_json, json_to_text

from estnltk.corpus_processing.parse_koondkorpus import get_text_subcorpus_name

skip_existing         = True   # skip existing files (continue analysis where it stopped previously)
skip_saving           = False  # skip saving (for debugging purposes)
record_sentence_fixes = True   # record types of sentence postcorrections (for debugging purposes)
add_clauses           = True   # add layer 'clauses'
add_syntax_ignore     = True   # add layer 'syntax_ignore'
add_gt_morph_analysis = True   # add layer 'gt_morph_analysis'

input_ext     = '.json'     # extension of input files
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


# The main program
if __name__ == '__main__':
    # =======  Parse input arguments
    arg_parser = argparse.ArgumentParser(description=\
    '''  Analyses JSON format text data with EstNLTK 1.6.x, adding layers of 
         analyses up to the level of morphological analysis (incl).
         Saves results as EstNLTK JSON export files (recommended), or 
         as pickle Text objects.
         This script is for processing large corpora -- Koondkorpus and 
         etTenTen -- with EstNLTK.
    ''')
    arg_parser.add_argument('in_dir', default = None, \
                                      help='the directory containing input files; '+\
                                           'Input files should be JSON files in UTF-8 encoding. '+\
                                           "It is expected that EstNLTK's function text_to_json "+\
                                           'was used for creating the files.'
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
            out_file_name_pckl = in_file_name.replace(input_ext, '.pickle')
            out_file_name_json = in_file_name.replace(input_ext, '.json')
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
            text = json_to_text(file=fnm)
            # Perform the analysis
            try:
                # 0) Add metadata
                if corpus_type.lower() == 'koond':
                    text_subcorpus = get_text_subcorpus_name( in_dir, in_file_name, None )
                    text.meta['subcorpus'] = str(text_subcorpus)

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

                # 3) Add clauses
                if add_clauses:
                    text.tag_layer(['clauses'])

                # 4) Convert morph analyses to GT format 
                if add_gt_morph_analysis:
                    gt_converter.tag( text )
                    
                # 5) Add syntax_ignore
                if add_syntax_ignore:
                    syntax_ignore_tagger.tag( text )

                # 6) Save results
                if not skip_saving:
                    if output_format == 'pickle':
                       with open( ofnm_pckl, 'wb' ) as fout:
                            pickle.dump(text, fout)
                    else:
                       text_to_json(text, file=ofnm_json)
                    new_files += 1

            # X) Log errors
            except RuntimeError as err:
                write_error_log( in_file_name, err )
                errors += 1
            except Exception as err:
                write_error_log( in_file_name, err )
                errors += 1
            processed += 1

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



