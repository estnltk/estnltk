from estnltk.taggers import RegexTagger
from .patterns import unit_patterns, email_patterns, number_patterns, initial_patterns


class TokenizationHintsTagger:

    def __init__(self,
                 return_layer=False,
                 conflict_resolving_strategy='MAX',
                 overlapped=False,
                 tag_numbers=True, 
                 tag_unit=True, 
                 tag_email=True, 
                 tag_initials=True):
        '''
        tag_numbers: boolean, default: True
            Tag numbers
                23  ->  23
                12 000  -> 12000
                -75 34.4 , 3 4  --> -7534,34
        tag_unit: boolean, default: True
            Tag fractional units of measure. km/h, m / s.
        tag_email: boolean, default: True
            Tag e-mails.
                bla@bla.bl
        '''
        _vocabulary = []
        if tag_numbers:
            _vocabulary.extend(number_patterns)
        if tag_unit:
            _vocabulary.extend(unit_patterns)
        if tag_email:
            _vocabulary.extend(email_patterns)
        if tag_initials:
            _vocabulary.extend(initial_patterns)
        self._tagger = RegexTagger(vocabulary=_vocabulary,
                                   attributes={'normalized'},
                                   conflict_resolving_strategy=conflict_resolving_strategy,
                                   overlapped=overlapped,
                                   return_layer=return_layer,
                                   layer_name='tokenization_hints',
                                   )

    def tag(self, text):
        return self._tagger.tag(text)
