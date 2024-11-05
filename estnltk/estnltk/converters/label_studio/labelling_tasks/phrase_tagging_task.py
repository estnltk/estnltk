import json
import warnings

from json import JSONDecodeError

from typing import List
from typing import Union
from typing import Literal
from typing import Optional
from typing import Callable

from estnltk import Text
from estnltk import Layer
from estnltk import Span

from estnltk.converters.label_studio.labelling_configurations.phrase_tagging_configuration import PhraseTaggingConfiguration

class PhraseTaggingTask:
    """
    An export-import module for Label Studio phrase tagging tasks which allows
    annotators to correct precomputed phrase borders.

    The user interface for the task is determined through the configuration object
    which is provided during the initialisation and can be further customised until
    the data export. Phrase spans and labels are taken form an input layer and
    refined annotations are later imported to output layer.

    The default Label Studio interface does not use or display meta information
    about the text to be labelled, but it is possible to specify which meta fields
    are added to the data object of the labelling task. All these fields are
    included as subfields of meta field.

    The precomputed borders are taken as spans of layer in the text object.
    Corresponding labels are computed with a separate labelling function.
    Since there is no way to statically check that the labelling function outputs
    labels that are specified in the configuration, a warning is issued if such
    an error occurs. After which it is possible to redefine labels in the
    configuration by looking at the list of labels outputted during the export.
    """

    def __init__(self,
                 configuration: PhraseTaggingConfiguration,
                 input_layer: str,
                 label_attribute: str = None,
                 labelling_function: Callable[[Span], Optional[str]] = None,
                 output_layer: str = None,
                 exported_meta_fields: List[str] = None,
                 imported_meta_fields: List[str] = None,
                 export_type: Literal['annotations', 'predictions'] = None,
                 scoring_function: Callable[[Span], float] = None
                 ):
        """
        Sets up the exporter-importer routines for data transfer between Python code and Label Studio.

        Parameters
        ----------
        configuration: PhraseTaggingConfiguration object
            Specifies details of Label Studio labelling interface
        input_layer: str
            Text layer that specifies phrases to be modified
        label_attribute: str
            Layer attribute that is used as phrase label.
            Always picks the first attribute value when multiple annotations are present.
        labelling_function: Callable[[Span], Optional[str]]
            Function that assigns a label to a phrase specified by a span.
            If the outcome is None the phrase is not exported.
            Can be set only if label_attribute is None
        output_layer: str
            Name of layer to which the corrected phrase borders are imported.
            Name of the annotator element in Label Studio labelling interface.
        exported_meta_fields: List[str]
            List of Text.meta components that are exported into JSON as subfields of the data.meta key.
        export_type: Literal['annotations', 'predictions']
            By default annotation unless scoring function is provided.
            Determines whether Label Studio treats exported phrases as manual annotations or predictions.
            The difference is largely scholastic unless scoring function is provided.
        imported_meta_fields: List[str]
            List of meta fields in the Label Studio output that are imported back to Python.
            Meta-data about border corrections is stored as corresponding attributes of the output layer.
            This allows to capture meta-data about the annotation process for each span.
        scoring_function Callable[[Span], float]
            A function that attaches a likelihood score for each phrase specified by a span.
            The score is used for active learning sampling mode in Label Studio.
            The outcome should be in range [0, 1].
        """
        self.exported_labels = set()

        if not isinstance(configuration, PhraseTaggingConfiguration):
            raise ValueError('Parameter configuration must be of type PhraseTaggingConfiguration')
        self.configuration = configuration

        if not isinstance(input_layer, str):
            raise ValueError('Parameter input_layer must be of type str')
        self.input_layer = input_layer

        if label_attribute is None and labelling_function is None:
            raise ValueError('One of the parameters label_attribute or labelling_function must be set')
        elif label_attribute is not None and labelling_function is not None:
            raise ValueError('Only one of the parameters label_attribute or labelling_function can be set')
        elif label_attribute is not None:
            if not isinstance(label_attribute, str):
                raise ValueError('Parameter label_attribute must be of type str')
            self.labelling_function = lambda span: span.annotations[0][label_attribute]
        elif labelling_function is not None:
            if not callable(labelling_function):
                raise ValueError('Parameter labelling_function must be callable')
            self.labelling_function = labelling_function

        if output_layer is None:
            self.configuration.annotator_element = 'phrase'
        else:
            self.configuration.annotator_element = output_layer

        if exported_meta_fields is None:
            self.exported_meta_fields = []
        elif not isinstance(exported_meta_fields, list):
            raise ValueError('Parameter exported_meta_fields must be a list of strings')
        elif not all(isinstance(field, str) for field in exported_meta_fields):
            raise ValueError('Parameter exported_meta_fields must be a list of strings')
        else:
            self.exported_meta_fields = exported_meta_fields

        if imported_meta_fields is None:
            self.imported_meta_fields = ['lead_time', 'created_at', 'updated_at']
        elif not isinstance(imported_meta_fields, list):
            raise ValueError('Parameter imported_meta_fields must be a list of strings')
        elif not all(isinstance(field, str) for field in imported_meta_fields):
            raise ValueError('Parameter imported_meta_fields must be a list of strings')
        else:
            self.imported_meta_fields = imported_meta_fields

        if export_type is None:
            self.export_type = 'annotations'
        elif export_type not in ['annotations', 'predictions']:
            raise ValueError("Parameter export_type must be either 'annotations' or 'predictions'")
        elif scoring_function is not None and export_type == 'annotations':
            raise ValueError("When scoring function is provided the parameter export_type must be set to 'predictions'")
        else:
            self.export_type = export_type

        if scoring_function is not None and not callable(scoring_function):
            raise ValueError('Parameter scoring_function must be callable')
        self.scoring_function = scoring_function

    @property
    def interface_file(self) -> str:
        """
        Configuration file for the Label Studio task.
        """
        return str(self.configuration)

    # noinspection PyTypeChecker,PyUnresolvedReferences
    def export_data(self, texts: Union[Text, List[Text]], file_path: str = None, **kwargs) -> str:
        """
        Exports text objects into string that can be used as Label Studio input.
        If file_path is set the result is written into the file, otherwise result is returned as a string.
        An appropriate exception is raised when file cannot be created or updated.
        Issues warnings if the labelling configuration is in conflict with exported phrase annotations.
        All additional arguments are passed to json.dumps(...) function.
        TODO: add correct stack_level to get rid of the last line -- a nontrivial task. see pandas
        https://github.com/pandas-dev/pandas/blob/7c836ed2ecaec55b788aedf053b74ee2a84685da/pandas/io/sql.py#L896
        """
        if isinstance(texts, Text):
            texts = [texts]
        if not isinstance(texts, list):
            raise ValueError('Parameter texts must be a of type Text or list of Text')

        self.exported_labels = set()
        tasks = [None] * len(texts)
        text_element = self.configuration.text_element
        for i, text in enumerate(texts):
            tasks[i] = {'data': {text_element: text.text}}
            tasks[i][self.export_type] = [{
                'result': self.layer_to_prediction(text[self.input_layer], self.labelling_function)
            }]

        # Check for unexpected items
        expected_labels = {item['value'] for item in self.configuration.class_labels}
        if not self.exported_labels <= expected_labels:
            warnings.warn(
                "\nUnexpected label classes occurred during the export.\n"
                "Use the field exported_labels to see all class labels generated by the export\n"
                "and update the labelling configuration by calling set_class_labels(...)", UserWarning)

        if file_path is not None:
            if not isinstance(file_path, str):
                raise ValueError('Parameter file_path must be a string')
            with open(file_path, 'w') as file:
                json.dump(tasks, file)
        else:
            return json.dumps(tasks, **kwargs)

    # noinspection PyTypeChecker,PyUnresolvedReferences
    def import_data(self,
                    json_input: str,
                    input_type: Literal['json', 'json-min'] = 'json',
                    layer_name: str = None,
                    label_attribute: str = 'label',
                    annotator_attribute: str = None,
                    ) -> List[Text]:
        """
        Parses JSON output files generated through Label Studio data export.
        Creates a text object with a layer containing Label Studio annotations.
        The layer is marked as ambiguous as we cannot guarantee that there is only one annotation for each phrase.

        The name of the layer is taken from the task configuration unless the layer name is explicitly specified.
        Parameter label_attribute specifies which layer attribute contains labels of annotated phrases.
        If annotator_attribute is set then annotator ID is added as a separate attribute to an annotated phrase.
        Additionally, list of imported meta fields (such as lead time) are extracted from the input file.

        Annotator ID-s are relevant only if several annotators work on the same task.
        Further details about annotators can be retrieved form the Label Studio server.

        The function fails only if there are naming conflicts between potential layer attributes or the input is
        not a valid JSON string. Otherwise, a failsafe parsing process is guaranteed to produce an output.
        All malformed annotations are ignored.
        """
        if layer_name is None:
            layer_name = self.configuration.annotator_element

        if input_type not in ['json', 'json-min']:
            raise ValueError("Parameter input_type must be either 'json' or 'json-min'")

        # Abort for irrecoverable attribute name conflicts
        if label_attribute in self.imported_meta_fields:
            raise ValueError('Parameter label_attribute conflicts with the field imported_meta_fields')
        if annotator_attribute is None:
            layer_attributes = [label_attribute] + self.imported_meta_fields
        else:
            if annotator_attribute == label_attribute:
                raise ValueError('Parameter annotation_attribute conflicts with label_attribute')
            if annotator_attribute in self.imported_meta_fields:
                raise ValueError('Parameter annotator_attribute conflicts with the field imported_meta_fields')
            layer_attributes = [label_attribute, annotator_attribute] + self.imported_meta_fields

        # Abort if JSON string is not valid
        try:
            task_list = json.loads(json_input)
        except JSONDecodeError as e:
            raise ValueError(f'Invalid JSON string: {str(e)}')

        if input_type == 'json':

            results = [None] * len(task_list)
            for i, task in enumerate(task_list):

                # Abort for invalid data
                data = task.get('data')
                if data is None:
                    results[i] = None
                    continue
                text = data.get(self.configuration.text_element)
                if text is None:
                    results[i] = None
                    continue

                results[i] = Text(text)
                layer = Layer(name=layer_name, attributes=layer_attributes, ambiguous=True)
                results[i].add_layer(layer)

                attributes = {}
                for annotation in task.get('annotations', []):
                    attributes[annotator_attribute] = annotation.get('completed_by')

                    for meta_field in self.imported_meta_fields:
                        field_value = annotation.get(meta_field)
                        if field_value is not None:
                            attributes[meta_field] = field_value

                    for span in annotation.get('result', []):
                        value_element = span.get('value')
                        if value_element is None:
                            continue
                        start = value_element.get('start')
                        if start is None:
                            continue
                        end = value_element.get('end')
                        if end is None or start >= end:
                            continue
                        # Each annotation can have only one label
                        labels = value_element.get('labels', [])
                        if len(labels) != 1:
                            continue
                        attributes[label_attribute] = labels[0]
                        layer.add_annotation((start, end), attribute_dict=attributes)

            return results

        else:
            results = [None] * len(task_list)
            for i, task in enumerate(task_list):

                # Abort for invalid data
                text = task.get(self.configuration.text_element)
                if text is None:
                    results[i] = None
                    continue

                results[i] = Text(task[self.configuration.text_element])
                layer = Layer(name=layer_name, attributes=layer_attributes, ambiguous=True)
                results[i].add_layer(layer)

                attributes = {annotator_attribute: task.get('annotator')}

                for meta_field in self.imported_meta_fields:
                    field_value = task.get(meta_field)
                    if field_value is not None:
                        attributes[meta_field] = field_value

                for span in task.get(self.configuration.annotator_element, []):
                    start = span.get('start')
                    if start is None:
                        continue
                    end = span.get('end')
                    if end is None or start >= end:
                        continue
                    # Each annotation can have only one label
                    labels = span.get('labels', [])
                    if len(labels) != 1:
                        continue
                    layer.add_annotation((start, end), attribute_dict={**attributes, label_attribute: labels[0]})

            return results

    def layer_to_prediction(self, layer: Layer, labelling_function: Callable[[Span], str]) -> List[dict]:
        """
        Helper function for data export. Converts layer into annotation format.
        """
        assert callable(labelling_function), "Labelling function must be of type Callable[[Span], str]"

        result = []
        text_element = self.configuration.text_element
        annotator_element = self.configuration.annotator_element

        for span in layer:
            span_label = labelling_function(span)
            if span_label is None:
                continue

            # Update the list of exported labels
            self.exported_labels.add(span_label)

            result.append({
                'value': {
                    'start': span.start,
                    'end': span.end,
                    'labels': [str(span_label)]
                },
                'from_name': annotator_element,
                'to_name': text_element,
                'type': 'labels'
            })

        return result
