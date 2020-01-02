from estnltk import Layer
from estnltk import Text
from estnltk import ElementaryBaseSpan


def empty_text_with_no_layers():
    text = Text('')
    text.meta['description'] = 'An empty text with no layers'
    return text


def empty_text_with_all_layer_types():
    text = Text('')
    text.meta['description'] = 'An empty text with all possible types of empty layers'

    layer_0 = Layer('layer_0', attributes=['attr', 'attr_0'])
    layer_1 = Layer('layer_1', attributes=['attr', 'attr_1'], ambiguous=True)
    layer_2 = Layer('layer_2', attributes=['attr', 'attr_2'], ambiguous=False, parent='layer_0')
    layer_3 = Layer('layer_3', attributes=['attr', 'attr_3'], ambiguous=True, parent='layer_1')
    layer_4 = Layer('layer_4', attributes=['attr', 'attr_4'], ambiguous=False, enveloping='layer_1')
    layer_5 = Layer('layer_5', attributes=['attr', 'attr_5'], ambiguous=True, enveloping='layer_0')
    text.add_layer(layer_0)
    text.add_layer(layer_1)
    text.add_layer(layer_2)
    text.add_layer(layer_3)
    text.add_layer(layer_4)
    text.add_layer(layer_5)
    return text


def sentence_with_no_layers():
    text = Text('Tere, maailm!')
    text.meta['description'] = 'A text sentence with no layers'
    return text


def sentence_with_all_layer_types():
    text = Text('Tere, maailm!')
    text.meta['description'] = 'A text sentence with all possible layer types of non-empty layers'

    layer_0 = Layer('layer_0', attributes=['attr', 'attr_0'], text_object=text)
    layer_0.add_annotation(ElementaryBaseSpan(0, 4), attr='L0-0', attr_0='A')
    layer_0.add_annotation(ElementaryBaseSpan(4, 5), attr='L0-1', attr_0='B')
    layer_0.add_annotation(ElementaryBaseSpan(6, 12), attr='L0-2', attr_0='C')
    layer_0.add_annotation(ElementaryBaseSpan(12, 13), attr='L0-3', attr_0='D')
    text.add_layer(layer_0)

    layer_1 = Layer('layer_1', attributes=['attr', 'attr_1'], text_object=text, ambiguous=True)
    layer_1.add_annotation(ElementaryBaseSpan(0, 4), attr='L1-0', attr_1='A')
    layer_1.add_annotation(ElementaryBaseSpan(0, 4), attr='L1-0', attr_1='B')
    layer_1.add_annotation(ElementaryBaseSpan(4, 5), attr='L1-1', attr_1='C')
    layer_1.add_annotation(ElementaryBaseSpan(6, 12), attr='L1-2', attr_1='D')
    layer_1.add_annotation(ElementaryBaseSpan(6, 12), attr='L1-2', attr_1='E')
    layer_1.add_annotation(ElementaryBaseSpan(12, 13), attr='L1-3', attr_1='F')
    text.add_layer(layer_1)

    layer_2 = Layer('layer_2', attributes=['attr', 'attr_2'], text_object=text, ambiguous=False, parent='layer_0')
    text.add_layer(layer_2)

    layer_3 = Layer('layer_3', attributes=['attr', 'attr_3'], text_object=text, ambiguous=True, parent='layer_1')
    text.add_layer(layer_3)

    layer_4 = Layer('layer_4', attributes=['attr', 'attr_4'], text_object=text, ambiguous=False, enveloping='layer_1')
    text.add_layer(layer_4)

    layer_5 = Layer('layer_5', attributes=['attr', 'attr_5'], text_object=text, ambiguous=True, enveloping='layer_0')
    text.add_layer(layer_5)

    return text


def paragraph_with_no_layers():
    text = Text('Sada kakskümmend kolm. Neli tuhat viissada kuuskümmend seitse koma kaheksa. Üheksakümmend tuhat.')
    text.meta['description'] = 'A text paragraph with no layers'
    return text
    

def paragraph_with_all_layer_types():
    text = Text('Sada kakskümmend kolm. Neli tuhat viissada kuuskümmend seitse koma kaheksa. Üheksakümmend tuhat.')
    text.meta['description'] = 'A text paragraph with all possible layer types of non-empty layers'

    layer_0 = Layer('layer_0', attributes=['attr', 'attr_0'])
    layer_0.add_annotation(ElementaryBaseSpan(0, 4), attr='L0-0', attr_0='100')
    layer_0.add_annotation(ElementaryBaseSpan(5, 9), attr='L0-1', attr_0='2')
    layer_0.add_annotation(ElementaryBaseSpan(5, 16), attr='L0-2', attr_0='20')
    layer_0.add_annotation(ElementaryBaseSpan(9, 14), attr='L0-3', attr_0='10')
    layer_0.add_annotation(ElementaryBaseSpan(17, 21), attr='L0-4', attr_0='3')
    layer_0.add_annotation(ElementaryBaseSpan(22, 27), attr='L0-5', attr_0='4')  # TODO start=23
    layer_0.add_annotation(ElementaryBaseSpan(28, 33), attr='L0-6', attr_0='1000')
    layer_0.add_annotation(ElementaryBaseSpan(34, 38), attr='L0-7', attr_0='5')
    layer_0.add_annotation(ElementaryBaseSpan(34, 42), attr='L0-8', attr_0='500')
    layer_0.add_annotation(ElementaryBaseSpan(38, 42), attr='L0-9', attr_0='100')
    layer_0.add_annotation(ElementaryBaseSpan(43, 47), attr='L0-10', attr_0='6')
    layer_0.add_annotation(ElementaryBaseSpan(43, 54), attr='L0-11', attr_0='60')
    layer_0.add_annotation(ElementaryBaseSpan(47, 52), attr='L0-12', attr_0='10')
    layer_0.add_annotation(ElementaryBaseSpan(55, 61), attr='L0-13', attr_0='7')
    layer_0.add_annotation(ElementaryBaseSpan(62, 66), attr='L0-14', attr_0=',')
    layer_0.add_annotation(ElementaryBaseSpan(67, 74), attr='L0-15', attr_0='8')
    layer_0.add_annotation(ElementaryBaseSpan(76, 82), attr='L0-16', attr_0='9')
    layer_0.add_annotation(ElementaryBaseSpan(76, 89), attr='L0-17', attr_0='90')
    layer_0.add_annotation(ElementaryBaseSpan(82, 87), attr='L0-18', attr_0='10')
    layer_0.add_annotation(ElementaryBaseSpan(90, 95), attr='L0-19', attr_0='1000')
    text.add_layer(layer_0)

    layer_1 = Layer('layer_1', attributes=['attr', 'attr_1'], text_object=text, ambiguous=True)
    layer_1.add_annotation(ElementaryBaseSpan(0, 4), attr='L1-0', attr_1='SADA')
    layer_1.add_annotation(ElementaryBaseSpan(5, 9), attr='L1-1', attr_1='KAKS')
    layer_1.add_annotation(ElementaryBaseSpan(5, 16), attr='L1-2', attr_1='KAKS')
    layer_1.add_annotation(ElementaryBaseSpan(5, 16), attr='L1-2', attr_1='KÜMME')
    layer_1.add_annotation(ElementaryBaseSpan(5, 16), attr='L1-2', attr_1='KAKSKÜMMEND')
    layer_1.add_annotation(ElementaryBaseSpan(9, 14), attr='L1-3', attr_1='KÜMME')
    layer_1.add_annotation(ElementaryBaseSpan(17, 21), attr='L1-4', attr_1='KOLM')
    layer_1.add_annotation(ElementaryBaseSpan(23, 27), attr='L1-5', attr_1='NELI')
    layer_1.add_annotation(ElementaryBaseSpan(28, 33), attr='L1-6', attr_1='TUHAT')
    layer_1.add_annotation(ElementaryBaseSpan(34, 38), attr='L1-7', attr_1='VIIS')
    layer_1.add_annotation(ElementaryBaseSpan(34, 42), attr='L1-8', attr_1='SADA')
    layer_1.add_annotation(ElementaryBaseSpan(34, 42), attr='L1-8', attr_1='VIIS')
    layer_1.add_annotation(ElementaryBaseSpan(34, 42), attr='L1-8', attr_1='VIISSADA')
    layer_1.add_annotation(ElementaryBaseSpan(38, 42), attr='L1-9', attr_1='SADA')
    layer_1.add_annotation(ElementaryBaseSpan(43, 47), attr='L1-10', attr_1='KUUS')
    layer_1.add_annotation(ElementaryBaseSpan(43, 54), attr='L1-11', attr_1='KUUS')
    layer_1.add_annotation(ElementaryBaseSpan(43, 54), attr='L1-11', attr_1='KÜMME')
    layer_1.add_annotation(ElementaryBaseSpan(43, 54), attr='L1-11', attr_1='KUUSKÜMMEND')
    layer_1.add_annotation(ElementaryBaseSpan(47, 52), attr='L1-12', attr_1='KÜMME')
    layer_1.add_annotation(ElementaryBaseSpan(55, 61), attr='L1-13', attr_1='SEITSE')
    layer_1.add_annotation(ElementaryBaseSpan(62, 66), attr='L1-14', attr_1='KOMA')
    layer_1.add_annotation(ElementaryBaseSpan(67, 74), attr='L1-15', attr_1='KAHEKSA')
    layer_1.add_annotation(ElementaryBaseSpan(76, 82), attr='L1-16', attr_1='ÜHEKSA')
    layer_1.add_annotation(ElementaryBaseSpan(76, 89), attr='L1-17', attr_1='ÜHEKSA')
    layer_1.add_annotation(ElementaryBaseSpan(76, 89), attr='L1-17', attr_1='KÜMME')
    layer_1.add_annotation(ElementaryBaseSpan(76, 89), attr='L1-17', attr_1='ÜHEKSAKÜMMEND')
    layer_1.add_annotation(ElementaryBaseSpan(82, 87), attr='L1-18', attr_1='KÜMME')
    text.add_layer(layer_1)

    layer_2 = Layer('layer_2', attributes=['attr', 'attr_2'], ambiguous=False, parent='layer_0')
    layer_2.add_annotation(layer_0[0], attr='L2-0', attr_2=100)
    layer_2.add_annotation(layer_0[1], attr='L2-1', attr_2=2)
    layer_2.add_annotation(layer_0[2], attr='L2-2', attr_2=20)
    layer_2.add_annotation(layer_0[3], attr='L2-3', attr_2=10)
    layer_2.add_annotation(layer_0[4], attr='L2-4', attr_2=3)
    layer_2.add_annotation(layer_0[5], attr='L2-5', attr_2=4)
    layer_2.add_annotation(layer_0[6], attr='L2-6', attr_2=1000)
    layer_2.add_annotation(layer_0[7], attr='L2-7', attr_2=5)
    layer_2.add_annotation(layer_0[8], attr='L2-8', attr_2=500)
    layer_2.add_annotation(layer_0[9], attr='L2-9', attr_2=100)
    layer_2.add_annotation(layer_0[10], attr='L2-10', attr_2=6)
    layer_2.add_annotation(layer_0[11], attr='L2-11', attr_2=60)
    layer_2.add_annotation(layer_0[12], attr='L2-12', attr_2=10)
    layer_2.add_annotation(layer_0[13], attr='L2-13', attr_2=7)
    layer_2.add_annotation(layer_0[15], attr='L2-14', attr_2=8)
    layer_2.add_annotation(layer_0[16], attr='L2-15', attr_2=9)
    layer_2.add_annotation(layer_0[17], attr='L2-16', attr_2=90)
    layer_2.add_annotation(layer_0[18], attr='L2-17', attr_2=10)
    layer_2.add_annotation(layer_0[19], attr='L2-18', attr_2=1000)
    text.add_layer(layer_2)

    layer_3 = Layer('layer_3', attributes=['attr', 'attr_3'], ambiguous=True, parent='layer_1')
    text.add_layer(layer_3)

    layer_4 = Layer('layer_4', attributes=['attr', 'attr_4'], ambiguous=False, enveloping='layer_0')
    layer_4.add_annotation([layer_0[0], layer_0[2], layer_0[4]], attr='L4-0', attr_4='123')
    layer_4.add_annotation([layer_0[5], layer_0[6], layer_0[8], layer_0[11], layer_0[13]], attr='L4-1', attr_4='4567')
    layer_4.add_annotation([layer_0[15]], attr='L4-2', attr_4='8')
    layer_4.add_annotation([layer_0[14]], attr='L4-3', attr_4=',')
    layer_4.add_annotation([layer_0[17], layer_0[19]], attr='L4-4', attr_4='90 000')
    text.add_layer(layer_4)

    layer_5 = Layer('layer_5', attributes=['attr', 'attr_5'], ambiguous=True, enveloping='layer_1')
    layer_5.add_annotation([layer_1[0], layer_1[1]], attr='L5-0-0', attr_5='SADA KAKS')
    layer_5.add_annotation([layer_1[0], layer_1[2]], attr='L5-1-1', attr_5='SADA KAKS')
    layer_5.add_annotation([layer_1[0], layer_1[2]], attr='L5-1-2', attr_5='SADA KÜMME')
    layer_5.add_annotation([layer_1[0], layer_1[2]], attr='L5-1-3', attr_5='SADA KAKSKÜMMEND')
    layer_5.add_annotation([layer_1[0], layer_1[2], layer_1[4]], attr='L5-2-4', attr_5='SADA KAKSKÜMMEND KOLM')
    layer_5.add_annotation([layer_1[5], layer_1[6]], attr='L5-3-5', attr_5='NELI TUHAT')
    layer_5.add_annotation([layer_1[7]], attr='L5-5-7', attr_5='VIIS')
    layer_5.add_annotation([layer_1[6], layer_1[7]], attr='L5-4-6', attr_5='TUHAT VIIS')
    layer_5.add_annotation([layer_1[8], layer_1[11]], attr='L5-6-8', attr_5='VIISSADA KUUS')
    layer_5.add_annotation([layer_1[8], layer_1[11]], attr='L5-6-9', attr_5='VIISSADA KÜMME')
    layer_5.add_annotation([layer_1[8], layer_1[11]], attr='L5-6-10', attr_5='VIISSADA KUUSKÜMMEND')
    layer_5.add_annotation([layer_1[12], layer_1[14], layer_1[15]], attr='L5-7-11', attr_5='KÜMME KOMA KAHEKSA')
    layer_5.add_annotation([layer_1[13], layer_1[14], layer_1[15]], attr='L5-8-12', attr_5='SEITSE KOMA KAHEKSA')
    text.add_layer(layer_5)

    return text


def example_text(instance: int) -> Text:
    """
    Creates text objects with different structure for testing from scratch to avoid potential errors in deepcopy.
    Each text object is equipped with meta field 'description' which characterises the text object, i.e., use
    example_text(instance).meta['description'] to get additional details about the text object.
    The instance number must be in the range 0, 1, ..., 5.
    """
    switcher = {
        0: empty_text_with_no_layers,
        1: empty_text_with_all_layer_types,
        2: sentence_with_no_layers,
        3: sentence_with_all_layer_types,
        4: paragraph_with_no_layers,
        5: paragraph_with_all_layer_types
    }

    if instance not in switcher:
        raise ValueError("Argument 'instance' must be in range({})".format(len(switcher)))
    return switcher[instance]()
