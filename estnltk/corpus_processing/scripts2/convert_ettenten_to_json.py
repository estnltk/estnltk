#
#   Script for preparing the etTenTen corpus before processing it with EstNLTK 1.6.x
#   
#   Splits the content of "etTenTen.vert" (or "ettenten13.processed.prevert") into
#  separate web pages, converts page contents into EstNLTK's Text objects (which will
#  contain text + metadata, but no linguistic analyses) and writes the results into
#  JSON format files.
#
#   Python version:  3.5.4
#

import re
import os
import os.path
import argparse

from datetime import datetime 
from datetime import timedelta

from estnltk.text import Text
from estnltk.converters import export_json, import_json

import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('etTenTenConverter')

output_ext = '.json'    # extension of output files

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


def create_new_text(doc_attribs, last_paragraph_texts, last_paragraph_attribs):
    ''' Creates a dict storing information gathered from a single web page.
    '''
    text_content = '\n\n'.join(last_paragraph_texts)
    text_content = re.sub('\n{3,}','\n\n', text_content)
    # Create a new Text object
    text = Text( text_content )
    # Add metadata
    for key, value in doc_attribs.items():
        if key in text.meta:
           raise Exception('(!) Unexpected: key "'+key+"' already in "+str(text.meta))
        text.meta[key] = value
    if last_paragraph_attribs:
        # If provided, add attributes of the paragraphs (HTML formatting)
        # Note: a current / temporary solution is to store the attributes 
        # as metadata
        # However, a proper solution would be to keep  attributes with the 
        # corresponding paragraphs (but this requires that the paragraphs
        # have been annotated in the first place)
        text.meta['_paragraphs'] = {}
        for par_id, par_attribs in enumerate(last_paragraph_attribs): 
            text.meta['_paragraphs'][par_id] = {}
            for key, value in par_attribs.items(): 
                text.meta['_paragraphs'][par_id][key] = value
    return text


def yield_docs( in_file, encoding='utf-8', \
                         discard_empty_paragraphs=True, \
                         store_paragraph_attributes=False ):
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
                    if not store_paragraph_attributes:
                        last_paragraph_attribs = []
                    yield create_new_text(last_attribs, \
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
            if not store_paragraph_attributes:
                last_paragraph_attribs = []
            yield create_new_text(last_attribs, \
                                  last_paragraph_texts, \
                                  last_paragraph_attribs)


# =======  Parse input arguments
arg_parser = argparse.ArgumentParser(description=''' 
  Splits the content of "etTenTen.vert" (or "ettenten13.processed.prevert") into
 separate web pages, converts page contents into EstNLTK's Text objects (which will
 contain text + metadata, but no linguistic analyses) and writes the results into
 JSON format files.
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
                                        'of conversion (Text objects in JSON format) will '+\
                                        'be written. Output files will have extension '+\
                                         output_ext,\
                                         )
arg_parser.add_argument('--amount', type=int, default = None, \
                                    help='the number of documents that are converted '+\
                                         'into JSON files. This is only used for testing '+\
                                         'purposes, e.g. if one wants to test the '+\
                                         'conversion of a small subset of documents.',\
                                    )
arg_parser.add_argument('--add_attribs', default = False,
                                    help='If set, then attributes of the <p>-tags '+\
                                         'will be stored in the metadata of the created '+\
                                         'Text objects (under the key "_paragraphs"). '+\
                                         '(By default, the attributes will not be stored)',\
                                         action='store_true')

args = arg_parser.parse_args()
in_file = args.in_file if os.path.isfile(args.in_file) else None
out_dir = args.out_dir if os.path.isdir(args.out_dir) else None
store_paragraph_attributes = args.add_attribs
convert_only_n_docs = args.amount


if in_file and out_dir:
    assert output_ext.startswith('.')
    # =======  Initialize
    domains     = {}
    urls        = {}
    document_id = 0
    startTime = datetime.now() 
    # =======  Process content doc by doc
    for text in yield_docs( in_file, encoding='utf-8', \
                            store_paragraph_attributes=store_paragraph_attributes ):
        if 'web_domain' not in text.meta:
            for k,v in text.items():
                print (k,':', v)
            raise Exception(' (!) Web domain name not available in text! ' )
        # Construct name of the file (based on web domain name)
        domain_name = text.meta['web_domain']
        domain_name = domain_name.replace('.', '_')
        fnm = domain_name+'__'+str(document_id)+output_ext
        out_file_path = os.path.join(out_dir, fnm)
        logger.info(' Writing document {0}'.format(out_file_path))
        # Export in json format
        export_json( text, file=out_file_path )
        document_id += 1
        if convert_only_n_docs and convert_only_n_docs <= document_id:
            break
    print()
    print( document_id,'documents converted. ')
    time_diff = datetime.now() - startTime
    print(' Total processing time: {}'.format(time_diff))
else:
    arg_parser.print_help()
