# -*- coding: utf-8 -*-
#
#     Splits large 'koondkorpus' text files ( as found in http://ats.cs.ut.ee/keeletehnoloogia/estnltk/koond.zip )
#    into smaller, more easily processable files;
#
#    More specifically:
#     *) Processes a single file or a directory of files (depending on the command line arguments);
#     *) Reads a file into an EstNLTK (ver 1.4) Text, and tokenizes into sentences;
#     *) If the number of sentences exceeds *max_sentences*, splits the text into smaller texts
#        (texts with maximum size *max_sentences*), writes smaller texts into separate files, and
#        deletes the old file;
#        Otherwise (the the number of sentences not exceeding *max_sentences*) leaves the file as is it.
#
#    Developed and tested under Python's version:  3.4.4
#
#

from __future__ import unicode_literals, print_function

import re
import sys, codecs
import os, os.path
import json
import argparse

from pprint import pprint 
from timeit import default_timer as timer

from estnltk import Text
from estnltk.names import *
from estnltk.corpus import write_document, read_document

max_sentences = 2500

def format_time( sec ):
    ''' Re-formats time duration in seconds (*sec*) into more easily readable 
        form, where (days,) hours, minutes, and seconds are explicitly shown.
        Returns the new duration as a formatted string.
    '''
    import time
    if sec < 864000:
       # Idea from:   http://stackoverflow.com/a/1384565
       return time.strftime('%H:%M:%S', time.gmtime(sec))
    else:
       days = int(sec / 864000)
       secs = sec % 864000
       return str(days)+'d, '+time.strftime('%H:%M:%S', time.gmtime(secs))


def split_Text( text, file_name, verbose = True ):
    ''' Tokenizes the *text* (from *file_name*) into sentences, and if the number of 
        sentences exceeds *max_sentences*, splits the text into smaller texts.

        Returns a list containing the original text (if no splitting was required),
        or a list containing results of the splitting (smaller texts);
    '''
    if verbose:
       print('  processing '+file_name+' ... ', end="" )
    # Tokenize text into sentences
    start = timer()
    text = text.tokenize_sentences()
    all_sentences = len(text[SENTENCES])
    end = timer()
    if verbose:
       print('  (tok time: '+format_time( end-start )+')', end="" )
    if all_sentences > max_sentences:
       # Acquire spans of length *max_sentences* from the text
       start = timer()
       i = 0
       spans = []
       len_total = 0
       while i < all_sentences:
            startSent = text[SENTENCES][i]
            endSent   = text[SENTENCES][min(i+(max_sentences-1), all_sentences-1)]
            span = (startSent[START], endSent[END])
            len_total += (span[1]-span[0])
            spans.append(span)
            i += max_sentences
       # Divide the text into spans
       text_spans = text.texts_from_spans(spans)
       assert len(text.text) >= len_total, '(!) Total spans_len must be =< than text_len: '+str(len_total)+'/'+str(len(text.text))
       new_texts  = []
       for i, small_text in enumerate( text_spans ):
           newText = Text( small_text )
           for key in text.keys():
               if key != TEXT and key != SENTENCES and key != PARAGRAPHS:
                  newText[key] = text[key]
           newText['_text_split_id']     = i
           newText['_text_split_origin'] = str(spans[i])  #  Convert it to string; Otherwise, split_by(*) may mistakenly consider 
                                                          #  it a layer and may run into error while trying to split it;
           newText['_text_split_file']   = file_name
           #print( json.dumps(newText) )
           new_texts.append( newText )
       end = timer()
       if verbose:
           print('  (split time: '+format_time( end-start )+')', end="" )
           print('  (sents: '+str(all_sentences)+', new_texts:'+str(len(new_texts))+')', end="")
           print()
       return new_texts
    else:
       if verbose:
           print('  (sents: '+str(all_sentences)+', no_split)', end=" \n")
       return [text]


def write_Text_into_file( text, old_file_name, out_dir, suffix='__split', verbose=True ):
    ''' Based on *old_file_name*, *suffix* and *out_dir*, constructs a new file name and 
        writes *text* (in the ascii normalised JSON format) into the new file.
    ''' 
    name = os.path.basename( old_file_name )
    if '.' in name:
       new_name = re.sub('\.([^.]+)$', suffix+'.\\1', name)
    else:
       new_name = name + suffix
    new_path = os.path.join( out_dir, new_name )
    start = timer()
    #write_document( text, new_path )  # <--- this leaves indent=2 - takes too much extra space ...
    o_f = codecs.open( new_path, mode='wb', encoding='ascii' )
    o_f.write( json.dumps( text ) )
    o_f.close()
    end = timer()
    timestamp = format_time( end-start )
    if verbose:
       print('  ==>  '+new_path+' (file writing time: '+timestamp+')' )


arg_parser = argparse.ArgumentParser(description=\
'''
  Splits large 'koondkorpus' text files into smaller, more easily processable files. More specifically: 1) Processes a 
 single file or a directory of files (depending on the command line arguments), 2) Reads a file into an EstNLTK (ver 1.4) 
 Text, and tokenizes into sentences, 3) If the number of sentences exceeds *max_sentences*, splits the text into smaller 
 texts (texts with maximum size *max_sentences*), writes smaller texts into separate files, and deletes the old file; 
 otherwise (if the number of sentences does not exceed *max_sentences*) leaves the file as is it.
''')
arg_parser.add_argument('in_file_or_dir', default = None, \
                                    help='the input file (for processing a single file) or'+\
                                         ' the directory containing input files'+\
                                         ' (for processing the directory instead of a '+\
                                         ' single file);'
)
arg_parser.add_argument('out_dir', default = None, \
                                    help='the output directory where the results of the processing'+\
                                         ' (split JSON files) will be written.' )
arg_parser.add_argument('-l', '--limit',  metavar='<max_sentences>', \
                                          type = int, default = max_sentences, \
                                          help='the maximum number sentences the JSON file is allowed'+\
                                               ' to contain; if this number is exceeded, the file will'+\
                                               ' be split into smaller files. Default: '+str(max_sentences) )
args = arg_parser.parse_args()
in_dir  = args.in_file_or_dir if os.path.isdir(args.in_file_or_dir) else None
in_file = args.in_file_or_dir if os.path.isfile(args.in_file_or_dir) else None
out_dir = args.out_dir if os.path.isfile(args.out_dir) else None
max_sentences = args.limit

if (in_dir or in_file) and out_dir:
    start = timer()
    if in_file:
       # *** Process a single file ***
       text  = read_document( in_file )
       texts = split_Text( text, in_file )
       if len(texts) > 1:
           # If the text has been split into smaller texts, write smaller texts into 
           # new files:
           for k, small_text in enumerate(texts):
               write_Text_into_file( small_text, in_file, out_dir, suffix='__'+("%03d"%k) )
           # Remove the old file afterwards
           os.remove( in_file )
    elif in_dir:
       # *** Process a directory ***
       all_files = os.listdir( in_dir )
       processed_files = 0
       split_files     = 0
       for in_file_name in all_files:
           if not in_file_name.endswith('.txt'):
              continue
           in_file = os.path.join( in_dir, in_file_name )
           text  = read_document( in_file )
           texts = split_Text( text, in_file )
           if len(texts) > 1:
               # If the text has been split into smaller texts, write smaller texts into 
               # new files:
               for k, small_text in enumerate(texts):
                   write_Text_into_file( small_text, in_file, out_dir, suffix='__'+("%03d"%k) )
               # Remove the old file afterwards
               os.remove( in_file )
               split_files += 1
           processed_files += 1
       print(' > Processed ',processed_files,' files.')
       print(' > Split ',split_files,' files.')
    end = timer() 
    print(' Total processing time: '+format_time( end-start ) )
else:
    arg_parser.print_help()


