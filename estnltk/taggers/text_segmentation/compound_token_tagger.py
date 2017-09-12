import regex as re

from typing import Union

from estnltk.text import Layer, SpanList
from estnltk.taggers import Tagger
from estnltk.taggers import RegexTagger
from estnltk.layer_operations import resolve_conflicts
from .patterns import unit_patterns, email_and_www_patterns, number_patterns, initial_patterns, abbreviation_patterns
from .patterns import case_endings_patterns


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
                 tag_email_and_www:bool = True,
                 tag_initials:bool = True,
                 tag_abbreviations:bool = True,
                 tag_case_endings:bool = True,
                 ):
        self.configuration = {'compound_types_to_merge': compound_types_to_merge,
                              'conflict_resolving_strategy': conflict_resolving_strategy,
                              'tag_numbers': tag_numbers,
                              'tag_units':tag_units,
                              'tag_email_and_www':tag_email_and_www,
                              'tag_initials':tag_initials,
                              'tag_abbreviations':tag_abbreviations,
                              'tag_case_endings':tag_case_endings}
        
        self._compound_types_to_merge     = compound_types_to_merge
        self._conflict_resolving_strategy = conflict_resolving_strategy
        # =========================
        #  1st level hints tagger
        # =========================
        _vocabulary_1 = [] 
        if tag_numbers:
            _vocabulary_1.extend(number_patterns)
        if tag_units:
            _vocabulary_1.extend(unit_patterns)
        if tag_email_and_www:
            _vocabulary_1.extend(email_and_www_patterns)
        if tag_initials:
            _vocabulary_1.extend(initial_patterns)
        if tag_abbreviations:
            _vocabulary_1.extend(abbreviation_patterns)
        self._tokenization_hints_tagger_1 = RegexTagger(vocabulary=_vocabulary_1,
                                   attributes=('normalized', '_priority_', 'pattern_type'),
                                   conflict_resolving_strategy=conflict_resolving_strategy,
                                   overlapped=False,
                                   layer_name='tokenization_hints',
                                   )
        # =========================
        #  2nd level hints tagger
        # =========================
        _vocabulary_2 = []
        if tag_case_endings:
            _vocabulary_2.extend(case_endings_patterns)
        self._tokenization_hints_tagger_2 = None
        if _vocabulary_2:
            self._tokenization_hints_tagger_2 = RegexTagger(vocabulary=_vocabulary_2,
                                                attributes=('normalized', '_priority_', 'pattern_type', \
                                                            'left_strict', 'right_strict'),
                                                conflict_resolving_strategy=conflict_resolving_strategy,
                                                overlapped=False,
                                                layer_name='tokenization_hints',
                                              )


    def tag(self, text: 'Text', return_layer=False) -> 'Text':
        '''
        Tag compound_tokens layer.
        '''
        compound_tokens_lists = []
        # 1) Apply RegexTagger in order to get hints for the 1st level tokenization
        conflict_status    = {}
        tokenization_hints = {}
        new_layer = self._tokenization_hints_tagger_1.tag(text, return_layer=True, status=conflict_status)
        for sp in new_layer.spans:
            #print('*',text.text[sp.start:sp.end], sp.pattern_type, sp.normalized)
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
                    compound_tokens_lists.append(spl)

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
                compound_tokens_lists.append(spl)
                hyphenation_status = None
                hyphenation_start = i
            last_end = token_span.end

        # 3) Apply tagging of 2nd level tokenization hints
        #    (join 1st level compound tokens + regular tokens, if needed)
        if self._tokenization_hints_tagger_2:
            compound_tokens_lists = \
                self._apply_2nd_level_compounding(text, compound_tokens_lists)


        # *) Finally: create a new layer and add spans to the layer
        layer = Layer(name=self.layer_name,
                      enveloping = 'tokens',
                      attributes=self.attributes,
                      ambiguous=False)
        for spl in compound_tokens_lists:
            layer.add_span(spl)

        # TODO:
        #if self._compound_types_to_merge:
        resolve_conflicts(layer, conflict_resolving_strategy=self._conflict_resolving_strategy)

        if return_layer:
            return layer
        text[self.layer_name] = layer
        return text


    def _apply_2nd_level_compounding(self, text:'Text', compound_tokens_lists:list):
        ''' 
            Executes _tokenization_hints_tagger_2 to get hints for 2nd level compounding.
            
            Performs the 2nd level compounding: joins together regular "tokens" and 
            "compound_tokens" (created by _tokenization_hints_tagger_1) according to the 
            hints.
            
            And finally, unifies results of the 1st level compounding and the 2nd level 
            compounding into a new compound_tokens_lists.
            Returns updated compound_tokens_lists.
        '''
        # Apply regexps to gain 2nd level of tokenization hints
        conflict_status    = {}
        tokenization_hints = {}
        new_layer = \
            self._tokenization_hints_tagger_2.tag(text, return_layer=True, status=conflict_status)
        # Find tokens that should be joined according to 2nd level hints and 
        # create new compound tokens based on them
        for sp in new_layer.spans:
            # get tokens covered by the span
            covered_compound_tokens = \
                self._get_covered_tokens( \
                    sp.start,sp.end,sp.left_strict,sp.right_strict,compound_tokens_lists )
            covered_tokens = \
                self._get_covered_tokens( \
                    sp.start,sp.end,sp.left_strict,sp.right_strict,text.tokens.spans )
            # remove regular tokens that are within compound tokens
            covered_tokens = \
                self._remove_overlapped_spans(covered_compound_tokens, covered_tokens)

            # check the leftmost and the rightmost tokens: 
            #    whether they satisfy the constraints left_strict and right_strict
            constraints_satisfied = True
            leftmost1 = \
                covered_tokens[0].start if covered_tokens else len(text.text)
            leftmost2 = \
                covered_compound_tokens[0].start if covered_compound_tokens else len(text.text)
            leftmost = min( leftmost1, leftmost2 )
            if sp.left_strict  and  sp.start != leftmost:
                # hint's left boundary was supposed to match exactly a token start, but did not
                constraints_satisfied = False
            rightmost1 = \
                covered_tokens[-1].end if covered_tokens else -1
            rightmost2 = \
                covered_compound_tokens[-1].end if covered_compound_tokens else -1
            rightmost = max( rightmost1, rightmost2 )
            if sp.right_strict  and  sp.end != rightmost:
                # hint's right boundary was supposed to match exactly a token end, but did not
                constraints_satisfied = False

            # If constraints were satisfied, add new compound token
            if (covered_compound_tokens or covered_tokens) and constraints_satisfied:
                # Create new SpanList
                spl = self._create_new_spanlist(text, covered_compound_tokens, covered_tokens, sp)
                # Remove old compound_tokens that are covered with the SpanList
                compound_tokens_lists = \
                    self._remove_overlapped_spans(covered_compound_tokens, compound_tokens_lists)
                # Insert new SpanList into compound_tokens
                self._insert_span(spl, compound_tokens_lists)

        return compound_tokens_lists


    def _get_covered_tokens(self, start:int, end:int, left_strict:bool, right_strict:bool, spans:list):
        '''
        Filters the list spans and returns a sublist containing spans within 
        the range (start, end).
        
        Parameters left_strict and right_strict can be used to loosen the range
        constraints; e.g. if left_strict==False, then returned spans can start 
        before the given start position.
        '''
        covered = []
        if spans:
            for span in spans:
                #print('>>>> ',text.text[span.start:span.end],span.start,span.end, start, end)
                if not left_strict and right_strict:
                    if start <= span.end and span.end <= end:
                        # span's end falls into target's start and end
                        covered.append( span )
                elif left_strict and not right_strict:
                    if start <= span.start and span.start <= end:
                        # span's start falls into target's start and end
                        covered.append( span )
                elif left_strict and right_strict:
                    if start <= span.start and span.end <= end:
                        # span entirely falls into target's start and end
                        covered.append( span )
        return covered


    def _remove_overlapped_spans(self, compound_token_spans:list, regular_spans:list):
        '''
        Filters the list regular_spans and removes spans  that  are  entirely
        contained within compound_token_spans. 
        Returns a new list containing filtered regular_spans.
        '''
        filtered = []
        for regular_span in regular_spans:
            is_entirely_overlapped = False
            for compound_token_span in compound_token_spans:
                if compound_token_span.start <= regular_span.start and \
                   regular_span.end <= compound_token_span.end:
                   is_entirely_overlapped = True
                   break
            if not is_entirely_overlapped:
                filtered.append(regular_span)
        return filtered


    def _insert_span(self, span:Union['Span', SpanList], spans:list):
        '''
        Inserts given span into spans so that the list remains sorted
        ascendingly according to text positions.
        '''
        i = 0
        inserted = False
        while i < len(spans):
            if span.end <= spans[i].start:
                spans.insert(i, span)
                inserted = True
                break
            i += 1
        if not inserted:
            spans.append(span)


    def _create_new_spanlist(self, text:'Text', compound_token_spans:list, regular_spans:list, joining_span:SpanList):
        '''
        Creates new SpanList that covers both compound_token_spans and regular_spans from given 
        text. Returns created SpanList.
        '''
        # 1) Get all tokens covered by compound_token_spans and regular_spans
        #    (basis material for the new spanlist)
        all_covered_tokens = []
        for compound_token_spanlist in compound_token_spans:
            for span in compound_token_spanlist:
                self._insert_span(span, all_covered_tokens)
        for span in regular_spans:
            self._insert_span(span, all_covered_tokens)

        # 2) Get attributes
        all_normalizations = {}
        all_types = []
        joining_span_type = joining_span.pattern_type if hasattr(joining_span, 'pattern_type') else None
        joining_span_type_added = False
        for compound_token_spanlist in compound_token_spans:
            span_start = compound_token_spanlist.start
            span_end   = compound_token_spanlist.end
            if compound_token_spanlist.normalized:   # if normalization != None
                all_normalizations[span_start] = ( compound_token_spanlist.normalized, \
                                                   span_end )
            if joining_span_type and \
               not joining_span_type_added and \
               span_start >= joining_span.end:
                all_types.append(joining_span_type)
                joining_span_type_added = True
            all_types.append(compound_token_spanlist.type)
        # Add joining span type (if it has not been added yet)
        if joining_span_type and \
           not joining_span_type_added:
            all_types.append(joining_span_type)

        # 3) Provide normalized string, if normalization is required
        if hasattr(joining_span, 'normalized') and joining_span.normalized:
            start = joining_span.start
            all_normalizations[start] = (joining_span.normalized, joining_span.end)
        normalized_str = None
        if len(all_normalizations.keys()) > 0:
            # reconstruct entire string (unnormalized)
            start_index = all_covered_tokens[0].start
            end_index   = all_covered_tokens[-1].end
            full_string = text.text[start_index : end_index]
            # reconstruct normalization if required
            i = start_index
            normalized = []
            while i < end_index+1:
                if i in all_normalizations:
                    # add normalized string
                    normalized.append(all_normalizations[i][0])
                    # move to the next position
                    i = all_normalizations[i][1]
                else:
                    # add single symbol
                    normalized.append(text.text[i:i+1])
                    i += 1
            normalized_str = ''.join(normalized)
        
        # 4) Create new SpanList and assign attributes
        spl = SpanList()
        spl.type = 'tokenization_hint'
        spl.spans = all_covered_tokens
        spl.normalized = normalized_str
        if all_types:
            spl.type = '+'.join(all_types)
        
        #print('>1>',[text.text[t.start:t.end] for t in all_covered_tokens] )
        #print('>2>',spl.type )
        #print('>3>',normalized_str )

        return spl

