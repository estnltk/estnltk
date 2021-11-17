import os

from estnltk import Layer

from estnltk.taggers import Tagger
from estnltk.taggers import VabamorfTagger
from estnltk.common import abs_path
from .punctuation_type_retagger import PunctuationTypeRetagger
from .morph_to_syntax_morph_retagger import MorphToSyntaxMorphRetagger
from .pronoun_type_retagger import PronounTypeRetagger
from .letter_case_retagger import LetterCaseRetagger
from .remove_adposition_analyses_retagger import RemoveAdpositionAnalysesRetagger
from .finite_form_retagger import FiniteFormRetagger
from .verb_extension_suffix_tagger import VerbExtensionSuffixRetagger
from .subcat_retagger import SubcatRetagger


class MorphExtendedTagger(Tagger):
    """Creates morph_extended layer which contains morph analysis attributes and syntax preprocessing attributes.
    In order to do so executes consecutively several syntax preprocessing rewriters.

    (Text object with morph_extended layer can be converted to VISL CG3 input
    format by export_CG3 method.)

    """
    input_layers = ['morph_analysis']
    output_layer = 'morph_extended'
    output_attributes = VabamorfTagger.output_attributes + ('punctuation_type',
                                                            'pronoun_type',
                                                            'letter_case',
                                                            'fin',
                                                            'verb_extension_suffix',
                                                            'subcat')

    conf_param = ['punctuation_type_retagger', 'morph_to_syntax_morph_retagger', 'pronoun_type_retagger',
                  'letter_case_retagger', 'remove_adposition_analyses_retagger', 'finite_form_retagger',
                  'verb_extension_suffix_retagger', 'subcat_retagger']

    def __init__(self,
                 output_layer='morph_extended',
                 input_morph_analysis_layer:str='morph_analysis',
                 fs_to_synt_rules_file=None,
                 allow_to_remove_all=False,
                 subcat_rules_file=None):
        """ Initializes MorphExtendedTagger

            Parameters
            -----------
            output_layer : str (default: 'morph_extended')
                Name of the output layer.
            
            input_morph_analysis_layer: str (default: 'morph_analysis')
                Name of the input morph_analysis layer;
            
            fs_to_synt_rules_file : str
                Name of the file containing rules for mapping from Filosoft's
                old mrf format to syntactic analyzer's preprocessing mrf format;
                (~~'tmorftrtabel.txt')

            subcat_rules_file : str
                Name of the file containing rules for adding subcategorization
                information to verbs/adpositions;
                (~~'abileksikon06utf.lx')

            allow_to_remove_all : bool
                Specifies whether the method remove_duplicate_analyses() is allowed to
                remove all analysis of a word token (due to the specific _K_-removal rules).
                The original implementation allowed this, but we are now restricting it
                in order to avoid words without any analyses;
                Default: False

        """
        self.output_layer = output_layer
        self.input_layers = [ input_morph_analysis_layer ]

        if fs_to_synt_rules_file is None:
            fs_to_synt_rules_file = abs_path('taggers/standard/syntax/preprocessing/rules_files/tmorftrtabel.txt')
        if subcat_rules_file is None:
            subcat_rules_file = abs_path('taggers/standard/syntax/preprocessing/rules_files/abileksikon06utf.lx')

        self.punctuation_type_retagger = PunctuationTypeRetagger()
        self.morph_to_syntax_morph_retagger = MorphToSyntaxMorphRetagger(input_layer = self.input_layers[0],
                                                                         fs_to_synt_rules_file=fs_to_synt_rules_file)
        self.pronoun_type_retagger = PronounTypeRetagger()
        self.letter_case_retagger = LetterCaseRetagger()
        self.remove_adposition_analyses_retagger = RemoveAdpositionAnalysesRetagger(allow_to_remove_all)
        self.finite_form_retagger = FiniteFormRetagger()
        self.verb_extension_suffix_retagger = VerbExtensionSuffixRetagger('morph_extended')
        self.subcat_retagger = SubcatRetagger(subcat_rules_file=subcat_rules_file)

    def _make_layer_template(self):
        """Creates and returns a template of the layer."""
        return Layer(name=self.output_layer,
                     attributes=self.output_attributes,
                     text_object=None,
                     parent=self.input_layers[0],
                     ambiguous=True)

    def _make_layer(self, text, layers, status=None):
        morph_layer = layers[self.input_layers[0]]

        layer = self.morph_to_syntax_morph_retagger.make_layer(text, {'morph_extended': morph_layer})

        self.punctuation_type_retagger.change_layer(text, {'morph_extended': layer})
        self.pronoun_type_retagger.change_layer(text, {'morph_extended': layer})
        self.letter_case_retagger.change_layer(text, {'morph_extended': layer})
        self.remove_adposition_analyses_retagger.change_layer(text, {'morph_extended': layer})
        self.finite_form_retagger.change_layer(text, {'morph_extended': layer})
        self.verb_extension_suffix_retagger.change_layer(text, {'morph_extended': layer})
        self.subcat_retagger.change_layer(text, {'morph_extended': layer})
        self.remove_adposition_analyses_retagger.change_layer(text, {'morph_extended': layer})

        # TODO: remove
        for span in layer:
            for annotation in span.annotations:
                if annotation['pronoun_type'] is not None:
                    annotation['pronoun_type'] = list(annotation['pronoun_type'])
                if annotation['subcat'] is not None:
                    annotation['subcat'] = list(annotation['subcat'])
                annotation['verb_extension_suffix'] = list(annotation['verb_extension_suffix'])

        # Fix layer name
        layer.name = self.output_layer
        return layer
