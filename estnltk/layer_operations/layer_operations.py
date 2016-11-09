"""
Low-level layer operations for Estnltk Text object.

"""
from operator import eq
from numpy import sort
from pandas import DataFrame

import regex as re
from collections import Counter, defaultdict


# ? Sven palus üles kirjutada küsimused, mis koodi silmitsedes tekivad.
# ? Kas kõik järgmised konstandid on mõttekad? 
# ? UNION on allpool ainult osaliselt kasutusel.
# ? ehk võiks enamlevinud konstandid importida
from estnltk.text import Layer

TEXT = 'text'
AND = 'AND'
OR = 'OR'

UNION = 'union'
INTERSECTION = 'intersection'
EXACT = 'exact'

START = 'start'
END = 'end'



#NEW API
def new_layer_with_regex(text, name='', patterns=[], flags=0):
    """Creates new layer to the Text instance with the name the user inputs."""
    spans = []
    for elem in patterns:
        for match in re.finditer(elem, text.text, flags=flags):
            spans.append(match.span())
    layer = Layer.from_span_tuples(name=name, spans=spans)
    text._add_layer(layer)
    return text


# def delete_layer(text, layers):
    # """Deletes layers in input list but except the 'text' layer. Modifies the *text*."""
    # delete = set(text.keys())
    # delete.intersection_update(set(layers))
    # delete.difference_update({TEXT})
    # for layer in delete:
        # del text[layer]
    # return text


# def keep_layer(text, layers):
    # """Keeps layers in input list and the 'text' layer. Modifies the *text*."""
    # delete = set(text.keys())
    # delete.difference_update(layers)
    # delete.difference_update({TEXT})
    # for layer in delete:
        # del text[layer]
    # return text


# def sort_layer(text, layer, update=False):
    # layer_to_sort = text[layer]
    # print('Layer to sort: ', layer_to_sort)
    # if update:
        # layer_sorted = sort(layer_to_sort, key=lambda e: (e[START], e[END]))
# # ? miks layer_sorted kasutusel pole. ehk võiks selle return-ida? või on siin tahetud kasutada ühel juhul meetodit 'sorted'?
    # else:
        # return sort(layer_to_sort, key=lambda e: (e[START], e[END]))



###############################################################

# def get_text(text, start=None, end=None, layer_element=None, span=None, marginal=0):
    # """Get text by start and end or by layer_element or by span.

    # Parameters
    # ----------
    # start: int, default: 0
    
    # end: int, default: len(text.text)
    
    # layer_element: dict, default: None
        # dict that contains 'start' and 'end'.
    
    # span: (int, int), default: None

    # marginal: int, default: 0
        # The number of extra characters at the beginning and at end of the 
        # returned text.
    
    # Returns
    # -------
    # str
        # Strings that corresponds to given *(start, end)* span. 
        # Default values return the whole text.
    # """
    # if layer_element != None:
        # start = layer_element[START]
        # end = layer_element[END]
    # elif span != None:
        # start, end = span
    # if start == None:
        # start = 0
    # if end == None:
        # end = len(text.text)
    # start = max(0, start - marginal)
    # end = min(len(text.text), end + marginal)
    # return text.text[start:end]


#NEW API
def unique_texts(layer, order=None):
    """Retrive unique texts of layer optionally ordered.

    Parameters
    ----------
    layer: Text Layer
    order: {None, 'asc', 'desc'} (default: None)
        If 'asc', then the texts are returned in ascending order by unicode lowercase.
        If 'desc', then the texts are returned in descending order by unicode lowercase.
        The ordering is nondeterministic if the lowercase versions of words are equal. 
        For example the list ['On', 'on'] is both in ascending and descending order. 
        Else, the texts returned have no particular order.

    Returns
    -------
    list of str
        List of unique texts of given layer.
    """
    texts = layer.text
    if order == None:
        return list(set(texts))
    if order == 'asc':
        return sorted(set(texts), reverse=False, key=str.lower)
    if order == 'desc':
        return sorted(set(texts), reverse=True, key=str.lower)
    raise ValueError('Incorrect order type.')


#NEW API
def count_by(layer, attributes, counter=None):
    """Create table of counts for every *layer* *attributes* value combination.
    
    Parameters
    ----------
    layer: Layer
        The layer which elements have the keys listed in *attributes*.
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

    if counter is None:
        counter = Counter()

    for span in layer:
        key = []
        for a in attributes:
            if a == 'text':
                key.append(span.text)
            else:
                key.append(getattr(span, a))
        key = tuple(key)
        counter[key] += 1

    return counter



#NEW API
def diff_layer(a, b, comp=eq):
    """Generator of layer differences.

    Parameters
    ----------
    a and b:
        Layer.
        No (start, end) duplicates may exist.
    comp: compare function, default: operator.eq
        Function that returns True if layer elements are equal and False otherwise.
        Only layer elements with equal spans are compared.

    Yields
    ------
    tuple(dict)
        Pairs of different layer elements. In place of missing layer element,
        None is returned.
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
        if x.start < y.start or x.start == y.start and x.end < y.end:
            yield (x, None)
            try:
                x = next(a)
            except StopIteration:
                a_end = True
            continue
        if x.start == y.start and x.end == y.end:
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

    if a_end and b_end:
        return

    if a_end:
        while True:
            yield (None, y)
            y = next(b)

    if b_end:
        while True:
            yield (x, None)
            x = next(a)



#NEW API
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
    dict
        Merged layer elements.
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
        if x.start < y.start or x.start == y.start and x.end < y.end:
            yield fun(x, None)
            try:
                x = next(a)
            except StopIteration:
                a_end = True
            continue
        if x.start == y.start and x.end == y.end:
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

############################################################
####### OLD API BELOW ######################################
############################################################


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
# ? kui meetodi nimes on intersection, siis miks siin äkki union
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



def apply_simple_filter(text, layer='', restriction='', option=OR):
    """Creates a layer with the options from user input. """
    dicts = []
    if layer == '':
        raise ValueError('Layer attribute cannot be empty.')
# ? milleks siin else
    else:
        if layer not in text.keys():
# ? milleks else
            raise ValueError('Layer not in Text instance.')
        else:
            if restriction == '':
# ? kas sihuke printimene on hea asi
                print('Notice: restriction left empty.')
                return text[layer]
# ? milleks else
            else:
                text_layer = text[layer]
                if option == OR:
                    for list_elem in text_layer:
                        for rule_key, rule_value in restriction.items():
# ? miks rule_value kasutusel pole
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
# ? miks rule_value kasutusel pole
                            if rule_key not in list_elem or restriction[rule_key] != list_elem[rule_key]:
                                condition = False
                                break
                        if condition:
                            dicts.append(list_elem)
                    if dicts == []:
                        print('No results.')
                    return dicts

def count_by_document(text, layer, attributes, counter=None):
    """Create table of counts for every *layer* *attributes* value combination.
    The result is 1 if the combination appears in the document and 0 otherwise.
    
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
    
    keys = set()
    for entry in layer:
        key = []
        for a in attributes:
            if a == TEXT:
                key.append(get_text(text, layer_element=entry))
            else:
                key.append(entry[a])
        key = tuple(key)
        keys.update({key})
    counter.update(keys)

    return counter


def dict_to_df(counter, table_type='keyvalue', attributes=[0, 1]):
    """Convert dict to pandas DataFrame table.
    
    Parameters
    ----------
    counter: dict

    table_type: {'keyvalue', 'cross'}

    attributes: list
        List of key names. Used if table_type=='keyvalue'.
    
    Returns
    -------
    DataFrame
        If table_type=='keyvalue', then the column indexes are attributes plus 
        'count' and the rows contain values of attributes and corresponding count.
    """

    if table_type == 'keyvalue':
        return DataFrame.from_records((a + (count,) for a, count in counter.items()), columns=attributes + ['count'])
    if table_type == 'cross':
        table = defaultdict(dict)
        for (a, b), c in counter.items():
            table[a][b] = c
        return DataFrame.from_dict(table, orient='index').fillna(value=0)


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
    dict
        head[0] and all duplicates of head[0] in layer.
    """

    old_head = head[0]
    yield old_head
    head[0] = next(layer)
    while head[0][START] == old_head[START] and head[0][END] == old_head[END]:
        old_head = head[0]
        yield old_head
        head[0] = next(layer)


def group_by_spans(layer, fun):
    """ Merge elements with equal spans. Generate a new layer with no duplicate spans.
    
    Parameters
    ----------
    layer: iterable
        Must be ordered by *(start, end)* values.
        
    fun: function fun(duplicates)
        duplicates: generator of one or more layer elements

        fun returns merge of duplicates
            
        Example::
            def fun(duplicates):
                result = {}
                for d in duplicates:
                    result.update(d)
                return result
    Yields
    ------
    dict
        Layer elements with no span duplicates. 
        Duplicates of input are merged by *merge_fun*.
    """
    layer = iter(layer)
    head = [next(layer)]
    while True:
        start, end = head[0][START], head[0][END]
        yield fun(duplicates_of(head, layer))
        while (start, end) == (head[0][START], head[0][END]):
            head = [next(layer)]

def conflicts(text, layer, multilayer=True):
    """Find conflicts in layer.
    The conflicts are:
    S: The start of the layer element is not a start of a word.
    E: The end of the layer element is not an end of a word.
    O: The layer element starts before the previous element ends or the layer 
       element ends after the next element starts. This method does not find 
       overlaps between all layer elements.
    M: There is a word start or word end inside the layer element. This is 
       checked if S, E or O is found.

    Parameters
    ----------
    text: Text
        Text that has the layer.
    layer: iterable, str
        The layer or the name of the layer in which the conflicts are searched for.
    multilayer: bool, default True
        If True, yields multilayer elements. First span is the current 
        trouble-maker, rest of the spans are left and right overlap if exist. 
        If False, yields simple layer elements, the span is not affected by 
        overlaps.
    
    Yields
    ------
    dict
        Description of the problem as a layer element. It has keys START, 
        END and 'syndreme'. 'syndrome' is a non-empty subsequence of 
        ['S', 'E', 'O', 'M'].
    """
    if isinstance(layer, str):
        layer = text[layer]
    layer = iter(layer)
    x = None
    try:
        y = next(layer)
    except StopIteration:
        return
    try:
        z = next(layer)
    except StopIteration:
        z = None
    while True:
        syndrome = []
        start = [y[START]]
        end = [y[END]]
        if y[START] not in text.word_starts:
            syndrome.append('S')
        if y[END] not in text.word_ends:
            syndrome.append('E')

        if x!=None and x[END]>y[START]:
            syndrome.append('O')
            start.append(x[START])
            end.append(x[END])
        if z!=None and y[END] > z[START]:
            if 'O' not in syndrome:
                syndrome.append('O')
            start.append(z[START])
            end.append(z[END])
        if len(syndrome) != 0:
            for span in text.word_spans:
                if y[START] < span[0] < y[END] or y[START] < span[1] < y[END]:
                    syndrome.append('M')
                    break
            if multilayer:
                yield {START:start, END:end, 'syndrome':''.join(syndrome)}
            else:
                yield {START:start[0], END:end[0], 'syndrome':''.join(syndrome)}

        if z == None:
            return
        x, y = y, z
        try:
            z = next(layer)
        except StopIteration:
            z = None
