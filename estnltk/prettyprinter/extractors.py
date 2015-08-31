# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from ..names import *

# TODO: define extractor and create the architecture
def check_word_tags(elem, values):
    # Perfoms a check if current word has any tags
    variable = elem['analysis'][0]
    # If tags are name based
    for values_key, values_value in dict(values).items():
        if isinstance(elem['text'], list):
            for el in elem['text']:
                if values_key == el:
                    return values_value
        else:
            if values_key == elem['text']:
                return values_value
    # If Tags are anything alse
    for key, value in variable.items():
        for values_key, values_value in values.items():
            if isinstance(value, list):
                for el in value:
                    if values_key == el:
                        return values_value
            else:
                if values_key == value:
                    return values_value

def lemmas(elem, values):
    pass


def postags(elem, values):
    pass

...

# TODO: come up with stuff that could be useful for users.
# Just make a best guess what might be useful.


def timex_types():
    pass

