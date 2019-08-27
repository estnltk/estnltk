#
#  Provides post-corrections after Vabamorf-based morphological 
#  analysis.
#  These post-corrections should be applied before morphological 
#  disambiguation.
# 
import regex as re
import os.path
import pickle

from typing import MutableMapping

from estnltk import Annotation
from estnltk.layer.layer import Layer
from estnltk.layer.span import Span

from estnltk.taggers import Retagger

from estnltk.taggers.morph_analysis.morf_common import IGNORE_ATTR
from estnltk.taggers.morph_analysis.morf_common import ESTNLTK_MORPH_ATTRIBUTES
from estnltk.taggers.morph_analysis.morf_common import VABAMORF_ATTRIBUTES
from estnltk.taggers.morph_analysis.morf_common import _get_word_text, _create_empty_morph_record
from estnltk.taggers.morph_analysis.morf_common import _span_to_records_excl
from estnltk.taggers.morph_analysis.morf_common import _is_empty_annotation
from estnltk.taggers.morph_analysis.morf_common import _postprocess_root

from estnltk.taggers.morph_analysis.proxy import MorphAnalyzedToken

# Default rules for correcting number analysis
DEFAULT_NUMBER_ANALYSIS_RULES = os.path.join(os.path.dirname(__file__),
                                'number_fixes/number_analysis_rules.csv')

class PostMorphAnalysisTagger(Retagger):
    """Applies post-corrections to ambiguous morphological analysis 
       layer before the disambiguation process.
       This tagger should be applied before VabamorfDisambiguator."""
    output_attributes = ESTNLTK_MORPH_ATTRIBUTES + (IGNORE_ATTR, )
    conf_param = ['depends_on', 'ignore_emoticons', 'ignore_xml_tags', 'fix_names_with_initials',
                  'fix_emoticons', 'fix_www_addresses', 'fix_email_addresses',
                  'fix_abbreviations', 'fix_number_postags', 'remove_duplicates',
                  'fix_number_analyses_using_rules',
                  'fix_number_analyses_by_replacing',
                  'fix_pronouns',
                  # Number analysis related
                  '_number_analysis_rules_file',
                  '_number_correction_rules',
                  # Names of input layers
                  '_input_cp_tokens_layer',
                  '_input_words_layer',
                  '_input_sentences_layer',
                  '_input_morph_analysis_layer',
                  # Regep patterns
                  '_pat_name_needs_underscore1',
                  '_pat_name_needs_underscore2',
                  '_pat_name_needs_uppercase',
                  '_pat_numeric']

    def __init__(self,
                 output_layer='morph_analysis',
                 input_compound_tokens_layer='compound_tokens',
                 input_words_layer='words',
                 input_sentences_layer='sentences',
                 ignore_emoticons:bool=True,
                 ignore_xml_tags:bool=True,
                 fix_names_with_initials:bool=True,
                 fix_emoticons:bool=True,
                 fix_www_addresses:bool=True,
                 fix_email_addresses:bool=True,
                 fix_abbreviations:bool=True,
                 remove_duplicates:bool=True,
                 fix_number_postags:bool=True,
                 fix_number_analyses_using_rules:bool=True,
                 number_analysis_rules:str=DEFAULT_NUMBER_ANALYSIS_RULES,
                 fix_number_analyses_by_replacing:bool=True,
                 
                 fix_pronouns:bool=False ):
        """Initialize PostMorphAnalysisTagger class.

        Parameters
        ----------
        output_layer: str (default: 'morph_analysis')
            Name of the morphological analysis layer that 
            will be corrected;
        
        input_compound_tokens_layer: str (default: 'compound_tokens')
            Name of the input words layer;
        
        input_words_layer: str (default: 'words')
            Name of the input words layer;
        
        input_sentences_layer: str (default: 'sentences')
            Name of the input sentences layer;
        
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
        
        fix_pronouns: bool (default: False)
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
                             input_sentences_layer,
                             output_layer]
        self._input_cp_tokens_layer      = self.input_layers[0]
        self._input_words_layer          = self.input_layers[1]
        self._input_sentences_layer      = self.input_layers[2]
        self._input_morph_analysis_layer = self.input_layers[3]
        self.depends_on   = self.input_layers
        
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
        self.fix_pronouns = fix_pronouns
        
        self.ignore_emoticons = ignore_emoticons
        self.ignore_xml_tags = ignore_xml_tags
        self.fix_names_with_initials = fix_names_with_initials
        self.fix_emoticons = fix_emoticons
        self.fix_www_addresses = fix_www_addresses
        self.fix_email_addresses = fix_email_addresses
        self.fix_abbreviations = fix_abbreviations
        self.fix_number_postags = fix_number_postags
        self.remove_duplicates = remove_duplicates
        
        # Compile regexes
        self._pat_name_needs_underscore1 = \
                re.compile('(\.)\s+([A-ZÖÄÜÕŽŠ])')
        self._pat_name_needs_underscore2 = \
                re.compile('([A-ZÖÄÜÕŽŠ]\.)([A-ZÖÄÜÕŽŠ])')
        self._pat_name_needs_uppercase = \
                re.compile('(\.\s+_)([a-zöäüõšž])')
        self._pat_numeric = \
                re.compile('^(?=\D*\d)[0-9.,\- ]+$')


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
        assert self._input_sentences_layer in layers
        assert self._input_words_layer in layers
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
                (if  fix_pronouns  is set);
           
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
        while morph_span_id < len(morph_spans):
            # 0) Convert SpanList to list of Span-s
            morph_annotations = morph_spans[morph_span_id].annotations

            # A) Remove duplicate analyses (if required)
            if self.remove_duplicates:
                morph_annotations = _remove_duplicate_morph_spans(morph_annotations)

            # A.2) Check for empty spans
            word = morph_annotations[0].span.parent
            is_empty = _is_empty_annotation(morph_annotations[0])
            if is_empty:
                empty_morph_record = \
                    _create_empty_morph_record(word=word,
                                               layer_attributes=current_attributes )
                # Add ignore attribute
                empty_morph_record[IGNORE_ATTR] = False
                # Carry over extra attributes
                if extra_attributes and len(morph_spans[morph_span_id].spans) > 0:
                    # Assume that extra attributes are same for each sub-span (of the word):
                    # therefore, carry over attribute values from the first span
                    first_span = morph_spans[morph_span_id].spans[0]
                    first_span_rec = _span_to_records_excl(first_span, [IGNORE_ATTR])
                    for extra_attr in extra_attributes:
                        empty_morph_record[extra_attr] = first_span_rec[extra_attr]
                # Record the new span
                ambiguous_span = Span(morph_spans[morph_span_id].base_span, layer=layers[self.output_layer])
                # Add the new annotation
                attributes = {attribute: empty_morph_record[attribute] for attribute in ambiguous_span.layer.attributes}
                ambiguous_span.add_annotation(Annotation(ambiguous_span, **attributes))
                morph_spans[morph_span_id] = ambiguous_span
                # Advance in the old morph_analysis layer
                morph_span_id += 1
                continue

            # B) Convert spans to records
            records = [_span_to_records_excl(annotation, [IGNORE_ATTR]) for annotation in morph_annotations]
            rewritten_recs = records
            normalized_word_str = _get_word_text( word )
            
            # B.1) Fix pronouns 
            if self.fix_pronouns and len(rewritten_recs) > 0:
                # B.1.1) Filter pronoun analyses: remove analyses in which the 
                #        normalized word is actually not a pronoun;
                token = MorphAnalyzedToken( normalized_word_str )
                rewritten_recs_new = []
                for rec in rewritten_recs:
                    if rec['partofspeech'] == 'P':
                        if token.is_pronoun:
                            rewritten_recs_new.append(rec)
                    else:
                        rewritten_recs_new.append(rec)
                rewritten_recs = rewritten_recs_new
            
            # B.2) Used rules (from CSV file) to fix number analyses
            if self.fix_number_analyses_using_rules and len(rewritten_recs) > 0:
                # B.2.1) Rewrite records of a single word
                if normalized_word_str.isalpha():
                    # skip number corrections if the normalized token consists of letters only
                    pass
                else:
                    found_analyses = \
                        self.find_analyses_for_numeric_token( normalized_word_str )
                    if found_analyses:
                        # Replace the old ones or take the intersection
                        if self.fix_number_analyses_by_replacing:
                            rewritten_recs = found_analyses
                        else:
                            rewritten_recs = [rec for rec in rewritten_recs if rec in found_analyses]

            # B.3) Carry over extra attributes
            if extra_attributes and len(rewritten_recs) > 0 and len(records) > 0:
                # Assume that extra attributes are same for each record (of the word):
                # therefore, carry over attribute values from the first record
                first_old_rec = records[0]
                for rec in rewritten_recs:
                    for extra_attr in extra_attributes:
                        # Note: carry over the extra attribute value only when 
                        # the record was changed (so that the attribute is missing 
                        # from the record)
                        if extra_attr not in rec:
                            rec[extra_attr] = first_old_rec[extra_attr]
            
            # C) Convert records back to spans
            #    Add IGNORE_ATTR
            ambiguous_span = Span(base_span=morph_spans[morph_span_id].base_span, layer=layers[self.output_layer])

            record_added = False
            for rec in rewritten_recs:
                if not rec:
                    # Skip if a record was deleted
                    continue
                # Carry over attributes
                for attr in current_attributes:
                    if attr in ['start', 'end', 'text']:
                        continue
                    attr_value = rec[attr] if attr in rec else None
                    if attr == 'root_tokens':
                        # make it hashable for Span.__hash__
                        rec[attr] = tuple(attr_value)
                    elif attr == IGNORE_ATTR:
                        rec[attr] = False
                    else:
                        rec[attr] = attr_value
                # Add record as an annotation
                rec = {attr: rec[attr] for attr in ambiguous_span.layer.attributes}
                ambiguous_span.add_annotation(Annotation(ambiguous_span, **rec))
                record_added = True

            # C.2) If no records were added (all were deleted),
            #      then add an empty record (unknown word)
            if not record_added:
                empty_morph_record = \
                    _create_empty_morph_record( word=word, \
                        layer_attributes = current_attributes )
                # Add ignore attribute
                empty_morph_record[IGNORE_ATTR] = False
                # Carry over extra attributes
                if extra_attributes and len(morph_spans[morph_span_id].spans) > 0:
                    # Assume that extra attributes are same for each sub-span (of the word):
                    # therefore, carry over attribute values from the first span
                    first_span = morph_spans[morph_span_id].spans[0]
                    first_span_rec = _span_to_records_excl(first_span, [IGNORE_ATTR])
                    for extra_attr in extra_attributes:
                        empty_morph_record[extra_attr] = first_span_rec[extra_attr]
                empty_morph_record = \
                    {attr: empty_morph_record[attr] for attr in ambiguous_span.layer.attributes}
                # Add the new annotation
                ambiguous_span.add_annotation(Annotation(ambiguous_span, **empty_morph_record))
            
            # D) Rewrite the old span with new one
            morph_spans[morph_span_id] = ambiguous_span
            # Advance in the old "morph_analysis" layer
            morph_span_id += 1

    # ========================================================================
    #   Corrections for number analyses (from VabamorfCorrectionRewriter)
    # ========================================================================

    @staticmethod
    def load_number_analysis_rules( csv_file:str ):
        '''Loads number analysis corrections from an input CSV file.
           Note: if a cached version of the file exists (a .pickle file) and 
           it is up to date, then loads the cached version, otherwise, loads 
           the csv file, and creates the cached version for the next loading.
        '''
        cache = csv_file + '.pickle'
        if not os.path.exists(cache) or os.stat(cache).st_mtime < os.stat(csv_file).st_mtime:
            df = read_csv(csv_file, na_filter=False, index_col=False)
            rules = defaultdict(dict)
            for _, r in df.iterrows():
                if r.suffix not in rules[r.number]:
                    rules[r.number][r.suffix] = []
                rules[r.number][r.suffix].append({'partofspeech': r.pos, 'form': r.form, 'ending':r.ending})
            with open(cache, 'wb') as out_file:
                pickle.dump(rules, out_file)
            return rules
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
        m = re.match('-?(\d+\.?)-?(\D*)$', token_str)
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
