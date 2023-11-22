from estnltk import Layer
from estnltk.taggers import Tagger
from estnltk import EnvelopingBaseSpan
from estnltk.taggers.standard.syntax.phrase_extraction.syntax_tree import SyntaxTree
from estnltk.taggers.standard.syntax.phrase_extraction.syntax_tree_operations import filter_nodes_by_attributes
from estnltk.taggers.standard.syntax.phrase_extraction.syntax_tree_operations import extract_base_spans_of_subtree


class PhraseExtractor(Tagger):
    """
    Extracts various types of phrases based on UD-syntax. 
    By default, searches subtrees with specific dependency relations but there are other options. 
    User can specify decorator to filter out and annotate phrases.
    There are sensible decorators for different phrase types.
    """

    conf_param = ['input_type', "deprel", "decorator", "output_layer"]

    def __init__(self,
                 decorator: callable = None,
                 output_layer='syntax_phrases',
                 sentences_layer='sentences',
                 words_layer='words',
                 syntax_layer="stanza_syntax",
                 deprel=None,
                 output_attributes=['root_id', 'root']
                 ):
        self.decorator = decorator
        self.deprel = deprel
        self.output_layer = output_layer
        self.output_attributes = output_attributes
        self.input_layers = [words_layer, sentences_layer, syntax_layer]

    def _make_layer_template(self):
        """Creates and returns a template of the layer."""
        layer = Layer(name=self.output_layer,
                      text_object=None,
                      attributes=self.output_attributes,
                      enveloping=self.input_layers[-1],
                      ambiguous=False,
                      serialisation_module='syntax_phrases_v0')
        return layer

    def _make_layer(self, text, layers, status=None):
        layer = self._make_layer_template()
        layer.text_object = text

        sentences_layer = self.input_layers[1]
        syntax_layer = self.input_layers[-1]
        
        text_word_idx = 0

        for sentence in layers[sentences_layer]:
            sent_end = text_word_idx + len(sentence)
            syntaxtree = SyntaxTree(syntax_layer_sentence=text[syntax_layer][text_word_idx:sent_end])
            ignore_nodes = filter_nodes_by_attributes(syntaxtree, 'deprel', self.deprel)
            for node in ignore_nodes:
                new_span = EnvelopingBaseSpan(sorted(extract_base_spans_of_subtree(syntaxtree, node)))
                annotation = {"root_id": syntaxtree.graph.nodes[node]['span']["id"],
                              "root": syntaxtree.graph.nodes[node]['span']}
                if self.decorator:
                    annotation = self.decorator(text, new_span, annotation)
                if annotation is not None:
                    layer.add_annotation(new_span, **annotation)
            text_word_idx = sent_end

        return layer
