from estnltk.layer.layer import Layer
from estnltk.taggers import Tagger
from typing import Sequence, Dict

class AttributeComparisonTagger(Tagger):
    """Compares the attributes of two layers"""

    conf_param = ['changeable_attributes', 'layers']

    def __init__(self,
                 output_layer: str,
                 input_layers: Sequence[str],
                 changeable_attributes: Dict[str, list],
                 layers = Sequence[Layer]):
        self.input_layers = input_layers
        self.output_layer = output_layer
        self.changeable_attributes = changeable_attributes
        self.layers = layers
        self.output_attributes = self.new_layer_attributes()[1]

    def _make_layer(self, text, layers, status):
        layer = Layer(name=self.output_layer, text_object=text,
                      attributes=['text'])

        new_layer_attributes = self.new_layer_attributes()
        map_attribute_names = new_layer_attributes[0]
        attributes = new_layer_attributes[1]

        """for attribute in layers[self.input_layers[0]].attributes:
            if attribute == 'head' or attribute in self.changeable_attributes:
                map_attribute_names[(None, attribute)] = attribute
                attributes.append(attribute)
                for i in range(len(self.input_layers)):
                    map_attribute_names[(i, attribute)] = attribute + str(i + 1)
                    attributes.append(attribute + str(i + 1))
            else:
                attributes.append(attribute)
                map_attribute_names[(0, attribute)] = attribute"""

        layer.attributes = tuple(attributes)

        for spans in zip(*layers.values()):
            base_span = spans[0].base_span
            assert all(base_span == span.base_span for span in spans)

            annotation = {attribute: spans[i].annotations[0][attr] if i is not None
            else spans[0][attr] if len(set([span[attr] for span in spans])) == 1 else None
                          for (i, attr), attribute in map_attribute_names.items()}

            layer.add_annotation(base_span, **annotation)

        return layer

    def new_layer_attributes(self):
        map_attribute_names = {}
        attributes = ['text']

        for attribute in self.layers[0].attributes:
            if attribute == 'head' or attribute in self.changeable_attributes:
                map_attribute_names[(None, attribute)] = attribute
                attributes.append(attribute)
                for i in range(len(self.input_layers)):
                    map_attribute_names[(i, attribute)] = attribute + str(i + 1)
                    attributes.append(attribute + str(i + 1))
            else:
                attributes.append(attribute)
                map_attribute_names[(0, attribute)] = attribute

        return map_attribute_names, attributes

    '''def new_layer(self, layers, name, changeable_attributes):
        layer = Layer(name=name, text_object=layers[0].text_object,
                      attributes=['text'])

        map_attribute_names = {}

        attributes = []

        for attribute in layers[0].attributes:
            if attribute == 'head' or attribute in changeable_attributes:
                map_attribute_names[(None, attribute)] = attribute
                attributes.append(attribute)
                for i in range(len(layers)):
                    map_attribute_names[(i, attribute)] = attribute + str(i + 1)
                    attributes.append(attribute + str(i + 1))
            else:
                attributes.append(attribute)
                map_attribute_names[(0, attribute)] = attribute

        layer.attributes += tuple(attributes)

        for spans in zip(*layers):
            base_span = spans[0].base_span
            assert all(base_span == span.base_span for span in spans)

            annotation = { attribute: spans[i].annotations[0][attr] if i is not None
                        else spans[0][attr] if len(set([span[attr] for span in spans])) == 1 else None
                        for (i, attr), attribute in map_attribute_names.items()}

            layer.add_annotation(base_span, **annotation)

        return layer'''