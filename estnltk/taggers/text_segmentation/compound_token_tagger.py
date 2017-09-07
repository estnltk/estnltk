import regex as re

from estnltk.text import Layer, SpanList
from estnltk.taggers import Tagger
from estnltk.taggers import RegexTagger
from estnltk.layer_operations import resolve_conflicts
from .patterns import unit_patterns, email_patterns, number_patterns, initial_patterns, abbreviation_patterns



class CompoundTokenTagger(Tagger):
    description = 'Tags adjacent tokens that should be analyzed as one word.'
    layer_name = 'compound_tokens'
    attributes = ('type', 'normalized')
    depends_on = ['tokens']
    configuration = None

    def __init__(self, 
                 compound_types_to_merge={'abbrevation', 'name'},
                 conflict_resolving_strategy='MAX',
                 tag_numbers:bool = True,
                 tag_units:bool = True,
                 tag_emails:bool = True,
                 tag_initials:bool = True,
                 tag_abbreviations:bool = True,
                 ):
        self.configuration = {'compound_types_to_merge': compound_types_to_merge,
                              'conflict_resolving_strategy': conflict_resolving_strategy,
                              'tag_numbers': tag_numbers,
                              'tag_units':tag_units,
                              'tag_emails':tag_emails,
                              'tag_initials':tag_initials,
                              'tag_abbreviations':tag_abbreviations}
        
        self._compound_types_to_merge     = compound_types_to_merge
        self._conflict_resolving_strategy = conflict_resolving_strategy
        
        _vocabulary = []
        if tag_numbers:
            _vocabulary.extend(number_patterns)
        if tag_units:
            _vocabulary.extend(unit_patterns)
        if tag_emails:
            _vocabulary.extend(email_patterns)
        if tag_initials:
            _vocabulary.extend(initial_patterns)
        if tag_abbreviations:
            _vocabulary.extend(abbreviation_patterns)
        self._tokenization_hints_tagger = RegexTagger(vocabulary=_vocabulary,
                                   attributes=('normalized', '_priority_', 'pattern_type'),
                                   conflict_resolving_strategy=conflict_resolving_strategy,
                                   overlapped=False,
                                   layer_name='tokenization_hints',
                                   )


    def tag(self, text: 'Text', return_layer=False) -> 'Text':
        layer = Layer(name=self.layer_name,
                      enveloping = 'tokens',
                      attributes=self.attributes,
                      ambiguous=False)

        # 1) Apply RegexTagger in order to get hints for tokenization
        conflict_status    = {}
        tokenization_hints = {}
        new_layer = self._tokenization_hints_tagger.tag(text, return_layer=True, status=conflict_status)
        for sp in new_layer.spans:
            #print(text.text[sp.start:sp.end], sp.pattern_type, sp.normalized)
            if hasattr(sp, 'pattern_type') and sp.pattern_type.startswith('negative:'):
                # This is a negative pattern (used for preventing other patterns from matching),
                # and thus should be discarded altogether ...
                continue
            end_node = {'end': sp.end}
            if hasattr(sp, 'pattern_type'):
                end_node['pattern_type'] = sp.pattern_type
            if hasattr(sp, 'normalized'):
                end_node['normalized'] = sp.normalized
            # Note: we assume that all conflicts have been resolved by 
            # RegexTagger, that is -- exactly one (compound) token begins 
            # from one starting position ...
            if sp.start in tokenization_hints:
                raise Exception( '(!) Unexpected overlapping tokenization hints: ', \
                                 [ text.text[sp2.start:sp2.end] for sp2 in new_layer.spans ] )
            tokenization_hints[sp.start] = end_node

        tokens = text.tokens.text
        hyphenation_status = None
        last_end = None
        # 2) Apply tokenization hints + hyphenation correction
        for i, token_span in enumerate(text.tokens):
            token = token_span.text
            # Check for tokenization hints
            if token_span.start in tokenization_hints:
                # Find where the new compound token should end 
                end_token_index = None
                for j in range( i, len(text.tokens) ):
                    if text.tokens[j].end == tokenization_hints[token_span.start]['end']:
                        end_token_index = j
                    elif tokenization_hints[token_span.start]['end'] < text.tokens[j].start:
                        break
                if end_token_index:
                    spl = SpanList()
                    spl.spans      = text.tokens[i:end_token_index+1]
                    spl.type       = 'tokenization_hint'
                    spl.normalized = None
                    if 'pattern_type' in tokenization_hints[token_span.start]:
                        spl.type = tokenization_hints[token_span.start]['pattern_type']
                    if 'normalized' in tokenization_hints[token_span.start]:
                        spl.normalized = tokenization_hints[token_span.start]['normalized']
                    layer.add_span(spl)

            # Perform hyphenation correction
            if hyphenation_status is None:
                if last_end==token_span.start and token_span.text == '-':
                        hyphenation_status = '-'
                else:
                    hyphenation_start = i
            elif hyphenation_status=='-':
                if last_end==token_span.start:
                    hyphenation_status = 'second'
                else:
                    hyphenation_status = 'end'
            elif hyphenation_status=='second':
                if last_end==token_span.start and token_span.text == '-':
                        hyphenation_status = '-'
                else:
                    hyphenation_status = 'end'
            if hyphenation_status == 'end' and hyphenation_start+1 < i:
                spl = SpanList()
                spl.spans = text.tokens[hyphenation_start:i]
                spl.type = 'hyphenation'
                spl.normalized = None
                layer.add_span(spl)
                hyphenation_status = None
                hyphenation_start = i
            last_end = token_span.end

        # TODO:
        #if self._compound_types_to_merge:
        resolve_conflicts(layer, conflict_resolving_strategy=self._conflict_resolving_strategy)

        if return_layer:
            return layer
        text[self.layer_name] = layer
        return text
