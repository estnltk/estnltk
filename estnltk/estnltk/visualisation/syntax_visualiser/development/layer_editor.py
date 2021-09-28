import os
import json
from typing import List
from IPython.display import display_html

from estnltk.common import abs_path
from estnltk.layer.span import Span
from estnltk.converters import layer_to_dict, dict_to_layer
from estnltk.visualisation.core import format_tag_attributes
from estnltk.visualisation.core import header_cell, value_cell, dropdown_cell
from estnltk.visualisation.syntax_visualiser.development.syntax_editor import SyntaxEditor


class LayerEditor:
    attributes = []

    def __init__(self, dropdown_values = [], dropdown_from_attributes = []):
        self.dropdown_values = dropdown_values
        self.dropdown_from_attributes = dropdown_from_attributes

    def __call__(self, layers, input_attributes, attributes_to_compare):
        syntax_editor = SyntaxEditor(layers, input_attributes, attributes_to_compare)
        self.layer = syntax_editor.layer
        display_html(self.table_creation(self.layer, self.layer.attributes, self.layer.text_object), raw=True)

    @property
    def css_style_tag(self):
        css_file = abs_path("visualisation/syntax_visualiser/development/syntax_visualiser.css")
        """
        Represents css file through <style> tag
        """
        with open(css_file) as css_file:
            output = ''.join(["<style>\n", css_file.read(), "</style>"])
        return output

    @property
    def event_handler_script_tag(self):
        js_file = abs_path("visualisation/syntax_visualiser/development/syntax_visualiser.js")
        """
        Imports event handling code as a <script> tag

        TODO: Add script tag
        """
        with open(js_file) as js_file:
            contents = js_file.read()
        return contents

    def header(self, attributes: List[str], layer) -> List[str]:
        row = ["<tr>"]
        for attribute in attributes:
            row.append(header_cell(attribute))
        row.append("</tr>")
        return row

    def table_cell(self, span: Span, attribute: str, i) -> List[str]:
        """
        This is a temporary function that should be inlined to the code
        """
        row = []
        if attribute in self.dropdown_values:
            values = [(attr, attr) for attr in self.dropdown_values[attribute]]
            values.insert(0, (span[attribute], span[attribute]) if span[attribute] is not None else ('', ''))

            row.extend(dropdown_cell(values, select_tag_attributes=format_tag_attributes(
                {'class': 'syntax_choice ' + attribute, 'id': attribute + str(i)})))

        elif attribute == "text":
            # This is a funky exception. Text is not an attribute! but a property
            # TODO: Correct this. How is jet unknown
            row.append(value_cell(span.text))
        else:
            # value_cell(span[attribute]) leaves cell blank when span[attribute] is 0
            if span[attribute] == 0:
                row.append(value_cell(str(span[attribute])))
            else:
                row.append(value_cell(span[attribute]))
        return row

    def table_head_attribute(self, attr, span, sentence, i):
        """
        Inline this code
        """
        default_value = span[attr]
        if default_value is None:
            default_choice = (default_value, '')
        elif default_value == 0:
            default_choice = (default_value, '0: ')
        else:
            default_choice = (default_value, str(default_value) + ': ' + sentence[default_value - 1].text)
            #default_choice = (default_value, str(default_value) + ': ' + sentence[sentence.text.index(span.text)].text)

        values = [default_choice, (None, '0: '),
                  *[(i + 1, "{}: {}".format(i + 1, span.text)) for i, span in enumerate(sentence)]]

        return dropdown_cell(values, select_tag_attributes=format_tag_attributes(
            {'class': 'syntax_choice head', 'id': attr + str(i)}))

    def table_creation(self, layer, attributes, text):
        """
        TODO: Separate
        * data injection script
        * DOM modification script
        * event handling script

        """
        # Data injection starts here!
        tables = [self.css_style_tag, "<script>",
                  "var changeable_attribute_count = " + str(len(self.dropdown_values) + 1) + "\n",
                  "if (typeof all_tables === 'undefined'){\n var all_tables = [];\n} \n else {\n all_tables = [] \n} \n"]


        # this is so attributes would get a working default value, but could also be changed
        if len(self.attributes) == 0:
            self.attributes = list(layer.attributes)
            layer_attributes = self.attributes
            layer_attributes.insert(0, 'text')
        else:
            layer_attributes = self.attributes

        for index, sentence in enumerate(text.sentences):

            # TODO: Encapsulate this as a function table_for_sentence
            # Does this function have a wrong output type?
            tables.append("all_tables.push(`<table class=\"iterable-table\">\n")
            tables.extend(self.header(layer_attributes, layer))

            # TODO: This is wrong way of getting spans of syntax layer
            # Paul, tell us how this should be done correctly!
            for i, span in enumerate(sentence):
                syntax_span = layer.get(span)

                tables.append("<tr>")
                # TODO: Inline these functions to get simple code
                for attribute in layer_attributes:
                    if attribute in self.dropdown_from_attributes:
                        tables.extend(self.table_head_attribute(attribute, syntax_span, sentence, i))
                    else:
                        tables.extend(self.table_cell(syntax_span, attribute, i))
                tables.append("</tr>\n")
            tables.append("</table>`); \n")
        # Data injection ends here!

        # Event handling starts here!
        tables.append(self.event_handler_script_tag)
        tables.append("</script>")
        # Event handling ends here!

        # Here we add buttons
        tables.append(
            "<button type=\"button\" id=\"save\">save</button><button type=\"button\" id=\"previous\">previous</button><button type=\"button\" id=\"next\">next</button>")
        # end buttons

        return "".join(tables)

    def create_layer_from_choices(self, all_values, original_layer):
        text = original_layer.text_object
        converted_all_values = {}
        for i in all_values.keys():
            for element in all_values[i]:
                start = 0
                for sentence in text.sentences[:int(i)]:
                    start += len(sentence)
                if start not in converted_all_values:
                    converted_all_values[start] = []
                converted_all_values[start].append(json.loads(element))

        new_layer_dict = layer_to_dict(original_layer)

        for index in range(len(new_layer_dict['spans'])):
            if index in converted_all_values:
                values_index = index
                for element in converted_all_values[values_index]:
                    for key in element:
                        if key != 'id':
                            new_layer_dict['spans'][index]['annotations'][0][key] = element[key]
                    index += 1

        return dict_to_layer(new_layer_dict, text_object=original_layer.text_object)
