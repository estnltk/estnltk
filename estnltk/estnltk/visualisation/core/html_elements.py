from html import escape
from collections.abc import Iterable
from typing import Any, Dict, List, Tuple, Union


def format_tag_attributes(attributes: Dict[str, str]) -> str:
    """
    Converts attribute dictionary to string that can be inserted to an HTML tag
    """
    return " ".join(['{}="{}"'.format(key, value) for key, value in attributes.items()])


def header_cell(header: str) -> str:
    """
    Creates a simple <th> cell for the header that is HTML escaped if needed.
    """
    return "<th>{}</th>".format(escape(header))


def value_cell(value: Union[Iterable, Any]) -> str:
    """
    Creates a simple <td> cell representing the value.

    If the value is list then values will be separated by space.
    All values are HTML escaped if needed.
    """
    if isinstance(value, str):
        return "<td>{0}</td>".format(escape(value))
    elif isinstance(value, Iterable):
        return "<td>{0}</td>".format(" ".join([escape(str(element)) for element in value]))
    elif value:
        return "<td>{0}</td>".format(escape(str(value)))
    else:
        return "<td></td>"


def dropdown_cell(values: List[Tuple], default_choice: int = 0, select_tag_attributes: str = "") -> List[str]:
    """
    Creates <td> cell with a dropdown selection element.

    :param values:  list of key-value tuples
    :param default_choice: index of initial choice
    :param select_tag_attributes: HTML attributes for <select> tag

    The key in the key-value tuple will be the value attribute for the <option> tag generated for the value.
    All values are HTML escaped if needed.
    """

    if not values:
        raise ValueError('values list cannot be empty')

    if select_tag_attributes:
        row = ["<td><select ", select_tag_attributes, ">"]
    else:
        row = ["<td><select>"]

    default_choice = max(0, default_choice) if default_choice < len(values) else 0

    row.append('<option value="{}">{}</option>'
               .format(escape(str(values[default_choice][0])), escape(str(values[default_choice][1]))))
    row.extend('<option value="{}">{}</option>'
               .format(escape(str(value[0])), escape(str(value[1]))) for value in values[:default_choice])
    row.extend('<option value="{}">{}</option>'
               .format(escape(str(value[0])), escape(str(value[1]))) for value in values[default_choice + 1:])

    row.append("</select></td>")
    return row
