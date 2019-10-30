import json
from typing import List
from IPython.display import display_html

from estnltk.layer.span import Span
from estnltk.converters import layer_to_dict, dict_to_layer
from estnltk.visualisation.core import format_tag_attributes
from estnltk.visualisation.core import header_cell, value_cell, dropdown_cell
from estnltk import Text


class SyntaxVisualiser:
    attributes = ["id", "text", "lemma", "head", "deprel", "upostag", "xpostag", "feats", "deps", "misc"]
    changeable_attributes = {'deprel': ["@ADVL", "@FCV", "ROOT", "@SUBJ"]}

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

    def new_layer(self, layers):
        new_layer_dict = layer_to_dict(layers[0])
        new_layer_attributes = list(new_layer_dict['attributes'])
        new_layer_attributes.insert(0, 'text')
        if len(layers) == 1:
            new_layer_dict['attributes'] = tuple(new_layer_attributes)

        if len(layers) > 1:
            layers_as_dict = []
            for i, layer in enumerate(layers):
                new_layer_attributes.insert(new_layer_attributes.index('head') + i + 1, 'head' + str(i + 1))
                for attribute in self.changeable_attributes:
                    new_layer_attributes.insert(new_layer_attributes.index(attribute) + i + 1, attribute + str(i + 1))
                new_layer_dict['attributes'] = tuple(new_layer_attributes)
                #new_layer_dict['attributes'] += ('head' + str(i + 1), 'deprel' + str(i + 1))
                layers_as_dict.append(layer_to_dict(layer))

            # This isn't the best and it currently only works if just head and deprel are changeable
            for index, annotation in enumerate(new_layer_dict['spans']):
                deprel_attributes = set()
                head_attributes = set()
                for i, layer in enumerate(layers_as_dict):
                    head = layer['spans'][index]['annotations'][0]['head']
                    deprel = layer['spans'][index]['annotations'][0]['deprel']
                    deprel_attributes.add(deprel)
                    head_attributes.add(head)
                    annotation['annotations'][0]['head' + str(i + 1)] = head
                    annotation['annotations'][0]['deprel' + str(i + 1)] = deprel

                if len(head_attributes) > 1:
                    annotation['annotations'][0]['head'] = None

                if len(deprel_attributes) > 1:
                    annotation['annotations'][0]['deprel'] = None

        #return dict_to_layer(new_layer_dict)
        return dict_to_layer(new_layer_dict, text_object=Text(" ".join(layers[0].text)))


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

            # As I have no imagination I will use integer keys for values
            values = list(enumerate(self.changeable_attributes[attribute]))

            try:
                default_value = self.changeable_attributes[attribute].index(span[attribute])
            except ValueError:
                default_value = 0

            row.extend(dropdown_cell(values, default_value, format_tag_attributes({'class': 'syntax_choice', 'id': attribute + str(i)})))

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
        # I use base spans as keys for values. I hope None is good for root
        values = [(None, '0: ')]
        values.extend([(span.base_span, "{}: {}".format(i + 1, span.text)) for i, span in enumerate(sentence)])

        # Head encoding is compartible with value list
        # This doesn't work when head attribute is None
        default_value = span["head"]

        # This should be removed in the future, for now I added it to check the rest of the table's functionality
        if default_value == None:
            default_value = 0


        return dropdown_cell(values, default_value, format_tag_attributes({'class': 'syntax_choice', 'id': 'head' + str(i)}))


    def data_import_script_tag(self, layers, attributes, text):

        tables = ["<script>",
                  "if (typeof all_tables === 'undefined'){\n var all_tables = [];\n} \n else {\n all_tables = [] \n} \n"]

        # TODO: Use proper namespacing to get rid of this if statement

        for index, sentence in enumerate(text.sentences):

            # TODO: Encapsulate this as a function table_for_sentence
            # Does this function have a wrong output type?
            tables.append("all_tables.push('<table class=\"iterable-table\">")
            tables.extend(self.header(attributes, layers))

            # TODO: This is wrong way of getting spans of syntax layer
            # Paul, tell us how this should be done correctly!
            for i, span in enumerate(sentence):
                syntax_span = layers[0].get(span)

                tables.append("<tr>")
                # TODO: Inline these functions to get simple code
                for attribute in attributes:
                    if attribute == "head":
                        tables.extend(self.table_head_attribute(syntax_span, sentence, i))
                    else:
                        tables.extend(self.table_cell(syntax_span, attribute))
                tables.append("</tr>\n")
            tables.append("</table>'); \n")

        tables.append("</script>")

        return "".join(tables)

    def table_creation(self, layers, attributes, text):
        """
        TODO: Separate
        * data injection script
        * DOM modification script
        * event handling script

        """
        # Data injection starts here!
        tables = [self.css_style_tag, "<script>",
                  "if (typeof all_tables === 'undefined'){\n var all_tables = [];\n} \n else {\n all_tables = [] \n} \n"]

        new_layer = self.new_layer(layers)
        new_layer_attributes = list(new_layer.attributes)
        # This removes deps, misc, parent_span and children from attributes
        new_layer_attributes = new_layer_attributes[0:len(new_layer_attributes) - 4]

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
        for value in all_values:
            for element in all_values[value]:
                converted_all_values.append(json.loads(element))

        new_layer_dict = layer_to_dict(original_layer)
        for index, annotation in enumerate(new_layer_dict['spans']):
            if index < len(converted_all_values):
                for key in converted_all_values[index]:
                    if key != 'id':
                        annotation['annotations'][0][key] = converted_all_values[index][key]

        return dict_to_layer(new_layer_dict)