#
#  Cuts the input Text object into a smaller Text by 
#  leaving out all spans from the syntax_ignore layer.
#  
#  Optionally, adds a words layer to the cut Text 
#  which has words' start & end indexes on the original 
#  (uncut) Text object, allowing to trace words' 
#  locations in the original Text.
#  
#  Use this class to as a preprocessor to create a 
#  syntactically analysable Text without the 
#  syntax_ignore text regions.
#
#  Some insipration from:
#  https://github.com/estnltk/syntax_experiments/tree/syntax_consistency/syntax_cutter_library
#
from estnltk import Text, Layer

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
        # Validate that syntax_ignore layer does not have any ovelapping spans
        syntax_ignore_layer = text[self.input_syntax_ignore_layer]
        for sid1, span_a in enumerate(syntax_ignore_layer):
            for sid2 in range(sid1+1, len(syntax_ignore_layer)):
                span_b = syntax_ignore_layer[sid2]
                # Check for overlap between spans
                if (span_a.start <= span_b.start <= span_b.end <= span_a.end or \
                    span_b.start < span_a.end < span_b.end or \
                    span_b.start < span_a.start < span_b.end):
                    raise ValueError(('(!) Unexpected overlapping spans in '+\
                                      'syntax_ignore layer:\nA: {!r}\nB: {!r}').format(span_a, 
                                                                                       span_b))
        # Collects parts of the new text string and
        # corresponding words layer
        old_words_layer = text[self.input_words_layer]
        old_text_str = text.text
        new_text_str = []
        new_word_annotations = []
        last_word_id = 0
        start = 0
        for ignore_span in syntax_ignore_layer:
            assert start <= ignore_span.start
            prev_region = new_text_str[-1] if len(new_text_str) > 0 else ''
            new_region  = old_text_str[start:ignore_span.start]
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
                       word_span.end < ignore_span.start:
                        annotation = {'original_start': word_span.start,
                                      'original_end': word_span.end,
                                      'original_index': last_word_id,
                                      'start': _base_len + (word_span.start-start),
                                      'end':   _base_len + (word_span.end-start)}
                        new_word_annotations.append( annotation )
                    if word_span.start > ignore_span.start or \
                       word_span.end > ignore_span.start:
                        # Stop if word falls out of the region
                        break
                    last_word_id += 1
            # new region start
            start = ignore_span.end
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
                        new_word_annotations.append( annotation )
                    last_word_id += 1
        # Construct new Text object
        new_text = Text(''.join(new_text_str))
        if self.add_words_layer:
            new_words_layer = \
                Layer('words', attributes=('original_start', 'original_end', 'original_index'))
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
                new_words_layer.add_annotation( (new_start, new_end), 
                                                        {'original_start': old_start,
                                                         'original_end':   old_end,
                                                         'original_index': old_index} )
            new_text.add_layer( new_words_layer )
        return new_text
