#
#  Legacy layer operations using the old API, relocated from:
#   https://github.com/estnltk/estnltk/blob/f2dbde4062cb103384b6949b722125543d3fe457/estnltk_core/estnltk_core/layer_operations/layer_operations.py#L295-L590
#

from itertools import groupby

from pandas import DataFrame

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
