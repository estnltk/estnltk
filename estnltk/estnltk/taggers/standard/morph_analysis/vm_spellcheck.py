#
#    Performs Vabamorf's spellcheck on the words layer and 
#   adds normalized forms to misspelled words, based on suggestions
#   of the spellchecker.
#

from estnltk.vabamorf.morf import Vabamorf

from estnltk import Annotation
from estnltk import Layer, Text
from estnltk.taggers import Retagger
from estnltk.taggers.standard.morph_analysis.morf_common import _get_word_texts

class SpellCheckRetagger(Retagger):
    '''Processes words with Vabamorf's spellchecker and adds normalized forms to misspelled words.'''
    conf_param = ['add_spellcheck', 'add_all_suggestions', 'keep_original_word', '_vm_instance']
    output_attributes = []
    
    def __init__(self, output_layer='words', add_all_suggestions=False, add_spellcheck=False, \
                       keep_original_word=False, vm_instance=None):
        """Initialize SpellCheckRetagger class.
        
        Parameters
        ----------
        output_layer: str (default: 'words')
            Name of the input / output words layer that will be normalized.
        add_spellcheck: boolean (default: False)
            If True, the attribute 'spelling' will be added to annotations.
            This attribute contains a boolean, showing if the original 
            word.text was spelled correctly.
        add_all_suggestions: boolean (default: False)
            If True, then all Vabamorf spellchecker's suggestions will be 
            added as normalized forms of the misspelled word.
            The default setting (add_all_suggestions=False) means that 
            only the first suggestion that is given for each misspelled word
            will be added as the normalized form. Note that picking the first 
            suggestion is likely not the best strategy, but the sophisticated 
            analysis about which one of the suggestions fits best into the 
            context is currently out of our scope.
        keep_original_word: boolean (default: False)
            If True, then the original word.text (the misspelled word) will 
            be added as one of the normalized_form's of the word.
            Some of the words that spellchecker thinks are wrong can actually
            analysed pretty well if the morphological guessing is enabled, so 
            you may want to keep to original word among the suggestions of 
            the spellchecker to enchance morphological analysis results.
            Note: this setting can only be used if add_all_suggestions is 
            True.
        vm_instance: estnltk.vabamorf.morf.Vabamorf
            An instance of Vabamorf that is to be used for 
            performing spellchecking.
        """
        self.input_layers = [output_layer]
        self.output_layer = output_layer
        self.output_attributes = ('normalized_form',)
        self.add_spellcheck = add_spellcheck
        self.add_all_suggestions = add_all_suggestions
        if self.add_spellcheck:
            self.output_attributes += ('spelling',)
        if not self.add_all_suggestions and keep_original_word:
            raise ValueError('Parameter conflict: keep_original_word can be True only if add_all_suggestions is True')
        self.keep_original_word = keep_original_word
        # Initialize Vabamorf's instance;
        _vm_instance = None
        if vm_instance:
            # Check Vabamorf Instance
            if not isinstance(vm_instance, Vabamorf):
                raise TypeError('(!) vm_instance should be of type estnltk.vabamorf.morf.Vabamorf')
            self._vm_instance = vm_instance
        else:
            self._vm_instance = Vabamorf.instance()


    def _change_layer(self, text, layers, status):
        """Processes the words layer with Vabamorf's spellchecker,
           and adds normalized forms to misspelled words.
        
        Parameters
        ----------
        text: estnltk.text.Text
            Text object that is to be processed.
            The Text object must have layer 'words'.

        layers: MutableMapping[str, Layer]
           Layers of the text. Contains mappings from the
           name of the layer to the Layer object. Must contain
           words;

        status: dict
           This can be used to store metadata on layer tagging.
        """
        words_layer = layers[ self.input_layers[0] ]
        normalized_form_newly_added = False
        attribute_added = False
        if 'normalized_form' not in words_layer.attributes:
            words_layer.attributes += ('normalized_form',)
            normalized_form_newly_added = True
            attribute_added = True
        if self.add_spellcheck and 'spelling' not in words_layer.attributes:
            words_layer.attributes += ('spelling',)
            attribute_added = True
        for word in words_layer:
            misspelled = False
            has_prev_normalizations = False
            if 'normalized_form' in words_layer.attributes and not normalized_form_newly_added:
                word_texts = _get_word_texts(word)
                if len(word_texts) > 0:
                    if not( word_texts[0] == word.text and len(word_texts) == 1 ):
                        has_prev_normalizations = True
                        misspelled = True
            else:
                word_texts = [word.text]
            suggestions = []
            spell_check_results = self._vm_instance.spellcheck(word_texts,suggestions=True)
            # Check if we have a misspelled word with suggestions
            for item in spell_check_results:
                if not item["spelling"]:
                    misspelled = True
                    if len(item["suggestions"]) > 0:
                        for new_suggestion in item["suggestions"]:
                            if new_suggestion not in suggestions and \
                               new_suggestion not in word_texts:
                                if self.add_all_suggestions:
                                    suggestions.append( new_suggestion )
                                elif not self.add_all_suggestions and len(suggestions) < 1:
                                    suggestions.append( new_suggestion )
            # Create new annotations that are to be replaced with old ones
            new_annotations = []
            if suggestions:
                #     
                # Keeping original word: 
                # (+) Pros of keeping original word text:
                #     1) spellchecker may suggest that proper nouns, such as 'Rammstein' and 'Erasmuse',
                #        are wrong, but morph analysis guesser can actually analyse these reasonably 
                #        well;
                #     2) spellchecker may suggest that nouns, such as 'krossikal' and 'reformarite',
                #        are wrong, but morph analysis guesser can actually analyse these reasonably 
                #        well;
                #     3) spellchecker may suggest that adverbs, such as 'tegelt', are wrong, but morph 
                #        analysis guesser can actually analyse these reasonably well;
                #     4) spellchecker may suggest corrections to interjections, such as 'oih' and 'Mhh',
                #        which actually need no corrections / normalizations in their lemmas;
                # (-) Cons of keeping original word text:
                #     One big con: all the spelling mistakes will be inside 'normalized words'...
                #     
                for suggestion in suggestions:
                    new_annotations.append({'normalized_form':suggestion})
                if self.keep_original_word:
                    new_annotations.append({'normalized_form':word.text})
            else:
                # No new suggestions
                if has_prev_normalizations:
                    # Let's put back previous normalizations
                    for prev_text in word_texts:
                        new_annotations.append({'normalized_form':prev_text})
                else:
                    new_annotations.append({'normalized_form':None})
            # Fill in attribute 'spelling' (if required)
            if self.add_spellcheck:
                for annotation in new_annotations:
                    annotation['spelling'] = not misspelled
            # ------------------------------------
            # Optimization: we only need to rewrite words annotations if 
            # attribute was added to the layer, or if suggestions were 
            # added to the misspelled word
            # ------------------------------------
            if attribute_added or suggestions:
                # Clear old annotations and add new ones
                word.clear_annotations()
                for new_annotation in new_annotations:
                    word.add_annotation( Annotation(word, **new_annotation) )

