from estnltk.taggers import Retagger


class LetterCaseRetagger(Retagger):
    """ The 'letter_case' attribute gets the value
            'cap' if the word has capital beginning
            None otherwise
    """

    conf_param = ['check_output_consistency']

    def __init__(self):
        self.input_layers = ['morph_extended']
        self.output_layer = 'morph_extended'
        self.output_attributes = ['letter_case']
        self.check_output_consistency = False

    def _change_layer(self, text, layers, status=None):
        layer = layers[self.output_layer]
        if self.output_attributes[0] not in layer.attributes:
            layer.attributes = layer.attributes + self.output_attributes
        for span in layer:
            if text.text[span.start].isupper():
                cap = 'cap'
            else:
                cap = None

            for annotation in span.annotations:
                annotation['letter_case'] = cap
        return layer
