# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import unittest

from ..text import Text
from ..mw_verbs.utils import WordTemplate
from ..syntax.utils   import Tree, build_trees_from_sentence
from ..names import *


class SyntacticTreesTest(unittest.TestCase):

    def construct_tree_1(self):
        # construct the tree for testing
        a  = Tree( {TEXT:'a'}, 0, 1, ['xxx'], parser='xxx' )
        b1 = Tree( {TEXT:'b'}, 1, 1, ['xxx'], parser='xxx' )
        b2 = Tree( {TEXT:'c'}, 2, 1, ['xxx'], parser='xxx' )
        c1 = Tree( {TEXT:'d'}, 3, 1, ['xxx'], parser='xxx' )
        c2 = Tree( {TEXT:'e'}, 4, 1, ['xxx'], parser='xxx' )
        d1 = Tree( {TEXT:'f'}, 5, 1, ['xxx'], parser='xxx' )
        e1 = Tree( {TEXT:'g'}, 6, 1, ['xxx'], parser='xxx' )
        f1 = Tree( {TEXT:'h'}, 7, 1, ['xxx'], parser='xxx' )
        a.add_child_to_subtree(0, b1)
        a.add_child_to_subtree(0, b2)
        a.add_child_to_subtree(1, c1)
        a.add_child_to_subtree(2, c2)
        a.add_child_to_subtree(4, d1)
        a.add_child_to_subtree(5, e1)
        a.add_child_to_subtree(6, f1)
        return a


    def test_get_children_depth(self):
        a = self.construct_tree_1()
        
        # All children of the node (a)
        children = sorted([c.word_id for c in a.get_children()])
        self.assertListEqual([1, 2, 3, 4, 5, 6, 7], children)

        # Children of the node (a) at depth 1 - direct children
        children1  = sorted([c.word_id for c in a.get_children(depth_limit=1)])
        self.assertListEqual([1, 2], children1)
        # Another way of getting direct children
        children2 = sorted([c.word_id for c in a.children])
        self.assertListEqual(children1, children2)
        
        # Children of the node (a) at depth 2 - direct children and grandchildren
        children = sorted([c.word_id for c in a.get_children(depth_limit=2)])
        self.assertListEqual([1, 2, 3, 4], children)

        # Children of the node (a) at depth 4 - all but the last node
        children = sorted([c.word_id for c in a.get_children(depth_limit=4)])
        self.assertListEqual([1, 2, 3, 4, 5, 6], children)
        
        
    def test_get_tree_depth(self):
        a = self.construct_tree_1()
        
        b1 = a.children[0]
        b2 = a.children[1]
        
        # Tree depths at the nodes (b1) and (b2):
        self.assertEqual(1, b1.get_tree_depth())
        self.assertEqual(4, b2.get_tree_depth())


    def test_get_children_include_self(self):
        a = self.construct_tree_1()
        children = [c.word_id for c in a.get_children( sorted=True, include_self=True )]
        self.assertListEqual([0, 1, 2, 3, 4, 5, 6, 7], children)


    def test_get_children_sorted(self):
        # construct the tree for testing
        a  = Tree( {TEXT:'a'}, 0, 1, ['xxx'], parser='xxx' )
        b1 = Tree( {TEXT:'b'}, 1, 1, ['xxx'], parser='xxx' )
        b2 = Tree( {TEXT:'c'}, 2, 1, ['xxx'], parser='xxx' )
        c1 = Tree( {TEXT:'d'}, 3, 1, ['xxx'], parser='xxx' )
        c2 = Tree( {TEXT:'e'}, 4, 1, ['xxx'], parser='xxx' )
        d1 = Tree( {TEXT:'f'}, 5, 1, ['xxx'], parser='xxx' )
        e1 = Tree( {TEXT:'g'}, 6, 1, ['xxx'], parser='xxx' )
        f1 = Tree( {TEXT:'h'}, 7, 1, ['xxx'], parser='xxx' )
        a.add_child_to_subtree(0, b2)
        a.add_child_to_subtree(0, b1)
        a.add_child_to_subtree(2, c2)
        a.add_child_to_subtree(1, c1)
        a.add_child_to_subtree(4, e1)
        a.add_child_to_subtree(4, d1)
        a.add_child_to_subtree(4, f1)
        # By default, the children should appear in the order of tree construction:
        children = [c.word_id for c in a.get_children()]
        self.assertListEqual([2, 1, 4, 6, 5, 7, 3], children)
        # If the 'sorted' argument will be added, the results will be sorted:
        children = [c.word_id for c in a.get_children( sorted=True )]
        self.assertListEqual([1, 2, 3, 4, 5, 6, 7], children)


    def sentence_2_syntax(self):
        return [{'end': 10, 'parser_out': [['@SUBJ', 2]], 'start': 0, 'sent_id': 0},\
                {'end': 16, 'parser_out': [['@<NN', 2], ['@ADVL', 2]], 'start': 11, 'sent_id': 0},\
                {'end': 26, 'parser_out': [['@FMV', -1]], 'start': 17, 'sent_id': 0},\
                {'end': 32, 'parser_out': [['@AN>', 4]], 'start': 27, 'sent_id': 0},\
                {'end': 38, 'parser_out': [['@OBJ', 2]], 'start': 33, 'sent_id': 0},\
                {'end': 39, 'parser_out': [['xxx', 4]], 'start': 38, 'sent_id': 0}]
                
    def sentence_2_morphology(self):
        return [{'start': 0, 'text': 'Naabritalu', 'end': 10, 'analysis': [{'partofspeech': 'S', 'form': 'sg g', 'lemma': 'naabritalu', 'root_tokens': ['naabri', 'talu'], 'clitic': '', 'root': 'naabri_talu', 'ending': '0'}, {'partofspeech': 'S', 'form': 'sg n', 'lemma': 'naabritalu', 'root_tokens': ['naabri', 'talu'], 'clitic': '', 'root': 'naabri_talu', 'ending': '0'}, {'partofspeech': 'S', 'form': 'sg p', 'lemma': 'naabritalu', 'root_tokens': ['naabri', 'talu'], 'clitic': '', 'root': 'naabri_talu', 'ending': '0'}]},\
                {'start': 11, 'text': 'Teele', 'end': 16, 'analysis': [{'partofspeech': 'H', 'form': 'sg g', 'lemma': 'Teele', 'root_tokens': ['Teele'], 'clitic': '', 'root': 'Teele', 'ending': '0'}, {'partofspeech': 'S', 'form': 'sg all', 'lemma': 'tee', 'root_tokens': ['tee'], 'clitic': '', 'root': 'tee', 'ending': 'le'}, {'partofspeech': 'H', 'form': 'sg n', 'lemma': 'Teele', 'root_tokens': ['Teele'], 'clitic': '', 'root': 'Teele', 'ending': '0'}]},\
                {'start': 17, 'text': 'valmistab', 'end': 26, 'analysis': [{'partofspeech': 'V', 'form': 'b', 'lemma': 'valmistama', 'root_tokens': ['valmista'], 'clitic': '', 'root': 'valmista', 'ending': 'b'}]},\
                {'start': 27, 'text': 'suurt', 'end': 32, 'analysis': [{'partofspeech': 'A', 'form': 'sg p', 'lemma': 'suur', 'root_tokens': ['suur'], 'clitic': '', 'root': 'suur', 'ending': 't'}]},\
                {'start': 33, 'text': 'kooki', 'end': 38, 'analysis': [{'partofspeech': 'S', 'form': 'adt', 'lemma': 'kook', 'root_tokens': ['kook'], 'clitic': '', 'root': 'kook', 'ending': '0'}, {'partofspeech': 'S', 'form': 'sg p', 'lemma': 'kook', 'root_tokens': ['kook'], 'clitic': '', 'root': 'kook', 'ending': '0'}]},\
                {'start': 38, 'text': '.', 'end': 39, 'analysis': [{'partofspeech': 'Z', 'form': '', 'lemma': '.', 'root_tokens': ['.'], 'clitic': '', 'root': '.', 'ending': ''}]} ]


    def test_build_trees_from_sentence(self):
        syntax = self.sentence_2_syntax()
        morhp  = self.sentence_2_morphology()
        # Test bulding the tree(s) for a single sentence
        trees = \
            build_trees_from_sentence( morhp, syntax, layer=LAYER_VISLCG3, sentence_id=0 )
        self.assertEqual(len(trees), 1)


    def test_get_children_by_label(self):
        syntax = self.sentence_2_syntax()
        morhp  = self.sentence_2_morphology()
        trees = \
            build_trees_from_sentence( morhp, syntax, layer=LAYER_VISLCG3, sentence_id=0 )
        root = trees[0]
        
        # Test getting children by label
        results = root.get_children( label="@SUBJ" )
        self.assertEqual(len(results), 1)
        subj    = results[0]
        self.assertEqual( subj.word_id, 0 )
        
        obj = root.get_children( label="@OBJ" )[0]
        self.assertEqual( obj.word_id, 4 )
        self.assertDictEqual( obj.syntax_token, {'end': 38, 'parser_out': [['@OBJ', 2]], 'start': 33, 'sent_id': 0} )


    def test_get_children_by_label_regexp(self):
        syntax = self.sentence_2_syntax()
        morhp  = self.sentence_2_morphology()
        trees = \
            build_trees_from_sentence( morhp, syntax, layer=LAYER_VISLCG3, sentence_id=0 )
        root = trees[0]
        
        # Test getting children by regexp describing the label
        results = root.get_children( label_regexp="(@SUBJ|@OBJ|@FMV)", include_self=True, sorted=True )
        self.assertEqual(len(results), 3)
        
        deprels = [ t.labels[0] for t in results ]
        self.assertListEqual(deprels, ['@SUBJ', '@FMV', '@OBJ'])


    def test_get_children_by_label_wordtemplate_1(self):
        syntax = self.sentence_2_syntax()
        morhp  = self.sentence_2_morphology()
        trees = \
            build_trees_from_sentence( morhp, syntax, layer=LAYER_VISLCG3, sentence_id=0 )
        root = trees[0]
        
        word_template = WordTemplate({ POSTAG:'[SH]'})  # get all nouns (proper and common)
        # Test getting children by word templates describing the words
        results = root.get_children( word_template=word_template, include_self=True, sorted=True )
        self.assertEqual(len(results), 3)
        
        deprels = [ t.labels[0] for t in results ]
        words   = [ t.text for t in results ]
        self.assertListEqual(deprels, ['@SUBJ', '@<NN', '@OBJ'])
        self.assertListEqual(words, ['Naabritalu', 'Teele', 'kooki'])


    def test_get_children_by_label_wordtemplate_2(self):
        syntax = self.sentence_2_syntax()
        morhp  = self.sentence_2_morphology()
        trees = \
            build_trees_from_sentence( morhp, syntax, layer=LAYER_VISLCG3, sentence_id=0 )
        root = trees[0]
        
        word_template = WordTemplate({FORM:'^(sg|pl) n$'})  # get all nominals
        # Test getting children by word templates describing the words && by syntactic label descriptions
        results = root.get_children( word_template=word_template, label_regexp="(@SUBJ|@OBJ)", include_self=True, sorted=True )
        self.assertEqual(len(results), 1)
        
        deprels = [ t.labels[0] for t in results ]
        words   = [ t.text for t in results ]
        self.assertListEqual(deprels, ['@SUBJ'])
        self.assertListEqual(words, ['Naabritalu'])

