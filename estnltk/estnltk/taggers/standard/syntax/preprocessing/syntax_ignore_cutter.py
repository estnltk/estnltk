#
#  SyntaxIgnoreCutter cuts the input Text object into 
#  a smaller Text by leaving out all spans from the 
#  syntax_ignore layer.
#  
#  Optionally, adds a words layer to the cut Text 
#  which has words' start & end indexes on the original 
#  (uncut) Text object, allowing to trace words' 
#  locations in the original Text. This can be used by 
#  the function add_syntax_layer_from_cut_text (also below)
#  to carry over syntax layer from the cut text to
#  the original text.
#  
#  Use SyntaxIgnoreCutter to as a preprocessor to create 
#  a syntactically analysable Text without the syntax_ignore 
#  text regions.
#  Use add_syntax_layer_from_cut_text to carry syntax layer
#  back to the original text after analysis.
#
#  Some insipration from:
#  https://github.com/estnltk/syntax_experiments/tree/syntax_consistency/syntax_cutter_library
#
from estnltk import Text, Layer
from estnltk.common import _get_word_texts

class SyntaxIgnoreCutter:
    """Cuts Text object into a smaller Text by leaving out 
    all spans of the syntax_ignore layer."""


    def __init__(self, input_syntax_ignore_layer:str='syntax_ignore',
                       input_words_layer:str='words',
                       output_words_layer:str='words',
                       add_words_layer:bool=True,
                       pad_segments_without_ws:bool=True,
                       padding_str:str=' '):
        """Initializes SyntaxIgnoreCutter.
        
        Parameters
        ----------
        input_syntax_ignore_layer: str (default: 'syntax_ignore')
            Name of the syntax_ignore in the input Text object.
            This is the layer used as a guide on cutting the 
            Text object.
        
        input_words_layer: str (default: 'words')
            Name of the words layer in the input Text object;

        output_words_layer: str (default: 'words')
            Name of the words layer in the output Text object;
        
        add_words_layer: bool (default: True)
            Whether the output Text should have a words layer 
            with extra start & end indexes referring to the 
            original (uncut) Text object;
        
        pad_segments_without_ws: bool (default: True)
            Whether the cutting process should pad consecutive 
            text segments with whitespace (the padding strings) 
            in case the consecutive segments do not have white-
            space at their end/start.
        
        padding_str:str (default: ' ')
            Padding string used when pad_segments_without_ws is 
            set. Normally, this should be a whitespace string. 
        """
        # Set input/output layer names
        self.input_syntax_ignore_layer = input_syntax_ignore_layer
        self.input_words_layer         = input_words_layer
        self.output_words_layer        = output_words_layer
        # Configuration
        self.add_words_layer = add_words_layer
        self.pad_segments_without_ws = pad_segments_without_ws
        self.padding_str = padding_str

    def _get_word_normalized_form(self, word: 'Span'):
        """A hack for properly retrieving a list of normalized_form 
           values for a word span.
           This should handle properly both the current format and 
           also some old and obscure formats, which some datasets
           are using.
        """
        norm_form = _get_word_texts( word )
        if len(norm_form) == 1 and norm_form[0] == word.text:
            norm_form = [None]
        return norm_form

    def cut(self, text: Text):
        """Cuts the input Text object into a smaller Text 
        by leaving out all text spans of the syntax_ignore 
        layer. 
        
        Parameters
        ----------
        text: Text
           Text object which will be cut;
        """
        # Validate layers of the input text
        if self.input_syntax_ignore_layer not in text.layers:
            raise Exception(('(!) Text object is missing required {!r} layer.'+\
                             '').format(self.input_syntax_ignore_layer))
        if self.input_words_layer not in text.layers:
            raise Exception(('(!) Text object is missing required {!r} layer.'+\
                             '').format(self.input_words_layer))
        # Detect ovelapping spans from the syntax_ignore layer
        syntax_ignore_layer = text[self.input_syntax_ignore_layer]
        overlapping_ignore_spans = {}
        for sid1, span_a in enumerate(syntax_ignore_layer):
            for sid2 in range(sid1+1, len(syntax_ignore_layer)):
                span_b = syntax_ignore_layer[sid2]
                # Check for overlap between spans
                if (span_a.start <= span_b.start <= span_b.end <= span_a.end or \
                    span_b.start < span_a.end < span_b.end or \
                    span_b.start < span_a.start < span_b.end):
                    if sid1 not in overlapping_ignore_spans:
                        overlapping_ignore_spans[sid1] = []
                    overlapping_ignore_spans[sid1].append( (sid2, span_b) )
                    if sid2 not in overlapping_ignore_spans:
                        overlapping_ignore_spans[sid2] = []
                    overlapping_ignore_spans[sid2].append( (sid1, span_a) )
        # Collects parts of the new text string and
        # corresponding words layer
        old_words_layer = text[self.input_words_layer]
        old_text_str = text.text
        new_text_str = []
        new_word_annotations = []
        last_word_id = 0
        start = 0
        skip_ignore_spans = set()
        for sid, ignore_span in enumerate(syntax_ignore_layer):
            if sid in skip_ignore_spans:
                continue
            ignore_span_start = ignore_span.start
            ignore_span_end   = ignore_span.end
            # In case there is an overlap between ignore spans,
            # take the largest stretch of overlapping spans
            if sid in overlapping_ignore_spans:
                span_indexes = []
                for (sid2, ignore_span2) in overlapping_ignore_spans[sid]:
                    # Get indexes
                    span_indexes.append( ignore_span2.start )
                    span_indexes.append( ignore_span2.end )
                    # Skip the overlapping span in future
                    skip_ignore_spans.add(sid2)
                span_indexes.append( ignore_span.start )
                span_indexes.append( ignore_span.end )
                span_indexes = sorted(span_indexes, reverse=False)
                assert span_indexes[0] <= span_indexes[-1]
                # Take min/max indexes as region's boundaries
                ignore_span_start = span_indexes[0]
                ignore_span_end   = span_indexes[-1]
            assert start <= ignore_span_start
            prev_region = new_text_str[-1] if len(new_text_str) > 0 else ''
            new_region  = old_text_str[start:ignore_span_start]
            # Check if there is a whitespace between two regions
            if self.pad_segments_without_ws:
                whitespace_requirements_met = \
                    len(prev_region) == 0 or \
                    (len(prev_region)>0 and prev_region[-1].isspace()) or \
                    (len(new_region)>0 and new_region[0].isspace())
                if not whitespace_requirements_met:
                    # pad the area between two text regions with whitespace
                    new_region = self.padding_str + new_region
            # Find region's length so far
            _base_len = sum( [len(s) for s in new_text_str] )
            new_text_str.append( new_region )
            # Collect word annotations inside the region
            if self.add_words_layer:
                while last_word_id < len(old_words_layer):
                    word_span = old_words_layer[last_word_id]
                    # Record words falling inside the region
                    if start <= word_span.start and \
                       word_span.end < ignore_span_start:
                        annotation = {'original_start': word_span.start,
                                      'original_end': word_span.end,
                                      'original_index': last_word_id,
                                      'start': _base_len + (word_span.start-start),
                                      'end':   _base_len + (word_span.end-start)}
                        if 'normalized_form' in old_words_layer.attributes:
                            annotation['normalized_form'] = \
                                self._get_word_normalized_form( word_span )
                        new_word_annotations.append( annotation )
                    if word_span.start > ignore_span_start or \
                       word_span.end > ignore_span_start:
                        # Stop if word falls out of the region
                        break
                    last_word_id += 1
            # new region start
            start = ignore_span_end
        # Add the remaining text (after ignore_spans have been exhausted)
        if start < len(old_text_str):
            prev_region = new_text_str[-1] if len(new_text_str) > 0 else ''
            new_region  = old_text_str[start:len(old_text_str)]
            # Check if there is a whitespace between two regions
            if self.pad_segments_without_ws:
                whitespace_requirements_met = \
                    len(prev_region) == 0 or \
                    (len(prev_region)>0 and prev_region[-1].isspace()) or \
                    (len(new_region)>0 and new_region[0].isspace())
                if not whitespace_requirements_met:
                    # pad the area between two text regions with whitespace
                    new_region = self.padding_str + new_region
            # Find region's length so far
            _base_len = sum( [len(s) for s in new_text_str] )
            new_text_str.append( new_region )
            # Collect word annotations inside the region
            if self.add_words_layer:
                while last_word_id < len(old_words_layer):
                    word_span = old_words_layer[last_word_id]
                    # Record words falling inside the region
                    if start <= word_span.start and \
                       word_span.end <= len(old_text_str):
                        annotation = {'original_start': word_span.start,
                                      'original_end': word_span.end,
                                      'original_index': last_word_id,
                                      'start': _base_len + (word_span.start-start),
                                      'end':   _base_len + (word_span.end-start)}
                        if 'normalized_form' in old_words_layer.attributes:
                            annotation['normalized_form'] = \
                                self._get_word_normalized_form( word_span )
                        new_word_annotations.append( annotation )
                    last_word_id += 1
        # Construct new Text object
        new_text = Text(''.join(new_text_str))
        if self.add_words_layer:
            new_attributes = ('original_start', 'original_end', 'original_index')
            if 'normalized_form' in old_words_layer.attributes:
                new_attributes = ('normalized_form',) + new_attributes
            new_words_layer = \
                Layer( self.output_words_layer, 
                       attributes=new_attributes, 
                       text_object=new_text,
                       ambiguous='normalized_form' in new_attributes )
            for a in new_word_annotations:
                old_start = a['original_start']
                old_end   = a['original_end']
                old_index = a['original_index']
                new_start = a['start']
                new_end   = a['end']
                # Sanity check: span on the old text should match with 
                # the span on the new text
                old_span_str = old_text_str[old_start:old_end]
                new_span_str = new_text.text[new_start:new_end]
                assert old_span_str == new_span_str, \
                    ('Mismatching spans of the input text and the cut text {!r} vs {!r} '+\
                     'at the input text location {!r}').format(old_span_str, 
                                                               new_span_str, 
                                                               (old_start,old_end))
                # Add annotation
                if new_words_layer.ambiguous:
                    # with 'normalized_form'
                    assert 'normalized_form' in a.keys()
                    for normalized_form in a['normalized_form']:
                        new_words_layer.add_annotation( (new_start, new_end), 
                                                           {'original_start':  old_start,
                                                            'original_end':    old_end,
                                                            'original_index':  old_index,
                                                            'normalized_form': normalized_form} )
                else:
                    # without 'normalized_form'
                    new_words_layer.add_annotation( (new_start, new_end), 
                                                            {'original_start': old_start,
                                                             'original_end':   old_end,
                                                             'original_index': old_index} )
            # Attach layer
            new_text.add_layer( new_words_layer )
        return new_text




def add_syntax_layer_from_cut_text(original_text: Text, cut_text: Text, syntax_layer: str, 
                                   original_words_layer: str='words',
                                   cut_words_layer: str='words',
                                   add_empty_spans: bool= False):
    """Carries over syntactic analysis layer from cut_text to original_text. 
       Returns original_text with the attached syntax_layer.
       
       Use this function for carrying syntax layer back to the original text 
       after applying SyntaxIgnoreTagger, SyntaxIgnoreCutter and syntactic 
       analysis.
       
       Parameters
       ----------
       original_text: Text
           Text object that was cut with SyntaxIgnoreCutter (resulting in cut_text).
       cut_text: Text
           Text object resulting from original_text being cut with SyntaxIgnoreCutter.
       syntax_layer: str
           Name of the syntactic analysis layer to be carried over from the cut_text
           to the original_text.
       original_words_layer: str (default: 'words')
           Name of the words layer in the original_text. This will be the parent of 
           the syntax_layer in the original_text.
       cut_words_layer: str (default: 'words')
           Name of the words layer in the cut_text. This layer must have extra attributes
           'original_start', 'original_end', 'original_index' which are used to determine
           and verify the words' locations in the the original_text.
       add_empty_spans: bool (default: False)
           If set, then empty syntax_layer spans/annotations are added for words in the 
           original_text that were left out from the cut_text. 
           Otherwise, ignorable words will not appear in the syntax_layer at all.
    """
    # Validate inputs
    if syntax_layer not in cut_text.layers:
        raise Exception('(!) Input cut_text is missing layer {!r}'.format(syntax_layer))
    if cut_words_layer not in cut_text.layers:
        raise Exception('(!) Input cut_text is missing layer {!r}'.format(cut_words_layer))
    if original_words_layer not in original_text.layers:
        raise Exception('(!) Input original_text is missing layer {!r}'.format(original_words_layer))
    if len(cut_text[syntax_layer]) != len(cut_text[cut_words_layer]):
        raise Exception('(!) Layers {!r} and {!r} have unexpectedly different sizes: {} vs {}'.format( \
                                cut_text[syntax_layer],
                                cut_text[cut_words_layer],
                                len(cut_text[syntax_layer]), 
                                len(cut_text[cut_words_layer]) ))
    missing_attribs = []
    for attr in ['original_start', 'original_end', 'original_index']:
        if attr not in cut_text[cut_words_layer].attributes:
            missing_attribs.append( attr )
    if missing_attribs:
        raise Exception('(!) Layer {!r} in the cut_text is missing attributes {!r}'.format(cut_words_layer, \
                                                                                           missing_attribs))
    # Create a new syntax layer based on the syntax layer of the cut_text
    in_syntax_layer = cut_text[syntax_layer]
    # Attributes for the new layer: take only the primary attributes
    out_attributes = \
        [a for a in in_syntax_layer.attributes if a not in in_syntax_layer.secondary_attributes]
    new_layer = Layer( name=in_syntax_layer.name,
                       attributes=out_attributes,
                       text_object=original_text,
                       parent=original_words_layer,
                       enveloping=None,
                       ambiguous=in_syntax_layer.ambiguous,
                       default_values=in_syntax_layer.default_values.copy() )
    # Index syntax layer: mark which syntax spans correspond to which words in the original_text
    syntax_layer_index = {}
    for sid, syntax_span in enumerate(in_syntax_layer):
        word_span = cut_text[cut_words_layer][sid]
        original_start = word_span.annotations[0]['original_start']
        original_end   = word_span.annotations[0]['original_end']
        original_index = word_span.annotations[0]['original_index']
        # Sanity check
        original_span = original_text.text[original_start:original_end]
        if original_span != syntax_span.text:
            raise Exception(('Mismatching spans of the original text and the cut text {!r} vs {!r} '+\
                             'at the original text location {!r}').format(original_span, 
                                                                      syntax_span.text, 
                                                                      (original_start, original_end)))
        syntax_layer_index[original_index] = syntax_span
    syntax_layer_id = 0
    for wid, word_span in enumerate(original_text[original_words_layer]):
        if wid in syntax_layer_index.keys():
            syntax_span = syntax_layer_index[wid]
            syntax_annotations = syntax_span.annotations[0]
            new_layer.add_annotation( word_span.base_span, \
                { a: syntax_annotations[a] for a in new_layer.attributes } )
        else:
            if add_empty_spans:
                # Add None values in place of ignored words (optional)
                new_layer.add_annotation( word_span.base_span, \
                    { a: None for a in new_layer.attributes } )
    original_text.add_layer( new_layer )
    return original_text