
from copy import copy
from estnltk.taggers import RegexTagger
from estnltk import Text
from pprint import pprint
from regexes_v import regexes
import datetime
import pandas as pd

class DateTagger:
    def __init__(self, return_layer=False, layer_name='date'):
        """
        Tags dates
        Parameters
        ----------
        return_layer - do not annotate the text object, return just the resulting layer
        layer_name - the name of the layer. Does nothing when return_layer is set
        """
        self.layer_name = layer_name
        self.return_layer = return_layer

    # If year is two digits, add 1900 or 2000
    def __clean_year(self, yearstring):
        year = int(yearstring)
        if year < 100:
            if year < 30:
                year += 2000
            else:
                year += 1900
        
        return year


    # Tag dates and add extracted_values attribute if date/datetime/time is valid
    def tag(self, text):
        if self.return_layer:
            t2 = copy(text)
            a2 = DateTagger()
            a2.tag(t2)
            return t2[a2.layer_name]
        
        else:
            if self.layer_name in text:
                return text
            else:
                tagger = RegexTagger(regexes, return_layer = False, layer_name = self.layer_name, conflict_resolving_strategy='MAX')    
        
        
                tagger.tag(text)
                if len(text[self.layer_name]) > 0:
                    for idx, d in enumerate(text[self.layer_name]):
                        text[self.layer_name][idx]['extracted_values'] = {}
                        if 'YEAR' in d['groups'] or 'LONGYEAR' in d['groups']:
                            if 'YEAR' in d['groups']:
                                year = self.__clean_year(d['groups']['YEAR'])
                            else:
                                year = int(d['groups']['LONGYEAR'])
                            if 'DAY' in d['groups']:
                                day = int(d['groups']['DAY'])
                                if 'hour' in d['groups']:
                                    if d['groups']['second'] == None:
                                        second = 0
                                    else:
                                        second = int(d['groups']['second'])
                                    try:    
                                        t = datetime.datetime(year = year,
                                                          month = int(d['groups']['MONTH']),
                                                          day = day,
                                                          hour = int(d['groups']['hour']),
                                                          minute = int(d['groups']['minute']),
                                                          second = second)
                                    
                                        text[self.layer_name][idx]['extracted_values']['datetime'] = t
                                    except ValueError:
                                        text[self.layer_name][idx]['extracted_values']['datetime'] = None   
                                
                                else:
                                    try:
                                        t = datetime.date(year = year,
                                                      month = int(d['groups']['MONTH']),
                                                      day = day)
                                        text[self.layer_name][idx]['extracted_values']['date'] = t
                                    except ValueError:
                                        text[self.layer_name][idx]['extracted_values']['date'] = None   
                        else:
                            if 'hour' in d['groups']:
                                if d['groups']['second'] == None:
                                        second = 0
                                else:
                                    second = int(d['groups']['second'])
                                try:    
                                    t = datetime.time(hour = int(d['groups']['hour']),
                                                  minute = int(d['groups']['minute']),
                                                  second = second)
                                    text[self.layer_name][idx]['extracted_values']['time'] = t
                                except ValueError:
                                    text[self.layer_name][idx]['extracted_values']['time'] = None   

                                
                return text


