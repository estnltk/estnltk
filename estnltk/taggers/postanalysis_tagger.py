#
#  Provides post-corrections after Vabamorf-based morphological 
#  analysis.
#  These post-corrections should be applied before morphological 
#  disambiguation.
# 
import regex as re

from estnltk.text import Span, SpanList, Layer, Text
from estnltk.taggers import Tagger

from estnltk.taggers.morf_common import IGNORE_ATTR
from estnltk.taggers.morf_common import ESTNLTK_MORPH_ATTRIBUTES
from estnltk.taggers.morf_common import VABAMORF_ATTRIBUTES
from estnltk.taggers.morf_common import _get_word_text, _create_empty_morph_span
from estnltk.taggers.morf_common import _is_empty_span

from estnltk.rewriting.postmorph.vabamorf_corrector import VabamorfCorrectionRewriter


class PostMorphAnalysisTagger(Tagger):
    description   = "Provides corrections to morphological analysis layer. "+\
                    "This tagger should be applied before morphological disambiguation."
    layer_name    = None
    attributes    = ESTNLTK_MORPH_ATTRIBUTES + (IGNORE_ATTR, )
    depends_on    = None
    configuration = None

    def __init__(self,
                 layer_name='morph_analysis', \
                 ignore_emoticons:bool=True, \
                 ignore_xml_tags:bool=True, \
                 fix_names_with_initials:bool=True, \
                 fix_emoticons:bool=True, \
                 fix_www_addresses:bool=True, \
                 fix_email_addresses:bool=True, \
                 fix_abbreviations:bool=True, \
                 fix_numeric:bool=True, \
                 remove_duplicates:bool=True, \
                 correction_rewriter=VabamorfCorrectionRewriter() ,\
                 **kwargs):
        """Initialize PostMorphAnalysisTagger class.

        Parameters
        ----------
        ignore_emoticons: bool (default: True)
            If True, then emoticons will be marked as to 
            be ignored by morphological disambiguation.

        ignore_xml_tags: bool (default: True)
            If True, then xml tags will be marked as to 
            be ignored by morphological disambiguation.

        fix_names_with_initials: bool (default: True)
            If True, then words that are of type 'name_with_initial'
            (a compound token type) will have their:
            1) partofspeech overwritten with 'H' (propername);
            2) root normalized: 
               2.1) underscores added between different parts of 
                    the name;
               2.2) name start positions converted to uppercase;

        fix_emoticons: bool (default: True)
            If True, then postags of all emoticons will be 
            overwritten with 'Z';

        fix_www_addresses: bool (default: True)
            If True, then postags of all www-addresses will be 
            overwritten with 'H';

        fix_email_addresses: bool (default: True)
            If True, then postags of all email addresses will be 
            overwritten with 'H';
        
        fix_abbreviations: bool (default: True)
            If True, then abbreviations with postags 'S' & 'H' 
            will have their postags overwritten with 'Y';
        
        fix_numeric: bool (default: True)
            If True, then postags of numeric and percentage
            tokens will be fixed (will be set to 'N');
        
        remove_duplicates: bool (default: True)
            If True, then duplicate morphological analyses
            will be removed while rewriting the layer.
        
        correction_rewriter (default: VabamorfCorrectionRewriter)
            Rewriter class that will be applied on rewriting the layer.
            
        """
        self.kwargs = kwargs
        self.layer_name = layer_name
       
        self.configuration = {'ignore_emoticons':ignore_emoticons,\
                              'ignore_xml_tags':ignore_xml_tags,\
                              'fix_names_with_initials':fix_names_with_initials,\
                              'fix_emoticons':fix_emoticons,\
                              'fix_www_addresses':fix_www_addresses,\
                              'fix_email_addresses':fix_email_addresses,\
                              'fix_abbreviations':fix_abbreviations,\
                              'fix_numeric':fix_numeric,\
                              'remove_duplicates':remove_duplicates,\
                              'correction_rewriter':correction_rewriter,\
        }
        self.configuration.update(self.kwargs)

        self.depends_on = ['compound_tokens', 'words', 'sentences', 'morph_analysis']
        
        # Compile regexes
        self.pat_name_needs_underscore1 = \
                re.compile('(\.)\s+([A-ZÖÄÜÕŽŠ])')
        self.pat_name_needs_underscore2 = \
                re.compile('([A-ZÖÄÜÕŽŠ]\.)([A-ZÖÄÜÕŽŠ])')
        self.pat_name_needs_uppercase = \
                re.compile('(\.\s+_)([a-zöäüõšž])')
        self.pat_numeric = \
                re.compile('^(?=\D*\d)[0-9.,\- ]+$')
                
        
        


    def tag(self, text: Text, return_layer=False) -> Text:
        """Provides corrections on morphological analyses of 
        given Text object.
        Also, rewrites the layer 'morph_analysis' with a new
        attribute '_ignore', and marks some of the words to 
        be ignored by future morphological disambiguation.
        
        Parameters
        ----------
        text: estnltk.text.Text
            Text object on which morphological analyses are to be
            corrected.
            The Text object must have layers 'words', 'sentences',
            'morph_analysis', 'compound_tokens'.
        return_layer: boolean (default: False)
            If True, then the corrected 'morph_analysis' will be 
            returned. Note: the returned layer still belongs to
            the input text.
            Otherwise, the Text object with the corrected layer 
            is returned;

        Returns
        -------
        Text or Layer
            If return_layer==True, then returns the corrected 
            'morph_analysis' layer (which still belongs to the
            Text object); otherwise returns the Text containing
            the corrected layer;
        """
        assert self.layer_name in text.layers
        assert 'compound_tokens' in text.layers
        
        # Take attributes from the input layer
        current_attributes = text[self.layer_name].attributes
        # Check if there are any extra attributes to carry over
        # from the old layer
        extra_attributes = []
        for cur_attr in current_attributes:
            if cur_attr not in self.attributes:
                extra_attributes.append( cur_attr )

        # --------------------------------------------
        #   Provide fixes that involve rewriting
        #   attributes of existing spans 
        #    (no removing or adding spans)
        # --------------------------------------------
        self._fix_based_on_compound_tokens( text )

        # --------------------------------------------
        #   Create a new layer with ignore attribute,
        #   and provide fixes that involve 
        #   adding/removing spans
        # --------------------------------------------
        self._rewrite_layer_and_fix( text )

        # --------------------------------------------
        #   Mark specific compound tokens as to be 
        #   ignored in future analysis
        # --------------------------------------------
        self._ignore_specific_compound_tokens( text )

        # --------------------------------------------
        #   Return layer or Text
        # --------------------------------------------
        # Return layer
        if return_layer:
            return text[self.layer_name]
        # Layer is already attached to the text, return it
        return text


    def _ignore_specific_compound_tokens( self, text: Text ):
        '''Mark morph analyses overlapping with specific compound tokens 
           (such as XML tags, emoticons) as analyses to be ignored during 
           morphological disambiguation.
           Which types of compound tokens will be marked depends on the 
           configuration of the tagger.
           
        Parameters
        ----------
        text: estnltk.text.Text
            Text object to which ignore-markings will be added.
        '''
        comp_token_id = 0
        for spanlist in text.morph_analysis.spans:
            if comp_token_id < len(text['compound_tokens'].spans):
                comp_token = text['compound_tokens'].spans[comp_token_id]
                if (comp_token.start == spanlist.start and \
                    spanlist.end == comp_token.end):
                    ignore_spans = False
                    # Found matching compound token
                    if self.configuration['ignore_emoticons'] and \
                       'emoticon' in comp_token.type:
                        ignore_spans = True
                    if self.configuration['ignore_xml_tags'] and \
                       'xml_tag' in comp_token.type:
                        ignore_spans = True
                    if ignore_spans:
                        # Mark all spans as to be ignored
                        for span in spanlist:
                            setattr(span, IGNORE_ATTR, True)
                    comp_token_id += 1
            else:
                # all compound tokens have been exhausted
                break


    def _fix_based_on_compound_tokens( self, text: Text ):
        '''Fixes morph analyses based on information about compound tokens.
           For instance, if a word overlaps with a compound token of type 
           'name_with_initial', then its partofspeech will be set to H
           (proper name), regardless the initial value of partofspeech. 
           Which fixes will be made depends on the configuration of the 
           tagger.
           
        Parameters
        ----------
        text: estnltk.text.Text
            Text object on which 'morph_analysis' will be corrected.
        '''
        comp_token_id  = 0
        has_normalized = 'normalized' in text['compound_tokens'].attributes
        for spanlist in text.morph_analysis.spans:
            if comp_token_id < len(text['compound_tokens'].spans):
                comp_token = text['compound_tokens'].spans[comp_token_id]
                if (comp_token.start == spanlist.start and \
                    spanlist.end == comp_token.end):
                    ignore_spans = False
                    # Found matching compound token
                    # 1) Fix names with initials, such as "T. S. Eliot"
                    if self.configuration['fix_names_with_initials'] and \
                       'name_with_initial' in comp_token.type:
                        for span in spanlist:
                            # If it is a verb, then skip the fixes 
                            # ( verbs are more complicated, may need 
                            #   changing form, ending etc. )
                            if getattr(span, 'partofspeech') == 'V':
                                continue
                            # Set partofspeech to H
                            setattr(span, 'partofspeech', 'H')
                            root = getattr(span, 'root')
                            # Fix root: if there is no underscore/space, add it 
                            root = \
                                self.pat_name_needs_underscore1.sub('\\1 _\\2', root)
                            root = \
                                self.pat_name_needs_underscore2.sub('\\1 _\\2', root)
                            # Fix root: convert lowercase name start to uppercase
                            root = \
                                self.pat_name_needs_uppercase.sub(_convert_to_uppercase, root)
                            #
                            #  Note: we  fix   only  'root', assuming that 
                            # 'root_tokens' and 'lemma' will be re-generated 
                            # based on it 
                            #
                            setattr(span, 'root', root)
                    # 2) Fix emoticons, such as ":D"
                    if self.configuration['fix_emoticons'] and \
                       'emoticon' in comp_token.type:
                        for span in spanlist:
                            # Set partofspeech to Z
                            setattr(span, 'partofspeech', 'Z')
                    # 3) Fix www-addresses, such as 'Postimees.ee'
                    if self.configuration['fix_www_addresses'] and \
                       ('www_address' in comp_token.type or \
                        'www_address_short' in comp_token.type):
                        for span in spanlist:
                            # Set partofspeech to H
                            setattr(span, 'partofspeech', 'H')
                    # 4) Fix email addresses, such as 'big@boss.com'
                    if self.configuration['fix_email_addresses'] and \
                       'email' in comp_token.type:
                        for span in spanlist:
                            # Set partofspeech to H
                            setattr(span, 'partofspeech', 'H')                            
                    comp_token_id += 1
                    # 5) Fix abbreviations, such as 'toim.', 'Tlk.'
                    if self.configuration['fix_abbreviations'] and \
                       ('abbreviation' in comp_token.type or \
                        'non_ending_abbreviation' in comp_token.type):
                        for span in spanlist:
                            # Set partofspeech to Y, if it is S or H
                            if getattr(span, 'partofspeech') in ['S', 'H']:
                                setattr(span, 'partofspeech', 'Y')
                    # 6) Fix partofspeech of numerics and percentages
                    if self.configuration['fix_numeric']:
                        if 'numeric' in comp_token.type or \
                           'percentage' in comp_token.type:
                            for span in spanlist:
                                # Change partofspeech from Y to N
                                if getattr(span, 'partofspeech') in ['Y']:
                                    setattr(span, 'partofspeech', 'N')
                        elif 'case_ending' in comp_token.type:
                            # a number with a case ending may also have 
                            # wrong partofspeech
                            for span in spanlist:
                                if getattr(span, 'partofspeech') in ['Y']:
                                    # if root looks like a numeric, 
                                    # then change pos Y -> N
                                    root = getattr(span, 'root')
                                    if self.pat_numeric.match(root):
                                        setattr(span, 'partofspeech', 'N')
            else:
                # all compound tokens have been exhausted
                break


    def _rewrite_layer_and_fix( self, text: Text ):
        '''Rewrites text's layer 'morph_analysis' by adding 
           attribute IGNORE_ATTR to it. Also provides fixes
           that require removal or addition of spans:
           1. Removes duplicate analyses;
           2. Rewrites elements of the layer using 
              correction_rewriter;
           3. ...
           
        Parameters
        ----------
        text: estnltk.text.Text
            Text object which 'morph_analysis' will be rewritten.
        '''
        # Take attributes from the input layer
        current_attributes = text[self.layer_name].attributes
        
        # Create a new layer
        new_morph_layer = Layer(name=self.layer_name,
                            parent='words',
                            ambiguous=True,
                            attributes=current_attributes +\
                            (IGNORE_ATTR,)
        )

        # Rewrite spans of the old layer
        morph_span_id = 0
        morph_spans   = text[self.layer_name].spans
        while morph_span_id < len(morph_spans):
            # 0) Convert SpanList to list of Span-s
            morph_spanlist = \
                [span for span in morph_spans[morph_span_id].spans]

            # A) Remove duplicate analyses (if required)
            if self.configuration['remove_duplicates']:
                morph_spanlist = \
                    _remove_duplicate_morph_spans( morph_spanlist )

            # A.2) Check for empty spans
            word = morph_spanlist[0].parent
            is_empty = _is_empty_span(morph_spanlist[0])
            if is_empty:
                new_morph_span = \
                    _create_empty_morph_span( word, \
                        layer_attributes = current_attributes )
                # Add ignore attribute
                setattr(new_morph_span, IGNORE_ATTR, False)
                # Record the new span
                new_morph_layer.add_span( new_morph_span )
                # Advance in the old "morph_analysis" layer
                morph_span_id += 1
                continue

            # B) Convert spans to records
            records = [ span.to_record() for span in morph_spanlist ]
            
            # B.1) Apply correction-rewriter:
            if self.configuration['correction_rewriter']:
                # B.1.1) Add 'word_normal'
                normalized_text = _get_word_text( word )
                for rec in records:
                    # Assume all analyses of a single word share common
                    # normal form
                    rec['word_normal'] = normalized_text
                # B.1.2) Rewrite records of a single word
                rewritten_recs = \
                    self.configuration['correction_rewriter'].rewrite(records)
                records = rewritten_recs
            
            # C) Convert records back to spans
            #    Add IGNORE_ATTR
            record_added = False
            for rec in records:
                if not rec:
                    # Skip if a record was deleted
                    continue
                new_morph_span = Span(parent=word)
                # Carry over attributes
                for attr in rec.keys():
                    if attr in ['start', 'end', 'text', 'word_normal']:
                        continue 
                    if attr == 'root_tokens':
                        # make it hashable for Span.__hash__
                        setattr(new_morph_span, attr, tuple(rec[attr]))
                    else:
                        setattr(new_morph_span, attr, rec[attr])
                # Add ignore attribute
                setattr(new_morph_span, IGNORE_ATTR, False)
                # Record the new span
                new_morph_layer.add_span(new_morph_span)
                record_added = True

            # C.2) If no records were added (all were deleted),
            #      then add an empty record (unknown word)
            if not record_added:
                new_morph_span = \
                    _create_empty_morph_span( word, \
                        layer_attributes = current_attributes )
                # Add ignore attribute
                setattr(new_morph_span, IGNORE_ATTR, False)
                # Record the new span
                new_morph_layer.add_span( new_morph_span )
                # Advance in the old "morph_analysis" layer

            # Advance in the old "morph_analysis" layer
            morph_span_id += 1

        # Overwrite the old layer
        delattr(text, self.layer_name)
        text[self.layer_name] = new_morph_layer


# =================================
#    Helper functions
# =================================

def _convert_to_uppercase( matchobj ):
    '''Converts second group of matchobj to uppercase, and 
       returns a concatenation of first and second group. '''
    return matchobj.group(1)+matchobj.group(2).upper()

def _remove_duplicate_morph_spans( spanlist: list ):
    '''Removes duplicate morphological analyses from given
       list of Span-s. Returns new list of Span-s.'''
    new_spanlist = []
    for s1, span1 in enumerate(spanlist):
        duplicateFound = False
        if s1+1 < len(spanlist):
            for s2 in range(s1+1, len(spanlist)):
                span2 = spanlist[s2]
                # Check for complete attribute match
                attr_matches = []
                for attr in VABAMORF_ATTRIBUTES:
                    attr_match = \
                       (getattr(span1,attr)==getattr(span2,attr))
                    attr_matches.append( attr_match )
                if all( attr_matches ):
                    duplicateFound = True
                    break
        if not duplicateFound:
            # If this span is unique, add it
            new_spanlist.append(span1)
    assert len(new_spanlist) <= len(spanlist)
    return new_spanlist
