# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import
import os
import json
import logging

logger = logging.getLogger(__name__)

from ..text import Text
from ..core import as_unicode

from elasticsearch.exceptions import ElasticsearchException

import argparse

# max batch size in total text length (not accounting layers etc)
MAX_BATCH_CHARS = 20000


class Importer(object):
    def __init__(self, path):
        self.path = path

    def import_data(self, database):
        file_list = os.listdir(self.path)
        data_list = []

        logger.info('Inserting {0} documents'.format(len(file_list)))
        n = len(file_list)

        num_chars = 0
        for i, name in enumerate(file_list):
            full_path = os.path.join(self.path, name)

            with open(full_path, 'rb') as f:
                text = Text(json.loads(as_unicode(f.read())))
                text.tag_analysis()
                data_list.append(text)
                num_chars += len(text.text)
            if num_chars > MAX_BATCH_CHARS:
                num_chars = 0
                try:
                    database.bulk_insert(data_list, refresh=False)
                except ElasticsearchException as e:
                    logger.error(e)
                data_list = []
                logger.info("{0:.1f} percent completed".format(float(i) / n * 100))

        if len(data_list) > 0:
            database.bulk_insert(data_list)
        database.refresh()


from .database import Database

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Import documents to elasticsearch database')
    parser.add_argument('index', type=str, help='The name of the index')
    parser.add_argument('directory', type=str, help='The directory containing JSON files that need to be imported')

    args = parser.parse_args()

    importer = Importer(args.directory)
    db = Database(args.index)
    importer.import_data(db)

