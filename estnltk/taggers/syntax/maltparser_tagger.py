#  Java-based Maltparser as a Tagger 

from typing import MutableMapping
import os, os.path

from estnltk import Text
from estnltk.layer.layer import Layer
from estnltk.taggers.retagger import Tagger

from estnltk.taggers import ConllMorphTagger
from estnltk.taggers import SyntaxDependencyRetagger
from estnltk.taggers.syntax.maltparser import MaltParser


class MaltParserTagger(Tagger):
    """Tags dependency syntactic analysis with MaltParser."""
    conf_param = ['_maltparser_inst', 'conll_morph_layer_name', 'conll_morph_tagger', \
                  'add_parent_and_children', 'syntax_dependency_retagger']

    def __init__(self, input_words_layer = 'words',
                       input_sentences_layer = 'sentences',
                       input_morph_extended_layer = 'morph_extended',
                       conll_morph_layer_name = 'conll_morph',
                       output_layer='maltparser_syntax',
                       add_parent_and_children=True):
        self.input_layers = [ input_words_layer,
                              input_sentences_layer,
                              input_morph_extended_layer ]
        self.output_layer = output_layer
        self.conll_morph_layer_name = conll_morph_layer_name
        self.output_attributes = ('id', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps', 'misc')
        self._maltparser_inst = MaltParser()
        self.conll_morph_tagger = ConllMorphTagger( output_layer = conll_morph_layer_name,            
                                                    morph_extended_layer = input_morph_extended_layer 
                                                   )
        self.add_parent_and_children = add_parent_and_children
        if self.add_parent_and_children:
            self.syntax_dependency_retagger = SyntaxDependencyRetagger(conll_syntax_layer=output_layer)
            self.output_attributes += ('parent_span', 'children')
        else:
            self.syntax_dependency_retagger = None


    def _make_layer(self, text: Text, layers: MutableMapping[str, Layer], status: dict):
        from conllu import parse_incr
        # Make conll_morph layer
        conll_morph_layer = \
            self.conll_morph_tagger.make_layer( text, layers )
        # Apply Maltparser and store results in a temporary file
        words_layer     = layers[self.input_layers[0]]
        sentences_layer = layers[self.input_layers[1]]
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
        with open(temp_file_name, "r", encoding="utf-8") as data_file:
            word_index = 0
            for conll_sentence in parse_incr(data_file):
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
        assert os.path.exists( temp_file_name )
        os.remove( temp_file_name )
        assert not os.path.exists( temp_file_name )

        if self.add_parent_and_children:
            # Add 'parent_span' & 'children' to the syntax layer
            self.syntax_dependency_retagger.change_layer(text, {self.output_layer : syntax_layer})
        
        # Return the resulting layer
        return syntax_layer



