# -*- coding: utf-8 -*-

"""
Low-level layer operations for Estnltk Text object.

"""
from numpy import sort
from pprint import pprint

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
