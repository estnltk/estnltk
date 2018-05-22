#  Selects a random subset of files from a large set of files, 
#  and copies into the given directory.
#  Input files should be koondkorpus or etTenTen texts in JSON 
#  format, as produced by scripts "convert_ettenten_to_json.py", 
#  and "convert_koondkorpus_to_json.py".
#
#     Developed and tested under Python's version:  3.5.4
#     Estnltk version: 1.6.x

import re
import os, os.path
import argparse

from shutil import copy2
from random import randint

from datetime import datetime 
from datetime import timedelta

from estnltk.converters import json_to_text

max_texts             = 5000
discard_empty_files   = True
only_simulate_copying = False
file_extension        = 'json'

pattern_empty_string = re.compile('^\s*$')

# The main program
if __name__ == '__main__':
    # *** Parse input arguments
    arg_parser = argparse.ArgumentParser(description=\
    ''' Selects a random subset of files from a large set of files, and
        copies into the given directory.
        Input files should be koondkorpus or etTenTen texts in JSON format, 
        as produced by scripts "convert_ettenten_to_json.py", and 
        "convert_koondkorpus_to_json.py".
    ''')
    arg_parser.add_argument('in_dir', default = None, \
                                      help='the directory containing input files;'
    )
    arg_parser.add_argument('out_dir', default = None, \
                                      help='the output directory where the results '+\
                                            ' (picked files) will be copied.' )
    arg_parser.add_argument('-l', '--limit',  metavar='<max_texts>', \
                                      type = int, default = max_texts, \
                                      help='the number files chosen randomly from <in_dir>'+\
                                           '; Default: '+str(max_texts) )
    arg_parser.add_argument('--discard-empty-files', dest='discard_empty_files', \
                                      default=discard_empty_files, \
                                      help='Whether files without textual content will be discarded. '+\
                                           'If set, then the text content of each file will be checked '+\
                                           'before picking the file, and files with no content will be '+\
                                           'discarded. '+\
                                           'Default: '+str(discard_empty_files),\
                                      action='store_true')
    arg_parser.add_argument('--only-simulate-copy', dest='only_simulate_copying', \
                                      default=only_simulate_copying, \
                                      help='Whether copying is only simulated, not actually performed'+\
                                           ' (for testing purposes); Default: '+str(only_simulate_copying),\
                                      action='store_true')
    args = arg_parser.parse_args()
    in_dir  = args.in_dir if os.path.isdir(args.in_dir) else None
    out_dir = args.out_dir if os.path.isdir(args.out_dir) else None
    only_simulate_copying    = args.only_simulate_copying
    discard_empty_files      = args.discard_empty_files
    max_texts = args.limit

    if out_dir and in_dir:
       startTime = datetime.now() 
       # *** Collect input files ***
       all_files = os.listdir( in_dir )
       print('*'*70)
       print(' Discovered',len(all_files),' files.')

       # *** Pick a random sample ***
       picked_files = set()
       while (len(picked_files) < max_texts and len(picked_files) < len(all_files) - 1):
           i = randint(0, len(all_files) - 1)
           text_file = all_files[i]
           if not text_file.endswith(file_extension):
              continue
           if text_file not in picked_files:
              pick_file = True
              if discard_empty_files:
                  # Check that the file has any textual content
                  fnm = os.path.join( in_dir, text_file )
                  text = json_to_text(file=fnm)
                  if len(text.text) == 0 or \
                     pattern_empty_string.match(text.text):
                         pick_file = False
              if pick_file:
                  picked_files.add( text_file )
       print()
       print('*'*70)
       print(' Picked random sample of ',len(picked_files),' files.')

       # *** Copy files to the selection directory ***
       print()
       print('*'*70)
       print(' Copying picked files to ', out_dir)
       files_copied = 0
       for in_file_name in picked_files:
           # source file
           copySource = os.path.join( in_dir, in_file_name )
           # target file
           out_file_name = in_file_name
           outfnm = os.path.join( out_dir, out_file_name )
           copyTarget = outfnm
           if only_simulate_copying:
              copyTarget = None
           # 3) perform copying
           if copyTarget != None:
              copy2( copySource, copyTarget )
              files_copied += 1
       print()
       print(' ',files_copied,'files copied.')
       time_diff = datetime.now() - startTime
       print(' Total processing time: {}'.format(time_diff))
    else:
       arg_parser.print_help()
