import os
from collections import OrderedDict
from random import Random

from estnltk import Layer
from estnltk.taggers.standard.syntax.syntax_dependency_retagger import SyntaxDependencyRetagger
from estnltk_neural.taggers.syntax.stanza_tagger.stanza_tagger import StanzaSyntaxTagger
from estnltk.taggers.standard.syntax.ud_validation.deprel_agreement_retagger import DeprelAgreementRetagger
from estnltk.taggers.standard.syntax.ud_validation.ud_validation_retagger import UDValidationRetagger
from estnltk.taggers import Tagger
from estnltk.converters.serialisation_modules import syntax_v0
from estnltk.downloader import get_resource_paths

from estnltk import Text


class StanzaSyntaxTaggerWithIgnore(Tagger):
    """
    This is an entity ignore tagger that creates a layer with the subtrees from stanza_syntax_ignore_entity layer
    "removed" so that the spans will have None values. The short sentence after subtree removal is tagged with 
    StanzaSyntaxTagger and the nwe spans are added to the output layer of this tagger.
    """
    
    conf_param = ['add_parent_and_children', 'syntax_dependency_retagger',
                  'input_type', 'dir', 'mark_syntax_error', 'mark_agreement_error', 'agreement_error_retagger',
                  'ud_validation_retagger', 'resources_path', 'ignore_layer', 'stanza_tagger']

    def __init__(self,
                 output_layer='syntax_without_entity',
                 sentences_layer='sentences',
                 words_layer='words',
                 input_morph_layer='morph_analysis',
                 ignore_layer = None, # e.g "syntax_ignore_entity_advmod",
                 input_type='morph_extended',  # or 'morph_extended', 'sentences'
                 add_parent_and_children=False,
                 resources_path=None,
                 mark_syntax_error=False,
                 mark_agreement_error=False,
                 stanza_tagger = None
                 ):
        
        self.add_parent_and_children = add_parent_and_children
        self.mark_syntax_error = mark_syntax_error
        self.mark_agreement_error = mark_agreement_error
        self.ignore_layer = ignore_layer
        if self.ignore_layer!=None:
            self.output_layer = output_layer#+"_"+self.ignore_layer.split("_")[-1:][0]
        else:
            self.output_layer=output_layer
        self.output_attributes = ('id', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps', 'misc', "status")
        self.input_type = input_type
        self.resources_path = resources_path
        

        if not resources_path:
            # Try to get the resources path for stanzasyntaxtagger. Attempt to download resources, if missing
            self.dir = get_resource_paths("stanzasyntaxtagger", only_latest=True, download_missing=True)
        else:
            self.dir = resources_path
        # Check that resources path has been set
        if self.dir is None:
            raise Exception('Models of StanzaSyntaxTagger are missing. '+\
                            'Please use estnltk.download("stanzasyntaxtagger") to download the models.')

        self.syntax_dependency_retagger = None
        if add_parent_and_children:
            self.syntax_dependency_retagger = SyntaxDependencyRetagger(syntax_layer=self.output_layer)
            self.output_attributes += ('parent_span', 'children')

        self.ud_validation_retagger = None
        if mark_syntax_error:
            self.ud_validation_retagger = UDValidationRetagger(output_layer=self.output_layer)
            self.output_attributes += ('syntax_error', 'error_message')

        self.agreement_error_retagger = None
        if mark_agreement_error:
            if not add_parent_and_children:
                raise ValueError('`add_parent_and_children` must be True for marking agreement errors.')
            else:
                self.agreement_error_retagger = DeprelAgreementRetagger(output_layer=self.output_layer)
                self.output_attributes += ('agreement_deprel',)

        if self.input_type not in ['sentences', 'morph_analysis', 'morph_extended', "stanza_syntax"]:
            raise ValueError('Invalid input type {}'.format(input_type))

        self.input_layers = [sentences_layer, words_layer, input_morph_layer, ignore_layer]     

        self.stanza_tagger = StanzaSyntaxTagger(input_type=self.input_type, input_morph_layer=self.input_type, 
                                            add_parent_and_children=True, resources_path=self.resources_path)


    def _make_layer_template(self):
        """Creates and returns a template of the layer."""
        layer = Layer(name=self.output_layer,
                      text_object=None,
                      attributes=self.output_attributes,
                      parent=self.input_layers[1], 
                      ambiguous=False )
        if self.add_parent_and_children:
            layer.serialisation_module = syntax_v0.__version__
        return layer


    def _make_layer(self, text, layers, status=None):
        
        ignore_layer = layers[self.input_layers[3]]
        word_layer = layers[self.input_layers[1]]

        layer = self._make_layer_template()
        layer.text_object=text

        empty_layer = self._make_layer_template()
        empty_layer.text_object=text

        ignored_tokens = [word for span in ignore_layer for word in span.words]
        tokens = [span for span in word_layer if span not in ignored_tokens]
        short_sent = " ".join([span.text for span in tokens])

        # tag the "short" sentence
        short_sentnce = Text(short_sent)
        short_sentnce.tag_layer('morph_extended')
        self.stanza_tagger.tag( short_sentnce )
        
        try:
            ss = 0 # location in short_sent 
            for i, span in enumerate(word_layer.spans):
                if span not in ignored_tokens:         
                    
                    new_span = short_sentnce.stanza_syntax[ss]      
                    
                    feats = None
                    if 'feats' in short_sentnce.stanza_syntax.attributes:
                        feats = new_span['feats']               
                    attributes = {'id': new_span.id, 'lemma': new_span['lemma'], 'upostag': new_span['upostag'], 'xpostag': new_span['xpostag'], 'feats': feats,
                                    'head': new_span['head'], 'deprel': new_span['deprel'], "status": "remained", 'deps': '_', 'misc': '_'}               
                    layer.add_annotation(span, **attributes)
                    
                    ss += 1                 
        except Exception as e:
            return empty_layer
        
    
        if self.add_parent_and_children:
            # Add 'parent_span' & 'children' to the syntax layer.
            self.syntax_dependency_retagger.change_layer(text, {self.output_layer: layer})

        if self.mark_syntax_error:
            # Add 'syntax_error' & 'error_message' to the layer.
            self.ud_validation_retagger.change_layer(text, {self.output_layer: layer})

        if self.mark_agreement_error:
            # Add 'agreement_deprel' to the layer.
            self.agreement_error_retagger.change_layer(text, {self.output_layer: layer})

        return layer
