from estnltk import Layer
from estnltk.taggers import Tagger
from estnltk import EnvelopingBaseSpan
from estnltk.taggers.system.rule_taggers import Ruleset
from typing import Union
from .syntax_tree import SyntaxTree
from .syntax_tree_operations import filter_nodes_by_attributes
from .syntax_tree_operations import extract_base_spans_of_subtree


class PhraseExtractor(Tagger):
    """
    This is a deprel ignore tagger applied to stanza_syntax layer that creates a new layer 
    from the spans that should be removed if words with given deprels are removed.
    """
    
    conf_param = ['input_type', "deprel"]

    def __init__(self,
                 #ruleset: Union[str, dict, list, Ruleset] = None,
                 #decorator: callable=None,
                 output_layer='syntax_ignore_entity',
                 sentences_layer='sentences',
                 words_layer='words',
                 morph_layer='morph_analysis',
                 syntax_layer="stanza_syntax",
                 input_type='stanza_syntax',  # or 'morph_extended', 'sentences'                
                 deprel=None,
                 output_attributes = ['entity_type', 'free_entity', 'is_valid', 'root']

                 ):
        
        #self.ruleset = ruleset
        #self.decorator = decorator
        self.deprel = deprel
        self.output_layer = output_layer #+ "_" + self.deprel
        self.output_attributes = output_attributes
        self.input_type = input_type

        if self.input_type in ['morph_analysis', 'morph_extended', "stanza_syntax", "conll_syntax"]:
            self.input_layers = [sentences_layer, morph_layer, words_layer, syntax_layer]
        else:
            raise ValueError('Invalid input type {}'.format(input_type))

    def _make_layer_template(self):
        """Creates and returns a template of the layer."""
        layer = Layer(name=self.output_layer,
                      text_object=None,
                      attributes=self.output_attributes,
                      enveloping=self.input_layers[1],
                      ambiguous=False)
        return layer

    def _make_layer(self, text, layers, status=None):
        
        stanza_syntax_layer = layers[self.input_layers[3]]
        
        layer = self._make_layer_template()
        layer.text_object = text
        
        if len(text.sentences) > 1:
            raise SystemExit('Input consist of more than 1 sentence.')
               
        # create syntax tree
        syntaxtree = SyntaxTree(syntax_layer_sentence=stanza_syntax_layer)       
        ignore_nodes = filter_nodes_by_attributes(syntaxtree, 'deprel', self.deprel)
        
        for node in ignore_nodes:
            new_span = EnvelopingBaseSpan(extract_base_spans_of_subtree(syntaxtree, node))
            layer.add_annotation(new_span, entity_type=None, free_entity=None, is_valid=None,
                                 root=syntaxtree.graph.nodes[node]['span'])

        return layer
