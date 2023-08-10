from typing import List
from estnltk import Text, Layer
import json
import random


class LabelStudioExporter:

    def __init__(self, filename: str, layers: List[str], label_level: str = 'annotation',
                 attribute: str = None,
                 attribute_values: List = None,checkbox=False):
        if attribute is not None and attribute_values is None:
            raise RuntimeError(
                "If attribute is given then possible attribute values must also be passed as an argument")
        self.filename = filename
        self.layers = layers
        self.attribute_values = attribute_values
        self.label_level = label_level
        self.attribute = attribute

        self.labeling_interface = self.interface_generator(checkbox)

    def interface_generator(self, checkbox = False):

        single_label = '\t<Label value="{label_value}" background="{background_value}"/> \n'
        conf_string = """
        <View>
            <Labels name="label" toName="text">\n"""
        mid_block = """
            </Labels>
        <Text name="text" value="$text"/>
            """
        if checkbox:
            end_block = """<Header value="Are the annotations correct?"/>
                <Choices name="review" toName="text">
                    <Choice value="yes"/>
                    <Choice value="no"/>
                </Choices>
            </View>"""
        else:
            end_block = """
            </View>"""

        if self.attribute_values is None:
            for layer in self.layers:
                conf_string += single_label.format(
                    label_value=layer,
                    background_value=("#" + "%06x" % random.randint(0, 0xFFFFFF)).upper()
                )
        else:
            for val in self.attribute_values:
                conf_string += single_label.format(
                    label_value=val,
                    background_value=("#" + "%06x" % random.randint(0, 0xFFFFFF)).upper()
                )

        conf_string += mid_block
        conf_string += end_block

        return conf_string

    def convert(self, texts, append=False):
        if append:
            with open(self.filename, "r") as input:
                existing = input.readlines()
            existing = "\n".join(existing)
            new_str = json.dumps([
            text_to_dict(text, self.layers, self.attribute)
            for text in texts])
            existing = existing[:-1]
            new_str = new_str[1:]
            new_str = existing + "," + new_str
            with open(self.filename, "w") as output:
                output.write(new_str)
        else:
            with open(self.filename, "wt") as output:
                json.dump([
                text_to_dict(text, self.layers, i, self.attribute)
                for i,text in enumerate(texts)], output, indent=2)


def text_to_dict(
        text: Text, layers: List[str],
        idx: int,
        attribute: str = None,
        text_name: str = 'text',
        labelset_name: str = 'label') -> dict:
    """
    Imports text together with the annotation layer to dict that is aligned with the Label Studio json input format.
    """

    predictions = []
    for layer_name in layers:
        layer = text[layer_name]
        for span in layer:

            all_attributes = ['start', 'end', 'text']
            if attribute is not None:
                all_attributes.append(attribute)
            annotation = {key: getattr(span, key) for key in all_attributes}
            annotation['idx'] = idx

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
