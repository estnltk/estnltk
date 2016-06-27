# -*- coding: utf-8 -*-

"""
Low-level layer operations for Estnltk Text object.

"""
from numpy import sort
from pandas import DataFrame

import regex as re

TEXT = 'text'
AND = 'AND'
OR = 'OR'

UNION = 'union'
INTERSECTION = 'intersection'
EXACT = 'exact'

START = 'start'
END = 'end'


def apply_simple_filter(text, layer='', restriction='', option=OR):
    """Creates a layer with the options from user input. """
    dicts = []
    if layer == '':
        raise ValueError('Layer attribute cannot be empty.')
    else:
        if layer not in text.keys():
            raise ValueError('Layer not in Text instance.')
        else:
            if restriction == '':
                print('Notice: restriction left empty.')
                return text[layer]
            else:
                text_layer = text[layer]
                if option == OR:
                    for list_elem in text_layer:
                        for rule_key, rule_value in restriction.items():
                            if rule_key in list_elem and restriction[rule_key] == list_elem[rule_key]:
                                if list_elem not in dicts:
                                    dicts.append(list_elem)
                    if dicts == []:
                        print('No results.')
                    return dicts
                if option == AND:
                    for list_elem in text_layer:
                        condition = True
                        for rule_key, rule_value in restriction.items():
                            if rule_key not in list_elem or restriction[rule_key] != list_elem[rule_key]:
                                condition = False
                                break
                        if condition:
                            dicts.append(list_elem)
                    if dicts == []:
                        print('No results.')
                    return dicts


def new_layer_with_regex(text, name='', pattern=[], flags=0):
    """Creates new layer to the Text instance with the name the user inputs."""
    text_copy = {k: v for k, v in text.items()}
    dicts = []
    for elem in pattern:
        matches = re.finditer(elem, text_copy['text'])
        for match in matches:
            start = match.span()[0]
            end = match.span()[1]
            text = match.group()
            dicts.append({'start': start, 'end': end, 'text': text})
    text_copy[name] = dicts
    return text_copy


def delete_layer(text, layers):
    """Deletes layers in input list, creates a copy of text instance by default."""
    text_copy = {k: v for k, v in text.items()}
    keys = text_copy.keys()
    for layer in layers:
        if layer == TEXT:
            continue
        elif layer in keys:
            del text_copy[layer]
        else:
            print("Layers not found:  %s" % layer)
    return text_copy


def keep_layer(text, layers):
    """Keeps layers in input list, creates a copy of text instance by default."""
    text_copy = {k: v for k, v in text.items()}
    keys = text_copy.keys()
    for layer in layers:
        if layer not in keys:
            print("Layers not found:  %s" % layer)
    for key in list(keys):
        if key == TEXT:
            continue
        if key not in layers:
            del text_copy[key]
    return text_copy


def sort_layer(text, layer, update=False):
    layer_to_sort = text[layer]
    print('Layer to sort: ', layer_to_sort)
    if update:
        layer_sorted = sort(layer_to_sort, key=lambda e: (e['start'], e['end']))
    else:
        return sort(layer_to_sort, key=lambda e: (e['start'], e['end']))


def compute_layer_intersection(text, layer1, layer2, method='union'):
    """Calculates the intersection of two layers in the input, by default method union is used."""
    first = text[layer1]
    second = text[layer2]
    result = []
    method = method.lower()
    if method == EXACT:
        for element1 in first:
            start1 = element1[START]
            end1 = element1[END]
            for element2 in second:
                start2 = element2[START]
                end2 = element2[END]
                if start1 == start2 and end1 == end2:
                    result.append({'start': start2, 'end': end2})

    if method == UNION:
        for element1 in first:
            start1 = element1[START]
            end1 = element1[END]
            for element2 in second:
                start2 = element2[START]
                end2 = element2[END]
                if end2 < start1 or end1 < start2:
                    pass
                elif start1 >= start2 and end1 >= end2:
                    result.append({'start': start2, 'end': end1})
                elif start1 <= start2 and end1 <= end2:
                    result.append({'start': start1, 'end': end2})
                elif start1 > start2 and end1 < end2:
                    result.append({'start': start2, 'end': end2})
                elif start1 < start2 and end1 > end2:
                    result.append({'start': start1, 'end': end1})

    if method == INTERSECTION:
        for element1 in first:
            start1 = element1[START]
            end1 = element1[END]
            for element2 in second:
                start2 = element2[START]
                end2 = element2[END]
                if end2 <= start1 or end1 <= start2:
                    pass
                elif start1 >= start2 and end1 >= end2:
                    result.append({'start': start1, 'end': end2})
                elif start1 <= start2 and end1 <= end2:
                    result.append({'start': start2, 'end': end1})
                elif start1 > start2 and end1 < end2:
                    result.append({'start': start1, 'end': end1})
                elif start1 < start2 and end1 > end2:
                    result.append({'start': start2, 'end': end2})
    return result


###############################################################


def unique_sorted_texts(text, layer, sep=' ', reverse=False):
    """
    Retrive unique sorted texts of layer.
        
    Parameters
    ----------
    text: Text
        Text that has the layer.
    layer: str
        Name of layer.
    sep: str (default: ' ')
        Separator for multilayer elements.
    reverse: boolean (default: False)
        If True, then the texts are returned in descending order.
    
    Returns
    -------
    list of str
        List of unique strings in given layer sorted by UTF-8 lowercase.
    """
    texts = text.texts(layer, sep)
    return sorted(set(texts), reverse=reverse, key=str.lower)


def tabulate_attribute_values(text, layer, attributes):
    """Create table of *layer*'s *attributes* value counts.
    
    Parameters
    ----------
    text: Text
        Text that has the layer.
    layer: str
        Name of the layer that has the keys *attributes*.
    attributes: list of str or str
        Name of *layer*'s key or list of *layer*'s key names.
        If *attributes* contains 'text', then the *layer*'s text is found using spans.
    
    Returns
    -------
    DataFrame
        DataFrame table. The column indexes are attributes plus 'count'.
        The rows contain values of attributes and corresponding count.
    """
    if not isinstance(attributes, list):
        attributes = [attributes]
    table = {}
    
    if 'text' in attributes:
        for entry, span_text in zip(text[layer], text.texts_from_spans(text.spans(layer))):
            key = []
            for a in attributes:
                if a == 'text':
                    key.append(span_text)
                else:
                    key.append(entry[a])
            key = tuple(key)
            table[key] = table.setdefault(key, 0) + 1
    else:
        for entry in text[layer]:
            key = tuple(entry[a] for a in attributes)        
            table[key] = table.setdefault(key, 0) + 1

    table = DataFrame.from_records((a+(count,) for a,count in table.items()), columns=attributes+['count'])

    return table


def diff_layer(a, b):
    """Generator of layer differences.
    
    Parameters
    ----------
    a and b: list of dict
        Estnltk layer. Must be sorted by *start* value. *start* value may not repeat.
    
    Returns
    -------
    generator
    """
    i = 0
    j = 0
    while i < len(a):
        if j >= len(b):
            yield (a[i], None)
            i += 1
            continue
        if a[i] == b[j]:
            i += 1
            j += 1
            continue
        if a[i]['start'] < b[j]['start']:
            yield (a[i], None)
            i += 1
            continue
        if a[i]['start'] > b[j]['start']:
            yield (None, b[j])
            j += 1
            continue
        yield (a[i], b[j])
        i += 1
        j += 1
    while j < len(b):
        yield (None, b[j])
        j += 1
        
        
def merge_layer(a, b, fun):
    # pooleli
    i = 0
    j = 0
    while i < len(a):
        if j >= len(b):
            yield a[i]
            i += 1
            continue
        if a[i] == b[j]:
            yield a[i]
            i += 1
            j += 1
            continue
        if a[i]['start'] < b[j]['start']:
            yield a[i]
            i += 1
            continue
        yield b[j]
        j += 1
    while j < len(b):
        yield b[j]
        j += 1
