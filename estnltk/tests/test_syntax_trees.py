# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import unittest

from ..text import Text
from ..syntax.utils import Tree
from ..names import *


class SyntacticTreesTest(unittest.TestCase):

    def construct_tree(self):
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
        a = self.construct_tree()
        
        # All children of the node (a)
        children = sorted([c.word_id for c in a.get_children()])
        self.assertListEqual([1, 2, 3, 4, 5, 6, 7], children)

        # Children of the node (a) at depth 1 - direct children
        children = sorted([c.word_id for c in a.get_children(depth_limit=1)])
        self.assertListEqual([1, 2], children)
        
        # Children of the node (a) at depth 2 - direct children and grandchildren
        children = sorted([c.word_id for c in a.get_children(depth_limit=2)])
        self.assertListEqual([1, 2, 3, 4], children)

        # Children of the node (a) at depth 4 - all but the last node
        children = sorted([c.word_id for c in a.get_children(depth_limit=4)])
        self.assertListEqual([1, 2, 3, 4, 5, 6], children)
        
        
    def test_get_tree_depth(self):
        a = self.construct_tree()
        
        b1 = a.children[0]
        b2 = a.children[1]
        
        # Tree depths at the nodes (b1) and (b2):
        self.assertEqual(1, b1.get_tree_depth())
        self.assertEqual(4, b2.get_tree_depth())
        