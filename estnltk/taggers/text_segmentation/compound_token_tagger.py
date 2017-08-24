import regex as re

from estnltk.text import Layer, SpanList
from estnltk.taggers import Tagger
from estnltk.layer_operations import resolve_conflicts
from .patterns import MACROS, ABBREVIATIONS


initial = re.compile(r'[{UPPERCASE}][{LOWERCASE}]?$'.format(**MACROS))
surname = re.compile(r'[{UPPERCASE}][{LOWERCASE}]{2,}$'.format(**MACROS))


class CompoundTokenTagger(Tagger):
    description = 'Tags adjacent tokens that should be analyzed as one word.'
    layer_name = 'compound_tokens'
    attributes = ['type']
    depends_on = ['tokens']
    configuration = None

    def __init__(self, 
                 compound_types_to_merge={'abbrevation', 'name'},
                 conflict_resolving_strategy='MAX'):
        self.configuration = {'compound_types_to_merge': compound_types_to_merge,
                            'conflict_resolving_strategy': conflict_resolving_strategy}
        
        self._compound_types_to_merge = compound_types_to_merge
        self._conflict_resolving_strategy = conflict_resolving_strategy


    def tag(self, text: 'Text', return_layer=False) -> 'Text':
        layer = Layer(name=self.layer_name,
                      enveloping = 'tokens',
                      attributes=self.attributes,
                      ambiguous=False)
        tokens = text.tokens.text
        name_status = None
        hyphenation_status = None
        last_end = None
        for i, span in enumerate(text.tokens):
            token = span.text

            # abbreviation
            if token.lower() in ABBREVIATIONS:
                spl = SpanList()
                if i+1<len(tokens) and tokens[i+1]=='.':
                    spl.spans = text.tokens[i:i+2]
                else:
                    spl.spans = text.tokens[i:i+1]
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
                    spl.spans = text.tokens[name_start:i+1]
                    spl.type = 'name'
                    layer.add_span(spl)
                    name_status = None
                else:
                    name_status = None

            # hyphenation
            if hyphenation_status is None:
                if last_end==span.start and span.text == '-':
                        hyphenation_status = '-'
                else:
                    hyphenation_start = i
            elif hyphenation_status=='-':
                if last_end==span.start:
                    hyphenation_status = 'second'
                else:
                    hyphenation_status = 'end'
            elif hyphenation_status=='second':
                if last_end==span.start and span.text == '-':
                        hyphenation_status = '-'
                else:
                    hyphenation_status = 'end'
            if hyphenation_status == 'end' and hyphenation_start+1 < i:
                spl = SpanList()
                spl.spans = text.tokens[hyphenation_start:i]
                spl.type = 'hyphenation'
                layer.add_span(spl)
                hyphenation_status = None
                hyphenation_start = i
            last_end = span.end

        # TODO:
        #if self._compound_types_to_merge:
        resolve_conflicts(layer, conflict_resolving_strategy=self._conflict_resolving_strategy)

        if return_layer:
            return layer
        text[self.layer_name] = layer
        return text
