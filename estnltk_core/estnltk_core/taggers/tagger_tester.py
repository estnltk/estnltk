from typing import List
from os import path

from estnltk_core import Layer
from estnltk_core.taggers import Tagger
from estnltk_core.converters import to_json_file, from_json_file
from estnltk_core.converters import layer_to_dict, dict_to_layer
from estnltk_core.converters import text_to_dict, dict_to_text

from typing import Union

class Test:
    def __init__(self, annotation: str, text: Union['BaseText', 'Text'], tagger: Tagger, expected_layer: Layer):
        self.annotation = annotation
        self.text = text
        self.tagger = tagger
        self.expected_layer = expected_layer
        self.expected_layer.text_object = text
        self.resulting_layer = self.tagger.make_layer(text=self.text, layers=self.text.layers)

    def run(self):
        assert self.resulting_layer == self.expected_layer, self.annotation + "Actual: " + str(self.resulting_layer) + ", Expected: " + str(self.expected_layer)

    def diagnose(self):
        return self.expected_layer.diff(self.resulting_layer)

    def _repr_html_(self):
        table_1 = self.expected_layer.get_overview_dataframe().to_html(index=False, escape=False)
        table_2 = self.expected_layer.attribute_values(('text', 'start', 'end') + self.expected_layer.attributes).to_html(index='text')
        return '\n'.join(('<h3>Test</h3>',
                          self.annotation,
                          '<h4>Input text</h4>',
                          self.text.text,
                          '<h4>Expected layer</h4>',
                          table_1,
                          table_2))

    def __repr__(self):
        return 'Test({}, {})'.format(self.annotation, self.text)


class TaggerTester:
    def __init__(self, tagger, input_file: str, target_file: str, serialisation_module=None):
        if not isinstance(tagger, Tagger):
            print('tagger is not an instance of Tagger:', type(tagger))
        self.tagger = tagger
        self.input_file = input_file
        self.target_file = target_file
        self.tests = []
        self.serialisation_module = serialisation_module

    def load(self):
        input_texts = [dict_to_text(text_dict) for text_dict in from_json_file(file=self.input_file)]
        expected_layers = [dict_to_layer(layer_dict, text_object) for
                           layer_dict, text_object in zip(from_json_file(self.target_file), input_texts)]
        self.tests = [Test(text.meta['test_description'], text, self.tagger, layer)
                      for text, layer in zip(input_texts, expected_layers)]
        return self

    def save_input(self, overwrite=False):
        if not overwrite and path.exists(self.input_file):
            print("Input texts file '" + self.input_file +
                  "' already exists. Use 'overwrite=True' to overwrite.")
        else:
            input_texts = [text_to_dict(test.text) for test in self.tests]
            to_json_file(input_texts, file=self.input_file)
            print("Created input texts file '" + self.input_file + "'.")

    def save_target(self, overwrite=False):
        if not overwrite and path.exists(self.target_file):
            print("Target layers file '" + self.target_file +
                  "' already exists. Use 'overwrite=True' to overwrite.")
        else:
            layer_dicts = [layer_to_dict(test.expected_layer) for test in self.tests]
            to_json_file(layer_dicts, file=self.target_file)
            print("Created target layers file '" + self.target_file + "'.")

    def add_test(self, annotation, text, expected_text: List[str]):
        expected_layer = self.tagger.make_layer(text=text, layers=text.layers)
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
