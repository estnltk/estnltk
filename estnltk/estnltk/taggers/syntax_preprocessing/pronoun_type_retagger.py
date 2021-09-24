import os
from pandas import read_csv
from collections import defaultdict
from estnltk.taggers import Retagger


class PronounTypeRetagger(Retagger):
    """ Adds 'pronoun_type' attribute to the analysis.
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
    """

    _dir = os.path.dirname(__file__)
    DEFAULT_PRONOUN_FILE = os.path.join(_dir, 'rules_files/pronouns.csv')

    conf_param = ['check_output_consistency', 'pronoun_types']

    def __init__(self, output_layer='morph_extended', pronoun_file=DEFAULT_PRONOUN_FILE):
        self.input_layers = [output_layer]
        self.output_layer = output_layer
        self.output_attributes = ['pronoun_type']
        self.check_output_consistency = False
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

    def _change_layer(self, text, layers, status=None):
        layer = layers[self.output_layer]
        if self.output_attributes[0] not in layer.attributes:
            layer.attributes = layer.attributes + self.output_attributes
        get_pronoun_type = self.pronoun_types.get
        for span in layer:
            for annotation in span.annotations:
                if annotation['partofspeech'] == 'P':
                    lemma = annotation['lemma']
                    annotation['pronoun_type'] = get_pronoun_type(lemma, ('invalid',))
                else:
                    annotation['pronoun_type'] = None

        return layer
