import os
from pandas import read_csv
from collections import defaultdict


class PronounTypeRewriter():
    ''' Adds 'pronoun_type' attribute to the analysis.
        Converts pronouns from Filosoft's mrf to syntactic analyzer's mrf format.

        Reads the pronoun types from pronoun_files.
        By default the pronoun_file is rules_files/pronouns.csv.
        Each line of the file contains comma separated pair of lemma and type.
        Example. An excerpt from the file:
            iga,det
            igasugune,dem
            igaüks,det
            ise,pos
            ise,det
            ise,refl
            iseenese,refl

        results a dict:

            pronoun_type = {'iga': ('det'),
                            'igasugune': ('dem'),
                            'igaüks': ('det'),
                            'ise': ('pos', 'det', 'refl'),
                            'iseenese': ('refl'),
                            }

        So, pronoun type is a tuple of str.

        If 'partofspeech' is not 'P', then pronoun type is None.
        If partofspeech is 'P', then gets the pronoun type from the dict
        pronoun_type. If lemma is not in the dict pronoun_type, then the pronoun
        type is ['invalid'].
    '''

    _dir = os.path.dirname(__file__)
    DEFAULT_PRONOUN_FILE = os.path.join(_dir, 'rules_files/pronouns.csv')

    def __init__(self, pronoun_file=DEFAULT_PRONOUN_FILE):
        self.pronoun_types = self.load_pronoun_types(pronoun_file)

    @staticmethod
    def load_pronoun_types(pronoun_file):
        assert os.path.exists(pronoun_file),\
            'Unable to find *pronoun_file* from location ' + pronoun_file
        df = read_csv(pronoun_file, header=None, index_col=False)
        pronoun_types = defaultdict(tuple)
        for a in df.iterrows():
            pronoun_types[a[1][0]] = pronoun_types[a[1][0]] + (a[1][1],)
        return pronoun_types

    def rewrite(self, record):
        for rec in record:
            if rec['partofspeech'] == 'P':
                lemma = rec['lemma'].split('-')[-1]
                rec['pronoun_type'] = self.pronoun_types.get(lemma, ('invalid',))
            else:
                rec['pronoun_type'] = None
        return record
