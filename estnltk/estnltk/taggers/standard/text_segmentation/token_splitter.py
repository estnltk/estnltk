#
#  TokenSplitter splits tokens into smaller tokens based on 
#  regular expression patterns. 
#  This is an optional tool that can be used to improve the 
#  splitting results of the TokensTagger.
# 

from typing import MutableMapping, List
import regex as re

from estnltk import Text
from estnltk import Layer
from estnltk.taggers import Retagger


class TokenSplitter( Retagger ):
    """Splits tokens into smaller tokens based on regular expression patterns."""
    output_layer      = 'tokens'
    input_layers      = ['tokens']
    output_attributes = ()
    conf_param = ['patterns', 'break_group_name']

    def __init__(self, 
                 patterns, 
                 output_layer:str='tokens',
                 break_group_name:str='end'):
        """Initializes TokenSplitter.
        
        Parameters
        ----------
        patterns: List[re.Pattern]
            A list of precompiled regular expression Patterns that 
            describe locations inside tokens where splits should
            be made. 
            Each pattern must contain a named group (break_group_name), 
            which marks a substring in the token after which the token 
            will be split into two pieces. 
        output_layer: str (default: 'tokens')
            Name of the layer which contains tokenization results;
        break_group_name: str (default: 'end')
            Name of the group (in Patterns) which marks a place in 
            the token string after which the token will be split 
            into two pieces. Defaults to 'end'.
        """
        # Set input/output layers
        self.output_layer = output_layer
        self.input_layers = [output_layer]
        self.output_attributes = ()
        # Set other configuration parameters
        if not (isinstance(break_group_name, str) and len(break_group_name) > 0):
            raise TypeError('(!) break_group_name should be a non-empty string.')
        self.break_group_name = break_group_name
        # Assert that all patterns are regular expressions in the valid format
        if not isinstance(patterns, list):
            raise TypeError('(!) patterns should be a list of compiled regular expressions.')
        # TODO: We use an adhoc way to verify that patterns are regular expressions 
        #       because there seems to be no common way of doing it both in py35 
        #       and py36
        for pat in patterns:
            # Check for the existence of methods/attributes
            has_match   = callable(getattr(pat, "match", None))
            has_search  = callable(getattr(pat, "search", None))
            has_pattern = getattr(pat, "pattern", None) is not None
            for (k,v) in (('method match()',has_match),\
                          ('method search()',has_search),\
                          ('attribute pattern',has_pattern)):
                if v is False:
                    raise TypeError('(!) Unexpected regex pattern: {!r} is missing {}.'.format(pat, k))
            symbolic_groups = pat.groupindex
            if self.break_group_name not in symbolic_groups.keys():
                raise TypeError('(!) Pattern {!r} is missing symbolic group named {!r}.'.format(pat, self.break_group_name))
        self.patterns = patterns


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
        add_spans    = []
        remove_spans = []
        for span in changeble_layer:
            token_str = text.text[span.start:span.end]
            for pat in self.patterns:
                m = pat.search(token_str)
                if m:
                    break_group_end = m.end( self.break_group_name )
                    if break_group_end > -1 and \
                       break_group_end > 0  and \
                       break_group_end < len(token_str):
                        # Make the split
                        add_spans.append( (span.start, span.start+break_group_end) )
                        add_spans.append( (span.start+break_group_end, span.end) )
                        remove_spans.append( span )
                        # Once a token has been split, then break and move on to 
                        # the next token ...
                        break
        if add_spans:
            assert len(remove_spans) > 0
            for old_span in remove_spans:
                changeble_layer.remove_span( old_span )
            for new_span in add_spans:
                changeble_layer.add_annotation( new_span )

