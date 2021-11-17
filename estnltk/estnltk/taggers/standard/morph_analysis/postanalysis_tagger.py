#
#  Provides post-corrections after Vabamorf-based morphological 
#  analysis.
#  These post-corrections should be applied before morphological 
#  disambiguation.
#
from collections import defaultdict
import regex as re
import os.path
import pandas
import pickle

from typing import MutableMapping

from estnltk import Annotation
from estnltk import Layer

from estnltk.taggers import Retagger

from estnltk.taggers.standard.morph_analysis.morf_common import IGNORE_ATTR
from estnltk.taggers.standard.morph_analysis.morf_common import ESTNLTK_MORPH_ATTRIBUTES
from estnltk.taggers.standard.morph_analysis.morf_common import VABAMORF_ATTRIBUTES
from estnltk.taggers.standard.morph_analysis.morf_common import NORMALIZED_TEXT
from estnltk.taggers.standard.morph_analysis.morf_common import _create_empty_morph_record
from estnltk.taggers.standard.morph_analysis.morf_common import _span_to_records_excl
from estnltk.taggers.standard.morph_analysis.morf_common import _is_empty_annotation
from estnltk.taggers.standard.morph_analysis.morf_common import _postprocess_root

from estnltk.taggers.standard.morph_analysis.proxy import MorphAnalyzedToken

# Default rules for correcting number analysis
DEFAULT_NUMBER_ANALYSIS_RULES = os.path.join(os.path.dirname(__file__),
                                'number_fixes/number_analysis_rules.csv')

class PostMorphAnalysisTagger(Retagger):
    """Applies post-corrections to ambiguous morphological analysis 
       layer before the disambiguation process.
       This tagger should be applied before VabamorfDisambiguator."""
    output_attributes = ESTNLTK_MORPH_ATTRIBUTES + (IGNORE_ATTR, )
    conf_param = ['ignore_emoticons', 'ignore_xml_tags', 'ignore_hashtags',
                  'fix_names_with_initials',
                  'fix_emoticons', 'fix_www_addresses', 'fix_email_addresses',
                  'fix_hashtags_and_usernames',
                  'fix_abbreviations', 'fix_number_postags', 'remove_duplicates',
                  'fix_number_analyses_using_rules',
                  'fix_number_analyses_by_replacing',
                  'remove_broken_pronoun_analyses',
                  # Number analysis related
                  '_number_analysis_rules_file',
                  '_number_correction_rules',
                  # Names of input layers
                  '_input_cp_tokens_layer',
                  # Regep patterns
                  '_pat_name_needs_underscore1',
                  '_pat_name_needs_underscore2',
                  '_pat_name_needs_uppercase',
                  '_pat_numeric']

    def __init__(self,
                 output_layer='morph_analysis',
                 input_compound_tokens_layer='compound_tokens',
                 input_words_layer='words',
                 ignore_emoticons:bool=True,
                 ignore_xml_tags:bool=True,
                 ignore_hashtags:bool=True,
                 fix_names_with_initials:bool=True,
                 fix_emoticons:bool=True,
                 fix_www_addresses:bool=True,
                 fix_email_addresses:bool=True,
                 fix_hashtags_and_usernames:bool=True,
                 fix_abbreviations:bool=True,
                 remove_duplicates:bool=True,
                 fix_number_postags:bool=True,
                 fix_number_analyses_using_rules:bool=True,
                 number_analysis_rules:str=DEFAULT_NUMBER_ANALYSIS_RULES,
                 fix_number_analyses_by_replacing:bool=True,
                 
                 remove_broken_pronoun_analyses:bool=False ):
        """Initialize PostMorphAnalysisTagger class.

        Parameters
        ----------
        output_layer: str (default: 'morph_analysis')
            Name of the morphological analysis layer that 
            will be corrected;
        
        input_compound_tokens_layer: str (default: 'compound_tokens')
            Name of the input compound_tokens layer;
        
        ignore_emoticons: bool (default: True)
            If True, then emoticons will be marked as to 
            be ignored by morphological disambiguation.

        ignore_xml_tags: bool (default: True)
            If True, then xml tags will be marked as to 
            be ignored by morphological disambiguation.
        
        ignore_hashtags: bool (default: True)
            If True, then hashtags will be marked as to 
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

        fix_hashtags_and_usernames: bool (default: True)
            If True, then Twitter-style hashtags and usernames
            will have their postags overwritten with 'H'.

        fix_abbreviations: bool (default: True)
            If True, then abbreviations with postags 'S' & 'H' 
            will have their postags overwritten with 'Y';
        
        remove_duplicates: bool (default: True)
            If True, then duplicate morphological analyses
            will be removed while rewriting the layer.
        
        fix_number_postags: bool (default: True)
            If True, then postags of numeric and percentage
            tokens will be fixed (will be changed from 
            'Y' to 'N');
       
        fix_number_analyses_using_rules: bool (Default: True)
            If True, then loads fixes for number analyses from the 
            CSV file number_analysis_rules, and applies to correct 
            the numeric tokens;
            For instance, '6te' will be analysed not as a pronoun
               ('6+sina //_P_ sg n //'), but as a number 
                '6+te // _N_ sg p //';
        
        number_analysis_rules: str (Defaults to: 'number_analysis_rules.csv')
            A CSV file containing rules for fixing numbers. Each 
            line should be in the form: 
               number_regexp,number_suffix,pos,form,ending
            For instance:
               ([1-9][0-9]*)?1[1-9]$,,N,?,0
               ([1-9][0-9]*)?1[1-9]$,lt,N,sg abl,lt
        
        fix_number_analyses_by_replacing:bool (default: True)
            If True, then during fixing number analyses old 
            analyses will be replaced by new analyses;
            If False, then old analyses will be filtered, that 
            is, the intersection of old analysis and new analysis
            will be taken as the new set of analyses;
            This option only works if the flag 
            fix_number_analyses_using_rules is set;
        
        remove_broken_pronoun_analyses: bool (default: False)
            If True, then words mistakenly analysed as pronouns
            (such as '11-endal' analysed as '11-ise', and
             '22-selt' analysed as '22-see') will have their 
            pronoun analyses deleted;
            (!) Important: if the target word has only pronoun 
            analyses, these fixes will erase all of its analyses, 
            and you cannot disambiguate the resulting text. So,
            use this option with care -- use it only when you 
            do not need morphological disambiguation;
        """
        # Set attributes & configuration
        # The output layer
        self.output_layer = output_layer
        # Names of the input layers
        self.input_layers = [input_compound_tokens_layer,
                             input_words_layer,
                             output_layer]
        self._input_cp_tokens_layer = input_compound_tokens_layer
        
        # Correction of number analyses
        # (formerly in VabamorfCorrectionRewriter)
        self.fix_number_analyses_using_rules = fix_number_analyses_using_rules
        self.fix_number_analyses_by_replacing = fix_number_analyses_by_replacing
        self._number_analysis_rules_file = number_analysis_rules
        if self.fix_number_analyses_using_rules:
            self._number_correction_rules = \
                self.load_number_analysis_rules( self._number_analysis_rules_file )
        # Correction of pronouns
        # (formerly in VabamorfCorrectionRewriter)
        self.remove_broken_pronoun_analyses = remove_broken_pronoun_analyses
        
        self.ignore_emoticons = ignore_emoticons
        self.ignore_xml_tags = ignore_xml_tags
        self.ignore_hashtags = ignore_hashtags
        self.fix_names_with_initials = fix_names_with_initials
        self.fix_emoticons = fix_emoticons
        self.fix_www_addresses = fix_www_addresses
        self.fix_email_addresses = fix_email_addresses
        self.fix_hashtags_and_usernames = fix_hashtags_and_usernames
        self.fix_abbreviations = fix_abbreviations
        self.fix_number_postags = fix_number_postags
        self.remove_duplicates = remove_duplicates
        
        # Compile regexes
        self._pat_name_needs_underscore1 = \
                re.compile(r'(\.)\s+([A-ZÖÄÜÕŽŠ])')
        self._pat_name_needs_underscore2 = \
                re.compile(r'([A-ZÖÄÜÕŽŠ]\.)([A-ZÖÄÜÕŽŠ])')
        self._pat_name_needs_uppercase = \
                re.compile(r'(\.\s+_)([a-zöäüõšž])')
        self._pat_numeric = \
                re.compile(r'^(?=\D*\d)[0-9.,\- ]+$')


    def _change_layer(self, raw_text: str, layers: MutableMapping[str, Layer], status: dict = None) -> None:
        """Provides corrections on the ambiguous morphological analysis 
           layer before the disambiguation process.
           
           Also, adds the layer 'morph_analysis' a new attribute '_ignore', 
           and marks some of the words to be ignored by future morphological 
           disambiguation.

           Parameters
           ----------
           raw_text: str
              Text string corresponding to the text which annotation
              layers will be corrected;
           layers: MutableMapping[str, Layer]
              Layers of the raw_text. Contains mappings from the name 
              of the layer to the Layer object.  The  mapping  must 
              contain compound_tokens, words, sentences, and morph_analysis 
              layers. The morph_analysis layer will be retagged.
           status: dict
              This can be used to store metadata on layer retagging.
        """
        assert self.output_layer in layers
        assert self._input_cp_tokens_layer in layers
        # --------------------------------------------
        #   Provide fixes that involve rewriting
        #   attributes of existing spans 
        #    (no removing or adding spans)
        # --------------------------------------------
        self._fix_based_on_compound_tokens( raw_text, layers, status )
        # --------------------------------------------
        #   Create a new layer with ignore attribute,
        #   and provide fixes that involve 
        #   adding/removing spans
        # --------------------------------------------
        self._rewrite_layer_and_fix( raw_text, layers, status )
        # --------------------------------------------
        #   Mark specific compound tokens as to be 
        #   ignored in future analysis
        # --------------------------------------------
        self._ignore_specific_compound_tokens( raw_text, layers, status )

    def _ignore_specific_compound_tokens(self, raw_text: str,
                                         layers: MutableMapping[str, Layer],
                                         status: dict = None ):
        """Mark morph analyses overlapping with specific compound tokens
           (such as XML tags, emoticons) as analyses to be ignored during 
           morphological disambiguation.
           Which types of compound tokens will be marked depends on the 
           configuration of the tagger.
           
           Parameters
           ----------
           raw_text: str
              Text string corresponding to the text which annotation
              layers will be corrected;
           layers: MutableMapping[str, Layer]
              Layers of the raw_text. Contains mappings from the name 
              of the layer to the Layer object.  The  mapping  must 
              contain compound_tokens, words, sentences, and morph_analysis 
              layers. The morph_analysis layer will be retagged.
           status: dict
              This can be used to store metadata on layer retagging.

        """
        comp_token_id = 0
        for morph_spanlist in layers[self.output_layer].spans:
            if comp_token_id < len(layers[self._input_cp_tokens_layer]):
                comp_token = layers[self._input_cp_tokens_layer][comp_token_id]
                if (comp_token.start == morph_spanlist.start and
                    morph_spanlist.end == comp_token.end):
                    ignore_spans = False
                    # Found matching compound token
                    if self.ignore_emoticons and \
                       'emoticon' in comp_token.type:
                        ignore_spans = True
                    if self.ignore_xml_tags and \
                       'xml_tag' in comp_token.type:
                        ignore_spans = True
                    if self.ignore_hashtags and \
                       'hashtag' in comp_token.type:
                        ignore_spans = True
                    if ignore_spans:
                        # Mark all spans as to be ignored
                        for annotation in morph_spanlist.annotations:
                            setattr(annotation, IGNORE_ATTR, True)
                    comp_token_id += 1
            else:
                # all compound tokens have been exhausted
                break

    def _fix_based_on_compound_tokens( self, raw_text: str,
                                       layers: MutableMapping[str, Layer],
                                       status: dict = None ):
        '''Fixes morph analyses based on information about compound tokens.
           For instance, if a word overlaps with a compound token of type 
           'name_with_initial', then its partofspeech will be set to H
           (proper name), regardless the initial value of partofspeech. 
           Which fixes will be made depends on the configuration of the 
           tagger.
           
           Parameters
           ----------
           raw_text: str
              Text string corresponding to the text which annotation
              layers will be corrected;
           layers: MutableMapping[str, Layer]
              Layers of the raw_text. Contains mappings from the name 
              of the layer to the Layer object.  The  mapping  must 
              contain compound_tokens, words, sentences, and morph_analysis 
              layers. The morph_analysis layer will be retagged.
           status: dict
              This can be used to store metadata on layer retagging.
        '''
        comp_token_id  = 0
        has_normalized = 'normalized' in layers[ self._input_cp_tokens_layer ].attributes
        for morph_spanlist in layers[self.output_layer].spans:
            if comp_token_id < len(layers[self._input_cp_tokens_layer]):
                comp_token = layers[self._input_cp_tokens_layer][comp_token_id]
                if (comp_token.start == morph_spanlist.start and
                    morph_spanlist.end == comp_token.end):
                    #  In order to avoid errors in downstream processing, let's 
                    # fix only non-empty spans, and skip the empty spans
                    is_empty = not morph_spanlist.annotations or _is_empty_annotation(morph_spanlist.annotations[0])
                    if is_empty:
                        # Next compound token
                        comp_token_id += 1
                        continue
                    
                    # Found compound token that matches a non-empty span
                    # 1) Fix names with initials, such as "T. S. Eliot"
                    if self.fix_names_with_initials and \
                       'name_with_initial' in comp_token.type:
                        for annotation in morph_spanlist.annotations:
                            # If it is a verb, then skip the fixes 
                            # ( verbs are more complicated, may need 
                            #   changing form, ending etc. )
                            if getattr(annotation, 'partofspeech') == 'V':
                                continue
                            # Set partofspeech to H
                            setattr(annotation, 'partofspeech', 'H')
                            root = getattr(annotation, 'root')
                            # Fix root: if there is no underscore/space, add it 
                            root = \
                                self._pat_name_needs_underscore1.sub('\\1 _\\2', root)
                            root = \
                                self._pat_name_needs_underscore2.sub('\\1 _\\2', root)
                            # Fix root: convert lowercase name start to uppercase
                            root = \
                                self._pat_name_needs_uppercase.sub(_convert_to_uppercase, root)
                            #
                            #  Note: we  fix   only  'root', assuming that 
                            # 'root_tokens' and 'lemma' will be re-generated 
                            # based on it 
                            #
                            setattr(annotation, 'root', root)
                    # 2) Fix emoticons, such as ":D"
                    if self.fix_emoticons and \
                       'emoticon' in comp_token.type:
                        for span in morph_spanlist.annotations:
                            # Set partofspeech to Z
                            setattr(span, 'partofspeech', 'Z')
                    # 3) Fix www-addresses, such as 'Postimees.ee'
                    if self.fix_www_addresses and \
                       ('www_address' in comp_token.type or \
                        'www_address_short' in comp_token.type):
                        for span in morph_spanlist.annotations:
                            # Set partofspeech to H
                            setattr(span, 'partofspeech', 'H')
                    # 4) Fix email addresses, such as 'big@boss.com'
                    if self.fix_email_addresses and \
                       'email' in comp_token.type:
                        for span in morph_spanlist.annotations:
                            # Set partofspeech to H
                            setattr(span, 'partofspeech', 'H')
                    # 5) Fix abbreviations, such as 'toim.', 'Tlk.'
                    if self.fix_abbreviations and \
                       ('abbreviation' in comp_token.type or \
                        'non_ending_abbreviation' in comp_token.type):
                        for span in morph_spanlist.annotations:
                            # Set partofspeech to Y, if it is S or H
                            if getattr(span, 'partofspeech') in ['S', 'H']:
                                setattr(span, 'partofspeech', 'Y')
                    # 6) Fix partofspeech of numerics and percentages
                    if self.fix_number_postags:
                        if 'numeric' in comp_token.type or \
                           'percentage' in comp_token.type:
                            for span in morph_spanlist.annotations:
                                # Change partofspeech from Y to N
                                if getattr(span, 'partofspeech') in ['Y']:
                                    setattr(span, 'partofspeech', 'N')
                        elif 'case_ending' in comp_token.type:
                            # a number with a case ending may also have 
                            # wrong partofspeech
                            for annotation in morph_spanlist.annotations:
                                if getattr(annotation, 'partofspeech') in ['Y']:
                                    # if root looks like a numeric, 
                                    # then change pos Y -> N
                                    root = getattr(annotation, 'root')
                                    if self._pat_numeric.match(root):
                                        setattr(annotation, 'partofspeech', 'N')
                    # 7) Fix hashtags and Twitter-style usernames
                    if self.fix_hashtags_and_usernames and \
                            ('hashtag' in comp_token.type or 
                             'username_mention' in comp_token.type):
                        # Set postags to 'H'
                        for span in morph_spanlist.annotations:
                            # Set partofspeech to H
                            setattr(span, 'partofspeech', 'H')
                            # TODO: some of these may be verbs, and 
                            # thus require special corrections
                    # Next compound token
                    comp_token_id += 1
            else:
                # all compound tokens have been exhausted
                break

    def _rewrite_layer_and_fix(self, raw_text: str,
                               layers: MutableMapping[str, Layer],
                               status: dict = None ):
        """Rewrites the morph_analysis layer by adding attribute
           IGNORE_ATTR to it. Also provides fixes that require 
           removal or addition of spans:
             1. Removes duplicate analyses;
             2. Applies rule-based corrections to number analyses
                (if  fix_number_analyses_using_rules  is set);
             3. Removes redundant pronoun analyses
                (if  remove_broken_pronoun_analyses  is set);
           
           Note that this method also tries to preserve any extra
           attributes of the morph_analysis layer. Every rewritten
           (or newly created) morph_analysis span will obtain its
           extra attribute values from the original morph_analysis
           of the word. If the original morph_analysis of the word 
           consisted of multiple spans / analyses, extra attribute 
           values will be carried over from the first span / analysis.
           
           Parameters
           ----------
           raw_text: str
              Text string corresponding to the text which annotation
              layers will be corrected;
           layers: MutableMapping[str, Layer]
              Layers of the raw_text. Contains mappings from the name 
              of the layer to the Layer object.  The  mapping  must 
              contain compound_tokens, words, sentences, and morph_analysis 
              layers. The morph_analysis layer will be retagged.
           status: dict
              This can be used to store metadata on layer retagging.

        """
        # Add IGNORE_ATTR to the input layer
        if IGNORE_ATTR not in layers[self.output_layer].attributes:
            layers[self.output_layer].attributes += (IGNORE_ATTR,)
        # Take attributes from the input layer
        current_attributes = layers[self.output_layer].attributes
        # Find extra attributes (if there are any)
        extra_attributes = []
        for cur_attr in current_attributes:
            if cur_attr not in self.output_attributes and \
               cur_attr != IGNORE_ATTR:
                extra_attributes.append( cur_attr )
        # Rewrite spans of the old layer
        morph_span_id = 0
        morph_spans = layers[self.output_layer].spans
        words_layer = layers[self.input_layers[1]]
        while morph_span_id < len(morph_spans):
            # 0) Convert SpanList to list of Span-s
            morph_annotations = morph_spans[morph_span_id].annotations
            
            # A) Remove duplicate analyses (if required)
            if self.remove_duplicates:
                morph_annotations = _remove_duplicate_morph_spans(morph_annotations)
            
            # A.2) Check for empty spans
            word = words_layer[morph_spans[morph_span_id].base_span]
            is_empty = _is_empty_annotation(morph_annotations[0])
            if is_empty:
                empty_morph_record = \
                    _create_empty_morph_record(word=word,
                                               layer_attributes=current_attributes )
                # Add ignore attribute
                empty_morph_record[IGNORE_ATTR] = False
                # Carry over extra attributes
                if extra_attributes and len(morph_spans[morph_span_id].annotations) > 0:
                    # Assume that extra attributes are same for each annotation (of the word):
                    # therefore, carry over attribute values from the first annotation
                    first_span = morph_spans[morph_span_id].annotations[0]
                    first_span_rec = _span_to_records_excl(first_span, [IGNORE_ATTR])
                    for extra_attr in extra_attributes:
                        empty_morph_record[extra_attr] = first_span_rec[extra_attr]
                # Record the new span
                # Add the new annotation
                attributes = {attribute: empty_morph_record[attribute]
                              for attribute in layers[self.output_layer].attributes}
                span = morph_spans[morph_span_id]
                span.clear_annotations()
                span.add_annotation(Annotation(span, **attributes))
                # Advance in the old morph_analysis layer
                morph_span_id += 1
                continue
            
            # B) Convert spans to records
            records = [_span_to_records_excl(annotation, [IGNORE_ATTR]) for annotation in morph_annotations]
            rewritten_recs = records
            
            # B.1) Fix pronouns
            if self.remove_broken_pronoun_analyses and len(rewritten_recs) > 0:
                # B.1.1) Filter pronoun analyses: remove analyses in which the
                #        normalized word is actually not a pronoun;
                rewritten_recs_new = []
                morph_analysed_tokens = {}
                for rec in rewritten_recs:
                    assert NORMALIZED_TEXT in rec, \
                       '(!) Record {!r} is missing the attribute {!r}'.format(rec, NORMALIZED_TEXT)
                    normalized_word = rec[NORMALIZED_TEXT]
                    if normalized_word is None:
                        rewritten_recs_new.append(rec)
                        continue
                    if normalized_word not in morph_analysed_tokens:
                        # Obtain morphological analysis for the token
                        morph_analysed_tokens[normalized_word] = \
                              MorphAnalyzedToken( normalized_word )
                    # Conflict: a non-pronoun has been marked as a pronoun 
                    has_conflict = (rec['partofspeech'] == 'P') and \
                                   (not morph_analysed_tokens[normalized_word].is_pronoun)
                    if not has_conflict:
                        rewritten_recs_new.append(rec)
                rewritten_recs = rewritten_recs_new
            
            # B.2) Used rules (from CSV file) to fix number analyses
            if self.fix_number_analyses_using_rules and len(rewritten_recs) > 0:
                # Find analyses of numeric tokens and attempt to make fixes
                all_found_analyses = {}
                for rid, rec in enumerate(rewritten_recs):
                    assert NORMALIZED_TEXT in rec, \
                       '(!) Record {!r} is missing the attribute {!r}'.format(rec, NORMALIZED_TEXT)
                    normalized_word = rec[NORMALIZED_TEXT]
                    if normalized_word is None or not any([c.isnumeric() for c in normalized_word]):
                        continue
                    found_analyses = \
                            self.find_analyses_for_numeric_token( normalized_word )
                    if found_analyses and len(found_analyses) > 0:
                        all_found_analyses[rid] = found_analyses
                if len( all_found_analyses.keys() ) > 0:
                     # Replace the old ones or take the intersection
                     rewritten_recs_new = []
                     if self.fix_number_analyses_by_replacing:
                         # Replace the old ones completely
                         for i in range(len(rewritten_recs)):
                             current_recs = [rewritten_recs[i]]
                             if i in all_found_analyses:
                                 current_recs = all_found_analyses[i]
                             rewritten_recs_new.extend(current_recs)
                     else:
                         # Take the intersection of new ones and old ones
                         for k in all_found_analyses.keys():
                             for rec in all_found_analyses[k]:
                                 if rec in rewritten_recs and \
                                    rec not in rewritten_recs_new:
                                     rewritten_recs_new.append(rec)
                     rewritten_recs = rewritten_recs_new
            
            # B.3) Carry over extra attributes and add IGNORE_ATTR
            if len(rewritten_recs) > 0:
                layer_attributes = layers[self.output_layer].attributes
                # Assume that extra attributes are same for each record (of the word):
                # therefore, carry over attribute values from the first record
                first_old_rec = records[0] if len(records) > 0 else {}
                for rec in rewritten_recs:
                    # Carry over extra attributes
                    for extra_attr in extra_attributes:
                        # Note: carry over the extra attribute value only when 
                        # the record was changed (so that the attribute is missing 
                        # from the record)
                        if extra_attr not in rec and \
                           extra_attr in first_old_rec:
                            rec[extra_attr] = first_old_rec[extra_attr]
                    # Add IGNORE_ATTR
                    rec[IGNORE_ATTR] = False
                    # Just in case there is garbage, remove it
                    to_delete = []
                    for rec_attr in rec.keys():
                        if rec_attr not in layer_attributes:
                            to_delete.append(rec_attr)
                    if to_delete:
                        for rec_attr in to_delete:
                            del rec[rec_attr]
             
            # C.1) If no records were added (all were deleted),
            #      then add an empty record (unknown word)
            if len(rewritten_recs) == 0:
                empty_morph_record = \
                    _create_empty_morph_record(word=word, layer_attributes = current_attributes)
                # Add ignore attribute
                empty_morph_record[IGNORE_ATTR] = False
                # Carry over extra attributes
                if extra_attributes and len(morph_spans[morph_span_id].annotations) > 0:
                    # Assume that extra attributes are same for each annotation (of the word):
                    # therefore, carry over attribute values from the first annotation
                    first_span = morph_spans[morph_span_id].annotations[0]
                    first_span_rec = _span_to_records_excl(first_span, [IGNORE_ATTR])
                    for extra_attr in extra_attributes:
                        empty_morph_record[extra_attr] = first_span_rec[extra_attr]
                empty_morph_record = \
                    {attr: empty_morph_record[attr] for attr in layers[self.output_layer].attributes}
                # Add the new annotation
                rewritten_recs.append(empty_morph_record)
            
            # D) Rewrite the old span with new one
            span = morph_spans[morph_span_id]
            span.clear_annotations()
            for record in rewritten_recs:
                span.add_annotation(Annotation(span, **record))
            
            # Advance in the old "morph_analysis" layer
            morph_span_id += 1

    # ========================================================================
    #   Corrections for number analyses (from VabamorfCorrectionRewriter)
    # ========================================================================

    @staticmethod
    def create_number_analysis_rules_cache( csv_file:str=DEFAULT_NUMBER_ANALYSIS_RULES, force=False ):
        '''Creates a pickled version of the number analysis corrections CSV file.
           Note: the new pickled version is only created iff: 1) the pickle file 
           does not exist, 2) the pickle file is outdated, or 3) force==True;
        '''
        if not os.path.exists(csv_file):
            raise FileNotFoundError('(!) Missing number analysis corrections csv file: {!r}'.format(csv_file))
        cache = csv_file + '.pickle'
        if not os.path.exists(cache) or os.stat(cache).st_mtime < os.stat(csv_file).st_mtime or force==True:
            rules = PostMorphAnalysisTagger.load_number_analysis_rules_csv( csv_file )
            with open(cache, 'wb') as out_file:
                pickle.dump(rules, out_file)


    @staticmethod
    def load_number_analysis_rules_csv( csv_file:str ):
        '''Loads number analysis corrections from an input CSV file.'''
        df = pandas.read_csv(csv_file, na_filter=False, index_col=False)
        rules = defaultdict(dict)
        for _, r in df.iterrows():
            if r.suffix not in rules[r.number]:
                rules[r.number][r.suffix] = []
            rules[r.number][r.suffix].append({'partofspeech': r.pos, 'form': r.form, 'ending':r.ending})
        return rules


    @staticmethod
    def load_number_analysis_rules( csv_file:str ):
        '''Loads number analysis corrections from an input CSV or pickle file.
           If a cached version of the file exists (a .pickle file), then loads 
           the cached version, otherwise, loads from the CSV file.
        '''
        cache = csv_file + '.pickle'
        if not os.path.exists(cache):
            # Read number analysis rules from CSV file (can be slow)
            return PostMorphAnalysisTagger.load_number_analysis_rules_csv(csv_file)
        else:
            # Read rules from the pickle file
            with open(cache, 'rb') as in_file:
                rules = pickle.load(in_file)
            return rules


    def find_analyses_for_numeric_token( self, token_str ):
        '''Finds corrected morphological analyses for given 
           numeric token.
           Corrections are looked up from self._number_correction_rules
           Returns corrected records, or an empty list, if no 
           corrections are available.
        '''
        m = re.match(r'-?(\d+\.?)-?(\D*)$', token_str)
        if not m:
            return []
        number_str = m.group(1)
        ordinal_number_str = number_str.rstrip('.') + '.'
        ending = m.group(2)
        result = []
        # Add missing hyphens
        number_str_final = number_str
        ordinal_number_str_final = ordinal_number_str
        if token_str.startswith('-'):
            number_str_final = '-'+number_str_final
            ordinal_number_str_final = '-'+ordinal_number_str_final
        if token_str.endswith('-'):
            number_str_final = number_str_final+'-'
            ordinal_number_str_final = ordinal_number_str_final+'-'
        # Apply rules
        for number_re, analyses in self._number_correction_rules.items():
            if re.match(number_re, number_str):
                # Add analyses according to the ending
                for analysis in analyses.get( ending, [] ):
                    if analysis['partofspeech'] == 'O':
                        root, root_tokens, lemma = \
                            _postprocess_root( ordinal_number_str_final, analysis['partofspeech'] )
                        a = dict()
                        a['root'] = root
                        a['lemma'] = lemma
                        a['root_tokens'] = root_tokens
                        a['clitic'] = ''
                    else:
                        root, root_tokens, lemma = \
                            _postprocess_root( number_str_final, analysis['partofspeech'] )
                        a = dict()
                        a['root'] = root
                        a['lemma'] = lemma
                        a['root_tokens'] = root_tokens
                        a['clitic'] = ''
                    a.update(analysis)
                    result.append(a)
                break
        return result


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
