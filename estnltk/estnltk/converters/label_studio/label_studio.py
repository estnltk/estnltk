import json
from typing import List, Dict, Union

Layer = List[Dict[str, any]]
REQUIRED_ATTRIBUTES = frozenset(('start', 'end', 'text'))


def export_texts(
        fname: str, texts: Union[List[str], str], layers: Union[List[Layer], Layer],
        label_attribute: str = 'label',
        other_attributes: List[str] = (),
        text_name: str = 'text', labelset_name: str = 'label'):
    """
    Writes texts together with annotations to file in the JSON format used by Label Studio.
    The length of texts and layers arguments must match or otherwise not all texts are annotated.

    label_attribute:   an attribute in the layer that used as the entity type
    other_attributes:  other attributes that characterise to the entity e.g. match score

    The import to Label Studio succeeds if the labelling configuration corresponds to the NER template

    <View>
      <Labels name="label" toName="text">
        <Label value="PER" background="red"/>
        <Label value="ORG" background="darkorange"/>
        <Label value="LOC" background="orange"/>
        <Label value="MISC" background="green"/>
      </Labels>
      <Text name="text" value="$text"/>
    </View>

    and arguments text_name and labelset_name coincide with the name attribute of <Text> and <Labels> fields, e.g.
    text_name = 'text' and labelset_name='label' for the example configuration shown above.
    """

    try:
        output = open(fname, "wt")
    except OSError:
        raise ValueError("Could not open/read file: {}".format(fname))

    # Convert arguments to lists if needed
    if isinstance(texts, str):
        texts = [texts]
    if isinstance(layers, list) and (len(layers) == 0 or isinstance(layers[0], dict)):
        layers = [layers]

    if len(texts) != len(layers):
        raise ValueError("The is a mismatch between text and layer counts")

    exported_attributes = sorted(REQUIRED_ATTRIBUTES.union(other_attributes))
    json.dump([
        text_to_dict(text, layer, label_attribute, exported_attributes, text_name, labelset_name)
        for text, layer in zip(texts, layers)], output, indent=2)


def text_to_dict(
        text: str, layer: Layer,
        label_attribute: str = 'label',
        exported_attributes: List[str] = ('start', 'end', 'text'),
        text_name: str = 'text',
        labelset_name: str = 'label') -> dict:
    """
    Imports text together with the annotation layer to dict that is aligned with the Label Studio json input format.
    """

    predictions = []
    for span in layer:

        # Ignore spans without labels
        label = span.get(label_attribute, None)
        if label is None:
            continue

        annotation = {key: span[key] for key in exported_attributes if key in span.keys()}
        annotation['labels'] = [str(label)]

        predictions.append({
            'value': annotation,
            'to_name': text_name,
            'from_name': labelset_name,
            'type': 'labels'})

    return {
        'annotations': [],
        'predictions': [{'result': predictions}],
        'data': {'text': text}
    }
