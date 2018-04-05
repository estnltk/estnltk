# -*- coding: utf-8 -*-
#
#   Loads file names from a directory containing a large number of 
#   files (e.g. ~700000), and splits the file names into given number
#   of subsets. Use this script to enable parallel processing of
#   Koondkorpus and etTenTen files: split files into N subsets, and 
#   evoke N instances of the script "process_and_save_results.py"
#   to process the files.
#
#   Developed and tested under Python's version:  3.5.4
#

import os, os.path
import argparse

from datetime import datetime 
from datetime import timedelta

input_ext = '.json'    # extension of input files

def save_file_names( files_list, out_fnm ):
    ''' Saves the list of file names into the file out_fnm.
    '''
    with open(out_fnm, 'w', encoding='utf-8') as f:
       for fnm in files_list:
           f.write(fnm+'\n')

# The main program
if __name__ == '__main__':
    # *** Parse input arguments
    arg_parser = argparse.ArgumentParser(description=\
    ''' Loads file names from a directory containing a large number of 
        files (e.g. ~700000), and splits the file names into given number
        of subsets. Use this script to enable parallel processing of
        Koondkorpus and etTenTen files: split files into N subsets with this
        script, and then evoke N instances of the script 
        "process_and_save_results.py" to process the files.
    ''')
    arg_parser.add_argument('in_dir', default = None, \
                                      help='the directory containing input files. '+\
                                           'Expected extension of the input files is '+\
                                           ''+input_ext+""
    )
    arg_parser.add_argument('--splits', type=int, default = None, \
                                        help='number of splits (integer);')
    args = arg_parser.parse_args()
    in_dir = args.in_dir if os.path.isdir(args.in_dir) else None
    nr_of_splits = args.splits


    if in_dir and nr_of_splits and nr_of_splits > 0:
        startTime = datetime.now() 
        # *** Collect input files ***
        all_files = os.listdir( in_dir )
        print('*'*70)
        print(' Found',len(all_files),'files.')
        print(' Splitting into',nr_of_splits,'groups.')
        # *** Create placeholders for groups
        groups = []
        for i in range(nr_of_splits):
            groups.append([])
        # *** Split names into groups
        j = 0
        processed = 0
        for in_file_name in all_files:
            fnm = os.path.join( in_dir, in_file_name )
            # skip dirs and non-input files
            if os.path.isdir( fnm ):
                continue
            if not fnm.endswith( input_ext ):
                continue
            groups[j].append( in_file_name )
            j += 1
            if j >= nr_of_splits:
                j = 0
            processed += 1
            # report elapsed time
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
        # Save groups into separate files
        print()
        print(' Saving groups:')
        dirname = in_dir.replace('/','_').replace('\\','_').replace(':','_')
        for i in range(nr_of_splits):
            out_fnm = dirname+'__'+str(i+1)+'_of_'+str(nr_of_splits)+'.txt'
            print(' --> '+out_fnm+' ('+str(len(groups[i]))+' items)')
            save_file_names( groups[i], out_fnm )
        # Report final statistics about the processing
        print(' ',processed,'files processed.')
        time_diff = datetime.now() - startTime
        print(' Total processing time: {}'.format(time_diff))
    else:
        arg_parser.print_help()




