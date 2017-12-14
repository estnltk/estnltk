#
#  Provides common variables and constants for modules using 
#  Vabamorf-based morphological processing.
# 

# Default parameters to be passed to Vabamorf
# Note: these defaults are from  estnltk.vabamorf.morf
DEFAULT_PARAM_DISAMBIGUATE = True
DEFAULT_PARAM_GUESS        = True
DEFAULT_PARAM_PROPERNAME   = True
DEFAULT_PARAM_PHONETIC     = False
DEFAULT_PARAM_COMPOUND     = True

# Morphological analysis attributes used by Vabamorf
VABAMORF_ATTRIBUTES = ('root', 'ending', 'clitic', 'form', 'partofspeech')

# Morphological analysis attributes used by ESTNLTK
ESTNLTK_MORPH_ATTRIBUTES = ('lemma', 'root', 'root_tokens', 'ending', 'clitic', 'form', 'partofspeech')

# Name of the ignore attribute. During the morphological 
# disambiguation, all spans of "morph_analysis" that have 
# ignore attribute set to True will be skipped;
IGNORE_ATTR = '_ignore'


# ========================================================
#    Util for carrying over extra attributes from 
#          old EstNLTK Span to the new EstNLTK Span
# ========================================================

from estnltk.text import Span, SpanList

def carry_over_extra_attributes( old_spanlist:SpanList, \
                                 new_spanlist:list, \
                                 extra_attributes:list ):
    '''Carries over extra attributes from the old spanlist to the new 
       spanlist.
       Assumes:
       * each span from new_spanlist appears also in old_spanlist, and it can
         be detected by comparing spans by VABAMORF_ATTRIBUTES;
       * new_spanlist contains less or equal number of spans than old_spanlist;
        
       Parameters
       ----------
       old_spanlist: estnltk.spans.SpanList
           SpanList containing morphological analyses of a single word.
           The source of values of extra attributes.

       new_spanlist: list of estnltk.spans.Span
           List of newly created Span-s. The target to where extra 
           attributes and their values need to be written.
        
       extra_attributes: list of str
           List of names of extra attributes that need to be carried 
           over from old_spanlist to new_spanlist.

       Raises
       ------
       Exception
           If some item from new_spanlist cannot be matched with any of 
           the items from the old_spanlist;
    '''
    assert len(old_spanlist.spans) >= len(new_spanlist)
    for new_span in new_spanlist:
        # Try to find a matching old_span for the new_span
        match_found = False
        old_span_id = 0
        while old_span_id < len(old_spanlist.spans):
            old_span = old_spanlist.spans[old_span_id]
            # Check that all morph attributes match 
            # ( Skip 'lemma' & 'root_tokens', as these 
            #   were derived from 'root' )
            attr_matches = []
            for attr in VABAMORF_ATTRIBUTES:
                attr_match = (getattr(old_span,attr)==getattr(new_span,attr))
                attr_matches.append( attr_match )
            if all( attr_matches ):
                # Set extra attributes
                for extra_attr in extra_attributes:
                    setattr(new_span, \
                            extra_attr, \
                            getattr(old_span,extra_attr))
                match_found = True
                break
            old_span_id += 1
        if not match_found:
            new_pos = str((new_span.start, new_span.end))
            raise Exception('(!) Error on carrying over attributes of morph_analysis: '+\
                            'Unable to find a matching old span for the new span at '+\
                            'the location '+new_pos+'.')

