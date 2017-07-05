import regex as re
from estnltk.text import Layer, SpanList
from .patterns import MACROS, ABBREVIATIONS
from estnltk.layer_operations import resolve_conflicts

initial = re.compile(r'[{UPPERCASE}][{LOWERCASE}]?$'.format(**MACROS))
surname = re.compile(r'[{UPPERCASE}][{LOWERCASE}]{2,}$'.format(**MACROS))

class CompoundTokenTagger:
    def __init__(self, 
                 compound_types_to_merge={'abbrevation', 'name'},
                 conflict_resolving_strategy='MAX'):
        self._compound_types_to_merge = compound_types_to_merge
        self._conflict_resolving_strategy = conflict_resolving_strategy

    def tag(self, text: 'Text') -> 'Text':
        layer = Layer(name='compound_tokens',
                      enveloping = 'words',
                      attributes=['type'],
                      ambiguous=False)
        tokens = text.words.text
        name_status = None
        for i, token in enumerate(tokens):
            # abbreviation
            if token.lower() in ABBREVIATIONS:
                spl = SpanList()
                if i+1<len(tokens) and tokens[i+1]=='.':
                    spl.spans = text.words[i:i+2]
                else:
                    spl.spans = text.words[i:i+1]
                spl.type = 'non_ending_abbreviation'
                layer.add_span(spl)
            # automaton for names
            if name_status is None:
                if initial.match(token):
                    name_status = 'initial'
                    name_start = i
            elif name_status == 'initial':
                if token == '.':
                    name_status = 'point'
                else:
                    name_status = None
            elif name_status == 'point':
                if initial.match(token):
                    name_status = 'initial'
                elif surname.match(token):
                    spl = SpanList()
                    spl.spans = text.words[name_start:i+1]
                    spl.type = 'name'
                    layer.add_span(spl)
                    
                    name_status = None
                else:
                    name_status = None

        # TODO:
        #if self._compound_types_to_merge:
        resolve_conflicts(layer, conflict_resolving_strategy=self._conflict_resolving_strategy)
        
        text['compound_tokens'] = layer
        return text
