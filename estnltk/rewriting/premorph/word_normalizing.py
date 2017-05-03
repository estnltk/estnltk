from pandas import read_csv
from pandas.io.common import EmptyDataError
from os.path import dirname, join

from estnltk.rewriting.helpers.morph_analyzed_token import MorphAnalyzedToken


class WordNormalizingRewriter:
    def __init__(self):
        file = join(dirname(__file__), 'rules_files/ignore.csv')
        self.ignore = self.load_ignore(file)
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
