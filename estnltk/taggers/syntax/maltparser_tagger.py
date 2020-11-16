#  Java-based Maltparser as a Tagger 

from typing import MutableMapping
import os, os.path

from estnltk.text import Text
from estnltk.layer.layer import Layer
from estnltk.taggers.retagger import Tagger

from estnltk.taggers import SyntaxDependencyRetagger
from estnltk.taggers.syntax.maltparser import MaltParser


class MaltParserTagger(Tagger):
    """Tags dependency syntactic analysis with MaltParser."""
    conf_param = ['_maltparser_inst', 'add_parent_and_children', 'syntax_dependency_retagger']

    def __init__(self, input_words_layer='words',
                 input_sentences_layer='sentences',
                 input_conll_morph_layer='conll_morph',
                 output_layer='maltparser_syntax',
                 add_parent_and_children=True,
                 input_type='visl_morph'): # can be morph_only, morph_extended, visl_morph

        self.input_layers = [input_words_layer,
                             input_sentences_layer,
                             input_conll_morph_layer]
        self.output_layer = output_layer
        self.output_attributes = ('id', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps', 'misc')

        if input_type == 'morph_only':
            self._maltparser_inst = MaltParser(model_name='model_morph')
        elif input_type == 'morph_extended':
            self._maltparser_inst = MaltParser(model_name='model_morph_ext')
        else:
            self._maltparser_inst = MaltParser()

        self.add_parent_and_children = add_parent_and_children
        if self.add_parent_and_children:
            self.syntax_dependency_retagger = SyntaxDependencyRetagger(conll_syntax_layer=output_layer)
            self.output_attributes += ('parent_span', 'children')
        else:
            self.syntax_dependency_retagger = None

    def _make_layer(self, text: Text, layers: MutableMapping[str, Layer], status: dict):
        # Import from conllu only if we know for sure that MaltParser is going to be applied
        from conllu import parse_incr
        # Apply Maltparser and store results in a temporary file
        words_layer       = layers[self.input_layers[0]]
        sentences_layer   = layers[self.input_layers[1]]
        conll_morph_layer = layers[self.input_layers[2]]
        len_words = len(words_layer)
        temp_file_name = self._maltparser_inst.parse_detached_layers(text, 
                                                                     sentences_layer,
                                                                     words_layer,
                                                                     conll_morph_layer,
                                                                     return_type='temp_output_file' )
        # Construct syntax layer
        syntax_layer = Layer(name=self.output_layer,
                             text_object=text,
                             attributes=self.output_attributes,
                             ambiguous=False
                             )
        assert os.path.exists( temp_file_name )
        with open(temp_file_name, "r", encoding="utf-8") as data_file:
            word_index = 0
            for conll_sentence in parse_incr(data_file, fields=('id', 'form', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps', 'misc')):
                for conll_word in conll_sentence:
                    token = conll_word['form']
                    if word_index >= len_words:
                        raise Exception("can't match file with words layer")
                    while token != words_layer[word_index].text:
                        word_index += 1
                        if word_index >= len_words:
                            raise Exception("can't match file with words layer")
                    w_span = words_layer[word_index]
                    # add values for 'id', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps', 'misc'
                    syntax_layer.add_annotation((w_span.start, w_span.end), **conll_word)
                    word_index += 1
            assert len_words == len( syntax_layer )

        # Clean up: remove temporary file
        os.remove( temp_file_name )
        assert not os.path.exists( temp_file_name )

        if self.add_parent_and_children:
            # Add 'parent_span' & 'children' to the syntax layer
            self.syntax_dependency_retagger.change_layer(text, {self.output_layer : syntax_layer})
        
        # Return the resulting layer
        return syntax_layer



