# -*- coding: utf-8 -*-

"""
Low-level layer operations for Estnltk Text object.

"""
from operator import eq
from numpy import sort
from pandas import DataFrame

import regex as re
from collections import Counter

#? Sven palus üles kirjutada küsimused, mis koodi silmitsedes tekivad.
#? Kas kõik järgmised konstandid on mõttekad? 
#? UNION on allpool ainult osaliselt kasutusel.
#? ehk võiks enamlevinud konstandid importida

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
#? miks rule_value kasutusel pole
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
#? miks rule_value kasutusel pole
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
            dicts.append({START: start, END: end, 'text': text})
    text_copy[name] = dicts
    return text_copy


def delete_layer(text, layers):
    """Deletes layers in input list but except the 'text' layer. Modifies the *text*."""
    delete = set(text.keys())
    delete.intersection_update(set(layers))
    delete.difference_update({TEXT})
    for layer in delete:
        del text[layer]
    return text


def keep_layer(text, layers):
    """Keeps layers in input list and the 'text' layer. Modifies the *text*."""
    delete = set(text.keys())
    delete.difference_update(layers)
    delete.difference_update({TEXT})
    for layer in delete:
        del text[layer]
    return text


def sort_layer(text, layer, update=False):
    layer_to_sort = text[layer]
    print('Layer to sort: ', layer_to_sort)
    if update:
        layer_sorted = sort(layer_to_sort, key=lambda e: (e[START], e[END]))
#? miks layer_sorted kasutusel pole. ehk võiks selle return-ida? või on siin tahetud kasutada ühel juhul meetodit 'sorted'?
    else:
        return sort(layer_to_sort, key=lambda e: (e[START], e[END]))


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
                    result.append({START: start2, END: end2})
#? kui meetodi nimes on intersection, siis miks siin äkki union
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
                    result.append({START: start2, END: end1})
                elif start1 <= start2 and end1 <= end2:
                    result.append({START: start1, END: end2})
                elif start1 > start2 and end1 < end2:
                    result.append({START: start2, END: end2})
                elif start1 < start2 and end1 > end2:
                    result.append({START: start1, END: end1})

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
                    result.append({START: start1, END: end2})
                elif start1 <= start2 and end1 <= end2:
                    result.append({START: start2, END: end1})
                elif start1 > start2 and end1 < end2:
                    result.append({START: start1, END: end1})
                elif start1 < start2 and end1 > end2:
                    result.append({START: start2, END: end2})
    return result


###############################################################

def get_text(text, start=None, end=None, layer_element=None, span=None):
    """Get text by start and end or by layer_element or by span.

    Parameters
    ----------
    start: int, default: None
    
    end: int, default: None
    
    layer_element: dict, default: None
        dict that contains 'start' and 'end'.
    
    span: (int, int), default: None
    
    Returns
    -------
    str
        Strings that corresponds to given *(start, end)* span. 
        Default values return the whole text.
    """
    if start != None and end != None:
        return text.text[start:end]
    if layer_element != None:
        return text.text[layer_element[START]:layer_element[END]]
    if span != None:
        return text.text[span[0]:span[1]]
    return text.text


def unique_texts(text, layer, sep=' ', order=None):
    """Retrive unique texts of layer optionally ordered.
        
    Parameters
    ----------
    text: Text
        Text that has the layer.
    layer: str
        Name of layer.
    sep: str (default: ' ')
        Separator for multilayer elements.
    order: {None, 'asc', 'desc'} (default: None)
        If 'asc', then the texts are returned in ascending order by unicode lowercase.
        If 'desc', then the texts are returned in descending order by unicode lowercase.
        Else, the texts returned have no particular order.
    
    Returns
    -------
    list of str
        List of unique texts of given layer.
    """
    texts = text.texts(layer, sep)
    if order == None:
        return list(set(texts))
    if order == 'asc':
        return sorted(set(texts), reverse=False, key=str.lower)
    if order == 'desc':
        return sorted(set(texts), reverse=True, key=str.lower)
    raise ValueError('Incorrect order type.')


def count_by(text, layer, attributes, counter=None):
    """Create table of counts for every *layer* *attributes* value combination.
    
    Parameters
    ----------
    text: Text
        Text that has the layer.
    layer: iterable, str
        The layer or the name of the layer which elements have the keys listed in *attributes*.
    attributes: list of str or str
        Name of *layer*'s key or list of *layer*'s key names.
        If *attributes* contains 'text', then the *layer*'s text is found using spans.
    table: collections.defaultdict(int), None, default: None
        If table==None, then new 
        If table!=None, then the table is updated and returned.
    
    Returns
    -------
    collections.Counter
        The keys are tuples of values of attributes. 
        The values are corresponding counts.
    """
    if isinstance(layer, str):
        layer = text[layer]
    if not isinstance(attributes, list):
        attributes = [attributes]
    if counter == None:
        counter = Counter()
    
    for entry in layer:
        key = []
        for a in attributes:
            if a == TEXT:
                key.append(get_text(text, layer_element=entry))
            else:
                key.append(entry[a])
        key = tuple(key)
        counter[key] += 1

    return counter


def count_by_as_df(text, layer, attributes):
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
    table = count_by(text, layer, attributes, {})
    return DataFrame.from_records((a+(count,) for a,count in table.items()), columns=attributes+['count'])

        
def diff_layer(a, b, comp=eq):
    """Generator of layer differences.
        
    Parameters
    ----------
    a and b: list of dict
        Estnltk layer. Must be sorted by *start* and *end* values. 
        No (start, end) dublicates may exist.
    comp: compare function, default: operator.eq
        Function that returns True if layer elements are equal and False otherwise.
        Only layer elements with equal spans are compared.
    
    Returns
    -------
    Generator of different pairs.
    """
    a = iter(a)
    b = iter(b)
    a_end = False
    b_end = False
    try:
        x = next(a)
    except StopIteration:
        a_end = True
    try:
        y = next(b)
    except StopIteration:
        b_end = True
    
    while not a_end and not b_end:
        if x[START] < y[START] or x[START] == y[START] and x[END] < y[END]:
            yield (x, None)
            try:
                x = next(a)
            except StopIteration:
                a_end = True
            continue
        if x[START] == y[START] and x[END] == y[END]:
            if not comp(x, y):
                yield (x, y)
            try:
                x = next(a)
            except StopIteration:
                a_end = True
            try:
                y = next(b)
            except StopIteration:
                b_end = True
            continue
        yield (None, y)
        try:
            y = next(b)
        except StopIteration:
            b_end = True
    
    if a_end:
        while True:
            yield (None, y)
            y = next(b)

    if b_end:
        while True:
            yield (x, None)
            x = next(a)
                

def merge_layer(a, b, fun):
    """Generator of merged layers.
        
    Parameters
    ----------
    a and b: iterable of dict
        Iterable of Estnltk layer elements. Must be ordered by *(start, end)*.
    
    fun: merge function
        Function that merges two layer elements. Must accept one None value.
        Example::

            def fun(x, y):
                if x == None:
                    return y
                return x
            
    Yields
    ------
    generator
        Generator of merged layer elements.
    """
    a = iter(a)
    b = iter(b)
    a_end = False
    b_end = False
    try:
        x = next(a)
    except StopIteration:
        a_end = True
    try:
        y = next(b)
    except StopIteration:
        b_end = True
    
    while not a_end and not b_end:
        if x[START] < y[START] or x[START] == y[START] and x[END] < y[END]:
            yield fun(x, None)
            try:
                x = next(a)
            except StopIteration:
                a_end = True
            continue
        if x[START] == y[START] and x[END] == y[END]:
            yield fun(x, y)
            try:
                x = next(a)
            except StopIteration:
                a_end = True
            try:
                y = next(b)
            except StopIteration:
                b_end = True
            continue
        yield fun(None, y)
        try:
            y = next(b)
        except StopIteration:
            b_end = True

    if a_end and b_end:
        return
    
    if a_end:
        while True:
            yield fun(None, y)
            y = next(b)

    if b_end:
        while True:
            yield fun(x, None)
            x = next(a)


def duplicates_of(head, layer):
    """ Generator of all duplicates (by (start, end) values) of head[0] in layer.
    
    Parameters
    ----------
    head: list
        head[0] is a layer element
    layer: list of dict
        Must be ordered by *(start, end)* values.
    
    Yields
    ------
    head[0] and all duplicates of head[0] in layer.
    """
    
    old_head = head[0]
    yield old_head
    head[0] = next(layer)
    while head[0][START] == old_head[START] and head[0][END] == old_head[END]:
        old_head = head[0]
        yield old_head
        head[0] = next(layer)


def merge_duplicates(layer, merge_fun):
    """ Generate a new layer with no duplicates.
    
    Parameters
    ----------
    layer: iterable
        Must be ordered by *(start, end)* values.
        
    merge_fun: function merge_fun(duplicates)
        duplicates: generator of one or more layer elements

        merge_fun returns merge of duplicates
            
        Example::
            def merge_fun(duplicates):
                result = {}
                for d in duplicates:
                    result.update(d)
                return result
    Yields
    ------
    Layer elements with no span duplicates. 
    Duplicates of input are merged by *merge_fun*.
    """
    head = [next(layer)]
    while True:
        start, end = head[0][START], head[0][END]
        yield merge_fun(duplicates_of(head, layer))
        while (start, end) == (head[0][START], head[0][END]):
            head = [next(layer)]

def conflicts(text, layer):
    """Find conflicts in layer.
    The conflicts are:
    1. The start of the layer element is not a start of a word.
    2. The end of the layer element is not an end of a word.
    3. The layer element ends after the next element starts. This method does not find overlaps between all layer elements.
    
    Yields
    ------
        dict
        Description of the problem.
    """
    if isinstance(layer, str):
        layer = text[layer]
    layer = iter(layer)
    try:
        x = next(layer)
    except StopIteration:
        return
    while True:
        if x['start'] not in text.word_starts:
            if x['end'] not in text.word_ends:
                yield dict(start=x['start'], end=x['end'], problem='B1')
            else:
                yield dict(start=x['start'], end=x['end'], problem='B2')
        elif x['end'] not in text.word_ends:
            yield dict(start=x['start'], end=x['end'], problem='A')

        try:
            y = next(layer)
        except StopIteration:
            return
        if x['end'] > y['start']:
            yield dict(start=x['start'], end=y['end'], problem='overlap')
        x = y
