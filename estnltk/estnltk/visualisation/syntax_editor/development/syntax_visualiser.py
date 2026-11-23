import json
from typing import List
from IPython.display import display_html

from estnltk import Layer
from estnltk.layer.span import Span
from estnltk.converters import layer_to_dict, dict_to_layer
from estnltk.visualisation.core import format_tag_attributes
from estnltk.visualisation.core import header_cell, value_cell, dropdown_cell
from estnltk.taggers import AttributeComparator


class SyntaxVisualiser:
    # attributes = ["id", "text", "lemma", "head", "deprel", "upostag", "xpostag", "feats", "deps", "misc"]
    attributes = []
    changeable_attributes = {'deprel': ['@<KN', '@<NN', '@<P', '@<Q', '@ADVL', '@AN>', '@DN>', '@FCV', '@FMV', '@J', '@NN>', '@OBJ', '@P>', '@PRD', '@Punc', '@SUBJ', '@Vpart', 'ROOT']}

    def __call__(self, layers, text):
        display_html(self.table_creation(layers, self.attributes, text), raw=True)

    @property
    def css_style_tag(self):
        """
        Represents css file through <style> tag
        """
        with open("syntax_visualiser.css") as css_file:
            output = ''.join(["<style>\n", css_file.read(), "</style>"])
        return output

    @property
    def event_handler_script_tag(self):
        """
        Imports event handling code as a <script> tag

        TODO: Add script tag
        """
        with open("syntax_visualiser.js") as js_file:
            contents = js_file.read()
        return contents

    def new_layer_attributes(self, layers, attributes_to_compare, attributes_to_keep):
        attributes = []

        for attribute in attributes_to_keep:
            if attribute == 'head' or attribute in attributes_to_compare:
                attributes.append(attribute)
                for i in range(len(layers)):
                    attributes.append(attribute + "_" + str(i + 1))
            else:
                attributes.append(attribute)

        return attributes


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
        if attribute in self.changeable_attributes:
            values = [(attr, attr) for attr in self.changeable_attributes[attribute]]
            values.insert(0, (span[attribute], span[attribute]) if span[attribute] is not None else ('', ''))

            row.extend(dropdown_cell(values, select_tag_attributes=format_tag_attributes({'class': 'syntax_choice ' + attribute, 'id': attribute + str(i)})))

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

    def table_head_attribute(self, span, sentence, i):
        """
        Inline this code
        """
        default_value = span['head']
        if default_value is None:
            default_choice = (default_value, '')
        elif default_value == 0:
            default_choice = (default_value, '0: ')
        else:
            default_choice = (default_value, str(default_value) + ': ' + sentence[default_value - 1].text)

        values = [default_choice, (None, '0: '), *[(i + 1, "{}: {}".format(i + 1, span.text)) for i, span in enumerate(sentence)]]

        return dropdown_cell(values, select_tag_attributes=format_tag_attributes({'class': 'syntax_choice head', 'id': 'head' + str(i)}))

    def table_creation(self, layers, attributes, text):
        """
        TODO: Separate
        * data injection script
        * DOM modification script
        * event handling script

        """
        # Data injection starts here!
        tables = [self.css_style_tag, "<script>", "var changeable_attribute_count = " + str(len(self.changeable_attributes) + 1) + "\n",
                  "if (typeof all_tables === 'undefined'){\n var all_tables = [];\n} \n else {\n all_tables = [] \n} \n"]

        #new_layer = self.new_layer(layers, "new")
        #map_attr, attr = self.new_layer_attributes(layers, self.changeable_attributes, layers[0].attributes)

        #attr = self.new_layer_attributes(layers, self.changeable_attributes, layers[0].attributes)
        attributes_to_compare = [a for a in self.changeable_attributes]
        attributes_to_compare.insert(0, 'head')
        new_layer = AttributeComparator("new", [layer.name for layer in layers], layers[0].attributes[:-4], attributes_to_compare)\
            .make_layer(layers[0].text_object, {layer.name: layer for layer in layers})

        # this is so attributes would get a working default value, but could also be changed
        if len(self.attributes) == 0:
            self.attributes = list(new_layer.attributes)
            new_layer_attributes = self.attributes
            new_layer_attributes.insert(0, 'text')
        else:
            new_layer_attributes = self.attributes

        for index, sentence in enumerate(text.sentences):

            # TODO: Encapsulate this as a function table_for_sentence
            # Does this function have a wrong output type?
            tables.append("all_tables.push(`<table class=\"iterable-table\">\n")
            tables.extend(self.header(new_layer_attributes, new_layer))

            # TODO: This is wrong way of getting spans of syntax layer
            # Paul, tell us how this should be done correctly!
            for i, span in enumerate(sentence):
                syntax_span = new_layer.get(span)

                tables.append("<tr>")
                # TODO: Inline these functions to get simple code
                for attribute in new_layer_attributes:
                    if attribute == "head":
                        tables.extend(self.table_head_attribute(syntax_span, sentence, i))
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
        converted_all_values = []
        for i in range(len(all_values)):
            for element in all_values[str(i)]:
                converted_all_values.append(json.loads(element))

        new_layer_dict = layer_to_dict(original_layer)
        for index, annotation in enumerate(new_layer_dict['spans']):
            if index < len(converted_all_values):
                for key in converted_all_values[index]:
                    if key != 'id':
                        annotation['annotations'][0][key] = converted_all_values[index][key]

        return dict_to_layer(new_layer_dict, text_object=original_layer.text_object)