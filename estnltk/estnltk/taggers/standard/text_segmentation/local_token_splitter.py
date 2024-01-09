#
#  LocalTokenSplitter splits tokens into smaller tokens based on 
#  regular expression patterns and user-defined functions for 
#  determining the split point. 
#  This is an optional tool that can be used to improve the 
#  splitting results of the TokensTagger.
#
#  Original source:
#  https://github.com/estnltk/smart-search/blob/469f54a1382d5cb2e717cdc7224774b7678a647e/demod/toovood/riigi_teataja_pealkirjaotsing/01_dokumentide_indekseerimine/estnltk_patches/local_token_splitter.py
#
from typing import List
from typing import Tuple
from typing import Callable
from typing import MutableMapping

import regex as re

from copy import copy

from estnltk import Text
from estnltk import Layer
from estnltk.taggers import Retagger


class LocalTokenSplitter(Retagger):
    """
    Splits tokens into smaller tokens based on regular expression patterns. 
    Exact split points will be determined by user-defined functions in split rules. 
    One token can be split only once. No recursive splitting strategies are supported.
    If several patterns match then the first in the pattern list is applied.
    Decisions to split or not can depend only on the token itself and not general context.
    """

    output_layer = 'tokens'
    input_layers = ['tokens']
    output_attributes = ()
    conf_param = ['split_patterns']

    def __init__(self,
                 split_rules: List[Tuple[re.Pattern, Callable[[str, re.regex.Match], int]]],
                 output_layer: str = 'tokens'):
        """Initializes LocalTokenSplitter.

        Parameters
        ----------
        split_rules: List[Tuple[re.Pattern, Callable[[str, re.regex.Match]
            A list of precompiled regular expression Patterns together
            with function that determines the split point.
            If match occurs but split_point == -1 then the match is
            discarded and other patterns are tested.

            The function gets two inputs:
            - token text
            - match object
            and has to compute the split point based on this information.

        output_layer: str (default: 'tokens')
            Name of the layer which contains tokenization results
        """
        # Set input/output layers
        self.output_layer = output_layer
        self.input_layers = [output_layer]
        self.output_attributes = ()

        # Assert that all patterns are in the valid format
        if not isinstance(split_rules, list):
            raise TypeError('(!) patterns should be a list of compiled regular expressions.')
        # Validate split_rules
        for rule in split_rules:
            if len(rule) != 2:
                raise TypeError(f'(!) Illegal split_rule {rule!r}. A split_rule should '+\
                                 'consist of two items: a regex pattern and a callable.')
            pat = rule[0]
            has_match   = callable(getattr(pat, "match", None))
            has_search  = callable(getattr(pat, "search", None))
            has_pattern = getattr(pat, "pattern", None) is not None
            for (k,v) in (('method match()',has_match),\
                          ('method search()',has_search),\
                          ('attribute pattern',has_pattern)):
                if v is False:
                    raise TypeError('(!) Unexpected regex pattern: {!r} is missing {}.'.format(pat, k))
            if not callable(rule[1]):
                raise TypeError(f'(!) {rule[1]!r} should be a callable, not {type(rule[1])}.')
        self.split_patterns = copy(split_rules)

    def _change_layer(self, text: Text, layers: MutableMapping[str, Layer], status: dict):
        """Rewrites the tokens layer by splitting its tokens into
           smaller tokens where necessary.

           Parameters
           ----------
           text: str
              Text object which annotations will be changed;

           layers: MutableMapping[str, Layer]
              Layers of the text. Contains mappings from the name
              of the layer to the Layer object. Must contain
              the tokens layer.

           status: dict
              This can be used to store metadata on layer tagging.
        """
        # Get changeble layer
        changeble_layer = layers[self.output_layer]
        # Iterate over tokens
        add_spans = []
        remove_spans = []
        for span in changeble_layer:
            token_str = text.text[span.start:span.end]
            for pat, split_point in self.split_patterns:
                match = pat.search(token_str)
                if match is None:
                    continue

                delta = split_point(token_str, match)
                if delta < 0 or delta >= len(token_str):
                    continue

                # Make split
                add_spans.append((span.start, span.start + delta))
                add_spans.append((span.start + delta, span.end))
                remove_spans.append(span)
                # Once a token has been split, then break and move on to
                # the next token ...
                break

        if add_spans:
            assert len(remove_spans) > 0
            for old_span in remove_spans:
                changeble_layer.remove_span( old_span )
            for new_span in add_spans:
                changeble_layer.add_annotation( new_span )