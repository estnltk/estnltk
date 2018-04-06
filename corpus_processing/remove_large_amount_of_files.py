#   Deletes all the files from the given directory that contains a
#  large amount of files.
#
#   Deleting a large amount of files (more than half a million) with
#  standard command line tools, such as the bash rm command, can be 
#  tricky (you may run into errors like "Argument list too long"). 
#  You can use this script to perform the deletion with the help
#  of Python.
#
#     Developed and tested under Python's version:  3.5.4
#

import sys
import os, os.path

import argparse

from datetime import datetime
from datetime import timedelta

sort_input              = False
do_not_ask_confirmation = False

# The main program
if __name__ == '__main__':
    # *** Parse input arguments
    arg_parser = argparse.ArgumentParser(description=\
    ''' Deletes all the files from the given directory that contains a
        large amount of files.
        
        Deleting a large amount of files (e.g. more than half a million 
        files) with standard command line tools, such as the bash rm 
        command, can be tricky (you may run into errors like "Argument 
        list too long"). You can use this script to avoid the hassle
        and perform the deletion with the help of Python.
    ''')
    arg_parser.add_argument('in_dir', default = None, \
                                      help='the directory containing the files '+\
                                           'that need to be deleted;'
    )
    arg_parser.add_argument('-y', '--yes-I-confirm', dest='do_not_ask_confirmation', \
                                      default=do_not_ask_confirmation, \
                                      help='If set, then the files will be deleted '+ \
                                           'without asking for user confirmation; '+\
                                           'Default: '+str(do_not_ask_confirmation),\
                                      action='store_true')
    args = arg_parser.parse_args()
    in_dir = args.in_dir if os.path.isdir(args.in_dir) else None
    do_not_ask_confirmation = args.do_not_ask_confirmation
    if in_dir:
        in_args_found = True
        # *** Process a directory ***
        all_files = os.listdir( in_dir )
        confirmed = True
        if not do_not_ask_confirmation:
            print(' Deleting',len(all_files),'files from ',in_dir,' [y/n]?')
            answer = input()
            if not( answer and answer.strip().lower() in ['y', 'yes'] ):
                 confirmed = False
        if confirmed:
            deleted = 0
            startTime = datetime.now() 
            if sort_input:
                 all_files = sorted(all_files)
            for in_file_name in all_files:
                 in_file = os.path.join( in_dir, in_file_name )
                 os.remove( in_file )
                 deleted += 1
            print(' > Removed ',deleted,' files.')
            time_diff = datetime.now() - startTime
            print(' Total processing time: {}'.format(time_diff))
    else:
       in_args_found = False
    if not in_args_found:
       print('Please provide input argument: \n <in_dir> !')


