#
#  Script for converting KoondKorpus XML TEI files to EstNTLK JSON format files.
#  Ported from the version 1.4.1.1:
#    https://github.com/estnltk/estnltk/blob/1.4.1.1/estnltk/examples/convert_koondkorpus.py
#    ( with modifications )
# 

import os
import os.path
import argparse
from argparse import RawTextHelpFormatter

import logging

from datetime import datetime
from datetime import timedelta

from estnltk.corpus_processing.parse_koondkorpus import get_div_target
from estnltk.corpus_processing.parse_koondkorpus import parse_tei_corpus

from estnltk.converters import text_to_json

logger = None  # <-- To be initialized later

output_ext = 'json'    # extension of output files

def process(start_dir, out_dir, encoding='utf-8', \
            add_tokenization=False,\
            preserve_tokenization=False, \
            create_empty_docs=True, \
            sentence_separator='\n' ):
    """Traverses recursively start_dir to find XML TEI documents,
       converts found documents to EstNLTK Text objects, and saves 
       as JSON files (into the out_dir).
    
    Parameters
    ----------
    start_dir: str
        The root directory which is recursively traversed to find 
        XML files;
    out_dir: str
        The directory where results (EstNLTK Texts in JSON format)
        are to be saved;
    encoding: str
        Encoding of the XML files. (default: 'utf-8')
    add_tokenization: boolean
        If True, then tokenization layers 'tokens', 'compound_tokens',
        'words', 'sentences', 'paragraphs' will be added to all newly 
        created Text instances;
        If preserve_tokenization is set, then original tokenization in 
        the document will be preserved; otherwise, the tokenization will be
        created with EstNLTK's default tokenization tools;
        (Default: False)
    preserve_tokenization: boolean
        If True, then the created documents will have layers 'tokens', 
        'compound_tokens', 'words', 'sentences', 'paragraphs', which 
        follow the original segmentation in the XML file. 
        (In the XML, sentences are between <s> and </s>, paragraphs are 
        between <p> and </p>, and words separated by spaces);
        Note that the layer 'compound_tokens' will always remain empty 
        because koondkorpus files do no contain information about token 
        compounding.
        (default: False)
    create_empty_docs: boolean
        If True, then documents are also created if there is no textual 
        content, but only metadata content.
        Note: an empty document may be a captioned table or a figure, 
        which content has been removed from the XML file. Depending on 
        the goals of the analysis, the caption may still be useful, 
        so, by default, empty documents are preserved;
        (default: True)
    sentence_separator: str
        String to be used as a sentence separator during the reconstruction
        of the text. The parameter value should be provided, None is not 
        allowed.
        (Default: '\n')
    """
    global logger
    xml_count  = 0
    json_count = 0
    startTime = datetime.now()
    no_documents_created = []
    for dirpath, dirnames, filenames in os.walk(start_dir):
        if len(dirnames) > 0 or len(filenames) == 0 or 'bin' in dirpath:
            continue
        for fnm in filenames:
            full_fnm = os.path.join(dirpath, fnm)
            out_prefix = os.path.join(out_dir, fnm)
            target = get_div_target(full_fnm)
            if os.path.exists(out_prefix + '_0.'+output_ext):
                logger.debug('Skipping file {0}, because it seems to be already processed'.format(full_fnm))
                continue
            logger.debug('Processing file {0} with target {1}'.format(full_fnm, target))
            docs = []
            docs = parse_tei_corpus(full_fnm, target=[target], encoding=encoding, \
                                    add_tokenization=add_tokenization, \
                                    preserve_tokenization=preserve_tokenization, \
                                    record_xml_filename=True, \
                                    sentence_separator=sentence_separator )
            xml_count += 1
            empty_docs = []
            for doc_id, doc in enumerate(docs):
                out_fnm = '{0}_{1}.{2}'.format(out_prefix, doc_id, output_ext)
                logger.debug('Writing document {0}'.format(out_fnm))
                if not create_empty_docs and len(doc.text) == 0:
                   # Skip creating an empty document
                   continue
                if len(doc.text) == 0:
                   empty_docs.append(out_fnm)
                text_to_json(doc, file = out_fnm)
                json_count += 1
            if empty_docs:
                logger.warn('Warning: empty documents created for {0}: {1}'.format(fnm, empty_docs))
            elif not docs:
                logger.warn('Warning: no documents created for {0}'.format(fnm))
                no_documents_created.append(fnm)
    if no_documents_created:
        logger.warn('No documents created for XML files: {0}'.format(no_documents_created))
    logger.info(' Total {0} XML files processed '.format(xml_count))
    logger.info(' Total {0} JSON files created '.format(json_count))
    time_diff = datetime.now() - startTime
    logger.info(' Total processing time: {}'.format(time_diff))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=
       "Converts Koondkorpus XML TEI files to EstNLTK's Text objects, and writes into JSON files.", \
       formatter_class=RawTextHelpFormatter
    )
    parser.add_argument('startdir', type=str, 
                        help='The path of the downloaded and extracted koondkorpus files')
    parser.add_argument('outdir', type=str, 
                        help='The directory to store output results')
    parser.add_argument('-e', '--encoding', type=str, default='utf-8', \
                        help='Encoding of the TEI XML files (Default: "utf-8").')
    parser.add_argument('-t', '--tokenization', dest='tokenization', \
                        help='specifies if and how texts will be reconstructed and tokenized: \n\n'+ \
                             '* none -- the text string will be reconstructed by joining words \n'+\
                             '  and sentences from the original XML mark-up by spaces, and paragraphs\n'+\
                             '  by double newlines. Tokenization layers will not be created.\n\n'+\
                             
                             '* preserve -- the text string will be reconstructed by joining \n'+\
                             '  words from the original XML mark-up by spaces, sentences by \n'+\
                             '  newlines, and paragraphs by double newlines. Tokenization layers \n'+\
                             '  will be created, and they\'ll preserve the original tokenization \n'+\
                             '  of XML files.\n'+\
                             "    Note #1: tokenization layers 'tokens', 'compound_tokens', \n"+\
                             "    'words', 'sentences', 'paragraphs' will be created;\n"+\
                             "    Note #2: the layer 'compound_tokens' will always remain empty \n"+\
                             '    because koondkorpus files do no contain information about token \n'+\
                             '    compounding;\n'+\
                             "    Note #3: the layer 'tokens' will be equal to the layer 'words';"+\
                             '  \n\n'+\

                             '* estnltk -- the text string will be reconstructed by joining words \n'+\
                             '  and sentences from the original XML mark-up by spaces, and \n'+\
                             "  paragraphs by double newlines. Tokenization layers will be created \n"+\
                             "  with EstNLTK's default tokenizers, overwriting the original \n"+\
                             '  tokenization mark-up from XML files.\n'
                             "    Note #1: tokenization layers 'tokens', 'compound_tokens', \n"+\
                             "    'words', 'sentences', 'paragraphs' will be created;\n"+\
                             "(Default: none)",\
                        choices=['none', 'preserve', 'estnltk'], \
                        default='none' )
    parser.add_argument('-f', '--force_sentence_end_newlines', dest='force_sentence_end_newlines', \
                        default=False, \
                        action='store_true', \
                        help="If set, then during the reconstruction of a text string, sentence \n"+
                             "endings from the original XML mark-up will always be marked with\n"+
                             "newlines in the text string, regardless the tokenization option\n"+\
                             "used.\n"
                             "You can use this option if you want to replace spaces between the \n"+\
                             "original sentences with newlines when using the tokenization options\n"+\
                             " -t none, or -t estnltk.\n"+\
                             "(Default: False)",\
                        )
    parser.add_argument('--logging', dest='logging', action='store', default='info',\
                        choices=['debug', 'info', 'warning', 'error', 'critical'],\
                        help='Logging level (default: info)')
    
    args = parser.parse_args()
    add_tokenization      = args.tokenization in ['preserve', 'estnltk']
    preserve_tokenization = args.tokenization == 'preserve'
    sentence_separator    = ' '
    if preserve_tokenization or args.force_sentence_end_newlines:
       sentence_separator = '\n'
    logging.basicConfig( level=(args.logging).upper() )
    logger = logging.getLogger('koondkonverter')
    process(args.startdir, args.outdir, args.encoding, \
                           add_tokenization=add_tokenization, \
                           preserve_tokenization=preserve_tokenization,\
                           sentence_separator=sentence_separator )
