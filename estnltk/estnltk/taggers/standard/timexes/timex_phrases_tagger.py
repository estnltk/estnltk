from typing import Optional

from estnltk import Text, Layer

from estnltk.taggers import Tagger
from estnltk.taggers.standard.timexes.timex_tagger import TimexTagger

class TimexPhrasesTagger(Tagger):
    """
    A cut-down version of TimexTagger that detects only timex phrases. 
    Uses TimexTagger to create preliminary timexes layer, but does 
    not attempt to normalize timexes. 
    The output layer will only contain output attributes ('tid', 'type', 
    'part_of_interval'). Optionally, an attribute ('is_broken_phrase',) 
    can be added if an attempt is made to envelop timexes over standard 
    words (which may result in tokenization conflicts).
    """
    conf_param = ('input_words_layer', 'envelop', '_timexTagger')
    output_attributes = ('tid', 'type', 'part_of_interval')
    input_layers = ()
    
    def __init__(self, output_layer='pre_timexes', envelop=False, input_words_layer='words'):
        self.output_layer = output_layer
        self.envelop = envelop
        if self.envelop:
            # envelop timexes around words layer
            self.input_words_layer = input_words_layer
            self.input_layers = (input_words_layer,)
            self.output_attributes = ('tid', 'type', 'part_of_interval', 'is_broken_phrase')
            self._timexTagger = TimexTagger( output_layer=output_layer,
                                             enveloped_words_layer=self.input_words_layer,
                                             mark_part_of_interval=True,
                                             output_ordered_dicts=True )
        else:
            # make stand-alone timexes layer (more accurate phrases)
            self.input_words_layer = None
            self.input_layers = ()
            self.output_attributes = ('tid', 'type', 'part_of_interval')
            self._timexTagger = TimexTagger( output_layer=output_layer )

    def __enter__(self):
        # Initialize Java-based TimexTagger
        self._timexTagger.__enter__()
        return self


    def __exit__(self, *args):
        # Close Java-based TimexTagger
        self._timexTagger.__exit__(*args)
        return False


    def close(self):
        # Close Java-based TimexTagger
        self._timexTagger.close()

    def _make_layer_template(self):
        if self.envelop:
            return Layer(name=self.output_layer, text_object=None, 
                         enveloping=self.input_words_layer, 
                         attributes=self.output_attributes)
        else:
            return Layer(name=self.output_layer, text_object=None, 
                         attributes=self.output_attributes)
    
    def _make_layer(self, text, layers, status=None):
        new_layer = self._make_layer_template()
        new_layer.text_object = text
        timexes_layer = self._timexTagger.make_layer(text, layers, status)
        for timex in timexes_layer:
            new_annotation = { 'tid': timex.annotations[0]['tid'],
                               'type': timex.annotations[0]['type'],
                               'part_of_interval': None }
            if timex.annotations[0]['part_of_interval'] is not None:
                new_annotation['part_of_interval'] = \
                    timex.annotations[0]['part_of_interval']['tid']
            if self.envelop:
                new_annotation['is_broken_phrase'] = \
                    timex.annotations[0]['broken_phrase']
            new_layer.add_annotation( timex.base_span, new_annotation )
        new_layer.meta = timexes_layer.meta
        return new_layer
