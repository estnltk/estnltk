# -*- coding: utf-8 -*-
#
#    Script for preparing the etTenTen corpus before processing it with EstNLTK 1.6.0.
#    
#    Splits the content of "etTenTen.vert" (or "ettenten13.processed.prevert") into
#   separate web pages, converts page contents into JSON objects, adds metadata and 
#   writes the output (JSON objects) into text files.
#
#    Python version:  3.5.4
#

import os
import os.path
import json
import argparse
import re
import codecs

from datetime import datetime 
from datetime import timedelta

import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('etTenTenConverter')

output_ext = '.txt'    # extension of output files

# =======  Helpful utils

# Pattern for capturing names & values of attributes
tag_attrib_pat = re.compile('([^= ]+)="([^"]+?)"')

def parse_tag_attributes( tag_line ):
    ''' Fetches names & values of attributes from an XML tag string.
    '''
    attribs = {}
    for attr_match in tag_attrib_pat.finditer(tag_line):
        key   = attr_match.group(1)
        value = attr_match.group(2)
        if key in attribs:
           raise Exception(' (!) Unexpected: attribute "'+key+'" appears more than once in: '+tag_line)
        attribs[key] = value
    return attribs

def create_new_text_dict(doc_attribs, last_paragraph_texts, last_paragraph_attribs):
    ''' Creates a dict storing information gathered from a single web page.
    '''
    text_content = '\n\n'.join(last_paragraph_texts)
    text_content = re.sub('\n{3,}','\n\n', text_content)
    text_dict = {}
    # Add textual data
    text_dict['text'] = text_content
    # Add metadata
    for key, value in doc_attribs.items():
        if key in text_dict:
           raise Exception('(!) Unexpected: key "'+key+"' already in "+str(text_dict))
        text_dict[key] = value
    if last_paragraph_attribs:
        # If provided, add attributes of the paragraphs (HTML formatting)
        text_dict['paragraphs'] = {}
        for par_id, par_attribs in enumerate(last_paragraph_attribs): 
            text_dict['paragraphs'][par_id] = {}
            for key, value in par_attribs.items(): 
                text_dict['paragraphs'][par_id][key] = value
    return text_dict

def yield_docs( in_file, encoding='utf-8', discard_empty_paragraphs=True ):
    ''' Reads the input etTenTen corpus file document by document, and yields 
        dict objects corresponding to the documents.'''
    # Patterns for detecting tags
    corpusTagStart  = re.compile("<corpus[^<>]*>")
    docTagStart     = re.compile("<doc[^<>]+>")
    pTagStart       = re.compile("<p([^<>]+)>")
    pTagEnd         = re.compile("</p>")
    # Initialize
    lines = 0
    inside_p               = False
    last_attribs           = None
    last_paragraph_texts   = []
    last_paragraph_attribs = []
    with open( in_file, mode='r', encoding=encoding ) as f:
        # Process the content line by line
        for line in f:
            stripped_line = line.strip()
            mdoc = docTagStart.search(stripped_line)
            mpar =   pTagStart.search(stripped_line)
            epar =     pTagEnd.search(stripped_line)
            mcor = corpusTagStart.search(stripped_line)
            if mdoc: # start of a new document
                # A) Save the old content
                if len(last_paragraph_texts) > 0:
                    # Check if the last paragraph was empty
                    if discard_empty_paragraphs:
                        while len(last_paragraph_texts) > 0:
                            last_par = last_paragraph_texts[-1]
                            if len(last_par) == 0 or re.match('^\s+$', last_par):
                                # If it was empty, remove the empty paragraph
                                last_paragraph_texts.pop()
                                last_paragraph_attribs.pop()
                            else:
                                break
                    # Create and yield new document
                    yield create_new_text_dict(last_attribs, \
                                               last_paragraph_texts, \
                                               last_paragraph_attribs)
                # B) Start storing new content
                attribs = parse_tag_attributes( stripped_line )
                last_attribs           = attribs
                last_paragraph_texts   = []
                last_paragraph_attribs = []
                inside_p = False
            # New paragraph
            if mpar and not inside_p:
                inside_p = True
                if discard_empty_paragraphs:
                    # Check if the last paragraph was empty
                    if last_paragraph_texts:
                        last_par = last_paragraph_texts[-1]
                        if len(last_par) == 0 or re.match('^\s+$', last_par):
                            # If it was empty, remove the empty paragraph
                            last_paragraph_texts.pop()
                            last_paragraph_attribs.pop()
                attribs = parse_tag_attributes( stripped_line )
                # Add new paragraph
                last_paragraph_texts.append('')
                last_paragraph_attribs.append(attribs)
            # Paragraph's end
            if epar:
                  inside_p = False
            # Text content inside paragraph
            if inside_p and not mpar and len( stripped_line ) > 0:
                line = re.sub('\n{2,}','\n', line)
                last_paragraph_texts[-1] += line
            lines += 1
        # Process the last item
        if len(last_paragraph_texts) > 0:
            # Check if the last paragraph was empty
            if discard_empty_paragraphs:
                while len(last_paragraph_texts) > 0:
                    last_par = last_paragraph_texts[-1]
                    if len(last_par) == 0 or re.match('^\s+$', last_par):
                        # If it was empty, remove the empty paragraph
                        last_paragraph_texts.pop()
                        last_paragraph_attribs.pop()
                    else:
                        break
            # Create and yield new document
            yield create_new_text_dict(last_attribs, \
                                       last_paragraph_texts, \
                                       last_paragraph_attribs)


# =======  Parse input arguments
arg_parser = argparse.ArgumentParser(description=''' 
  Splits the content of "etTenTen.vert" (or "ettenten13.processed.prevert") into
 separate web pages, converts page contents into JSON objects, adds metadata and 
 writes the output (JSON objects) into text files.
''')
arg_parser.add_argument('in_file', default = None, \
                                   help='the content of etTenTen corpus in a single '+\
                                        'text file (file named "etTenTen.vert" or '+\
                                        '"ettenten13.processed.prevert"). The file '+\
                                        'should (loosely) follow the XML format: the '+\
                                        'content of the whole corpus should be inside '+\
                                        '<corpus>-tags, and each single document (web '+\
                                        'page) should be within <doc>-tags. Textual '+\
                                        'content inside <doc>-tags should be cleaned '+\
                                        'from most of the other HTML-tags, except <p>-tags.',\
                                        )
arg_parser.add_argument('out_dir', default = None, \
                                   help='the output directory where the results '+\
                                        'of conversion (JSON text files) will be '+\
                                        'written. Output files will have extension '+\
                                         output_ext,\
                                         )
arg_parser.add_argument('--amount', type=int, default = None, \
                                    help='the number of documents that are converted '+\
                                         'into JSON files. This is only used for testing '+\
                                         'purposes, e.g. if one wants to test the '+\
                                         'conversion of a small subset of documents.',\
                                    )
args = arg_parser.parse_args()
in_file = args.in_file if os.path.isfile(args.in_file) else None
out_dir = args.out_dir if os.path.isdir(args.out_dir) else None
convert_only_n_docs = args.amount

if in_file and out_dir:
    assert output_ext.startswith('.')
    # =======  Initialize
    domains     = {}
    urls        = {}
    document_id = 0
    startTime = datetime.now() 
    # =======  Process content doc by doc
    for text in yield_docs( in_file, encoding='utf-8' ):
        if 'web_domain' not in text:
            for k,v in text.items():
                print (k,':', v)
            raise Exception(' (!) Web domain name not available in text! ' )
        domain_name = text['web_domain']
        domain_name = domain_name.replace('.', '_')
        fnm = domain_name+'__'+str(document_id)+output_ext
        out_file_path = os.path.join(out_dir, fnm)
        logger.info(' Writing document {0}'.format(out_file_path))
        # Output the results 
        # ( for consistency, use the same output method as in 
        #   https://github.com/estnltk/estnltk/blob/1.4.1/estnltk/corpus.py#L80 )
        with codecs.open(out_file_path, 'wb', 'ascii') as f:
            f.write( json.dumps(text, indent=2) )
        document_id += 1
        if convert_only_n_docs and convert_only_n_docs <= document_id:
            break
    print()
    print( document_id,'documents converted. ')
    time_diff = datetime.now() - startTime
    print(' Total processing time: {}'.format(time_diff))
else:
    arg_parser.print_help()
