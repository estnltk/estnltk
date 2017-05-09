import os
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

            pronoun_type = {'iga': ['det'],
                            'igasugune': ['dem'],
                            'igaüks': ['det'],
                            'ise': ['pos', 'det', 'refl'],
                            'iseenese': ['refl'],
                            }

        So, pronoun type is a list of str.

        If 'partofspeech' is not 'P', then pronoun type is None.
        If partofspeech is 'P', then gets the pronoun type from the dict
        pronoun_type. If lemma is not in the dict pronoun_type, then the pronoun
        type is ['invalid'].
    '''

    
    def __init__(self, pronoun_file=None):
        # TODO: use method load_pronoun_types
        if pronoun_file:
            assert os.path.exists(pronoun_file),\
                'Unable to find *pronoun_file* from location ' + pronoun_file
        else:
            pronoun_file = os.path.dirname(__file__)
            pronoun_file = os.path.join(pronoun_file,
                                             'rules_files/pronouns.csv')
            assert os.path.exists(pronoun_file),\
                'Missing default *pronoun_file* ' + pronoun_file

        self.pronoun_type = defaultdict(list)
        with open(pronoun_file, 'r') as in_f:
            for l in in_f:
                pronoun, t = l.split(',')
                self.pronoun_type[pronoun.strip()].append(t.strip())

    @staticmethod
    def load_pronoun_types(pronoun_file=None):
        if pronoun_file:
            assert os.path.exists(pronoun_file),\
                'Unable to find *pronoun_file* from location ' + pronoun_file
        else:
            pronoun_file = os.path.dirname(__file__)
            pronoun_file = os.path.join(pronoun_file,
                                             'rules_files/pronouns.csv')
            assert os.path.exists(pronoun_file),\
                'Missing default *pronoun_file* ' + pronoun_file

        pronoun_type = defaultdict(list)
        with open(pronoun_file, 'r') as in_f:
            for l in in_f:
                pronoun, t = l.split(',')
                pronoun_type[pronoun.strip()].append(t.strip())
        return pronoun_type

    def rewrite(self, record):
        for rec in record:
            if rec['partofspeech'] == 'P':
                pronoun_type = self.pronoun_type.get(rec['lemma'])
                if pronoun_type is None:
                    pronoun_type = ['invalid']
                else:
                    pronoun_type = pronoun_type.copy()
                rec['pronoun_type'] = pronoun_type
            else:
                rec['pronoun_type'] = None
        return record
