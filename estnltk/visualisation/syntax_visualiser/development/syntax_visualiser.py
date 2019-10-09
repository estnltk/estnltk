import html
from IPython.display import display_html


class SyntaxVisualiser:
    attributes = ["text", "id", "lemma", "upostag", "xpostag", "feats", "head", "deprel", "deps", "misc"]
    deprel = ["@ADVL", "@FCV", "ROOT", "@SUBJ"]

    #def __call__(self, layers,text):
    #    display_html(self.tables(layers, self.attributes, self.deprel, text), raw=True)

    def __call__(self, layers, text):
        display_html(self.test(layers, self.attributes, self.deprel, text), raw=True)

    def css(self):
        with open("syntax_visualiser.css") as css_file:
            contents = css_file.read()
            output = ''.join(["<style>\n", contents, "</style>"])
        return output

    def event_handler_code(self):
        with open("syntax_visualiser.js") as js_file:
            contents = js_file.read()
            # output = ''.join(["<script>\n var text_id=", str(self._text_id),"\n", contents, "</script>"])
        return contents

    def table_column(self, layers, attribute, deprel, text, index=None, sentence=None):
        cellid = 0
        if sentence is None:
            sentence = 0
        word = 0
        if index is not None:
            table_elements = ["<td><table><tr><th>", attribute, str(index), "</th></tr>"]
        else:
            table_elements = ["<td><table><tr><th>", attribute, "</th></tr>"]
        if attribute == "feats":
            for element in getattr(layers, attribute):
                table_elements.extend(
                    ["<tr><td id = \"", str(attribute), str(sentence), ";", str(index), ";", str(cellid), "\">"])
                cellid += 1
                if element is not None:
                    for key in element:
                        table_elements.extend([str(key), " "])
                else:
                    table_elements.append(str(element))
                table_elements.append("</td></tr>")
        elif attribute == "deprel" and index == 1:
            for element in getattr(layers, attribute):
                table_elements.extend(
                    ["<tr><td id = \"", str(attribute), str(sentence), ";", str(index), ";", str(cellid), "\">"])
                cellid += 1
                table_elements.extend(
                    ["<select class = \"syntax_choice\" id = \"deprel", str(sentence), ";", str(index), ";",
                     str(cellid), "\"><option value=\"", str(cellid), ";original\">", html.escape(element),
                     "</option>"])
                for deprel_element in deprel:
                    if element != deprel_element:
                        table_elements.extend(
                            ["<option value=", str(sentence), ";", str(cellid), ";", deprel_element, ">",
                             str(deprel_element), "</option>"])
                table_elements.extend(["</select>", "</td></tr>"])
        elif attribute == "head":
            for element in getattr(layers, attribute):
                if word == len(text.sentences[sentence]):
                    word = 0
                    sentence += 1
                if index == 1:
                    table_elements.extend(
                        ["<tr><td id = \"", str(attribute), str(sentence), ";", str(index), ";", str(cellid), "\">"])
                    cellid += 1
                    #muuda seda
                    if element == 0:
                        table_elements.extend(
                            ["<select class = \"syntax_choice\" id=\"head", str(sentence), ";", str(index), ";",
                             str(cellid), " onchange=\"get_select_value();\"><option value=\"", str(cellid),
                             ";original\">",
                             str(element), "</option>"])
                    else:
                        table_elements.extend(
                            ["<select class = \"syntax_choice\" id=\"head", str(sentence), ";", str(index), ";",
                             str(cellid), " onchange=\"get_select_value();\"><option value=\"", str(cellid),
                             ";original\">",
                             str(element), ": ", str(text.sentences[sentence].text[element - 1]),
                             "</option><option value=\"", str(cellid), ";0\">", "0", "</option>"])

                    for i in range(len(text.sentences[sentence])):
                        table_elements.extend(
                            ["<option value=", str(sentence), ";", str(cellid), ";", str(i + 1), ">", str(i + 1), ": ",
                             str(text.sentences[sentence].text[i]), "</option>"])
                else:
                    if element != 0:
                        table_elements.extend(
                            ["<tr><td id = \"", str(attribute), str(sentence), ";", str(index), ";", str(cellid), "\">",
                             str(element), ": ", str(text.sentences[sentence].text[element - 1])])
                    else:
                        table_elements.extend(
                            ["<tr><td id = \"", str(attribute), str(sentence), ";", str(index), ";", str(cellid), "\">",
                             str(element)])
                    cellid += 1
                word += 1
                table_elements.append("</select></td></tr>")
        else:
            for element in getattr(layers, attribute):
                table_elements.extend(
                    ["<tr><td id = \"", str(attribute), str(sentence), ";", str(index), ";", str(cellid), "\">",
                     str(element), "</td></tr>"])
                cellid += 1
        table_elements.append("</table></td>")
        return table_elements

    def table(self, layer, attributes, deprel, text):
        table_elements = [self.css(), "<table class=\"iterable-table\"><tr>"]
        for attribute in attributes:
            table_elements.extend(self.table_column(layer, attribute, deprel, text))
        table_elements.append("</tr></table>")
        return "".join(table_elements)

    def joint_table(self, layers, attributes, deprel, text, sentence=None):
        table_elements = [self.css(), self.event_handler_code(), "<table class=\"iterable-table\"><tr>"]
        for attribute in attributes:
            for i, layer in enumerate(layers):
                if attribute == "head" or attribute == "deprel":
                    table_elements.extend(self.table_column(layer, attribute, deprel, text, i + 1, sentence))
                elif i == 0:
                    table_elements.extend(self.table_column(layer, attribute, deprel, text, None, sentence))
        table_elements.append("</tr></table><button type=\"button\">save</button>")
        return "".join(table_elements)

    # def one_table(layers, attributes, deprel, text):
    #    tables = []
    #    for i in range(len(text.sentences)):
    #        tables.append(joint_table(layers, attributes, deprel, text, i))
    #    return "".join(tables)

    def tables(self, layers, attributes, deprel, text, sentence=None):
        start = 0
        end = 0
        tables = [self.css(), "<script>"]
        tables.append("console.log(typeof all_tables); \n if (typeof all_tables === 'undefined'){\n var all_tables = [];\n} \n else {\n all_tables = [] \n} \n")
        for index, sentence in enumerate(text.sentences):
            start = end
            end = start + len(sentence)
            table_elements = ["all_tables.push('<table class=\"iterable-table\"><tr>"]
            for attribute in attributes:
                for i, layer in enumerate(layers):
                    if attribute == "head" or attribute == "deprel":
                        table_elements.extend(
                            self.table_column(layer[start:end], attribute, deprel, text, i + 1, index))
                    elif i == 0:
                        table_elements.extend(self.table_column(layer[start:end], attribute, deprel, text, None, index))
            table_elements.append("</tr></table>'); \n")
            tables.extend(table_elements)
        tables.append(self.event_handler_code())
        tables.append("</script>")
        tables.append(
            "<button type=\"button\" id=\"save\">save</button><button type=\"button\" id=\"previous\">previous</button><button type=\"button\" id=\"next\">next</button>")
        return "".join(tables)

    def saving(self, saved_info, text, layer_count):
        info = saved_info.split(",")
        separated_info = []
        start = 0
        end = 0
        for sentence in text.sentences:
            sentence_info = []
            start = end
            end = start + len(sentence) * layer_count
            for i in range(start, end):
                sentence_info.append(info[i])
            separated_info.append(sentence_info)
        return separated_info

    def test(self, layers, attributes, deprel, text):
        cellid = 0
        start = 0
        end = 0
        #tables = [self.css()]
        tables = [self.css(), "<script>"]
        tables.append("console.log(typeof all_tables); \n if (typeof all_tables === 'undefined'){\n var all_tables = [];\n} \n else {\n all_tables = [] \n} \n")
        for index, sentence in enumerate(text.sentences):
            start = end
            end = start + len(sentence)
            #tables.append("<table><tr>")
            tables.append("all_tables.push('<table class=\"iterable-table\"><tr>")
            for attribute in attributes:
                tables.extend(["<th>", attribute, "</th>"])
            tables.append("</tr>")
            for i in range(len(sentence)):
                tables.append("<tr>")
                for attribute in attributes:
                    if attribute == "feats":
                        tables.append("<td>")
                        element = layers[0][start:end][str(attribute)][i]
                        if element is None:
                            tables.append(str(element))
                        else:
                            for key in element:
                                tables.extend([str(key), " "])
                        tables.append("</td>")


                    elif attribute == "deprel":
                        tables.append("<td>")
                        element = layers[0][start:end][str(attribute)][i]
                        tables.extend(
                            ["<select class = \"syntax_choice\" id = \"deprel", str(i), ";",
                             str(cellid), "\"><option value=\"", str(cellid), ";original\">", html.escape(element),
                             "</option>"])
                        for deprel_element in deprel:
                            if element != deprel_element:
                                tables.extend(
                                    ["<option value=", str(cellid), ";", deprel_element, ">",
                                     str(deprel_element), "</option>"])
                        tables.extend(["</select>", "</td>"])


                    elif attribute == "head":
                        tables.append("<td>")
                        element = layers[0][start:end][str(attribute)][i]
                        tables.extend(["<select class = \"syntax_choice\" id=\"head", str(i), ";",
                             str(cellid), "\"><option value=\"", str(cellid),
                             ";original\">"])
                        if element == 0:
                            tables.append(str(element))
                        else:
                            tables.extend([str(element), ": ", str(sentence.text[element - 1])])
                        tables.extend(["</option><option value=\"", str(cellid), ";0\">", "0", "</option>"])

                        for j in range(len(sentence)):
                            tables.extend(
                                ["<option value=", str(cellid), ";", str(j + 1), ">", str(j + 1),
                                 ": ",
                                 str(sentence.text[j]), "</option>"])


                    else:
                        tables.extend(["<td>", str(layers[0][start:end][str(attribute)][i]), "</td>"])
                tables.append("</tr>")
            tables.append("</table>'); \n")
            #tables.append("</table>")
        tables.append(self.event_handler_code())
        tables.append("</script>")
        tables.append(
            "<button type=\"button\" id=\"save\">save</button><button type=\"button\" id=\"previous\">previous</button><button type=\"button\" id=\"next\">next</button>")
        return "".join(tables)