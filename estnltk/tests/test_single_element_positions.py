import unittest
import estnltk.single_layer_operations as element_positions


class Tests(unittest.TestCase):
    def test_touching_right(self):
        self.assertTrue(element_positions.touching_right({'start': 0, 'end': 10}, {'start': 10, 'end': 20}))
        self.assertFalse(element_positions.touching_right({'start': 0, 'end': 9}, {'start': 10, 'end': 20}))
        self.assertFalse(element_positions.touching_right({'start': 0, 'end': 11}, {'start': 10, 'end': 20}))
        self.assertFalse(element_positions.touching_right({'start': 10, 'end': 20}, {'start': 0, 'end': 10}))
        self.assertFalse(element_positions.touching_right({'start': 20, 'end': 21}, {'start': 10, 'end': 20}))

    def test_touching_left(self):
        self.assertFalse(element_positions.touching_left({'start': 0, 'end': 10}, {'start': 10, 'end': 20}))
        self.assertFalse(element_positions.touching_left({'start': 0, 'end': 9}, {'start': 10, 'end': 20}))
        self.assertFalse(element_positions.touching_left({'start': 0, 'end': 11}, {'start': 10, 'end': 20}))
        self.assertTrue(element_positions.touching_left({'start': 10, 'end': 20}, {'start': 0, 'end': 10}))


    def test_hovering_right(self):
        self.assertTrue(element_positions.hovering_right({'start': 10, 'end': 20}, {'start': 25, 'end': 35}))
        self.assertFalse(element_positions.hovering_right({'start': 25, 'end': 35}, {'start': 10, 'end': 20}))
        self.assertFalse(element_positions.hovering_right({'start': 25, 'end': 35}, {'start': 35, 'end': 36}))
        self.assertFalse(element_positions.hovering_right({'start': 25, 'end': 35}, {'start': 26, 'end': 34}))

    def test_hovering_left(self):
        self.assertTrue(element_positions.hovering_left({'start': 25, 'end': 35}, {'start': 10, 'end': 20}))
        self.assertTrue(element_positions.hovering_left({'start': 25, 'end': 35}, {'start': 10, 'end': 20}))
        self.assertFalse(element_positions.hovering_left({'start': 25, 'end': 35}, {'start': 35, 'end': 36}))
        self.assertFalse(element_positions.hovering_left({'start': 25, 'end': 35}, {'start': 26, 'end': 34}))


    def test_right(self):
        self.assertTrue(element_positions.right({'start': 0, 'end': 10}, {'start': 10, 'end': 20}))
        self.assertTrue(element_positions.right({'start': 0, 'end': 9}, {'start': 10, 'end': 20}))

        self.assertFalse(element_positions.right({'start': 25, 'end': 36}, {'start': 35, 'end': 36}))
        self.assertFalse(element_positions.right({'start': 25, 'end': 35}, {'start': 26, 'end': 34}))


    def test_left(self):
        self.assertFalse(element_positions.left({'start': 0, 'end': 10}, {'start': 10, 'end': 20}))
        self.assertFalse(element_positions.left({'start': 0, 'end': 9}, {'start': 10, 'end': 20}))
        self.assertFalse(element_positions.left({'start': 25, 'end': 36}, {'start': 35, 'end': 36}))
        self.assertFalse(element_positions.left({'start': 25, 'end': 35}, {'start': 26, 'end': 34}))

        self.assertTrue(element_positions.left({'start': 10, 'end': 20}, {'start': 0, 'end': 10}))
        self.assertTrue(element_positions.left({'start': 10, 'end': 20}, {'start': 0, 'end': 10}))

    def test_nested(self):
        self.assertTrue(element_positions.nested({'start': 10, 'end': 20}, {'start': 10, 'end': 20}))
        self.assertTrue(element_positions.nested({'start': 10, 'end': 20}, {'start': 10, 'end': 15}))
        self.assertTrue(element_positions.nested({'start': 10, 'end': 20}, {'start': 14, 'end': 15}))

        self.assertFalse(element_positions.nested({'start': 11, 'end': 20}, {'start': 10, 'end': 20}))
        self.assertFalse(element_positions.nested({'start': 10, 'end': 14}, {'start': 10, 'end': 15}))

    def test_equal(self):
        self.assertTrue(element_positions.equal({'start': 10, 'end': 20}, {'start': 10, 'end': 20}))
        self.assertFalse(element_positions.equal({'start': 11, 'end': 20}, {'start': 10, 'end': 20}))

    def test_nested_aligned_right(self):
        self.assertTrue(element_positions.nested_aligned_right({'start': 10, 'end': 20}, {'start': 12, 'end': 20}))
        self.assertTrue(element_positions.nested_aligned_right({'start': 10, 'end': 20}, {'start': 10, 'end': 20}))
        self.assertFalse(element_positions.nested_aligned_right({'start': 10, 'end': 20}, {'start': 10, 'end': 19}))
        self.assertFalse(element_positions.nested_aligned_right({'start': 11, 'end': 20}, {'start': 10, 'end': 19}))


    def test_nested_aligned_left(self):
        self.assertTrue(element_positions.nested_aligned_left({'start': 10, 'end': 20}, {'start': 10, 'end': 20}))
        self.assertTrue(element_positions.nested_aligned_left({'start': 10, 'end': 20}, {'start': 10, 'end': 19}))
        self.assertFalse(element_positions.nested_aligned_left({'start': 10, 'end': 20}, {'start': 11, 'end': 19}))
        self.assertFalse(element_positions.nested_aligned_left({'start': 11, 'end': 20}, {'start': 10, 'end': 19}))


    def test_overlapping_right(self):
        self.assertTrue(element_positions.overlapping_right({'start': 10, 'end': 20}, {'start': 10, 'end': 21}))
        self.assertTrue(element_positions.overlapping_right({'start': 15, 'end': 20}, {'start': 16, 'end': 21}))
        self.assertFalse(element_positions.overlapping_right({'start': 10, 'end': 20}, {'start': 11, 'end': 19}))
        self.assertFalse(element_positions.overlapping_right({'start': 11, 'end': 20}, {'start': 10, 'end': 19}))


    def test_overlapping_left(self):
        self.assertTrue(element_positions.overlapping_left({'start': 10, 'end': 20}, {'start': 9, 'end': 15}))
        self.assertTrue(element_positions.overlapping_left({'start': 15, 'end': 20}, {'start': 10, 'end': 16}))
        self.assertFalse(element_positions.overlapping_left({'start': 10, 'end': 20}, {'start': 10, 'end': 19}))
