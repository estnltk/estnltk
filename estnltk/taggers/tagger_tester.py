from typing import List
from os import path

from estnltk.text import Text, Layer
from estnltk.taggers import Tagger
from estnltk.converters import text_to_json, json_to_text
from estnltk.converters import layer_to_json, json_to_layer


class Test:
    def __init__(self, annotation: str, text: Text, tagger: Tagger, expected_layer: Layer):
        self.annotation = annotation
        self.text = text
        self.tagger = tagger
        self.expected_layer = expected_layer
        self.resulting_layer = self.tagger.make_layer(self.text.text, self.text.layers)

    def run(self):
        assert self.resulting_layer == self.expected_layer, self.annotation

    def diagnose(self):
        return self.expected_layer.diff(self.resulting_layer)

    def __repr__(self):
        return 'Test({}, {})'.format(self.annotation, self.text)


class TaggerTester:
    def __init__(self, tagger, input_file: str, target_file: str):
        if not isinstance(tagger, Tagger):
            print('tagger is not an instance of Tagger:', type(tagger))
        self.tagger = tagger
        self.input_file = input_file
        self.target_file = target_file
        self.tests = []

    def load(self):
        input_texts = json_to_text(file=self.input_file)
        expected_layers = json_to_layer(input_texts, file=self.target_file)
        self.tests = [Test(text.meta['test_description'], text, self.tagger, layer)
                      for text, layer in zip(input_texts, expected_layers)]
        return self

    def save_input(self, overwrite=False):
        if not overwrite and path.exists(self.input_file):
            print("Input texts file '" + self.input_file +
                  "' already exists. Use 'overwrite=True' to overwrite.")
        else:
            input_texts = [test.text for test in self.tests]
            text_to_json(input_texts, self.input_file)
            print("Created input texts file '" + self.input_file + "'.")

    def save_target(self, overwrite=False):
        if not overwrite and path.exists(self.target_file):
            print("Target layers file '" + self.target_file +
                  "' already exists. Use 'overwrite=True' to overwrite.")
        else:
            input_texts = [test.text for test in self.tests]
            expected_layers = [test.expected_layer for test in self.tests]
            layer_to_json(expected_layers, input_texts, self.target_file)
            print("Created target layers file '" + self.target_file + "'.")

    def add_test(self, annotation, text, expected_text: List[str]):
        expected_layer = self.tagger.make_layer(text.text, text.layers)
        expected_layer.text_object = text
        assert expected_text == expected_layer.text, 'expected_text: {} != {}'.format(expected_layer.text, expected_text)
        text.meta['test_description'] = annotation
        test = Test(annotation, text, tagger=self.tagger, expected_layer=expected_layer)
        test.run()
        self.tests.append(test)

    def run_tests(self):
        assert self.tests, 'no tests to run'
        for test in self.tests:
            try:
                test.run()
                print(test.annotation, 'PASSED')
            except Exception:
                print(test.annotation, 'FAILED')
                raise

    def inspect_tests(self, show='failing'):
        for t in self.tests:
            fail = False
            try:
                t.run()
            except AssertionError:
                fail = True
            if fail or show == 'all':
                yield t

    def __repr__(self):
        template = 'TaggerTester(tagger={self.tagger}, input_file={self.input_file}, target_file={self.target_file})'
        return template.format(self=self)
