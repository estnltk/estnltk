from estnltk.taggers import TaggerNew, MergeTagger

from estnltk.taggers.measurement_tagging.robust_date_number_tagger import RobustDateNumberTagger
from estnltk.taggers.measurement_tagging.measurement_object_tagger import MeasurementObjectTagger
from estnltk.taggers.measurement_tagging.unit_tagger import UnitTagger


class MeasurementTagger(TaggerNew):
    """
    Runs RobustDatesNumbersTagger, MeasurementObjectTagger and UnitsTagger and merges the results.
    """
    description = 'Wraps RobustDatesNumbersTagger, MeasurementObjectTagger and UnitsTagger.'
    attributes = []
    depends_on = []
    conf_param = ['date_number_tagger', 'measurement_object_tagger', 'unit_tagger', 'merge_tagger']

    def __init__(self,
                 attributes=('grammar_symbol', 'regex_type', 'value'),
                 conflict_resolving_strategy='MAX',
                 overlapped=True,
                 layer_name='grammar_tags',
                 ):
        self.attributes = attributes
        self.layer_name = layer_name
        self.date_number_tagger = RobustDateNumberTagger(
            layer_name='dates_numbers',
            conflict_resolving_strategy=conflict_resolving_strategy,
            overlapped=overlapped)
        self.measurement_object_tagger = MeasurementObjectTagger(
            layer_name='measurement_objects',
            conflict_resolving_strategy=conflict_resolving_strategy,
            overlapped=overlapped)
        self.unit_tagger = UnitTagger(
            layer_name='units',
            conflict_resolving_strategy=conflict_resolving_strategy,
            overlapped=overlapped)
        self.merge_tagger = MergeTagger(layer_name='grammar_tags',
                                        input_layers=['dates_numbers', 'units', 'measurement_objects'],
                                        attributes=('grammar_symbol', 'value'))

    def make_layer(self, raw_text, input_layers, status):
        layers = {}
        layers['dates_numbers'] = self.date_number_tagger.make_layer(raw_text, input_layers, status=status)
        layers['measurement_objects'] = self.measurement_object_tagger.make_layer(raw_text, input_layers, status=status)
        layers['units'] = self.unit_tagger.make_layer(raw_text, input_layers, status=status)
        return self.merge_tagger.make_layer(raw_text, layers, status)
