import json
import warnings
import pandas as pd

from typing import Literal, Callable

from estnltk import Text, Layer, Span
from estnltk.converters.label_studio.labelling_configurations import (
    DiffTaggingConfiguration,
)

from estnltk_core.layer_operations import diff_layer


class DiffTaggingTask:
    """
    An export-import module for Label Studio diff tagging tasks which allows
    annotators to choose the correct annotation between differing precomputed
    annotations.

    The user interface for the task is determined through the configuration object
    which is provided during the initialisation and can be further customised until
    the data export. Phrase spans and labels are taken form two input layer and
    validated annotations are later imported to an output layer.

    The default Label Studio interface does not use or display meta information
    about the text to be labelled, but it is possible to specify which meta fields
    are added to the data object of the labelling task. All these fields are
    included as subfields of meta field.

    The precomputed annotations are taken as spans of layer in the text object.
    Corresponding labels are computed with a separate labelling function.
    Since there is no way to statically check that the labelling function outputs
    labels that are specified in the configuration, a warning is issued if such
    an error occurs. After which it is possible to redefine labels in the
    configuration by looking at the list of labels outputted during the export.
    """

    def __init__(
        self,
        configuration: DiffTaggingConfiguration,
        label_attribute: str | None = None,
        labelling_function: Callable[[Span], str | None] | None = None,
        exported_meta_fields: list[str] | None = None,
        imported_meta_fields: list[str] | None = None,
    ):
        """
        Sets up the exporter-importer routines for data transfer between Python code and Label Studio.

        Parameters
        ----------
        configuration: DiffTaggingConfiguration object
            Specifies details of Label Studio labelling interface
        label_attribute: str
            Layer attribute that is used as phrase label.
            Always picks the first attribute value when multiple annotations are present.
        labelling_function: Callable[[Span], str | None]
            Function that assigns a label to a phrase specified by a span.
            If the outcome is None the phrase is not exported.
            Can be set only if label_attribute is None
        exported_meta_fields: list[str]
            List of Text.meta components that are exported into JSON as subfields of the data.meta key.
        imported_meta_fields: list[str]
            List of meta fields in the Label Studio output that are imported back to Python.
            Meta-data about border corrections is stored as corresponding attributes of the output layer.
            This allows to capture meta-data about the annotation process for each span.
        """
        self.exported_labels = set()
        self.configuration = configuration

        if label_attribute is None and labelling_function is None:
            raise ValueError(
                "One of the parameters label_attribute or labelling_function must be set"
            )
        elif label_attribute is not None and labelling_function is not None:
            raise ValueError(
                "Only one of the parameters label_attribute or labelling_function can be set"
            )
        elif label_attribute is not None:
            self.labelling_function = lambda span: span.annotations[0][label_attribute]
        elif labelling_function is not None:
            self.labelling_function = labelling_function

        if exported_meta_fields is None:
            self.exported_meta_fields = []
        elif not all(isinstance(field, str) for field in exported_meta_fields):
            raise ValueError("Parameter exported_meta_fields must be a list of strings")
        else:
            self.exported_meta_fields = exported_meta_fields

        if imported_meta_fields is None:
            self.imported_meta_fields = ["lead_time", "created_at", "updated_at"]
        elif not all(isinstance(field, str) for field in imported_meta_fields):
            raise ValueError("Parameter imported_meta_fields must be a list of strings")
        else:
            self.imported_meta_fields = imported_meta_fields

    @property
    def interface_file(self) -> str:
        """
        Configuration file for the Label Studio task.
        """
        return str(self.configuration)

    def export_data(
        self,
        texts: Text | list[Text],
        text_ids: int | list[int] | None = None,
        file_path: str | None = None,
        **kwargs
    ) -> str | None:
        """
        Exports text objects into string that can be used as Label Studio 
        input. If file_path is set the result is written into the file,
        otherwise result is returned as a string. An appropriate exception
        is raised when file cannot be created or updated. Issues warnings
        if the labelling configuration is in conflict with exported phrase
        annotations. It is possible to pass additional text ids that will
        be saved to the text_id meta field. Additional keyword arguments
        are passed to json.dumps(...).
        """
        if isinstance(texts, Text):
            texts = [texts]

        if isinstance(text_ids, int):
            text_ids = [text_ids]

        tasks = self.__layers_to_predictions(texts=texts, text_ids=text_ids)

        # Check for unexpected items
        expected_labels = {item["value"] for item in self.configuration.class_labels}
        if not self.exported_labels <= expected_labels:
            warnings.warn(
                "\nUnexpected label classes occurred during the export.\n"
                "Use the field exported_labels to see all class labels generated by the export\n"
                "and update the labelling configuration by calling set_class_labels(...)",
                UserWarning,
            )

        if file_path is not None:
            with open(file_path, "w") as file:
                json.dump(tasks, file, **kwargs)
        else:
            return json.dumps(tasks, **kwargs)

    def import_data(
        self,
        json_input: str,
        input_type: Literal["json", "json-min"] = "json",
        layer_name: str | None = None,
        label_attribute: str = "label",
        annotator_attribute: str | None = None,
        output_type: Literal["table", "text"] = "table",
    ) -> list[Text] | pd.DataFrame:
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

        if input_type not in ["json", "json-min"]:
            raise ValueError("Parameter input_type must be 'json'")
        elif input_type == "json-min":
            raise ValueError(f"JSON-MIN format not supported")

        # Abort for irrecoverable attribute name conflicts
        if label_attribute in self.imported_meta_fields:
            raise ValueError(
                "Parameter label_attribute conflicts with the field imported_meta_fields"
            )

        if annotator_attribute is None:
            layer_attributes = [label_attribute] + self.imported_meta_fields
        elif annotator_attribute == label_attribute:
            raise ValueError(
                "Parameter annotation_attribute conflicts with label_attribute"
            )
        elif annotator_attribute in self.imported_meta_fields:
            raise ValueError(
                "Parameter annotator_attribute conflicts with the field imported_meta_fields"
            )
        else:
            layer_attributes = [
                label_attribute,
                annotator_attribute,
            ] + self.imported_meta_fields

        # Abort if JSON string is not valid
        try:
            task_list = json.loads(json_input)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON string: {str(e)}")

        return self.__import_json(
            task_list,
            label_attribute,
            annotator_attribute,
            layer_attributes,
            output_type,
        )

    def __import_json(
        self,
        task_list: list,
        label_attribute: str,
        annotator_attribute: str | None,
        layer_attributes: list[str],
        output_type: Literal["table", "text"] = "table",
    ) -> list[Text] | pd.DataFrame:
        """
        Parse label studio exported json
        """
        stats = list()
        texts = dict()
        for task in task_list:
            data = task.get("data")
            meta = task.get("meta")
            if data is None or meta is None:
                continue

            text_idx = meta.get("text_idx")
            if text_idx is None:
                continue

            annotations = task.get("annotations", [])
            if len(annotations) == 0:
                continue

            annotation = annotations[0]
            pred = annotation.get("prediction")
            if pred is None:
                continue

            pred_res = pred.get("result")
            res = annotation.get("result")
            if pred_res is None or res is None:
                continue

            attributes = dict()
            if annotator_attribute:
                attributes[annotator_attribute] = annotation.get("completed_by")

            for meta_field in self.imported_meta_fields:
                field_value = annotation.get(meta_field)
                if field_value is not None:
                    attributes[meta_field] = field_value

            valid = filter(lambda a: a.get("from_name") == "validated_annotation", res)
            valid = next(valid).get("value")
            if valid is None:
                continue

            choices = valid.get("choices", [])
            if len(choices) == 0:
                continue

            choice = choices[0]
            if choice not in [
                self.configuration.input_text_field_a,
                self.configuration.input_text_field_b,
            ]:
                continue

            val = list(filter(lambda p: p.get("to_name") == choice, pred_res))
            if len(val) == 0:
                continue

            val = val[0].get("value")
            if val is None:
                continue

            start = val.get("start")
            end = val.get("end")
            annt = val.get("labels", [])

            if start is None or end is None or len(annt) == 0:
                continue

            if start >= end:
                continue

            if output_type == "text":
                if text_idx not in texts:
                    texts[text_idx] = Text(data[self.configuration.text_element_a])

                text = texts[text_idx]
                if self.configuration.annotator_element not in text.layers:
                    text.add_layer(
                        Layer(
                            self.configuration.annotator_element,
                            attributes=layer_attributes,
                            ambiguous=True,
                        )
                    )

                validated_layer = text[self.configuration.annotator_element]
                validated_layer.add_annotation(
                    (start, end), attribute_dict={label_attribute: annt[0]} | attributes
                )
            else:
                stats.append(
                    {
                        "text_idx": text_idx,
                        "start": start,
                        "end": end,
                        label_attribute: annt[0],
                        "choice": choice,
                    }
                    | attributes
                )

        if output_type == "text":
            return list(texts.values())
        else:
            return pd.DataFrame(stats)

    def __layers_to_predictions(
        self, texts: list[Text], text_ids: list[int] | None = None
    ) -> list[dict]:
        """
        Convert conflicting annotations between layer a and layer b to
        label-studio preditcions
        """
        tasks = []

        if text_ids is not None and len(texts) != len(text_ids):
            raise ValueError(f"Got {len(texts)} texts, but {len(text_ids)} text ids!")

        it = zip(text_ids, texts) if text_ids is not None else enumerate(texts)
        for text_idx, text in it:
            if self.configuration.layer_a not in text.layers:
                raise ValueError(
                    f"Text {text_idx} doesn't have {self.configuration.layer_a} layer"
                )

            if self.configuration.layer_b not in text.layers:
                raise ValueError(
                    f"Text {text_idx} doesn't have {self.configuration.layer_b} layer"
                )

            layer_a = text[self.configuration.layer_a]
            layer_b = text[self.configuration.layer_b]
            for span_a, span_b in diff_layer(layer_a, layer_b):
                predictions = []
                if span_a:
                    label_annt = self.labelling_function(span_a)
                    if label_annt is None:
                        continue

                    pred = {
                        "from_name": "predicted_labels",
                        "to_name": self.configuration.text_element_a,
                        "type": "labels",
                        "value": {
                            "start": span_a.start,
                            "end": span_a.end,
                            "labels": [label_annt],
                        },
                    }

                    self.exported_labels.add(label_annt)
                    predictions.append(pred)

                if span_b:
                    label_annt = self.labelling_function(span_b)
                    if label_annt is None:
                        continue

                    pred = {
                        "from_name": "predicted_labels",
                        "to_name": self.configuration.text_element_b,
                        "type": "labels",
                        "value": {
                            "start": span_b.start,
                            "end": span_b.end,
                            "labels": [label_annt],
                        },
                    }

                    self.exported_labels.add(label_annt)
                    predictions.append(pred)

                task = {
                    "data": {
                        self.configuration.input_text_field_a: text.text,
                        self.configuration.input_text_field_b: text.text,
                    },
                    "predictions": [{"result": predictions}],
                    "meta": {"text_idx": text_idx},
                }

                tasks.append(task)

        return tasks
