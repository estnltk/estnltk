
from estnltk import Text
import estnltk
from estnltk.taggers import Tagger
from estnltk import Span, Layer, Text
from estnltk.taggers.standard.morph_analysis.morf_common import IGNORE_ATTR
import json

from estnltk.taggers import VabamorfAnalyzer
from estnltk.taggers import PostMorphAnalysisTagger
from estnltk_neural.taggers import BertMorphTagger
#from bert_morph_tagger import BertMorphTagger

from estnltk.vabamorf.morf import Vabamorf
from estnltk.taggers import CompoundTokenTagger


class VabamorfWithBertTagger(Tagger):
    """
    Tagger that creates and refines 'morph_analysis' layer with
      1. VabamorfAnalyzer
      2. PostMorphAnalysisTagger
      3. BertMorphTagger
      and returns 'morph_analysis' or user defined layer. 
      PostMorphAnalysisTagger can be disabled using use_postanalysis=False (default True)
    """

    conf_param = ['use_postanalysis', 'vabamorf', 'post_morph', 'bert', 'output_layer', 'slang_lex', 'device','vm_instance' , 'input_layers', 'correct_verb_annotation', 'change_to_bert_form']
    output_layer = 'morph_analysis'
    output_attributes = ['normalized_text', 'lemma', 'root', 'root_tokens', 'ending', 'clitic', 'form', 'partofspeech']
    input_layers = ('words', 'sentences')

    def __init__(self,
                post_morph=None,
                 vabamorf = None,
                 bert = None,
                 vm_instance = None,
                 use_postanalysis: bool=True,
                 output_layer:str=output_layer,
                 slang_lex: bool=True,
                 device:str='cpu', # for gpu - 'cuda'
                 input_layers=input_layers,
                correct_verb_annotation: bool = True,
                change_to_bert_form: bool = True,
                ):

        self.output_layer = output_layer
        self.slang_lex = slang_lex
        self.device = device
        self.vm_instance = vm_instance
        self.input_layers=input_layers

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

        
        self.vabamorf = VabamorfAnalyzer(output_layer=self.output_layer, vm_instance=_vm_instance)
        self.post_morph = PostMorphAnalysisTagger(output_layer=self.output_layer)
        self.bert = BertMorphTagger(output_layer=self.output_layer, 
                                                            disambiguate=True, 
                                                            device=self.device, 
                                                            correct_verb_annotation=self.correct_verb_annotation,
                                                            change_to_bert_form=self.change_to_bert_form,)
        self.use_postanalysis = use_postanalysis

       
    def _make_layer_template(self):
        return Layer(name=self.output_layer, text_object=None, attributes=self.output_attributes, parent=self.input_layers[0], ambiguous=True)
        
    
    def _make_layer(self, text, layers, status=None):

        # --------------------------------------------
        #   Morphological analysis
        # --------------------------------------------
        #text.tag_layer( self.vabamorf.input_layers )
        morph_layer = self.vabamorf.make_layer( text, layers, status )

        # --------------------------------------------
        #   Adding necessary layers for post processing
        # -------------------------------------------- 
        layers2 = layers.copy()
        layers2["words"] = text["words"]
        layers2["sentences"] = text["sentences"]
        compound_tokens = \
           Layer(name=CompoundTokenTagger.output_layer, \
                 attributes=CompoundTokenTagger.output_attributes, \
                 text_object=text,\
                 ambiguous=False)
        layers2["compound_tokens"] = compound_tokens
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
        #   Bert based analysis
        # --------------------------------------------
        self.bert.change_layer( text, layers2, status )

        return morph_layer





