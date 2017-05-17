import re
from estnltk.text import Layer

class TokenizationHintsTagger:
    regexes = ['([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', # e-mail: ab@cd.ef
               '-?\d+[\d+ ]*\d+', # numbers separated by space: -123 456 789
              ]
    patterns = [re.compile(r) for r in regexes]

    def tag(self, text):
        spans = []
        for p in self.patterns:
            for m in p.finditer(text.text):
                spans.append(m.span())
        spans.sort() # TODO: remove conflicts
                
        hints = Layer(name='tokenization_hints').from_records([{
                                                   'start': start,
                                                   'end': end
                                                  } for start, end in spans], rewriting=True)
        text['tokenization_hints'] = hints
        return text
