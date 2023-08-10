from estnltk import Layer
from estnltk.taggers.standard.syntax.phrase_extraction.syntax_tree_operations import *

from .stanza_syntax_tagger import StanzaSyntaxTaggerWithIgnore


class ConsistencyDecorator:
    """
    Decorator for PhraseTagger.
    Is required to determine syntax conservation score after removing a phrase from sentence.
    """

    def __init__(self, input_type, model_path, output_layer, syntax_layer, morph_layer):
        self.resources_path = model_path
        if not self.resources_path:
            raise ValueError('Missing resources path for StanzaSyntaxTagger')

        self.output_layer = output_layer
        self.syntax_layer = syntax_layer
        self.morph_layer = morph_layer

        self.syntax_tagger = StanzaSyntaxTaggerWithIgnore(ignore_layer=self.output_layer, input_type=input_type,
                                                 input_morph_layer=self.morph_layer, add_parent_and_children=True,
                                                 resources_path=self.resources_path)

        self.syntax_input_layers = self.syntax_tagger.input_layers

    def __call__(self, text_object, phrase_span, annotations):
        """
        Adds three syntax conservation scores for the shortened sentence.
        Shortened sentence is obtained by removing the phrase in the phrase_span from the text.
        """
        # syntax_tagger requires phrases_layer to compute syntax for shortened sentence
        phrases_layer = Layer(name=self.output_layer,
                              text_object=text_object,
                              attributes=['root_id', 'root'],
                              parent=None,
                              ambiguous=False,
                              enveloping=self.syntax_layer,
                              )
        phrases_layer.add_annotation(phrase_span, **annotations)

        input_layers = {layer: text_object[layer] for layer in self.syntax_input_layers if layer in text_object.layers}
        input_layers.update({self.output_layer: phrases_layer})
        shortened_syntax_layer = self.syntax_tagger.make_layer(text_object, input_layers)

        las_score, uas, la = get_graph_edge_difference(text_object[self.syntax_layer],
                                                       shortened_syntax_layer,
                                                       phrases_layer,
                                                       False)

        annotations.update({
            'syntax_conservation_score': las_score,
            "unlabelled_attachment_score": uas,
            "label_accuracy": la})

        return annotations
