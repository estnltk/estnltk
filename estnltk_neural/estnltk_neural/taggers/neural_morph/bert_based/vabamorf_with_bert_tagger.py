#
#  Provides Vabamorf-based morphological analysis with Bert-based disambiguation. 
#

from estnltk import Text
from estnltk.taggers import Tagger
from estnltk.taggers import Retagger
from estnltk import Span, Layer, Text
from estnltk.taggers.standard.morph_analysis.morf_common import IGNORE_ATTR
from estnltk.taggers.standard.morph_analysis.morf_common import DEFAULT_PARAM_PHONETIC
from estnltk.taggers.standard.morph_analysis.morf_common import DEFAULT_PARAM_COMPOUND
from estnltk.taggers.standard.morph_analysis.morf_common import DEFAULT_PARAM_STEM
import json

from estnltk.taggers import VabamorfAnalyzer
from estnltk.taggers import PostMorphAnalysisTagger
from estnltk_neural.taggers import BertMorphTagger

from estnltk.vabamorf.morf import Vabamorf
from estnltk.taggers import CompoundTokenTagger


class VabamorfWithBertTagger(Tagger):
    """Tags Vabamorf-based morphological analysis with Bert-based disambiguation. 
    Under the hood, applies the following taggers 
     1. VabamorfAnalyzer
     2. PostMorphAnalysisTagger
     3. BertMorphTagger
    and returns 'morph_analysis' or user defined layer. 
    PostMorphAnalysisTagger can be disabled using use_postanalysis=False (default True).
    
    VabamorfAnalyzer will be applied with the default parameters guess = True and 
    propername = True, but parameters slang_lex, compound, phonetic, stem can be changed. 
    """

    conf_param = ['use_postanalysis', 'vabamorf', 'post_morph', 'bert_disamb', 'output_layer', 'slang_lex', "compound",
                  "phonetic", "stem", 'device', 'vm_instance', 'input_layers', 'correct_verb_annotation', 'change_to_bert_form',
                  'post_disambiguator']
    output_layer = 'morph_analysis'
    output_attributes = ['normalized_text', 'lemma', 'root', 'root_tokens', 'ending', 'clitic', 'form', 'partofspeech']
    input_layers = ('words', 'sentences')

    def __init__(self,
                 output_layer:str = output_layer,
                 input_layers: 'List[str]' = ['words', 'sentences'],
                 input_compound_tokens_layer: str = None,
                 compound: bool = DEFAULT_PARAM_COMPOUND,
                 phonetic: bool = DEFAULT_PARAM_PHONETIC,
                 stem: bool     =  DEFAULT_PARAM_STEM,
                 vm_instance: 'estnltk.vabamorf.morf.Vabamorf' = None,
                 slang_lex: bool = True,
                 use_postanalysis: bool = True,
                 device:str = 'cpu', # for gpu - 'cuda'
                 correct_verb_annotation: bool = True,
                 change_to_bert_form: bool = True,
                 post_disambiguator: 'Retagger' = None):
        """Initialize VabamorfWithBertTagger class.
        
        Parameters
        ----------
        output_layer: str (default: 'morph_analysis')
            Name of the layer where analysis results are stored.
        input_layers: List[str] (default: ['words', 'sentences'])
            Names of the input words and sentences layers.
        input_compound_tokens_layer: str (default: None)
            Name of the input compound_tokens layer. 
            If set to None (default), then no compound tokens layer is 
            assumed to be attached to the input Text object, and the 
            post_morph will use an empty compound tokens layer.
            Otherwise, the input Text object should have that layer 
            and it is also used by the post_morph as an input. 
        compound: boolean (default: True)
            VabamorfAnalyzer: Add compound word markers to root forms.
        phonetic: boolean (default: False)
            VabamorfAnalyzer: Add phonetic information to root forms.
        stem: boolean (default: False)
            VabamorfAnalyzer: Replace lemma with word stem in the 'root' and 
            'root_tokens' (so called stem-based morphological analysis). 
            In the stem-based analysis, inflectional forms are not normalized 
            to their lemmas, but instead kept as they are, and only endings 
            are separated from roots. 
            For instance, with lemma-based analysis (default), the 
            word 'läks' gets root='mine' (lemma='minema'); 
            however, with the stem-based analysis, the word 'läks' 
            gets root='läk' (with ending='s' and no lemma). 
            Note that with stem-based analysis, there will be no 
            lemmas in the output.
        vm_instance: estnltk.vabamorf.morf.Vabamorf
            An instance of Vabamorf that is to be used for 
            analysing text morphologically. Note that if you 
            provide a custom instance, the parameters compound, 
            phonetic, stem and slang_lex will have no effect. 
        slang_lex: boolean (default: False)
            If True, then uses an extended version of Vabamorf's binary lexicon, 
            which provides valid analyses to spoken and slang words, such as 
            'kodukas', 'mõnsa', 'mersu', 'kippelt'. However, using "the slang 
            lexicon" also hinders Vabamorf's ability to clearly distinguish 
            between written language and slang words, and this is the reason 
            that "the slang lexicon" is not switched on by default;
            Note: this only works if you leave the parameter vm_instance 
            unspecified;
        use_postanalysis: boolean (default: True)
            Whether PostMorphAnalysisTagger will be applied for post-correcting 
            morph layer. Post-corrections will be applied after Vabamorf's morph 
            analysis and before Bert-based disambiguation.
        device (str):
            The device to run the Bert model on ('cpu' or 'cuda'). 
            Defaults to 'cpu'.
        correct_verb_annotation (bool):
            Bert-based disambiguation: if there is word multiplicity but not verb 
            multiplicity and correct annotation could be chosen based on Bert 
            partofspeech, then correct_verb_annotation=True will take the Vabamorf 
            annotation that matches Bert prediction. The comparison is done 
            with "neg" removed from Bert predicted "form".
        change_to_bert_form (bool):
            Bert-based disambiguation: In case of verbs: if there is multiplicity 
            but not verb multiplicity and Bert prediction form contains "neg" while 
            Vabamorf does not, then Vabamorf annotation will be changed to also 
            include "neg" if change_to_bert_form=True. This is tested on UD treebank
            2.18 where out of 1945 words (with no verb multiplicity) 91.98% matched
            UD annotation if "neg" was exluded from Bert prediction.
        post_disambiguator (Retagger, default: None)
            An estnltk.taggers.Retagger that refines Bert's predictions. It is passed
            on to the BertMorphTagger created by this tagger, and applied to Bert's
            own layer before that layer is used to disambiguate the Vabamorf based
            morph analysis layer. Defaults to None (not applied).
            Example: MorphHomonymsRetagger, which re-evaluates form homonymous words
            with a specialized expert model. 
        """

        self.output_layer = output_layer
        self.compound     = compound
        self.phonetic     = phonetic
        self.stem         = stem
        self.slang_lex    = slang_lex
        self.device       = device
        self.vm_instance  = vm_instance
        self.use_postanalysis = use_postanalysis
        assert len(input_layers) == 2
        self.input_layers = input_layers
        # Update dependencies: add dependencies specific to post_morph
        if self.use_postanalysis and input_compound_tokens_layer is not None:
            self.input_layers.append( input_compound_tokens_layer )
        if self.stem:
            # Modify output layer's attributes: remove lemma
            new_output_attributes = ()
            for attr in self.output_attributes:
                if attr != 'lemma':
                    new_output_attributes += (attr,)
            self.output_attributes = new_output_attributes
        self.correct_verb_annotation = correct_verb_annotation
        self.change_to_bert_form = change_to_bert_form
        
        _vm_instance = None
        if self.vm_instance:
            if self.slang_lex:
                raise ValueError('(!) Cannot use slang_lex=True if vm_instance is already provided')
        else :
            if not self.slang_lex:
                # Use standard written language lexicon (default)
                _vm_instance = Vabamorf.instance()
            else:
                # Use standard written language lexicon extended with slang & spoken words
                from estnltk.vabamorf.morf import VM_LEXICONS
                nosp_lexicons = [lex_dir for lex_dir in VM_LEXICONS if lex_dir.endswith('_nosp')]
                assert len(nosp_lexicons) > 0, \
                    "(!) Slang words lexicon with suffix '_nosp' not found from the default list of lexicons: {!r}".format(VM_LEXICONS)
                _vm_instance = Vabamorf( lexicon_dir=nosp_lexicons[-1] )

        self.vabamorf = VabamorfAnalyzer(output_layer=self.output_layer, 
                                         input_words_layer=self.input_layers[0],
                                         input_sentences_layer=self.input_layers[1],
                                         compound=self.compound,
                                         phonetic=self.phonetic,
                                         stem=self.stem, 
                                         vm_instance=_vm_instance)
        input_compound_tokens_layer = "compound_tokens" if input_compound_tokens_layer is None else input_compound_tokens_layer
        self.post_morph = PostMorphAnalysisTagger(output_layer=self.output_layer,
                                                  input_compound_tokens_layer=input_compound_tokens_layer,
                                                  input_words_layer=self.input_layers[0],
                                                  stem=self.stem)
        self.post_disambiguator = post_disambiguator
        self.bert_disamb = BertMorphTagger(output_layer=self.output_layer,
                                           words_layer=self.input_layers[0],
                                           sentences_layer=self.input_layers[1],
                                           disambiguate=True,
                                           device=self.device,
                                           correct_verb_annotation=self.correct_verb_annotation,
                                           change_to_bert_form=self.change_to_bert_form,
                                           post_disambiguator=self.post_disambiguator,)


    def _make_layer_template(self):
        """Creates and returns a template of the layer."""
        return Layer(name=self.output_layer, text_object=None, attributes=self.output_attributes, parent=self.input_layers[0], ambiguous=True)


    def _make_layer(self, text, layers, status=None):
        """Analyses given Text object morphologically.

        Parameters
        ----------
        text: estnltk.text.Text
            Text object that is to be analysed morphologically.
            The Text object must have layers 'words', 'sentences'.

        layers: MutableMapping[str, Layer]
           Layers of the text. Contains mappings from the
           name of the layer to the Layer object. Must contain
           words, and sentences;

        status: dict
           This can be used to store metadata on layer tagging.
        """

        # --------------------------------------------
        #   Morphological analysis
        # --------------------------------------------
        morph_layer = self.vabamorf.make_layer( text, layers, status )
        layers2 = layers.copy()
        layers2[self.input_layers[0]] = layers[self.input_layers[0]]  # words
        layers2[self.input_layers[1]] = layers[self.input_layers[1]]  # sentences
        # --------------------------------------------
        #   Adding necessary layers for post processing
        # -------------------------------------------- 
        if self.use_postanalysis and self.post_morph:
            if len(self.input_layers) == 2:
                # Make an empty compound tokens layer
                compound_tokens = \
                   Layer(name=CompoundTokenTagger.output_layer, \
                         attributes=CompoundTokenTagger.output_attributes, \
                         text_object=text,\
                         ambiguous=False)
                layers2["compound_tokens"] = compound_tokens
            elif len(self.input_layers) == 3:
                # Assure a compound tokens layer exists
                assert self.post_morph.input_layers[0] in layers.keys(), \
                    f'(!) Missing required input layer {self.post_morph.input_layers[0]}'
                layers2[self.input_layers[2]] = layers[self.input_layers[2]]

        layers2[self.output_layer] = morph_layer
        
        # --------------------------------------------
        #   Post-processing after analysis
        # --------------------------------------------
        if self.use_postanalysis and self.post_morph:
            self.post_morph.change_layer( text, layers2, status )
            #  Remove _ignore from the output layer
            if IGNORE_ATTR in layers2[self.output_layer].attributes:
                layers2[self.output_layer].attributes = [attr for attr in layers2[self.output_layer].attributes if attr != IGNORE_ATTR]
                for span in layers2[self.output_layer]:
                    for annotation in span.annotations:
                        delattr(annotation, IGNORE_ATTR)
                        
        # --------------------------------------------
        #   Bert based disambiguation
        # --------------------------------------------
        self.bert_disamb.change_layer( text, layers2, status )

        return morph_layer





