# -*- coding: utf-8 -*-
""" 
    Provides a pretty-printer method that can be used for graphically formatting annotated 
    texts in terminal. Currently allows to surround annotations with brackets, to underline 
    annotations, and to change color of font for annotations;
    
    Usage example::
    
        from estnltk import Text
        from estnltk.prettyprinter.terminalprettyprinter import tprint
        text = Text('Mees, keda me otsisime, oli sealt juba läinud.').tag_verb_chains()
        
        # Print text in a manner that clauses are surrounded with brackets and verb chains 
        # are underlined
        tprint( text, ['clauses','verb_chains'],[{'bracket':True},{'underline':True}] )
    
    Note that coloring and underlining visualizations require that the  terminal  supports 
    ANSI escape codes for formatting the output. Not all terminals support such formatting,
    e.g. Python's IDLE environment lacks the support. In this case, the only viable 
    visualization option is to surround the annotations with brackets, and other options 
    will produce unexecuted escape sequences into the textual output.
    
"""
from __future__ import unicode_literals, print_function, absolute_import

from ..text  import Text
from ..names import TEXT, START, END
from .extractors import texts_simple, texts_multi

# ================================================================
#    Producing a tag (an ANSI escape code) for coloring a text
# ================================================================

def _get_ANSI_colored_font( color ):
    ''' Returns an ANSI escape code (a string) corresponding to switching the font
        to given color, or None, if the given color could not be associated with 
        the available colors.
        
        See also:
          https://en.wikipedia.org/wiki/ANSI_escape_code#Colors
          http://stackoverflow.com/questions/287871/print-in-terminal-with-colors-using-python
    '''
    color = (color.replace('-','')).lower()
    #
    #   Bright colors:
    #
    if color == 'white':
        return '\033[97m'
    elif color in ['cyan', 'aqua']:
        return '\033[96m'
    elif color in ['purple', 'magneta', 'fuchsia']:
        return '\033[95m'
    elif color == 'blue':
        return '\033[94m'
    elif color in ['yellow', 'gold']:
        return '\033[93m'
    elif color in ['green', 'lime']:
        return '\033[92m'
    elif color == 'red':
        return '\033[91m'
    #
    #   Dark colors:
    #
    elif color in ['grey', 'gray', 'silver']:
        return '\033[37m'
    elif color in ['darkcyan', 'teal']:
        return '\033[36m'
    elif color in ['darkpurple', 'darkmagneta']:
        return '\033[35m'
    elif color in ['darkblue', 'navy']:
        return '\033[34m'
    elif color in ['darkyellow', 'olive']:
        return '\033[33m'
    elif color == 'darkgreen':
        return '\033[32m'
    elif color in ['darkred', 'maroon']:
        return '\033[31m'
    return None

# ================================================================
#    Constructing indexes of formatted annotations
# ================================================================

def _construct_start_index(text, layer, markup_settings, spansStartingFrom=None):
    ''' Creates an index which stores all annotations of given text layer,
        indexed by the start position of the annotation (annotation[START]).
        Alternatively, if the index spansStartingFrom is already provided
        as an input argument, obtains annotation information from the given 
        text layer, and stores into the index;
        
        The method also creates an ( ANSI-terminal compatible ) mark-up of 
        the annotations (generates start and end tags), following the 
        specification in markup_settings. The markup_settings should be a
        dict, setting at least one of the following visualisation options:
          * 'bracket' : True -- annotations will be surrounded with brackets; 
                                This works in any terminal;
          * 'underline' : True -- annotations will be underlined; This works in 
                                  an ANSI compatible terminal;
          * 'color' : ('red', 'green', 'blue' etc. ) -- annotated text will be 
                                                        displayed in given color; 
                                                        this works in an ANSI 
                                                        compatible terminal;
        
        Each start position (in the index) is associated with a list of 
        annotation objects (annotations starting from that position).
        An annotation object is a list containing the following information:
         *) START position (of the annotation),
         *) END position (of the annotation),
         *) layer (name), 
         *) startTags -- graphic or textual formatting of the start tag, 
         *) endTags -- graphic or textual formatting of the end tag, 
         *) graphicFormatting -- boolean (whether graphic formatting was used?), 
         *) bracketing -- boolean (whether bracketing was used?), 
       
        Multiple annotation objects starting from the same position are sorted by 
        their length: longer annotations preceding the shorter ones;
       
        The method returns created (or augmented) index (a dict object indexed 
        by START positions);
    '''
    if not markup_settings or not isinstance(markup_settings, dict):
       raise Exception('Error: markup_settings should be a dict containing markup specification;')
    # ----------------------------
    # 1) Construct start and end tags, considering the formatting settings
    startTags = ''
    endTags   = ''
    graphicFormatting = False
    bracketing        = False
    # -- Underlining
    if ('u' in markup_settings and markup_settings['u']) or \
       ('underline' in markup_settings and markup_settings['underline']):
       startTags += '\033[4m'
       endTags   += '\033[0m'
       graphicFormatting = True
    colorName = markup_settings['c'] if 'c' in markup_settings else None
    colorName = markup_settings['color'] if 'color' in markup_settings else colorName
    # -- Coloring
    if colorName:
       color = _get_ANSI_colored_font( colorName )
       if color:
          startTags += color
          endTags   += '\033[0m'
          graphicFormatting = True
       else:
          raise Exception('Unknown color:', colorName)
    # -- Bracketing
    if ('b' in markup_settings and markup_settings['b']) or \
       ('bracket' in markup_settings and markup_settings['bracket']):
       startTags += '['
       # Add ending bracket before graphics ends (otherwise the 
       # graphics have no effect on the ending bracket)
       endTags    = ']'+endTags
       bracketing = True
    # Hack: if both bracketing and graphic formatting are used, add graphic
    #       formatting before the closing bracket of the endTag (to ensure
    #       that graphic formatting of the ending bracket is not overwritten
    #       mistakenly);
    if graphicFormatting and bracketing:
       startTags2 = startTags.rstrip('[')
       endTags    = startTags2+endTags

    # ----------------------------
    # 2) Get extractor for the elements of given layer
    # >>> The following code borrows from estnltk.prettyprinter.marker :
    # decide which extractor to use
    # first just assume we need to use a multi layer text extractor
    extractor = lambda t: texts_multi(t, layer)
    # if user has specified his/her own callable, use it
    if hasattr(layer, '__call__'):
        extractor = layer
    elif text.is_simple(layer):
        # the given layer is simple, so use simple text extractor
        extractor = lambda t: texts_simple(t, layer)
    # >>>

    # ----------------------------
    # 3) Store an annotation for each span of given layer
    if not spansStartingFrom:
        spansStartingFrom = {}
    for elem in extractor(text):
        if elem[START] not in spansStartingFrom:
           spansStartingFrom[elem[START]] = []
        span1 = [elem[START], elem[END], layer, startTags, endTags, graphicFormatting, bracketing]
        # Insert the span into the index
        if not spansStartingFrom[elem[START]]:
           spansStartingFrom[elem[START]].append( span1 )
        else:
           # Make sure that spans are inserted in the order of decreasing length: 
           #  longer spans preceding the shorter ones;
           inserted = False
           for i in range( len(spansStartingFrom[elem[START]]) ):
               span2 = spansStartingFrom[elem[START]][i]
               # If an existing span is shorter than the current span, insert the
               # current span before the existing span ...
               if span1[1] > span2[1]:
                  spansStartingFrom[elem[START]].insert( i, span1 )
                  inserted = True
                  break
               elif span1[1] == span2[1] and span1[2] < span2[2]:
                  # If both spans have equal length, order the spans in the alphabetical
                  # order of layer names:
                  spansStartingFrom[elem[START]].insert( i, span1 )
                  inserted = True
                  break
           if not inserted:
               spansStartingFrom[elem[START]].append(span1)
    return spansStartingFrom


def _construct_end_index( spansStartingFrom ):
   ''' Creates an index which stores all annotations (from spansStartingFrom) 
       by their end position in text (annotation[END]).
       
       Each start position (in the index) is associated with a list of 
       annotation objects (annotations ending at that position).
       An annotation object is also a list containing the following information:
        *) endTags -- graphic or textual formatting of the end tag,
        *) START position (of the annotation);
        *) layer name;
         
       Multiple annotation objects ending at the same position are sorted by 
       their length: shorter annotations preceding the longer ones;
   '''
   endIndex = {}
   for i in spansStartingFrom:
       for span1 in spansStartingFrom[i]:
           # keep the record of endTags, start positions (for determining the length)
           # and layer names
           endSpan1 = [ span1[4], span1[0], span1[2] ]
           endLoc1 = span1[1]
           if endLoc1 not in endIndex:
              endIndex[endLoc1] = []
              endIndex[endLoc1].append( endSpan1 )
           else:
              # Make sure that spans are inserted in the order of increasing length: 
              #   shorter spans preceding the longer ones;
              inserted = False
              for i in range( len(endIndex[endLoc1]) ):
                  endSpan2 = endIndex[endLoc1][i]
                  # If an existing span is longer than the current span, insert the
                  # current span before the existing span ...
                  if endSpan2[1] < endSpan1[1]:
                     endIndex[endLoc1].insert( i, endSpan1 )
                     inserted = True
                     break
                  elif endSpan2[1] == endSpan1[1] and endSpan2[2] < endSpan1[2]:
                     # If both spans have equal length, order the spans in the 
                     # alphabetical order of layer names:
                     endIndex[endLoc1].insert( i, endSpan1 )
                     inserted = True
                     break
              if not inserted:
                  endIndex[endLoc1].append( endSpan1 )
   return endIndex


def _fix_overlapping_graphics( spansStartingFrom ):
    ''' Provides a fix for overlapping annotations that are formatted graphically
        (underlined or printed in non-default color).
        
        If two graphically formatted annotations overlap, and if one annotation,
        say A, ends within another annotation, say B, then ending of graphics of A
        also causes graphics of B to end, and so, the end of A should restart the
        the graphics of B for a continuous visualisation;
        This method modifies ending tags in a way that annotations ending within
        other annotations will also contain restarts of the corresponding (super)-
        annotations, so that a continuous formatting is ensured.
    '''
    for startIndex in sorted( spansStartingFrom.keys() ):
        for span1 in spansStartingFrom[startIndex]:
            # If the span is not graphic, we don't have no worries - we can just skip it
            if not span1[5]:
               continue
            # Otherwise: check for other graphic spans that overlap with the given span
            span1Start = span1[0]
            span1End   = span1[1]
            for i in range( span1Start, span1End ):
                if i in spansStartingFrom:
                   for span2 in spansStartingFrom[i]:
                       span2Start = span2[0]
                       span2End   = span2[1]
                       # If the spans are not the same, and the span2 is graphic
                       if span2 != span1 and span2[5]:
                          # if the overlapping graphic span ends before the current span,
                          # we have to restart the graphic formatting of given span after 
                          # the end of the overlapping span
                          if span2End <= span1End:
                             if not span1[6]:
                                # If span1 is not bracketed, just add it at the end of
                                # the overlapping span
                                span2[4] += span1[3]
                             else:
                                # If span1 is bracketed, add it at the end of the 
                                # overlapping span without brackets
                                wb = span1[3].rstrip('[')
                                span2[4] += wb

# ================================================================
#    Constructing the formatted output
# ================================================================

default_markup_settings = [ \
    {'b':True, 'c':'green'}, \
    {'b':True, 'c':'cyan'}, \
    {'b':True, 'c':'yellow'}, \
    {'b':True, 'c':'white'}, \
    {'b':True, 'c':'purple'}, \
    {'b':True, 'c':'blue'}, \
    {'b':True, 'c':'red'}, \
    {'b':True, 'c':'teal'}, \
    {'b':True, 'c':'darkmagneta'}, \
    {'b':True, 'c':'navy'}, \
    {'b':True, 'c':'olive'}, \
    {'b':True, 'c':'maroon'}, \
]

def _preformat( text, layers, markup_settings = None ):
   ''' Formats given text, adding a special ( ANSI-terminal compatible ) markup
       to the annotations of given layers, and returns formatted text as a
       string.
       *) layers is a list containing names of the layers to be preformatted in 
          the text (these layers must be present in Text);
       *) markup_settings should be a list containing annotation options for each
          layer: one dict with options per layer;
          One dict can contain the following visualization options:
          * 'bracket' : True -- annotations will be surrounded with brackets; This 
                                works in any terminal;
          * 'underline' : True -- annotations will be underlined; This works in ANSI 
                                  compatible terminal;
          * 'color' : ('red', 'green', 'blue' etc. ) -- annotated text will be 
                      displayed in given color; this works in ANSI compatible 
                      terminal;
       *) Alternatively, if markup_settings is undefined, up to 12 layers can be 
          visualized following the default settings;
        
       Parameters
       ----------
       text: Text
          a text object. Must contain given layers;
       layer: list of str
          list of layer names to be visualised;
       markup_settings: list of dict
          list of dictionaries containing user-defined visualization options;
          (one dict per layer)
        
       Returns
       -------
       text: str
          preformatted text, where elements of given layers have been marked up, using 
          an ANSI-terminal compatible markup;
   '''
   if markup_settings and len(layers) != len(markup_settings):
       raise Exception(' Input arguments layers and markup_settings should be equal size lists.')
   elif not markup_settings and len(layers) <= len(default_markup_settings):
       # Use default markup settings
       markup_settings = default_markup_settings[0:len(layers)]
   elif not markup_settings:
       raise Exception(' Input argument markup_settings not defined.')
   #
   # 1) Construct the index of annotations (for each layer); 
   #    Annotations are indexed by their start positions;
   #    The index also contains start and end tags of each annotation;
   spansStartingFrom = {}
   for i in range( len(layers) ):
       layer    = layers[i]
       settings = markup_settings[i]
       spansStartingFrom = _construct_start_index(text, layer, settings, spansStartingFrom)
   #
   # 2) Fix overlapping graphic annotations in the index
   #    (to ensure continuous formatting of annotations)
   _fix_overlapping_graphics( spansStartingFrom )
   #
   # 3) Index the annotations by their end positions
   endTags = _construct_end_index( spansStartingFrom )
   
   #
   # 4) Construct the output string
   return_str = []
   for i in range( len(text[TEXT]) ):
       c = text[TEXT][i]
       emptyTags = []
       if i in endTags:
          for tag in endTags[i]:
              if tag[1] != i:
                 # Non-empty tag
                 return_str.append( tag[0] )
              else:
                 # Empty tag
                 emptyTags.append( tag )
       if i in spansStartingFrom:
          for span in spansStartingFrom[i]:
              return_str.append( span[3] )
              if span[0] == span[1]:
                 # Empty tag: Add the closing tag
                 for emptyEndTag in emptyTags:
                     if span[2] == emptyEndTag[2]:
                        return_str.append( emptyEndTag[0] )
       return_str.append( c )
   if len(text[TEXT]) in spansStartingFrom:
       for span in spansStartingFrom[len(text[TEXT])]:
           return_str.append( span[3] )
   if len(text[TEXT]) in endTags:
       for tag in endTags[len(text[TEXT])]:
           return_str.append( tag[0] )
   # Hack: fix for a potential overflow / unclosed graphics
   if return_str and '\033' in return_str[-1] and \
      not return_str[-1].endswith('\033[0m'):
      return_str.append( '\033[0m' )
   return ''.join(return_str)


# ================================================================
# ================================================================
#    Main method : a pretty-printer for terminal
# ================================================================
# ================================================================

def tprint( text, layers, markup_settings = None ):
    ''' Formats given text, adding a special ( ANSI-terminal compatible ) markup
        to the annotations of given layers, and prints the formatted text to the 
        screen. 
        *) layers is a list containing names of the layers to be preformatted in 
           the text (these layers must be present in Text);
        *) markup_settings should be a list containing annotation options for each
           layer: one dict with options per layer;
           One dict can contain the following visualization options:
           * 'bracket' : True -- annotations will be surrounded with brackets; This 
                                 works in any terminal;
           * 'underline' : True -- annotations will be underlined; This works in ANSI 
                                   compatible terminal;
           * 'color' : ('red', 'green', 'blue' etc. ) -- annotated text will be 
                       displayed in given color; this works in ANSI compatible 
                       terminal;
        *) Alternatively, if markup_settings is undefined, up to 12 layers can be 
           visualized following the default settings;
        
        Parameters
        ----------
        text: Text
           a text object. Must contain given layers;
        layer: list of str
           list of layer names to be visualised;
        markup_settings: list of dict
           list of dictionaries containing user-defined visualization options;
           (one dict per layer)
    '''
    if markup_settings and len(layers) != len(markup_settings):
       raise Exception(' Input arguments layers and markup_settings should be equal size lists.')
    elif not markup_settings and len(layers) <= len(default_markup_settings):
       # Use a subset from default markup settings
       markup_settings = default_markup_settings[0:len(layers)]
    elif not markup_settings:
       raise Exception(' Input argument markup_settings not defined.')
    print( _preformat(text, layers, markup_settings=markup_settings) )


def preformat(text, layer, markup_settings):
    if isinstance(text, Text):
       # Backwards compatibility with the old version
       if isinstance(layer, str):
          if not markup_settings:
              return _preformat( text, [layer], markup_settings = None )
          elif markup_settings and isinstance(markup_settings, dict):
              return _preformat( text, [layer], markup_settings = [markup_settings] )
       elif isinstance(layer, list):
          if not markup_settings:
              return _preformat( text, layer, markup_settings = None )
          elif markup_settings:
              return _preformat( text, layer, markup_settings = markup_settings )
       else:
          raise Exception('Unexpected name of the layer: ', layer)
    else:
       raise Exception('Unexpected input text (should be an instance of Text): ', text)
    return None
