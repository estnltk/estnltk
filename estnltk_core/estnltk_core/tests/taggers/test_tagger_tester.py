import pytest
import os
import regex as re

from estnltk_core.common import load_text_class
from estnltk_core.taggers.tagger_tester import TaggerTester

from estnltk_core.taggers import Tagger
from estnltk_core import Layer


def path(filename):
    return os.path.join(os.path.dirname(__file__), filename)


input_file = path('test_tagger_tester_input.json')
target_file = path('test_tagger_tester_target.json')


def test_tagger_tester():
    class NumberTagger(Tagger):
        """Tags numbers.

        """
        conf_param = ['regex']

        def __init__(self,
                     output_layer='numbers',
                     output_attributes=(),
                     input_layers=()
                    ):
            self.output_layer = output_layer
            self.output_attributes = output_attributes
            self.input_layers = input_layers
            self.regex = re.compile(r'-?\d+')

        def _make_layer(self, text, layers, status=None):
            layer = Layer(self.output_layer, text_object=text)
            for m in self.regex.finditer(text.text):
                layer.add_annotation((m.start(), m.end()))
            if isinstance(status, dict):
                status['NumberTagger message'] = self.output_layer + ' layer created successfully'
            return layer

    tagger = NumberTagger()
    assert not os.path.exists(input_file), 'remove file before running the test: ' + input_file
    assert not os.path.exists(target_file), 'remove file before running the test: ' + target_file

    tester = TaggerTester(tagger=tagger, input_file=input_file, target_file=target_file)

    Text = load_text_class()
    text = Text('')
    tester.add_test(annotation='empty text', text=text, expected_text=[])

    text = Text('-12,3')
    tester.add_test(annotation='simple', text=text, expected_text=['-12', '3'])

    with pytest.raises(AssertionError):
        tester.add_test(annotation='simple', text=text, expected_text=['-12'])

    tester.save_input()
    tester.save_target()
    assert os.stat(input_file).st_size > 0
    assert os.stat(target_file).st_size > 0
    open(input_file, 'w').close()
    open(target_file, 'w').close()
    tester.save_input()
    tester.save_target()
    assert os.stat(input_file).st_size == 0
    assert os.stat(target_file).st_size == 0
    tester.save_input(overwrite=True)
    tester.save_target(overwrite=True)
    assert os.stat(input_file).st_size > 0
    assert os.stat(target_file).st_size > 0

    tester.run_tests()

    class NumberTagger(Tagger):
        """Tags numbers.

        """
        conf_param = ['regex']

        def __init__(self,
                     output_layer='numbers',
                     output_attributes=(),
                     input_layers=()
                    ):
            self.output_layer = output_layer
            self.output_attributes = output_attributes
            self.input_layers = input_layers
            self.regex = re.compile(r'-?\d')  # this regex is changed

        def _make_layer(self, text, layers, status=None):
            layer = Layer(self.output_layer, text_object=text)
            for m in self.regex.finditer(text.text):
                layer.add_annotation((m.start(), m.end()))
            if isinstance(status, dict):
                status['NumberTagger message'] = self.output_layer + ' layer created successfully'
            return layer

    tagger = NumberTagger()
    tester = TaggerTester(tagger=tagger, input_file=input_file, target_file=target_file).load()

    with pytest.raises(AssertionError):
        tester.run_tests()

    failed_tests = list(tester.inspect_tests())
    assert len(failed_tests) == 1
    assert failed_tests[0].annotation == 'simple'
    assert failed_tests[0].diagnose() == 'numbers layer spans differ'


def test_cleanup():
    if os.path.exists(input_file):
        os.remove(input_file)
    if os.path.exists(target_file):
        os.remove(target_file)
