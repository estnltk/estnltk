from typing import List
from estnltk import Text, Layer
import json
import random


class LabelStudioExporter:

    def __init__(self, filename: str, texts: List[Text], layer: str, label_level: str = 'annotation',
                 attribute: str = None,
                 attribute_values: List = None):
        if attribute is not None and attribute_values is None:
            raise RuntimeError(
                "If attribute is given then possible attribute values must also be passed as an argument")
        self.filename = filename
        self.texts = texts
        self.layer = layer
        self.attribute_values = attribute_values
        self.label_level = label_level
        self.attribute = attribute

        self.labeling_interface = self.interface_generator()

    def interface_generator(self):

        single_label = '\t<Label value="{label_value}" background="{background_value}"/> \n'
        conf_string = """
        <View>
            <Labels name="label" toName="text">\n"""
        end_block = """
            </Labels>
        <Text name="text" value="$text"/>
        </View>"""

        if self.attribute_values is None:
            conf_string += single_label.format(
                label_value=self.layer,
                background_value=("#" + "%06x" % random.randint(0, 0xFFFFFF)).upper()
            )
        else:
            for val in self.attribute_values:
                conf_string += single_label.format(
                    label_value=val,
                    background_value=("#" + "%06x" % random.randint(0, 0xFFFFFF)).upper()
                )

        conf_string += end_block

        return conf_string

    def convert(self):
        try:
            output = open(self.filename, "wt")
        except OSError:
            raise ValueError("Could not open/read file: {}".format(self.filename))

        json.dump([
            text_to_dict(text, text[self.layer], self.attribute)
            for text in self.texts], output, indent=2)


def text_to_dict(
        text: Text, layer: Layer,
        attribute: str = None,
        text_name: str = 'text',
        labelset_name: str = 'label') -> dict:
    """
    Imports text together with the annotation layer to dict that is aligned with the Label Studio json input format.
    """

    predictions = []
    for span in layer:

        all_attributes = ['start', 'end', 'text']
        all_attributes.append(attribute)

        annotation = {key: getattr(span, key) for key in all_attributes}
        if attribute is None:
            annotation['labels'] = [layer.name]
        else:
            annotation['labels'] = [annotation[attribute]]

        if isinstance(annotation['text'], list):
            annotation['text'] = ' '.join(annotation['text'])

        predictions.append({
            'value': annotation,
            'to_name': text_name,
            'from_name': labelset_name,
            'type': 'labels'})

    return {
        'annotations': [],
        'predictions': [{'result': predictions}],
        'data': {'text': text.text}
    }
