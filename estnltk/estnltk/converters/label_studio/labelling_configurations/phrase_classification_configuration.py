from random import seed, randint

from typing import List
from typing import Union
from typing import Dict

from estnltk.converters.label_studio.labelling_configurations.default_color_schemes import DEFAULT_BG_COLORS

class PhraseClassificationConfiguration:
    """
    A simple way to define configuration file for Label Studio phrase classification tasks.
    Phrase classification can be used to mark predicted phrases borders as correct or incorrect.
    Another option is to sub-categorise phrases into fixed set of subclasses.
    Fields of the configuration object specify all available configuration options.
    The result can be accessed through str() function.
    """

    def __init__(self,
                 phrase_labels: Union[List[str], Dict[str, str]],
                 class_labels: Dict[str, str],
                 choice_type: str = None,
                 header: str = None,
                 header_placement: str = None,
                 rand_seed: int = None
                 ):
        """
        Defines visual phrase labels in the classification task together with background colors of selections.
        If the parameter 'phrase_labels' is a list then default coloring scheme is used.
        To specify background colors, specify parameter 'phrase_labels' as a dictionary of label-color pairs.

        To specify the class selection, provide the parameter 'class_labels' as a dictionary of class-label pairs
        where label encodes the option text and class encodes the formal class name.
        By default, the choice type is set to 'single-ratio' and the user sees radio button. Other options are
        single (only single checkbox can be selected) and multiple (several checkboxes can be selected).
        It is possible to set hotkeys (keyboard shortcuts) for choice classes by assigning the hotkeys field.

        IMPORTANT: Do not use 'true' and 'false' choice values in 'choice_labels' as this confuses Label Studio.
        Use 'True' and 'False' choice labels instead if you really need standard naming of binary outcomes.

        By default, the header is placed to the middle between labelled text and choices if specified.
        Possible choices for the header placement are 'top', 'middle', 'bottom'.

        Finally, it is possible to specify the name of the text field in the Labels Studio data to be displayed
        and labelled by setting the field input_text_fields. The value must match the field name that contains the
        text to be labelled in your json exports. By default, this is set to be 'text'.
        """

        if isinstance(phrase_labels, list):
            colors = DEFAULT_BG_COLORS.get(len(phrase_labels), None)
            if colors is None:
                if rand_seed is not None:
                    seed( rand_seed )
                colors = [f"#{randint(0, 0xFFFFFF):06X}" for _ in range(len(phrase_labels))]
            self.phrase_labels = [{'value': label, 'background': colors[i]} for i, label in enumerate(phrase_labels)]
        elif isinstance(phrase_labels, dict):
            self.phrase_labels = [{'value': label, 'background': color} for label, color in phrase_labels.items()]
        else:
            raise ValueError('Expecting to see phrase_labels as a list of labels or dictionary of label-color pairs')

        if isinstance(class_labels, dict):
            self.choice_labels = [{'value': text, 'alias': alias} for alias, text in class_labels.items()]
        else:
            raise ValueError('Expecting to see class_labels as dictionary of class-label pairs')

        self.header = header
        self.input_text_field = 'text'
        self.phrase_annotator_element = 'phrase'
        self.text_element = 'text'
        self.class_annotator_element = 'phrase_class'
        self.choice_required = 'true'

        if choice_type is None:
            self.choice_type = 'single-radio'
        elif choice_type in ['single', 'single-radio', 'multiple']:
            self.choice_type = choice_type
        else:
            raise ValueError("Parameter choice_type can have values 'single', 'single-radio' or 'multiple'")

        if header_placement is None:
            self.header_placement = 'middle'
        elif header_placement in ['top', 'middle', 'bottom']:
            self.header_placement = header_placement
        else:
            raise ValueError("Parameter header_placement can have values 'top', 'middle' or 'bottom'")

    @property
    def hotkeys(self):
        return {item['alias']: item.get('hotkey', None) for item in self.choice_labels}

    @hotkeys.setter
    def hotkeys(self, values: Dict[str, str]):
        if not isinstance(values, dict):
            raise ValueError('Expecting to see input as a dictionary of choice-hotkey pairs')
        if len(values) != len(self.choice_labels):
            raise ValueError('The number of choice-hotkey pairs does not match with choice count')

        index = {item['alias']: loc for loc, item in enumerate(self.choice_labels)}
        for alias, hotkey in values.items():
            loc = index.get(alias, None)
            if loc is None:
                raise ValueError('Unknown class label inside a choice-hotkey pair')
            self.choice_labels[loc]['hotkey'] = hotkey

    def __str__(self):
        """
        Outputs the XML configuration file for Label Studio
        """
        result = "<View>\n"
        if self.header and self.header_placement == 'top':
            result += f'  <Header value="{self.header}" />'

        result += f'  <Labels name="{self.phrase_annotator_element}" toName="{self.input_text_field}" >\n    '
        label_tags = [None] * len(self.phrase_labels)
        for i, label_dict in enumerate(self.phrase_labels):
            attributes = " ".join(f'{key}="{value}"'for key, value in label_dict.items())
            label_tags[i] = f'<Label {attributes} />'
        result += '\n    '.join(label_tags) + "\n  </Labels>"

        result += f'\n  <Text name="{self.text_element}" value="${self.input_text_field}" />\n'

        if self.header and self.header_placement == 'middle':
            result += f'  <Header value="{self.header}" />\n'

        result += f'  <Choices name="{self.class_annotator_element}" toName="{self.text_element}" choice="{self.choice_type}" >\n    '
        choice_tags = [None] * len(self.choice_labels)
        for i, label_dict in enumerate(self.choice_labels):
            attributes = " ".join(f'{key}="{value}"'for key, value in label_dict.items())
            choice_tags[i] = f'<Choice {attributes} />'
        result += '\n    '.join(choice_tags) + "\n  </Choices>\n"

        if self.header and self.header_placement == 'bottom':
            result += f'  <Header value="{self.header}" />\n'
        result += '</View>'
        return result