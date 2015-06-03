# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import
import unittest

from ..dividing import contains, filter_containing, divide


class ContainsTest(unittest.TestCase):

    def test_span_contains_span(self):
        A = (5, 10)
        B = (6, 10)
        C = (5, 9)

        self.assertTrue(contains(A, B))
        self.assertTrue(contains(A, C))
        self.assertFalse(contains(B, A))
        self.assertFalse(contains(C, A))

    def test_list_contains_span(self):
        self.assertTrue(contains([(1, 7), (9, 15)], (13, 15)))
        self.assertTrue(contains([(1, 7), (9, 15)], (3, 5)))
        self.assertFalse(contains([(11, 17), (19, 115)], (0, 11)))
        self.assertFalse(contains([(11, 17), (19, 115)], (200, 211)))

    def test_span_contains_list(self):
        self.assertTrue(contains((100, 200), [(100, 200)]))
        self.assertTrue(contains((100, 200), [(110, 120), (160, 170)]))
        self.assertFalse(contains((100, 200), [(110, 120), (160, 170), (220, 221)]))
        self.assertFalse(contains((100, 200), [(91, 99), (160, 170)]))
        self.assertFalse(contains((100, 200), [(91, 104), (160, 170)]))

    def test_list_contains_list(self):
        self.assertTrue(contains([(1, 5), (10, 15), (20, 25)], [(3, 4), (13, 15), (21, 25)]))
        self.assertTrue(contains([(1, 5), (10, 15), (20, 25)], [(13, 15)]))
        self.assertFalse(contains([(1, 5), (10, 15), (20, 25)], [(1, 5), (10, 16), (21, 22)]))


class FilterTest(unittest.TestCase):

    def test_filter_containing(self):
        self.assertEqual(filter_containing((10, 20), (13, 15)), (13, 15))
        self.assertEqual(filter_containing((10, 20), [(13, 15), (19, 22)]), [(13, 15)])
        self.assertEqual(filter_containing([(5, 10), (11, 15)], (11, 13)), (11, 13))
        self.assertEqual(filter_containing([(5, 10), (11, 15)], (10, 13)), None)
        self.assertEqual(filter_containing((0, 100), [(0, 50), (100, 101), (150, 200)]), [(0, 50)])

        self.assertEqual(filter_containing((10, 20), (15, 20), True), (5, 10))


def element(start, end):
    return {'start': start, 'end': end}


class DivideTest(unittest.TestCase):

    def test_span_divide_span(self):
        outer = [element(0, 100), element(101, 200)]
        inner = [element(0, 10), element(201, 210)]
        divs = divide(inner, outer)
        expected = [[element(0, 10)], []]
        self.assertListEqual(expected, divs)

    def test_span_divide_list(self):
        outer = [element(0, 100), element(101, 200)]
        inner = [element([0, 100, 150], [50, 101, 200])]
        divs = divide(inner, outer)
        expected = [[element([0], [50])], [element([150], [200])]]
        self.assertListEqual(expected, divs)

    def test_list_divide_span(self):
        outer = [element([0, 100, 200], [50, 150, 250])]
        inner = [element(40, 45), element(150, 160), element(240, 250)]
        expected = [[element(40, 45), element(240, 250)]]
        divs = divide(inner, outer)
        self.assertListEqual(expected, divs)

    def test_list_divide_list(self):
        outer = [element([0, 100], [50, 150]), element([200, 300], [250, 350])]
        inner = [element([25, 225], [50, 250]), element([325, 425], [350, 450])]
        expected = [[element([25], [50])], [element([225], [250]), element([325], [350])]]
        divs = divide(inner, outer)
        self.assertListEqual(expected, divs)


class TranslateTest(unittest.TestCase):

    def test_span_translate_span(self):
        outer = [element(0,10), element(20,30), element(40,50), element(70, 80)]
        inner = [element(5,10), element(45,50)]
        expected = [[element(5, 10)], [], [element(5, 10)], []]
        divs = divide(inner, outer, translate=True)
        self.assertListEqual(expected, divs)

    def test_span_translate_list(self):
        outer = [element(100, 200)]
        inner = [element([80, 90, 100, 150, 160, 200, 210], [85, 95, 105, 155, 165, 205, 215])]
        expected = [[element([0, 50, 60], [5, 55, 65])]]
        divs = divide(inner, outer, translate=True)
        self.assertListEqual(expected, divs)

    def test_list_translate_span(self):
        outer = [element([0, 100], [50, 150]), element([50], [100])]
        inner = [element(0, 10), element(100, 110)]
        expected = [[element(0, 10), element(50, 60)], []]
        divs = divide(inner, outer, translate=True, sep='')
        self.assertListEqual(expected, divs)

    def test_list_translate_list(self):
        outer = [element([0, 100], [10, 110]), element([10], [100])]
        inner = [element([0, 10, 100], [1, 11, 101])]
        expected = [[element([0, 20], [1, 21])], [element([0], [1])]]
        divs = divide(inner, outer, translate=True, sep='1234567890')
        self.assertListEqual(expected, divs)
