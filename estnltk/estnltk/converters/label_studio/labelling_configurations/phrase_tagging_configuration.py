from random import seed, randint

from typing import List
from typing import Union
from typing import Dict

from estnltk.converters.label_studio.labelling_configurations.default_color_schemes import DEFAULT_BG_COLORS

class PhraseTaggingConfiguration:
    """
    A simple way to define configuration file for Label Studio phrase tagging tasks.
    In such a task the goal is to detect phrase types together with phrase borders.
    Fields of the configuration object specify all available configuration options.
    The result can be accessed through str() function.
    """

    def __init__(self, class_labels: Union[List[str], Dict[str, str]], header: str = None, granularity: str = None, 
                       rand_seed: int = None):
        """
        Defines class labels that are used in the labelling task together with background colors of selections.
        If the parameter 'class_labels' is a list then default coloring scheme is used.
        To specify background colors, the parameter 'class_labels' must be a dictionary of label-color pairs.
        By default, the labeling window does not have a header and selection granularity is word level.

        It is possible to set hotkeys (keyboard shortcuts) and aliases (subscripts for text selections) for classes.
        For that one has to use appropriately named properties.

        Finally, it is possible to specify the name of the text field in the Labels Studio data to be displayed
        and labelled by setting the field input_text_field. The value must match the field name that contains the
        text to be labelled in your json exports. By default, this is set to be 'text'.
        """
        self.class_labels = None
        self.set_class_labels(class_labels, rand_seed=rand_seed)

        self.header = header
        self.input_text_field = 'text'
        self.annotator_element = 'phrase'
        self.text_element = 'text'

        if granularity is None:
            self.granularity = 'word'
        elif granularity in ['symbol', 'word']:
            self.granularity = granularity
        else:
            raise ValueError("Parameter granularity can have values 'symbol' or 'word'")

    def set_class_labels(self, class_labels: Union[List[str], Dict[str, str]], rand_seed: int = None):
        """
        Defines class labels that are used in the labelling task together with background colors of selections.
        For existing configurations, this process clears other class-specific settings such as hotkeys and aliases.
        """
        if isinstance(class_labels, list):
            colors = DEFAULT_BG_COLORS.get(len(class_labels), None)
            if colors is None:
                if rand_seed is not None:
                    seed( rand_seed )
                colors = [f"#{randint(0, 0xFFFFFF):06X}" for _ in range(len(class_labels))]
            self.class_labels = [{'value': label, 'background': colors[i]} for i, label in enumerate(class_labels)]
        elif isinstance(class_labels, dict):
            self.class_labels = [{'value': label, 'background': color} for label, color in class_labels.items()]
        else:
            raise ValueError('Expecting to see class_labels as a list of labels or dictionary of label-color pairs')

    @property
    def background_colors(self):
        return {item['value']: item.get('background', None) for item in self.class_labels}

    @background_colors.setter
    def background_colors(self, values: Dict[str, str]):
        if not isinstance(values, dict):
            raise ValueError('Expecting to see input as a dictionary of label-color pairs')
        if len(values) != len(self.class_labels):
            raise ValueError('The number of label-color pairs does not match with class count')

        index = {item['value']: loc for loc, item in enumerate(self.class_labels)}
        for label, color in values.items():
            loc = index.get(label, None)
            if loc is None:
                raise ValueError('Unknown class label inside a label-color pair')
            self.class_labels[loc]['background'] = color

    @property
    def hotkeys(self):
        return {item['value']: item.get('hotkey', None) for item in self.class_labels}

    @hotkeys.setter
    def hotkeys(self, values: Dict[str, str]):
        if not isinstance(values, dict):
            raise ValueError('Expecting to see input as a dictionary of label-hotkey pairs')
        if len(values) != len(self.class_labels):
            raise ValueError('The number of label-hotkey pairs does not match with class count')

        index = {item['value']: loc for loc, item in enumerate(self.class_labels)}
        for label, hotkey in values.items():
            loc = index.get(label, None)
            if loc is None:
                raise ValueError('Unknown class label inside a label-hotkey pair')
            self.class_labels[loc]['hotkey'] = hotkey

    @property
    def aliases(self):
        return {item['value']: item.get('alias', None) for item in self.class_labels}

    @aliases.setter
    def aliases(self, values: Dict[str, str]):
        if not isinstance(values, dict):
            raise ValueError('Expecting to see input as a dictionary of label-hotkey pairs')
        if len(values) != len(self.class_labels):
            raise ValueError('The number of label-hotkey pairs does not match with class count')

        index = {item['value']: loc for loc, item in enumerate(self.class_labels)}
        for label, alias in values.items():
            loc = index.get(label, None)
            if loc is None:
                raise ValueError('Unknown class label inside a label-hotkey pair')
            self.class_labels[loc]['alias'] = alias

    # noinspection PyTypeChecker
    def __str__(self):
        """
        Outputs the XML configuration file for Label Studio
        """
        result = "<View>\n"
        if self.header is not None:
            result += f'  <Header value="{self.header}" />\n'

        result += f'  <Labels name="{self.annotator_element}" toName="{self.input_text_field}" >\n    '
        label_tags = [None] * len(self.class_labels)
        for i, label_dict in enumerate(self.class_labels):
            attributes = " ".join(f'{key}="{value}"'for key, value in label_dict.items())
            label_tags[i] = f'<Label {attributes} />'
        result += '\n    '.join(label_tags) + "\n  </Labels>"

        result += f'\n  <Text name="{self.text_element}" value="${self.input_text_field}"'
        result += f' granularity="{self.granularity}" />'
        result += '\n</View>'
        return result









