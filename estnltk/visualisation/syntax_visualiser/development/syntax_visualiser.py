import html
from IPython.display import display_html
import json
from estnltk.converters import layer_to_dict, dict_to_layer


class SyntaxVisualiser:
    attributes = ["id", "text", "lemma", "head", "deprel", "upostag", "xpostag", "feats", "deps", "misc"]
    changeable_attributes = {'deprel': ["@ADVL", "@FCV", "ROOT", "@SUBJ"]}

    def __call__(self, layers, text):
        display_html(self.table_creation(layers, self.attributes, text), raw=True)

    def css(self):
        with open("syntax_visualiser.css") as css_file:
            contents = css_file.read()
            output = ''.join(["<style>\n", contents, "</style>"])
        return output

    def event_handler_code(self):
        with open("syntax_visualiser.js") as js_file:
            contents = js_file.read()
        return contents


    def header(self, attributes, layers):
        row = ["<tr>"]
        for attribute in attributes:
            if attribute == "head" or attribute in self.changeable_attributes:
                row.extend(["<th>", attribute, "</th>"])
                for i in range(len(layers)):
                    row.extend(["<th>", attribute, str(i + 1), "</th>"])
            else:
                row.extend(["<th>", attribute, "</th>"])
        row.append("</tr>")
        return row

    def table_row(self, attribute, layers, start, end, i):
        row = []
        if attribute == "feats":
            row.append("<td>")
            element = layers[0][start:end][str(attribute)][i]
            if element is None:
                row.append(str(element))
            else:
                for key in element:
                    row.extend([str(key), " "])
            row.append("</td>")
        elif attribute in self.changeable_attributes:
            dropdown_elements = []
            for layer in layers:
                dropdown_value = layer[start:end][str(attribute)][i]
                if dropdown_value not in dropdown_elements:
                    dropdown_elements.append(dropdown_value)
            row.append("<td>")
            row.extend(
                ["<select class = \"syntax_choice\" id = \"", attribute, str(i), "\"><option value=\"original", str(attribute), "\">"])
            if len(dropdown_elements) == 1:
                row.append(html.escape(dropdown_elements[0]))
            row.append("</option>")
            for value in self.changeable_attributes[attribute]:
                # if element != deprel_element:
                row.extend(
                    ["<option value=\"", attribute, str(value), "\">",
                     str(value), "</option>"])
            row.extend(["</select>", "</td>"])
            for layer in layers:
                row.extend(["<td>", html.escape(str(layer[start:end][str(attribute)][i])), "</td>"])
        else:
            row.extend(["<td>", str(layers[0][start:end][str(attribute)][i]), "</td>"])
        return row

    def table_head(self, sentence, layers, start, end, i):
        row = []
        head_elements = []
        for layer in layers:
            head_element = layer[start:end]["head"][i]
            if head_element not in head_elements:
                head_elements.append(head_element)
        row.append("<td>")
        row.extend(["<select class = \"syntax_choice\" id=\"head", str(i), "\"><option value=\"head\">"])
        if len(head_elements) == 1:
            row.append(str(head_elements[0]))
            if head_elements[0] != 0:
                row.extend([": ", str(sentence.text[head_elements[0] - 1])])
        row.extend(["</option><option value=\"head", str(i), "\">", "0", "</option>"])

        for j in range(len(sentence)):
            row.extend(
                ["<option value=\"head", str(j + 1), "\">", str(j + 1),
                 ": ",
                 str(sentence.text[j]), "</option>"])

        row.append("</select></td>")

        for layer in layers:
            td_text = layer[start:end]["head"][i]
            if td_text == 0:
                row.extend(["<td>", str(td_text), "</td>"])
            else:
                row.extend(["<td>", str(td_text), ": ", sentence.text[td_text - 1], "</td>"])
        return row

    def table_creation(self, layers, attributes, text):
        start = 0
        end = 0
        tables = [self.css(), "<script>"]
        tables.append("if (typeof all_tables === 'undefined'){\n var all_tables = [];\n} \n else {\n all_tables = [] \n} \n")
        for index, sentence in enumerate(text.sentences):
            start = end
            end = start + len(sentence)
            tables.append("all_tables.push('<table class=\"iterable-table\">")
            table_header = self.header(attributes, layers)
            tables.extend(table_header)
            for i in range(len(sentence)):
                tables.append("<tr>")
                for attribute in attributes:
                    if attribute == "head":
                        tables.extend(self.table_head(sentence, layers, start, end, i))
                    else:
                        tables.extend(self.table_row(attribute, layers, start, end, i))
                tables.append("</tr>")
            tables.append("</table>'); \n")
        tables.append(self.event_handler_code())
        tables.append("</script>")
        tables.append(
            "<button type=\"button\" id=\"save\">save</button><button type=\"button\" id=\"previous\">previous</button><button type=\"button\" id=\"next\">next</button>")
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