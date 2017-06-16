from pandas import read_csv
from pandas.io.common import EmptyDataError
import os

from estnltk.rewriting import MorphAnalyzedToken

DEFAULT_IGNORE_LIST = os.path.join(os.path.dirname(__file__), 'rules_files', 'ignore.csv')


class WordNormalizingRewriter:
    def __init__(self, ignore_file:str=DEFAULT_IGNORE_LIST):
        self.ignore = self.load_ignore(ignore_file)
        self.hyphen_removing_rewriter = HyphenRemovingRewriter()


    @staticmethod
    def load_ignore(file):
        try:
            df = read_csv(file, na_filter=False, header=None)
            return set(df[0])
        except EmptyDataError:
            return set()

    def rewrite(self, record):
        if record['text'] in self.ignore:
            return None

        record = self.hyphen_removing_rewriter.rewrite(record)

        return record


class HyphenRemovingRewriter:

    def rewrite(self, record):
        token = MorphAnalyzedToken(record['text'])
        if token is token.normal:
            return None
        record['normal'] = token.normal.text
        return record
