"""
Lihtkihi elementidega opereerimise tööriistad.
"""


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
    assert not (nested(elem1, elem2) or nested(elem2, elem1)), 'deletion not defined for nested elements'
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
    assert not (nested(elem1, elem2) or nested(elem2, elem1)), 'deletion not defined for nested elements'
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