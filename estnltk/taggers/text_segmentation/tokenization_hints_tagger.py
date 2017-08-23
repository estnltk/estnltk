from estnltk.taggers import RegexTagger
from .patterns import unit_patterns, email_patterns, number_patterns, initial_patterns, abbreviation_patterns


class TokenizationHintsTagger:

    def __init__(self,
                 return_layer=False,
                 conflict_resolving_strategy='MAX',
                 overlapped=False,
                 tag_numbers=True, 
                 tag_unit=True, 
                 tag_email=True, 
                 tag_initials=False,
                 tag_abbreviations=False,
                 ):
        '''
        return_layer: bool
            If True, TokenizationHintsTagger.tag(text) returns a layer. 
            If False,TokenizationHintsTagger.tag(text) annotates the text object
            with the layer and returns None.
        conflict_resolving_strategy: 'ALL', 'MAX', 'MIN' (default: 'MAX')
            Strategy to choose between overlapping events.
        overlapped: bool (Default: False)
            If True, the match of a regular expression may overlap with a match
            of the same regular expression.

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
        tag_initials: boolean, Defaul: True
            A. H. Tammsaare
        '''
        self._layer_name = 'tokenization_hints'
        self._attributes = ('normalized', '_priority_')
        self._depends_on = ()
        
        _vocabulary = []
        if tag_numbers:
            _vocabulary.extend(number_patterns)
        if tag_unit:
            _vocabulary.extend(unit_patterns)
        if tag_email:
            _vocabulary.extend(email_patterns)
        if tag_initials:
            _vocabulary.extend(initial_patterns)
        if tag_abbreviations:
            _vocabulary.extend(abbreviation_patterns)
        self._tagger = RegexTagger(vocabulary=_vocabulary,
                                   attributes=self._attributes,
                                   conflict_resolving_strategy=conflict_resolving_strategy,
                                   overlapped=overlapped,
                                   return_layer=return_layer,
                                   layer_name=self._layer_name,
                                   )
        self._conf = ''.join(('return_layer=', str(return_layer),
                              ", conflict_resolving_strategy='", conflict_resolving_strategy,"'",
                              ', overlapped=',str(overlapped),
                              ', tag_numbers=',str(tag_numbers), 
                              ', tag_unit=',str(tag_unit), 
                              ', tag_email=',str(tag_email), 
                              ', tag_initials=',str(tag_initials),
                              ', tag_abbreviations=',str(tag_abbreviations)))


    def tag(self, text, status={}):
        return self._tagger.tag(text, status)

    def configuration(self):
        record = {'name':self.__class__.__name__,
                  'layer':self._layer_name,
                  'attributes':self._attributes,
                  'depends_on': self._depends_on,
                  'conf':self._conf}
        return record

    def _repr_html_(self):
        import pandas
        pandas.set_option('display.max_colwidth', -1)
        df = pandas.DataFrame.from_records([self.configuration()], columns=['name', 'layer', 'attributes', 'depends_on', 'conf'])
        return df.to_html(index=False)
