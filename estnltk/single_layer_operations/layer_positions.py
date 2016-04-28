"""
Lihtkihi elementidega opereerimise tööriistad.
"""
import copy


def touching_right(x, y):
    """
    xxxxxxxx
            yyyyy
    """
    return x['end'] == y['start']


def touching_left(x, y):
    """
         xxxxxxxx
    yyyyy
    """
    return touching_right(y, x)


def hovering_right(x, y):
    """
    xxxxxxxx
              yyyyy
    """
    return x['end'] < y['start']


def hovering_left(x, y):
    """
            xxxxxxxx
    yyyyy
    """
    return hovering_right(y, x)


def right(x, y):
    return touching_right(x, y) or hovering_right(x, y)


def left(x, y):
    return right(y, x)


def nested(x, y):
    """
    xxxxxxxx
      yyyyy
    """
    return x['start'] <= y['start'] <= y['end'] <= x['end']


def equal(x, y):
    """
    xxxxxxxx
    yyyyyyyy
    """
    return nested(x, y) and nested(y, x)


def nested_aligned_right(x, y):
    """
    xxxxxxxx
       yyyyy
    """
    return nested(x, y) and x['end'] == y['end']


def nested_aligned_left(x, y):
    """
    xxxxxxxx
    yyyyy
    """
    return nested(x, y) and x['start'] == y['start']


def overlapping_left(x, y):
    """
      xxxxxxxx
    yyyyy
    """
    return y['start'] < x['start'] < y['end']


def overlapping_right(x, y):
    """
    xxxxxxxx
          yyyyy
    """
    return y['start'] < x['end'] < y['end']


def conflict(x, y):
    return nested(x, y) or nested(y, x) or overlapping_left(x, y) or overlapping_right(x, y)



########################################################################################################################
########################################################################################################################
########################################################################################################################


def delete_left(elem1, elem2):
    """
    xxxxx
       yyyyy
    ---------
    xxx
       yyyyy
    """
    # assert not (nested(elem1, elem2) or nested(elem2, elem1)), 'deletion not defined for nested elements'
    if overlapping_right(elem1, elem2):
        elem1['end'] = elem2['start']
    return elem1, elem2


def delete_right(elem1, elem2):
    """
    xxxxx
       yyyyy
    ---------
    xxxxx
         yyy
    """
    # assert not (nested(elem1, elem2) or nested(elem2, elem1)), 'deletion not defined for nested elements'
    if overlapping_left(elem1, elem2):
        elem2['start'] = elem1['end']
    return elem1, elem2


def in_by_identity(lst, ob):
    """
    Returns True if ob is in lst by identity
    """
    for i in lst:
        if i is ob:
            return True
    return False


def pop_first_by_identity(lst, ob):
    for i in range(len(lst)):
        if lst[i] is ob:
            break
    else:
        return None
    return lst.pop(i)



def iterate_intersecting_pairs(layer):
    """
    Given a layer of estntltk objects, yields pairwise intersecting elements.
    Breaks when the layer is changed or deleted after initializing the iterator.
    """
    yielded = set()
    ri = layer[:]  # Shallow copy the layer
    for i1, elem1 in enumerate(ri):
        for i2, elem2 in enumerate(ri):
            if i1 != i2 and elem1['start'] <= elem2['start'] < elem1['end']:
                inds = (i1, i2) if i1 < i2 else (i2, i1)
                if inds not in yielded and in_by_identity(layer, elem1) and in_by_identity(layer, elem2):
                    yielded.add(inds)
                    yield elem1, elem2




def discard(a, b, **kwargs):
    return {}

def merge(a, b, func, **kwargs):
    assert equal(a, b)
    return dict(start=a['start'], end=a['end'], **func(a, b, **kwargs))


def difference(x, y):
    assert nested(x, y)

    if nested_aligned_left(x, y):
        a, b = union(copy.deepcopy(x), copy.deepcopy(y))
        rest = copy.deepcopy(x)
        rest['start'] = a['end']
        res = [a,b,rest]
    elif nested_aligned_right(x, y):
        a, b = union(copy.deepcopy(x), copy.deepcopy(y))
        rest = copy.deepcopy(x)
        rest['end'] = a['start']
        res = [a,b,rest]
    else:
        r1, r2, middle = copy.deepcopy(x), copy.deepcopy(x), copy.deepcopy(x)
        r1['end'] = y['start']
        r2['start'] = y['end']

        middle['start'] = y['start']
        middle['end'] = y['end']

        res = [r1, r2, middle, y]

    return res




def union(x, y):
    flip = x['start'] > y['start']
    if flip:
        x, y = y, x


    if nested(x, y):
        #choose y coords
        x['start'] = y['start']
        x['end'] = y['end']

    elif overlapping_left(x, y):
        y['start'] = x['start']
        x['end'] = y['end']

    elif overlapping_right(x, y):
        x['start'] = y['start']
        y['end'] = x['end']
    else:
        raise AssertionError('should not happen')

    return (x, y) if not flip else (y, x)


def make_layer_nonconflicting(layer, merge_func):
    #funktsiooni loogika:
    #iga konflikti korral:
    #    kui elemendid on võrdsed, kombineeri need
    #    kui üks element on teise sees, jaga nad kolmeks või neljaks
    #    kui elemendid on ülekattega, jaga need kolmeks
    #korda funktsiooni kuni konflikte pole

    # On ilmne, et elemendi tükeldamine ei tekita uusi konflikte, küll võib see põhjustada, et ühe tsükliga kõiki üles ei leita
    # On ilmne, et kahe võrdse elemendi ühendamine ei tekita uusi konflikte
    # Seega peavad konfliktid minema nulli.

    while True:
        while True:
            if not list(iterate_intersecting_pairs(layer)):
                break

            for a, b in iterate_intersecting_pairs(layer):
                a, b = (a, b) if a['start'] <= b['start'] else (b, a)

                if equal(a, b):
                    if a is not b:
                        layer.append(merge(pop_first_by_identity(layer, a),
                            pop_first_by_identity(layer, b), merge_func, value='equal'))
                    continue

                elif nested(a, b) or nested(b, a):
                    if nested(b, a):
                        a, b = b, a

                    pop_first_by_identity(layer, b)
                    pop_first_by_identity(layer, a)
                    diff = difference(a, b)
                    layer.extend(diff)
                    continue

                elif overlapping_right(a, b):
                    mida, midb = union(copy.deepcopy(a), copy.deepcopy(b))
                    layer.append(merge(mida, midb, merge_func, value='overlapping_right'))

                    a_m = copy.deepcopy(a)
                    a, b = delete_left(a, mida)
                    _, b = delete_right(midb, b)
                    continue

                else:
                    print('should not happen')


'''
#Küsimusi ja vastuseid:
#K: Miks see moodul eksisteerib?
#V: Näiteprobleemiks mitmeselt tokeniseeritud tekstide järelpuhastamine. Näiteks kui samasse kihti said tekstist
#  "12.jaanuar 2014"
# markerid {"12":täisarv, "2014":täisarv, "12.jaanuar 2014": kuupäev},
#soovime me neist alles jätta vaid kuupäevatähenduse. Selle mooduliga saab sääraseid konflikte lihtkihtides lahendada.

#K: Miks see moodul just selline on?
#V: ... see on keeruline küsimus. Nõudmised olid, et
# 1) Kasutaja saaks kihist kustutada konkreetset objekti (mitte kõiki sama väärtusega objekte)
# 2) Kasutaja saaks keset iteratsiooni kihti elemente lisada ja kihi elementide järjekorda muuta.
# Tulemuseks on, et me itereerime üle shallow-copy elementidest väljakutse hetkel ja enne ülekattega paari
# väljastamist kontrollime, kas väljastatavad elemendid on ikka veel esialgses listis alles.
# Seega ei garanteeri me, et me leiame ülekatted, mis tekkisid peale iteratsiooni algust. Samas ei garanteeri me,
# et me EI leia ülekatteid, mis tekkisid peale iteratsiooni algust.

#K: Mida te siis õigupoolest garanteerite?
#V: funktsioon "iterate_intersecting_pairs" leiab kõik ülekattega paarid, mis eksisteerivad kihis väljakutse hetkel.
#   funktsioonid "delete_left" ja "delete_right" ei tekita uusi ülekatteid
#   funktsioon "pop_first_by_identity" ei tekita uusi ülekatteid

#K: Kas sa näitlikustaksid seda moodulit väga sünteetilise näitega?
#V: See on küsimus ainult sõna formaalses mõttes. Aga miks ka mitte...

import estnltk
text = estnltk.Text('Kui Arno isaga koolimajja jõudis, olid tunnid juba alanud.')
text['overlapping'] = [{'start':0, 'end':text.text.find(',')},
                       {'end':len(text.text), 'start':text.text.find(',') - 5},
                       {'start':0, 'end':len(text.text)}]

print('At the start we are overlapping ', len(list(iterate_intersecting_pairs(text['overlapping']))))

for a, b in iterate_intersecting_pairs(text['overlapping']):
    #Tagame, et a ei ole b algusest paremal
    if a['start'] < b['start']:
        pass
    else:
        a, b = b, a

    #Kui b on a-st ülekattega paremal
    if overlapping_right(a, b):
        delete_left(a, b)

    #Kui b on täielikult a sees
    if nested(a, b):
        #kustutame kihist kahest elemendist suurema
        pop_first_by_identity(text['overlapping'], a)


print('In the end we are overlapping  ', len(list(iterate_intersecting_pairs(text['overlapping']))))
'''