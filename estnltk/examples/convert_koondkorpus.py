# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import os
import os.path
import argparse
import logging

from estnltk.teicorpus import parse_tei_corpus
from estnltk.corpus import write_document

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('koondkonverter')


def get_target(fnm):
    if 'drtood' in fnm:
        return 'dissertatsioon'
    if 'ilukirjandus' in fnm:
        return 'tervikteos'
    if 'seadused' in fnm:
        return 'seadus'
    if 'EestiArst' in fnm:
        return 'ajakirjanumber'
    if 'foorumid' in fnm:
        return 'teema'
    if 'kommentaarid' in fnm:
        return 'kommentaarid'
    if 'uudisgrupid' in fnm:
        return 'uudisgrupi_salvestus'
    if 'jututoad' in fnm:
        return 'jututoavestlus'
    if 'stenogrammid' in fnm:
        return 'stenogramm'
    return 'artikkel'


def process(start_dir, out_dir):
    for dirpath, dirnames, filenames in os.walk(start_dir):
        if len(dirnames) > 0 or len(filenames) == 0 or 'bin' in dirpath:
            continue
        for fnm in filenames:
            full_fnm = os.path.join(dirpath, fnm)
            out_prefix = os.path.join(out_dir, fnm)
            target = get_target(full_fnm)
            if os.path.exists(out_prefix + '_0.txt'):
                logger.info('Skipping file {0}, because it seems to be already processed'.format(full_fnm))
                continue
            logger.info('Processing file {0} with target {1}'.format(full_fnm, target))
            docs = parse_tei_corpus(full_fnm, target=target)
            for doc_id, doc in enumerate(docs):
                out_fnm = '{0}_{1}.txt'.format(out_prefix, doc_id)
                logger.info('Writing document {0}'.format(out_fnm))
                write_document(doc, out_fnm)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert a bunch of TEI XML files to Estnltk JSON files")
    parser.add_argument('startdir', type=str, help='The path of the downloaded and extracted koondkorpus files')
    parser.add_argument('outdir', type=str, help='The directory to store output results')
    args = parser.parse_args()

    process(args.startdir, args.outdir)
