#
#  Provides post-corrections after Vabamorf-based morphological 
#  analysis.
#  These post-corrections should be applied before morphological 
#  disambiguation.
# 
import regex as re

from estnltk.text import Span, Layer, Text
from estnltk.taggers import Tagger
from estnltk.taggers.morf import VabamorfTagger, IGNORE_ATTR



class PostMorphAnalysisTagger(Tagger):
    description   = "Provides corrections to morphological analysis layer. "+\
                    "This tagger should be applied before morphological disambiguation."
    layer_name    = None
    attributes    = ('lemma', 'root', 'root_tokens', 'ending', 'clitic', 'form', 'partofspeech', IGNORE_ATTR)
    depends_on    = None
    configuration = None

    def __init__(self,
                 layer_name='morph_analysis', \
                 ignore_emoticons:bool=True, \
                 ignore_xml_tags:bool=True, \
                 fix_names_with_initials:bool=True, \
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
        """
        self.kwargs = kwargs
        self.layer_name = layer_name
       
        self.configuration = {'ignore_emoticons':ignore_emoticons,\
                              'ignore_xml_tags':ignore_xml_tags,\
                              'fix_names_with_initials':fix_names_with_initials,\
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
        


    def tag(self, text: Text, return_layer=False) -> Text:
        """Provides corrections on morphological analyses of 
        given Text object.
        
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
        assert IGNORE_ATTR in text[self.layer_name].attributes
        
        # Take attributes from the input layer
        current_attributes = text[self.layer_name].attributes
        
        # --------------------------------------------
        #   Mark specific compound tokens as to be 
        #   ignored in future analysis
        # --------------------------------------------
        self._ignore_specific_compound_tokens( text )

        # --------------------------------------------
        #   Provide fixes based on compound tokens
        # --------------------------------------------
        self._fix_based_on_compound_tokens( text )

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
        comp_token_id = 0
        for spanlist in text.morph_analysis.spans:
            if comp_token_id < len(text['compound_tokens'].spans):
                comp_token = text['compound_tokens'].spans[comp_token_id]
                if (comp_token.start == spanlist.start and \
                    spanlist.end == comp_token.end):
                    ignore_spans = False
                    # Found matching compound token
                    if self.configuration['fix_names_with_initials'] and \
                       'name_with_initial' in comp_token.type:
                        for span in spanlist:
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
                    comp_token_id += 1
            else:
                # all compound tokens have been exhausted
                break


# =================================
#    Helper functions
# =================================
    
def _convert_to_uppercase( matchobj ):
    '''Converts second group of matchobj to uppercase, and 
       returns a concatenation of first and second group. '''
    return matchobj.group(1)+matchobj.group(2).upper()
