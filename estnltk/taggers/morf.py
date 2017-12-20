#
#  Provides Vabamorf-based morphological analysis and disambiguation.
#
#  VabamorfTagger can be used for end-to-end morphological processing.
#  Alternatively, the process can be broken down into substeps, using 
#  VabamorfAnalyzer and VabamorfDisambiguator.
# 

from estnltk.text import Span, SpanList, Layer, Text
from estnltk.taggers import Tagger
from estnltk.vabamorf.morf import Vabamorf
from estnltk.taggers.postanalysis_tagger import PostMorphAnalysisTagger

from estnltk.taggers.morf_common import DEFAULT_PARAM_DISAMBIGUATE, DEFAULT_PARAM_GUESS
from estnltk.taggers.morf_common import DEFAULT_PARAM_PROPERNAME, DEFAULT_PARAM_PHONETIC
from estnltk.taggers.morf_common import DEFAULT_PARAM_COMPOUND
from estnltk.taggers.morf_common import ESTNLTK_MORPH_ATTRIBUTES
from estnltk.taggers.morf_common import VABAMORF_ATTRIBUTES
from estnltk.taggers.morf_common import IGNORE_ATTR

from estnltk.taggers.morf_common import _get_word_text, _create_empty_morph_span
from estnltk.taggers.morf_common import _is_empty_span


class VabamorfTagger(Tagger):
    description   = "Tags morphological analysis on words. Uses Vabamorf's morphological analyzer and disambiguator."
    layer_name    = None
    attributes    = ESTNLTK_MORPH_ATTRIBUTES
    depends_on    = None
    configuration = None

    def __init__(self,
                 layer_name='morph_analysis',
                 postanalysis_tagger=PostMorphAnalysisTagger(),
                 **kwargs):
        """Initialize VabamorfTagger class.

        Note: Keyword arguments 'disambiguate', 'guess', 'propername',
        'phonetic' and 'compound' can be used to override the default 
        configuration of Vabamorf's morphological analyser. See the 
        description of VabamorfAnalyzer.tag method for details on
        configuration arguments.
        
        Parameters
        ----------
        layer_name: str (default: 'morph_analysis')
            Name of the layer where analysis results are stored.
        postanalysis_tagger: estnltk.taggers.Tagger (default: PostMorphAnalysisTagger())
            Tagger that is used to post-process "morph_analysis" layer after
            it is created (and before it is disambiguated).
            This tagger corrects morphological analyses, prepare morpho-
            logical analyses for disambiguation (if required) and fills in 
            values of extra attributes in morph_analysis Spans.
        """
        self.kwargs = kwargs
        self.layer_name = layer_name
       
        if postanalysis_tagger:
            # Check for Tagger
            assert isinstance(postanalysis_tagger, Tagger), \
                '(!) postanalysis_tagger should be of type estnltk.taggers.Tagger.'
            # Check for layer match
            assert hasattr(postanalysis_tagger, 'layer_name'), \
                '(!) postanalysis_tagger does not define layer_name.'
            assert postanalysis_tagger.layer_name == self.layer_name, \
                '(!) postanalysis_tagger should modify layer "'+str(self.layer_name)+'".'+\
                ' Currently, it modifies layer "'+str(postanalysis_tagger.layer_name)+'".'
            assert hasattr(postanalysis_tagger, 'attributes'), \
                '(!) postanalysis_tagger does not define any attributes.'
        self.postanalysis_tagger = postanalysis_tagger
        vm_instance = Vabamorf.instance()
        self.vabamorf_analyser      = VabamorfAnalyzer( vm_instance=vm_instance )
        self.vabamorf_disambiguator = VabamorfDisambiguator( vm_instance=vm_instance )
        

        self.configuration = {'postanalysis_tagger':self.postanalysis_tagger.__class__.__name__, }
        #                      'vabamorf_analyser':self.vabamorf_analyser.__class__.__name__,
        #                      'vabamorf_disambiguator':self.vabamorf_disambiguator.__class__.__name__ }
        self.configuration.update(self.kwargs)

        self.depends_on = ['words', 'sentences']


    def tag(self, text: Text, return_layer=False) -> Text:
        """Anayses given Text object morphologically. 
        
        Note: exact configuration of the analysis (e.g. 
        whether guessing of unknown words will be performed, 
        or whether analyses will be disambiguated) depends on 
        the initialization parameters of the class.
        
        Parameters
        ----------
        text: estnltk.text.Text
            Text object that is to be analysed morphologically.
            The Text object must have layers 'words', 'sentences'.
        return_layer: boolean (default: False)
            If True, then the new layer is returned; otherwise 
            the new layer is attached to the Text object, and the 
            Text object is returned;

        Returns
        -------
        Text or Layer
            If return_layer==True, then returns the new layer, 
            otherwise attaches the new layer to the Text object 
            and returns the Text object;
        """
        # Fetch parameters ( if missing, use the defaults )
        disambiguate = self.kwargs.get('disambiguate', DEFAULT_PARAM_DISAMBIGUATE)
        guess        = self.kwargs.get('guess',        DEFAULT_PARAM_GUESS)
        propername   = self.kwargs.get('propername',   DEFAULT_PARAM_PROPERNAME)
        phonetic     = self.kwargs.get('phonetic',     DEFAULT_PARAM_PHONETIC)
        compound     = self.kwargs.get('compound',     DEFAULT_PARAM_COMPOUND)
        # --------------------------------------------
        #   Morphological analysis
        # --------------------------------------------
        self.vabamorf_analyser.tag( text, \
                                    guess=guess,\
                                    propername=propername,\
                                    phonetic=phonetic, \
                                    compound=compound )
        morph_layer = text[self.layer_name]
        # --------------------------------------------
        #   Post-processing
        # --------------------------------------------
        if self.postanalysis_tagger:
            # Post-analysis tagger is responsible for either:
            # 1) Filling in extra_attributes in "morph_analysis" layer, or
            # 2) Making corrections in the "morph_analysis" layer, including:
            #    2.1) Creating new "morph_analysis" layer based on the existing 
            #         one, 
            #    2.1) Populating the new layer with corrected analyses,
            #    2.1) (if required) filling in extra_attributes in the new layer,
            #    2.2) Replacing the old "morph_analysis" in Text object with 
            #         the new one;
            self.postanalysis_tagger.tag(text)
        # --------------------------------------------
        #   Morphological disambiguation
        # --------------------------------------------
        if disambiguate:
            self.vabamorf_disambiguator.tag(text)
        # --------------------------------------------
        #   Return layer or Text
        # --------------------------------------------
        # Return layer
        if return_layer:
            delattr(text, self.layer_name) # Remove layer from the text
            return morph_layer
        # Layer is already attached to the text, return it
        return text


# ========================================================
#    Utils for converting Vabamorf dict <-> EstNLTK Span
# ========================================================

def _convert_morph_analysis_span_to_vm_dict( span ):
    ''' Converts a SpanList from the layer 'morph_analysis'
        into a dictionary object that has the structure
        required by the Vabamorf:
        { 'text' : ..., 
          'analysis' : [
             { 'root': ..., 
               'partofspeech' : ..., 
               'clitic': ... ,
               'ending': ... ,
               'form': ... ,
             },
             ...
          ]
        }
        Returns the dictionary.
    '''
    attrib_dicts = {}
    # Get lists corresponding to attributes
    for attr in VabamorfTagger.attributes:
        attrib_dicts[attr] = getattr(span, attr)
    # Rewrite attributes in Vabamorf's analysis format
    # Collect analysis dicts
    nr_of_analyses = len(attrib_dicts['lemma'])
    word_dict = { 'text' : span.text[0], \
                  'analysis' : [] }
    for i in range( nr_of_analyses ):
        analysis = {}
        for attr in attrib_dicts.keys():
            attr_value = attrib_dicts[attr][i]
            if attr == 'root_tokens':
                attr_value = list(attr_value)
            analysis[attr] = attr_value
        word_dict['analysis'].append(analysis)
    return word_dict


def _convert_vm_dict_to_morph_analysis_spans( vm_dict, word, \
                                              layer_attributes = None, \
                                              sort_analyses = True ):
    ''' Converts morphological analyses from the Vabamorf's 
        dictionary format to the EstNLTK's Span format, and 
        attaches the newly created span as a child of the 
        word.
        
        If sort_analyses=True, then analyses will be sorted 
        by root,ending,clitic,postag,form;
        
        Note: if word has no morphological analyses (e.g. it 
        is an unknown word), then returns an empty list.
        
        Returns a list of EstNLTK's Spans.
    '''
    spans = []
    current_attributes = \
        layer_attributes if layer_attributes else ESTNLTK_MORPH_ATTRIBUTES
    word_analyses = vm_dict['analysis']
    if sort_analyses:
        # Sort analyses ( to assure a fixed order, e.g. for testing purpose )
        word_analyses = sorted( vm_dict['analysis'], key = \
            lambda x: x['root']+x['ending']+x['clitic']+x['partofspeech']+x['form'], 
            reverse=False )
    for analysis in word_analyses:
        span = Span(parent=word)
        for attr in current_attributes:
            if attr in analysis:
                # We have a Vabamorf's attribute
                if attr == 'root_tokens':
                    # make it hashable for Span.__hash__
                    setattr(span, attr, tuple(analysis[attr]))
                else:
                    setattr(span, attr, analysis[attr])
            else:
                # We have an extra attribute -- initialize with None
                setattr(span, attr, None)
        spans.append(span)
    return spans


# ========================================================
#    Util for carrying over extra attributes from 
#          old EstNLTK Span to the new EstNLTK Span
# ========================================================

def _carry_over_extra_attributes( old_spanlist:SpanList, \
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


# ========================================================
#    Check if the span is to be ignored during 
#          the morphological disambiguation
# ========================================================

def _is_ignore_span( span ):
    ''' Checks if the given span (from the layer 'morph_analysis')
        has attribute IGNORE_ATTR, and whether all of its values 
        are True (which means: the span should be ignored). 
        
        Note: if some values are True, and others are False or None, 
        then throws an Exception because partial ignoring is 
        currently not implemented.
    '''
    if hasattr( span, IGNORE_ATTR ):
        ignore_values = getattr(span, IGNORE_ATTR)
        if ignore_values and all(ignore_values):
            return True
        if ignore_values and any(ignore_values):
            # Only some of the Spans have ignore=True, but 
            # partial ignoring is currently not implemented
            raise Exception('(!) Partial ignoring is currently not '+\
                            'implemented. Unexpected ignore attribute '+\
                            "values encountered at the 'morph_analysis' "+\
                            'span '+str((span.start,span.end))+'.')
    return False


# ===============================
#    VabamorfAnalyzer
# ===============================

class VabamorfAnalyzer(Tagger):
    description   = "Analyzes texts morphologically. Uses Vabamorf's analyzer. "+\
                    "Note: resulting analyses can be ambiguous. "
    layer_name    = None
    attributes    = VabamorfTagger.attributes
    depends_on    = None
    configuration = None
    
    def __init__(self,
                 layer_name='morph_analysis',
                 extra_attributes=None,
                 vm_instance=None,
                 **kwargs):
        """Initialize VabamorfAnalyzer class.

        Parameters
        ----------
        layer_name: str (default: 'morph_analysis')
            Name of the layer where analysis results are stored.
        extra_attributes: list of str (default: None)
            List containing names of extra attributes that will be 
            attached to Spans. All extra attributes will be 
            initialized to None.
        vm_instance: estnltk.vabamorf.morf.Vabamorf
            An instance of Vabamorf that is to be used for analysing
            text morphologically.
        """
        self.kwargs = kwargs
        if vm_instance:
            self.vm_instance = vm_instance
        else:
            self.vm_instance  = Vabamorf.instance()
        self.extra_attributes = extra_attributes
        self.layer_name = layer_name
        
        self.configuration = { 'vm_instance':self.vm_instance.__class__.__name__ }
        if self.extra_attributes:
            self.configuration['extra_attributes'] = self.extra_attributes
        self.configuration.update(self.kwargs)

        self.depends_on = ['words', 'sentences']


    def _get_wordlist(self, text:Text):
        ''' Returns a list of words from given text. If normalized word 
            forms are available, uses normalized forms instead of the 
            surface forms. '''
        result = []
        for word in text.words:
            result.append( _get_word_text( word ) )
        return result


    def tag(self, text: Text, \
                  return_layer=False, \
                  propername=DEFAULT_PARAM_PROPERNAME, \
                  guess     =DEFAULT_PARAM_GUESS, \
                  compound  =DEFAULT_PARAM_COMPOUND, \
                  phonetic  =DEFAULT_PARAM_PHONETIC ) -> Text:
        """Anayses given Text object morphologically. 
        
        Note: disambiguation is not performed, so the results of
        analysis will (most likely) be ambiguous.
        
        Parameters
        ----------
        text: estnltk.text.Text
            Text object that is to be analysed morphologically.
            The Text object must have layers 'words', 'sentences'.
        return_layer: boolean (default: False)
            If True, then the new layer is returned; otherwise 
            the new layer is attached to the Text object, and the 
            Text object is returned;
        propername: boolean (default: True)
            Propose additional analysis variants for proper names 
            (a.k.a. proper name guessing).
        guess: boolean (default: True)
            Use guessing in case of unknown words.
        compound: boolean (default: True)
            Add compound word markers to root forms.
        phonetic: boolean (default: False)
            Add phonetic information to root forms.

        Returns
        -------
        Text or Layer
            If return_layer==True, then returns the new layer, 
            otherwise attaches the new layer to the Text object 
            and returns the Text object;
        """
        # --------------------------------------------
        #   Use Vabamorf for morphological analysis
        # --------------------------------------------
        kwargs = {
            "disambiguate": False,  # perform analysis without disambiguation
            "guess"     : guess,\
            "propername": propername,\
            "compound"  : compound,\
            "phonetic"  : phonetic,\
        }
        # Perform morphological analysis sentence by sentence
        word_spans = text['words'].spans
        word_span_id = 0
        analysis_results = []
        for sentence in text['sentences'].spans:
            # A) Collect all words inside the sentence
            sentence_words = []
            while word_span_id < len(word_spans):
                span = word_spans[word_span_id]
                if sentence.start <= span.start and \
                    span.end <= sentence.end:
                    # Word is inside the sentence
                    sentence_words.append( \
                        _get_word_text( span ) 
                    )
                    word_span_id += 1
                elif sentence.end <= span.start:
                    break
            # B) Use Vabamorf for analysis 
            #    (but check length limitations first)
            if len(sentence_words) > 15000:
                # if 149129 < len(wordlist) on Linux,
                # if  15000 < len(wordlist) < 17500 on Windows,
                # then self.instance.analyze(words=wordlist, **self.kwargs) raises
                # RuntimeError: CFSException: internal error with vabamorf
                for i in range(0, len(sentence_words), 15000):
                    analysis_results.extend( self.vm_instance.analyze(words=sentence_words[i:i+15000], **kwargs) )
            else:
                analysis_results.extend( self.vm_instance.analyze(words=sentence_words, **kwargs) )

        # Assert that all words obtained an analysis 
        # ( Note: there must be empty analyses for unknown 
        #         words if guessing is not used )
        assert len(text.words) == len(analysis_results), \
            '(!) Unexpectedly the number words ('+str(len(text.words))+') '+\
            'does not match the number of obtained morphological analyses ('+str(len(analysis_results))+').'

        # --------------------------------------------
        #   Store analysis results in a new layer     
        # --------------------------------------------
        # A) Create layer
        morph_attributes = self.attributes
        current_attributes = morph_attributes
        if self.extra_attributes:
            for extra_attr in self.extra_attributes:
                current_attributes = current_attributes + (extra_attr,)
        morph_layer = Layer(name=self.layer_name,
                            parent='words',
                            ambiguous=True,
                            attributes=current_attributes )
        # B) Populate layer        
        for word, analyses_dict in zip(text.words, analysis_results):
            # Convert from Vabamorf dict to a list of Spans 
            spans = \
                _convert_vm_dict_to_morph_analysis_spans( \
                        analyses_dict, \
                        word, \
                        layer_attributes=current_attributes, \
                        sort_analyses = True )
            # Attach spans (if word has morphological analyses)
            for span in spans:
                morph_layer.add_span( span )
            if not spans:
                # if word has no morphological analyses (e.g.
                # it is an unknown word), then attach an 
                # empty Span as a placeholder
                empty_span = \
                    _create_empty_morph_span( \
                        word, \
                        layer_attributes=current_attributes )
                morph_layer.add_span( empty_span )

        # --------------------------------------------
        #   Return layer or Text
        # --------------------------------------------
        if return_layer:
            return morph_layer
        text[self.layer_name] = morph_layer
        return text

# ===============================
#    VabamorfDisambiguator
# ===============================

class VabamorfDisambiguator(Tagger):
    description   = "Disambiguates morphologically analysed texts. Uses Vabamorf's disambiguator."
    layer_name    = None
    attributes    = VabamorfTagger.attributes
    depends_on    = None
    configuration = None

    def __init__(self,
                 layer_name='morph_analysis',
                 vm_instance=None,
                 **kwargs):
        """Initialize VabamorfDisambiguator class.

        Parameters
        ----------
        layer_name: str (default: 'morph_analysis')
            Name of the layer where morphological analyses are stored
            in the input Text object.
            Note that this is also name of the layer where results of
            disambiguation are stored;
        vm_instance: estnltk.vabamorf.morf.Vabamorf
            An instance of Vabamorf that is to be used for analysing
            text morphologically;
        """
        self.kwargs = kwargs
        if vm_instance:
            self.vm_instance = vm_instance
        else:
            self.vm_instance = Vabamorf.instance()

        self.layer_name = layer_name

        self.configuration = { 'vm_instance':self.vm_instance.__class__.__name__ }
        self.configuration.update(self.kwargs)

        self.depends_on = ['words', 'sentences', self.layer_name]


    def tag(self, text: Text, \
                  return_layer=False ) -> Text:
        """Disambiguates morphological analyses on the given Text. 
        
        Parameters
        ----------
        text: estnltk.text.Text
            Text object that is to be disambiguated.
            The Text object must have layers 'words', 'sentences',
            'morph_analysis'.
        return_layer: boolean (default: False)
            If True, then the new layer with the results of 
            disambiguation is returned; 
            otherwise, the old layer of ambiguous morph analyses
            is deleted, the new layer is attached to the Text 
            object, and the Text object is returned;

        Returns
        -------
        Text or Layer
            If return_layer==True, then the new layer with the 
            results of disambiguation is returned; 
            otherwise, the old layer of ambiguous morph analyses
            is deleted, the new layer is attached to the Text 
            object, and the Text object is returned;
        """
        # --------------------------------------------
        #  Check for existence of required layers     
        #  Collect layer's attributes                 
        # --------------------------------------------
        for required_layer in self.depends_on:
            assert required_layer in text.layers, \
                '(!) Missing layer "'+str(required_layer)+'"!'
        # Take attributes from the input layer
        current_attributes = text[self.layer_name].attributes
        # Filter out IGNORE_ATTR (used for internal purposes only,
        # not to be the output)
        new_current_attributes = ()
        for cur_attr in current_attributes:
            # Skip IGNORE_ATTR
            if cur_attr == IGNORE_ATTR:
                continue
            new_current_attributes += (cur_attr, )
        current_attributes = new_current_attributes
        # Check if there are any extra attributes to carry over
        # from the old layer
        extra_attributes = []
        for cur_attr in current_attributes:
            if cur_attr not in self.attributes:
                extra_attributes.append( cur_attr )
        # Check that len(word_spans) >= len(morph_spans)
        morph_spans = text[self.layer_name].spans
        word_spans  = text['words'].spans
        assert len(word_spans) >= len(morph_spans), \
            '(!) Unexpectedly, the number of elements at the layer '+\
                 '"'+str(self.layer_name)+'" is greater than the '+\
                 'number of elements at the layer "words". There '+\
                 'should be one to one correspondence between '+\
                 'the layers.'
        # Create a new layer
        new_morph_layer = Layer(name=self.layer_name,
                                parent='words',
                                ambiguous=True,
                                attributes=current_attributes
        )
        # --------------------------------------------
        #  Disambiguate sentence by sentence
        # --------------------------------------------
        morph_span_id = 0
        word_span_id  = 0
        for sentence in text['sentences'].spans:
            # A) Collect all words/morph_analyses inside the sentence
            #    Assume: len(word_spans) >= len(morph_spans)
            sentence_word_spans  = []
            sentence_morph_spans = []
            sentence_morph_dicts = []
            words_missing_morph  = []
            ignored_word_ids     = set()
            while word_span_id < len(word_spans):
                # Get corresponding word span
                word_span  = word_spans[word_span_id]
                morph_span = None
                if sentence.start <= word_span.start and \
                    word_span.end <= sentence.end:
                    morphFound = False
                    # Get corresponding morph span
                    if morph_span_id < len(morph_spans):
                        morph_span = morph_spans[morph_span_id]
                        if word_span.start == morph_span.start and \
                           word_span.end == morph_span.end and \
                           not _is_empty_span( morph_span.spans[0] ):
                            # Word & morph found: collect items
                            sentence_word_spans.append( word_span )
                            sentence_morph_spans.append( morph_span )
                            if not _is_ignore_span( morph_span ):
                                # Add the dict only if it is not marked as 
                                # to be ignored 
                                word_morph_dict = \
                                    _convert_morph_analysis_span_to_vm_dict( \
                                        morph_span )
                                sentence_morph_dicts.append( word_morph_dict )
                            else:
                                # Remember that this word was ignored during 
                                # the disambiguation
                                ignored_word_ids.add( len(sentence_word_spans)-1 )
                            # Advance positions
                            morph_span_id += 1
                            word_span_id  += 1
                            morphFound = True
                    if not morphFound:
                        # Did not find any morph analysis for the word
                        words_missing_morph.append( word_span )
                        word_span_id  += 1
                        # Advance morph position, if morph was empty
                        if morph_span and _is_empty_span(morph_span.spans[0]):
                            morph_span_id += 1
                elif sentence.end <= word_span.start:
                    # Word falls out of the sentence: break
                    break
            # B) Validate that all words have morphological analyses;
            #    If not (e.g. guessing was switched off while analysing), 
            #    then we cannot perform the disambiguation;
            if words_missing_morph:
                missing_pos = [(w.start, w.end) for w in words_missing_morph]
                raise Exception('(!) Unable to perform morphological disambiguation '+\
                                'because words at positions '+str(missing_pos)+' '+\
                                'have no morphological analyses.')
            # C) Use Vabamorf for disambiguation
            disambiguated_dicts = []
            if sentence_morph_dicts:
                disambiguated_dicts = self.vm_instance.disambiguate(sentence_morph_dicts)
            # D) Convert Vabamorf's results to Spans
            wid = 0
            morph_dict_id = 0
            while wid < len(sentence_word_spans):
                # D.0) Find corresponding analysis_dict
                while wid in ignored_word_ids:
                    # Skip the ignored word(s): add old spans instead
                    old_morph_spans = sentence_morph_spans[wid]
                    for old_span in old_morph_spans:
                        new_morph_layer.add_span( old_span )
                    wid += 1
                if not wid < len(sentence_word_spans):
                    # Break if ignoring has passed sentence boundaries
                    break
                word = sentence_word_spans[wid]
                old_morph_spans = sentence_morph_spans[wid]
                analysis_dict   = disambiguated_dicts[morph_dict_id]
                
                # D.1) Convert dicts to spans
                spans = \
                    _convert_vm_dict_to_morph_analysis_spans( \
                        analysis_dict, \
                        word, \
                        layer_attributes=current_attributes )
                # D.2) Carry over attribute values (if needed)
                if extra_attributes:
                    _carry_over_extra_attributes( old_morph_spans, \
                                                  spans, \
                                                  extra_attributes )
                # D.3) Record spans
                for new_span in spans:
                    new_morph_layer.add_span( new_span )
                
                # Advance indices
                morph_dict_id += 1
                wid += 1

        # --------------------------------------------
        #   Return layer or Text
        # --------------------------------------------
        # Return layer
        if return_layer:
            return new_morph_layer
        # Overwrite the old layer
        delattr(text, self.layer_name)
        text[self.layer_name] = new_morph_layer
        return text
