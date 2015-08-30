# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import
import os
import json
import logging

logger = logging.getLogger(__name__)

from ..text import Text
from ..core import as_unicode
class Importer(object):

    def __init__(self, path):
        self.path = path

    def import_data(self, database):
        file_list = os.listdir(self.path)
        data_list = []

        logger.info('Inserting {0} documents'.format(len(file_list)))
        n = len(file_list)

        for i, name in enumerate(file_list):
            full_path = os.path.join(self.path,name)

            with open (full_path, 'rb') as f:
                text = Text(json.loads(as_unicode(f.read())))
                text.tag_analysis()
                data_list.append(text)

            if i % 100 == 0:
                database.bulk_insert(data_list)
                data_list = []
                logger.info("{0:.1f} percent completed".format(float(i)/n*100))

        if len(data_list) > 0:
            database.bulk_insert(data_list)


from .database import Database
logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    importer = Importer('/home/annett/keeletehnoloogia/estnltk/estnltk/wiki/text-examples')

    db = Database('test')
    importer.import_data(db)

