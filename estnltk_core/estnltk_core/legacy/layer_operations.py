from typing import Container
from itertools import groupby
from collections import Counter

from pandas import DataFrame

from estnltk_core.layer.layer import Layer, SpanList

#
#  Legacy layer operation, relocated from:
#  https://github.com/estnltk/estnltk/blob/217b0071829ec18f0769aa6b3228daab14bbfbe3/estnltk_core/estnltk_core/layer_operations/layer_filtering.py
# 

def apply_filter(layer: Layer, function: callable, preserve_spans: bool = False, drop_immediately: bool = False):
    '''Applies a filtering function on layer: all annotations not passing the function will be deleted.
    
       The function parameter is a callable that takes three parameters: Layer, span index and annotation index. 
       
       Setting preserve_spans=True forces to keep at least one annotation for every span.
       Setting drop_immediately=True causes the annotation to be immediately removed after the check-up with 
       the function ( TODO: probably we should to remove this option, as a non-recommended one? ).
    '''
    if drop_immediately:
        i = 0
        while i < len(layer):
            j = 0
            while j < len(layer[i].annotations):
                if preserve_spans and len(layer[i].annotations) == 1:
                    break
                if function(layer, i, j):
                    j += 1
                    continue
                if len(layer[i].annotations) == 1:
                    del layer[i].annotations[j]
                    i -= 1
                    break
                else:
                    del layer[i].annotations[j]
            i += 1
    else:
        to_remove = []
        for i, span in enumerate(layer):
            for j, annotation in enumerate(span.annotations):
                if not function(layer, i, j):
                    to_remove.append((i, j))
        for i, j in reversed(to_remove):
            if not preserve_spans or len(layer[i].annotations) > 1:
                del layer[i].annotations[j]


def drop_annotations(layer: Layer, attribute: str, values: Container, preserve_spans: bool=False):
    '''Drops only those annotations from the layer that have certain attribute values.
       Setting preserve_spans=True forces to keep at least one annotation for every span.'''
    to_remove = []

    for i, span in enumerate(layer):
        for j, annotation in enumerate(span.annotations):
            if getattr(annotation, attribute) in values:
                to_remove.append((i, j))
    for i, j in reversed(to_remove):
        if not preserve_spans or len(layer[i].annotations) > 1:
            del layer[i].annotations[j]


def keep_annotations(layer: Layer, attribute: str, values: Container, preserve_spans: bool=False):
    '''Keeps only those annotations in the layer that have certain attribute values.
       Setting preserve_spans=True forces to keep at least one annotation for every span.'''
    to_remove = []

    for i, span in enumerate(layer):
        for j, annotation in enumerate(span.annotations):
            if getattr(annotation, attribute) not in values:
                to_remove.append((i, j))
    for i, j in reversed(to_remove):
        if not preserve_spans or len(layer[i].annotations) > 1:
            del layer[i].annotations[j]

#
#  Legacy layer operation, relocated from:
#  https://github.com/estnltk/estnltk/blob/93310cbda16dc71f56a7d5b06124d093040fe684/estnltk_core/estnltk_core/layer_operations/layer_operations.py#L11-L36
# 

def unique_texts(layer: Layer, order=None):
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


#
#  Legacy layer operation, relocated from:
#  https://github.com/estnltk/estnltk/blob/93310cbda16dc71f56a7d5b06124d093040fe684/estnltk_core/estnltk_core/layer_operations/layer_operations.py#L107-L114
#

def get_enclosing_spans(layer: Layer, span):
    '''Yields layer's spans enclosing around the given span.
       Note: this is inefficient. Instead of using this function,
       use a regular iteration over spans of the enveloping layer 
       and over subspans of each (enveloping) span.
    '''
    base_span = span.base_span
    end = span.end
    for sp in layer:
        if base_span in sp.base_span:
            yield sp
        if end < sp.start:
            break

#
#  Legacy layer operation, relocated from:
#   https://github.com/estnltk/estnltk/blob/08aee4213e1fe1132c12b3393b545613a24940d0/estnltk_core/estnltk_core/layer_operations/layer_operations.py#L41-L78
#

def count_by(layer: Layer, attributes, counter=None):
    """Create table of counts for every *layer* *attributes* value combination.
    
    Note: this functionality is already covered by layer_operations.GroupBy.
    
    Parameters
    ----------
    layer: Layer
        The layer which elements have the keys listed in *attributes*.
    attributes: list of str or str
        Name of *layer*'s key or list of *layer*'s key names.
        If *attributes* contains 'text', then the *layer*'s text is found using spans.
    table: collections.Counter, None, default: None
        If table==None, then new 
        If table!=None, then the table is updated and returned.
    
    Returns
    -------
    collections.Counter
        The keys are tuples of values of attributes. 
        The values are corresponding counts.
    """
    if isinstance(attributes, str):
        attributes = [attributes]

    if counter is None:
        counter = Counter()

    for span in layer:
        key = []
        for a in attributes:
            if a == 'text':
                key.append(span.text)
            else:
                for annotation in span.annotations:
                    key.append(getattr(annotation, a))
        key = tuple(key)
        counter[key] += 1

    return counter

#
#  Legacy layer operation, relocated from:
#   https://github.com/estnltk/estnltk/blob/65b26140df807a0b0d0f76ddf22f274dc8049fed/estnltk_core/estnltk_core/layer_operations/aggregators/groupby.py#L84-L100
#

def group_by_layer(layer: Layer, by: Layer):
    """Groups layer's spans by an enveloping layer.
    
    :param layer: Layer
        Layer which spans will be grouped;
    :param by: Layer
        Layer that envelopes the groupable layer.
    :return:
        iterator of SpanList
    """
    for enveloping_span in by:
        span_list = SpanList()
        for span in enveloping_span.spans:
            sp = layer.get(span)
            if sp is not None:
                span_list.add_span(sp)
        yield span_list

#
#  Legacy layer operation, relocated from:
#   https://github.com/estnltk/estnltk/blob/535654dca55f0cc8067599c9da49f025e46e3554/estnltk_core/estnltk_core/layer_operations/merge.py#L71-L76
#

def iterate_spans(layer: 'Layer'):
    if layer.ambiguous:
        for ambiguous_span in layer:
            yield from ambiguous_span
    else:
        yield from layer

#
#  Legacy layer operations, relocated from:
#   https://github.com/estnltk/estnltk/blob/21a0d68f72ae714abab14fe2f730bf9c3df1e49e/estnltk_core/estnltk_core/layer_operations/layer_operations.py#L66-L74
#

def apply_to_annotations(layer: 'Layer', function: callable):
    for span in layer:
        for annotation in span:
            function(annotation)


def apply_to_spans(layer: 'Layer', function: callable):
    for span in layer:
        function(span)


#
#  Legacy layer operation, relocated from:
#   https://github.com/estnltk/estnltk/blob/051d0c3ff1931a50a799dae2916f7202a62ab46c/estnltk_core/estnltk_core/layer_operations/conflict_resolver.py#L13-L29
#

def iterate_conflicting_spans( layer: 'Layer' ):
    """Yields all pairs `(a, b)` of spans in the layer such that
       `a.start <= b.start` and `b.start < a.end`.
       
       Note: this function duplicates the functionality of 
       layer_operations.iterate_intersecting_spans(...) and 
       therefore was moved into legacy.
       
       :param layer: Layer
          input layer
       :returns generator
    """
    len_layer = len(layer)
    for i, a in enumerate(layer):
        a_end = a.end
        for j in range(i + 1, len_layer):
            b = layer[j]
            if a_end <= b.start:
                break
            yield a, b

#
#  Legacy layer operations, relocated from:
#   https://github.com/estnltk/estnltk/blob/f2dbde4062cb103384b6949b722125543d3fe457/estnltk_core/estnltk_core/layer_operations/layer_operations.py#L295-L590
#

############################################################
####### OLD API BELOW ######################################
############################################################
# TODO: cleanup

TEXT = 'text'
AND = 'AND'
OR = 'OR'

UNION = 'union'
INTERSECTION = 'intersection'
EXACT = 'exact'

START = 'start'
END = 'end'


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



# TODO: merge into remove_annotations
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
    for g in groupby(layer, lambda s: (s[START], s[END])):
        yield fun(g[1])
    return


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
