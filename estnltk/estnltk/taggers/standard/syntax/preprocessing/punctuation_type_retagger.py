import regex as re

from estnltk.taggers import Retagger


class PunctuationTypeRetagger(Retagger):
    """ Adds 'punctuation_type' attribute to the analysis.
        If partofspeech is 'Z', then gets the punctuation type from the 
        _punctConversions.

        If partofspeech is not 'Z', then punctuation_type is None.
        
        _punctConversions is a tuple of tuples, where each inner tuple contains
        a pair of elements: first is the regexp pattern to match the root and 
        the second is the punctuation type.

    TODO optimise patterns based on token set from reference corpus

    """
    conf_param = ['check_output_consistency']

    def __init__(self):
        self.input_layers = ['morph_extended']
        self.output_layer = 'morph_extended'
        self.output_attributes = ['punctuation_type']
        self.check_output_consistency = False

    def _change_layer(self, text, layers, status=None):
        layer = layers[self.output_layer]
        if self.output_attributes[0] not in layer.attributes:
            layer.attributes = layer.attributes + self.output_attributes

        for span in layer:
            for annotation in span.annotations:
                if annotation['partofspeech'] == 'Z':
                    annotation['punctuation_type'] = self._get_punctuation_type(annotation)
                else:
                    annotation['punctuation_type'] = None
        return layer

    _punctConversions = ((r"…$", "Ell"),
                         (r"\.\.\.$", "Ell"),
                         (r"\.\.$", "Els"),
                         (r"\.$", "Fst"),
                         (r",$", "Com"),
                         (r":$", "Col"),
                         (r";$", "Scl"),
                         (r"(\?+)$", "Int"),
                         (r"(\!+)$", "Exc"),
                         (r"(---?)$", "Dsd"),
                         (r"(-)$", "Dsh"),
                         (r"\($", "Opr"),
                         (r"\)$", "Cpr"),
                         (r'"$', "Quo"),
                         (r"«$", "Oqu"),
                         (r"»$", "Cqu"),
                         (r"“$", "Oqu"),
                         (r"”$", "Cqu"),
                         (r"<$", "Grt"),
                         (r">$", "Sml"),
                         (r"\[$", "Osq"),
                         (r"\]$", "Csq"),
                         (r"/$", "Sla"),
                         (r"\+$", "crd")
                         )

    def _get_punctuation_type(self, morph_extended):
        root = morph_extended['root']
        if root.rstrip('+0'):
            # eelmise versiooniga ühildumiseks
            # '0.0000000000000000000000000000000000000000000000000000000000'
            # '!+', '!++'
            # '(+'
            # '/+', '/++'
            root = root.rstrip('+0')
        for pattern, punct_type in self._punctConversions:
            if re.search(pattern, root):
                # kas match või search?     "//", ".-"
                # või hoopis pattern==morph_extended.root?
                # praegu on search, sest see klapib eelmise versiooniga
                return punct_type
            # mida teha kui matchi pole?
        if morph_extended['root'].endswith('+'):
            # eelmise versiooniga ühildumiseks
            return 'crd'
