import regex as re

class PunctuationTypeRewriter():
    ''' Adds 'punctuation_type' attribute to the analysis.
        If partofspeech is 'Z', then gets the punctuation type from the 
        _punctConversions.

        If partofspeech is not 'Z', then punctuation_type is None.
        
        _punctConversions is a tuple of tuples, where each inner tuple contains
        a pair of elements: first is the regexp pattern to match the root and 
        the second is the punctuation type.
    ''' 

    def rewrite(self, record):
        for rec in record:
            if rec['partofspeech'] == 'Z':
                rec['punctuation_type'] = self._get_punctuation_type(rec)
            else:
                rec['punctuation_type'] = None
        return record

    _punctConversions = (
                          ("…$",      "Ell"),
                          ("\.\.\.$", "Ell"),
                          ("\.\.$",   "Els"),
                          ("\.$",     "Fst"),
                          (",$",      "Com"),
                          (":$",      "Col"),
                          (";$",      "Scl"),
                          ("(\?+)$",  "Int"),
                          ("(\!+)$",  "Exc"),
                          ("(---?)$", "Dsd"),
                          ("(-)$",    "Dsh"),
                          ("\($",     "Opr"),
                          ("\)$",     "Cpr"),
                          ('\\\\"$',  "Quo"),
                          ("«$",      "Oqu"),
                          ("»$",      "Cqu"),
                          ("“$",      "Oqu"),
                          ("”$",      "Cqu"),
                          ("<$",      "Grt"),
                          (">$",      "Sml"),
                          ("\[$",     "Osq"),
                          ("\]$",     "Csq"),
                          ("/$",      "Sla"),
                          ("\+$",     "crd")
    )# double quotes are escaped by \


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
