from copy import deepcopy

from estnltk import Span
from estnltk import EnvelopingSpan
from estnltk import Layer
from estnltk import Text


# empty text
text_0 = Text('')
text_0.meta['description'] = 'empty text, no layers'

# empty text with all kinds of empty layers
text_1 = Text('')
text_1.meta['description'] = 'empty text with empty layers'

layer_0 = Layer('layer_0', attributes=['attr', 'attr_0'])
layer_1 = Layer('layer_1', attributes=['attr', 'attr_1'], ambiguous=True)
layer_2 = Layer('layer_2', attributes=['attr', 'attr_2'], ambiguous=False, parent='layer_0')
layer_3 = Layer('layer_3', attributes=['attr', 'attr_3'], ambiguous=True, parent='layer_1')
layer_4 = Layer('layer_4', attributes=['attr', 'attr_4'], ambiguous=False, enveloping='layer_1')
layer_5 = Layer('layer_5', attributes=['attr', 'attr_5'], ambiguous=True, enveloping='layer_0')
text_1['layer_0'] = layer_0
text_1['layer_1'] = layer_1
text_1['layer_2'] = layer_2
text_1['layer_3'] = layer_3
text_1['layer_4'] = layer_4
text_1['layer_5'] = layer_5

# short text
text_2 = Text('Tere, maailm!')
# short text with all kinds of layers
text_3 = Text('Tere, maailm!')
layer_0 = Layer('layer_0', attributes=['attr', 'attr_0'])
layer_0.add_span(Span(start=0,  end=4,  legal_attributes=['attr', 'attr_0'], attr='L0-0',  attr_0='A'))
layer_0.add_span(Span(start=4,  end=5,  legal_attributes=['attr', 'attr_0'], attr='L0-1',  attr_0='B'))
layer_0.add_span(Span(start=6,  end=12, legal_attributes=['attr', 'attr_0'], attr='L0-2',  attr_0='C'))
layer_0.add_span(Span(start=12, end=13, legal_attributes=['attr', 'attr_0'], attr='L0-3',  attr_0='D'))
text_3['layer_0'] = layer_0

layer_1 = Layer('layer_1', attributes=['attr', 'attr_1'], ambiguous=True)
layer_2 = Layer('layer_2', attributes=['attr', 'attr_2'], ambiguous=False, parent='layer_0')
layer_3 = Layer('layer_3', attributes=['attr', 'attr_3'], ambiguous=True, parent='layer_1')
layer_4 = Layer('layer_4', attributes=['attr', 'attr_4'], ambiguous=False, enveloping='layer_1')
layer_5 = Layer('layer_5', attributes=['attr', 'attr_5'], ambiguous=True, enveloping='layer_0')
text_3['layer_1'] = layer_1
text_3['layer_2'] = layer_2
text_3['layer_3'] = layer_3
text_3['layer_4'] = layer_4
text_3['layer_5'] = layer_5

t = """Sada kakskümmend kolm. Neli tuhat viissada kuuskümmend seitse koma kaheksa. Üheksakümmend tuhat."""
# text
text_4 = Text(t)

# text with layers
text_5 = Text(t)
text_5.meta['description'] = 'short text with layers'

layer_0 = Layer('layer_0', attributes=['attr', 'attr_0'])
layer_0.add_span(Span(start= 0, end= 4, legal_attributes=['attr', 'attr_0'], attr='L0-0',  attr_0='100'))
layer_0.add_span(Span(start= 5, end= 9, legal_attributes=['attr', 'attr_0'], attr='L0-1',  attr_0='2'))
layer_0.add_span(Span(start= 5, end=16, legal_attributes=['attr', 'attr_0'], attr='L0-2',  attr_0='20'))
layer_0.add_span(Span(start= 9, end=14, legal_attributes=['attr', 'attr_0'], attr='L0-3',  attr_0='10'))
layer_0.add_span(Span(start=17, end=21, legal_attributes=['attr', 'attr_0'], attr='L0-4',  attr_0='3'))
layer_0.add_span(Span(start=22, end=27, legal_attributes=['attr', 'attr_0'], attr='L0-5',  attr_0='4'))
layer_0.add_span(Span(start=28, end=33, legal_attributes=['attr', 'attr_0'], attr='L0-6',  attr_0='1000'))
layer_0.add_span(Span(start=34, end=38, legal_attributes=['attr', 'attr_0'], attr='L0-7',  attr_0='5'))
layer_0.add_span(Span(start=34, end=42, legal_attributes=['attr', 'attr_0'], attr='L0-8',  attr_0='500'))
layer_0.add_span(Span(start=38, end=42, legal_attributes=['attr', 'attr_0'], attr='L0-9',  attr_0='100'))
layer_0.add_span(Span(start=43, end=47, legal_attributes=['attr', 'attr_0'], attr='L0-10', attr_0='6'))
layer_0.add_span(Span(start=43, end=54, legal_attributes=['attr', 'attr_0'], attr='L0-11', attr_0='60'))
layer_0.add_span(Span(start=47, end=52, legal_attributes=['attr', 'attr_0'], attr='L0-12', attr_0='10'))
layer_0.add_span(Span(start=55, end=61, legal_attributes=['attr', 'attr_0'], attr='L0-13', attr_0='7'))
layer_0.add_span(Span(start=62, end=66, legal_attributes=['attr', 'attr_0'], attr='L0-14', attr_0=','))
layer_0.add_span(Span(start=67, end=74, legal_attributes=['attr', 'attr_0'], attr='L0-15', attr_0='8'))
layer_0.add_span(Span(start=76, end=82, legal_attributes=['attr', 'attr_0'], attr='L0-16', attr_0='9'))
layer_0.add_span(Span(start=76, end=89, legal_attributes=['attr', 'attr_0'], attr='L0-17', attr_0='90'))
layer_0.add_span(Span(start=82, end=87, legal_attributes=['attr', 'attr_0'], attr='L0-18', attr_0='10'))
text_5['layer_0'] = layer_0

layer_1 = Layer('layer_1', attributes=['attr', 'attr_1'], ambiguous=True)
layer_1.add_span(Span(start= 0, end= 4, legal_attributes=['attr', 'attr_1'], attr='L1-0',  attr_1='SADA'))
layer_1.add_span(Span(start= 5, end= 9, legal_attributes=['attr', 'attr_1'], attr='L1-1',  attr_1='KAKS'))

layer_1.add_span(Span(start= 5, end=16, legal_attributes=['attr', 'attr_1'], attr='L1-2',  attr_1='KAKS'))
layer_1.add_span(Span(start= 5, end=16, legal_attributes=['attr', 'attr_1'], attr='L1-2',  attr_1='KÜMME'))
layer_1.add_span(Span(start= 5, end=16, legal_attributes=['attr', 'attr_1'], attr='L1-2',  attr_1='KAKSKÜMMEND'))

layer_1.add_span(Span(start= 9, end=14, legal_attributes=['attr', 'attr_1'], attr='L1-3',  attr_1='KÜMME'))
layer_1.add_span(Span(start=17, end=21, legal_attributes=['attr', 'attr_1'], attr='L1-4',  attr_1='KOLM'))
layer_1.add_span(Span(start=22, end=27, legal_attributes=['attr', 'attr_1'], attr='L1-5',  attr_1='NELI'))
layer_1.add_span(Span(start=28, end=33, legal_attributes=['attr', 'attr_1'], attr='L1-6',  attr_1='TUHAT'))
layer_1.add_span(Span(start=34, end=38, legal_attributes=['attr', 'attr_1'], attr='L1-7',  attr_1='VIIS'))

layer_1.add_span(Span(start=34, end=42, legal_attributes=['attr', 'attr_1'], attr='L1-8',  attr_1='SADA'))
layer_1.add_span(Span(start=34, end=42, legal_attributes=['attr', 'attr_1'], attr='L1-8',  attr_1='VIIS'))
layer_1.add_span(Span(start=34, end=42, legal_attributes=['attr', 'attr_1'], attr='L1-8',  attr_1='VIISSADA'))

layer_1.add_span(Span(start=38, end=42, legal_attributes=['attr', 'attr_1'], attr='L1-9',  attr_1='SADA'))
layer_1.add_span(Span(start=43, end=47, legal_attributes=['attr', 'attr_1'], attr='L1-10', attr_1='KUUS'))

layer_1.add_span(Span(start=43, end=54, legal_attributes=['attr', 'attr_1'], attr='L1-11', attr_1='KUUS'))
layer_1.add_span(Span(start=43, end=54, legal_attributes=['attr', 'attr_1'], attr='L1-11', attr_1='KÜMME'))
layer_1.add_span(Span(start=43, end=54, legal_attributes=['attr', 'attr_1'], attr='L1-11', attr_1='KUUSKÜMMEND'))

layer_1.add_span(Span(start=47, end=52, legal_attributes=['attr', 'attr_1'], attr='L1-12', attr_1='KÜMME'))
layer_1.add_span(Span(start=55, end=61, legal_attributes=['attr', 'attr_1'], attr='L1-13', attr_1='SEITSE'))
layer_1.add_span(Span(start=62, end=66, legal_attributes=['attr', 'attr_1'], attr='L1-14', attr_1='KOMA'))
layer_1.add_span(Span(start=67, end=74, legal_attributes=['attr', 'attr_1'], attr='L1-15', attr_1='KAHEKSA'))
layer_1.add_span(Span(start=76, end=82, legal_attributes=['attr', 'attr_1'], attr='L1-16', attr_1='ÜHEKSA'))

layer_1.add_span(Span(start=76, end=89, legal_attributes=['attr', 'attr_1'], attr='L1-17', attr_1='ÜHEKSA'))
layer_1.add_span(Span(start=76, end=89, legal_attributes=['attr', 'attr_1'], attr='L1-17', attr_1='KÜMME'))
layer_1.add_span(Span(start=76, end=89, legal_attributes=['attr', 'attr_1'], attr='L1-17', attr_1='ÜHEKSAKÜMMEND'))

layer_1.add_span(Span(start=82, end=87, legal_attributes=['attr', 'attr_1'], attr='L1-18', attr_1='KÜMME'))
text_5['layer_1'] = layer_1


layer_2 = Layer('layer_2', attributes=['attr', 'attr_2'], ambiguous=False, parent='layer_0')
text_5['layer_2'] = layer_2

layer_3 = Layer('layer_3', attributes=['attr', 'attr_3'], ambiguous=True, parent='layer_1')
text_5['layer_3'] = layer_3

layer_4 = Layer('layer_4', attributes=['attr', 'attr_4'], ambiguous=False, enveloping='layer_0')
text_5['layer_4'] = layer_4

layer_5 = Layer('layer_5', attributes=['attr', 'attr_5'], ambiguous=True, enveloping='layer_1')
layer_5.add_span(EnvelopingSpan(spans=[layer_1[0], layer_1[1]], layer=layer_5, attributes={'attr': 'L5-0-0', 'attr_5': 'SADA KAKS'}))
layer_5.add_span(EnvelopingSpan(spans=[layer_1[0], layer_1[2]], layer=layer_5, attributes={'attr': 'L5-1-1', 'attr_5': 'SADA KAKS'}))
layer_5.add_span(EnvelopingSpan(spans=[layer_1[0], layer_1[2]], layer=layer_5, attributes={'attr': 'L5-1-2', 'attr_5': 'SADA KÜMME'}))
layer_5.add_span(EnvelopingSpan(spans=[layer_1[0], layer_1[2]], layer=layer_5, attributes={'attr': 'L5-1-3', 'attr_5': 'SADA KAKSKÜMMEND'}))
layer_5.add_span(EnvelopingSpan(spans=[layer_1[0], layer_1[2], layer_1[4]], layer=layer_5, attributes={'attr': 'L5-2-4', 'attr_5': 'SADA KAKSKÜMMEND KOLM'}))
layer_5.add_span(EnvelopingSpan(spans=[layer_1[5], layer_1[6]], layer=layer_5, attributes={'attr': 'L5-3-5', 'attr_5': 'NELI TUHAT'}))
layer_5.add_span(EnvelopingSpan(spans=[layer_1[7]], layer=layer_5, attributes={'attr': 'L5-5-7', 'attr_5': 'VIIS'}))
layer_5.add_span(EnvelopingSpan(spans=[layer_1[6], layer_1[7]], layer=layer_5, attributes={'attr': 'L5-4-6', 'attr_5': 'TUHAT VIIS'}))
layer_5.add_span(EnvelopingSpan(spans=[layer_1[8], layer_1[11]], layer=layer_5, attributes={'attr': 'L5-6-8', 'attr_5': 'VIISSADA KUUS'}))
layer_5.add_span(EnvelopingSpan(spans=[layer_1[8], layer_1[11]], layer=layer_5, attributes={'attr': 'L5-6-9', 'attr_5': 'VIISSADA KÜMME'}))
layer_5.add_span(EnvelopingSpan(spans=[layer_1[8], layer_1[11]], layer=layer_5, attributes={'attr': 'L5-6-10', 'attr_5': 'VIISSADA KUUSKÜMMEND'}))
layer_5.add_span(EnvelopingSpan(spans=[layer_1[12], layer_1[14], layer_1[15]], layer=layer_5, attributes={'attr': 'L5-7-11', 'attr_5': 'KÜMME KOMA KAHEKSA'}))
layer_5.add_span(EnvelopingSpan(spans=[layer_1[13], layer_1[14], layer_1[15]], layer=layer_5, attributes={'attr': 'L5-8-12', 'attr_5': 'SEITSE KOMA KAHEKSA'}))
text_5['layer_5'] = layer_5

texts = {0: text_0,  # empty text, no layers
         1: text_1,  # empty text, empty layers
         2: text_2,  # brief demo text, no layers
         3: text_3,  # brief demo text with layers
         4: text_4,  # short text, no layers
         5: text_5}  # short text with layers


def new_text(n):
    return deepcopy(texts[n])