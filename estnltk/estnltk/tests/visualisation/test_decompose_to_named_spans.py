from estnltk.visualisation.core.named_span_decomposition import decompose_to_elementary_named_spans
from estnltk_core import RelationLayer
from estnltk import Text


def test_decompose_empty_text_empty_layer():
    text = Text('')
    layer = RelationLayer('coreference', span_names=['mention', 'entity'], text_object=text)
    result = decompose_to_elementary_named_spans(layer, text.text)
    expected = ([['', []]], [])
    assert result == expected


def test_decompose_text_with_empty_layer():
    text = Text('Sada kakskümmend kolm. Neli tuhat viissada kuuskümmend seitse koma kaheksa. Üheksakümmend tuhat.')
    layer = RelationLayer('coreference', span_names=['mention', 'entity'], text_object=text)
    result = decompose_to_elementary_named_spans(layer, text.text)
    expected = ([['Sada kakskümmend kolm. Neli tuhat viissada kuuskümmend seitse koma kaheksa. Üheksakümmend tuhat.', []]], [])
    assert result == expected


def test_decompose_text_with_filled_layer():
    text = Text('Mari kirjeldas õhinal, kuidas ta väiksena "Sipsikut" luges: '+\
    '"Ma ei suutnud seda raamatut kohe kuidagi käest ära panna! Nii põnev oli see!"')
    coref_layer = RelationLayer('coreference', span_names=['mention', 'entity'], text_object=text)
    # Add relation based on a dictionary
    coref_layer.add_annotation( {'mention': (30, 32), 'entity': (0, 4)} )
    coref_layer.add_annotation( {'mention': (61, 63), 'entity': (0, 4)} )
    # Add relation by keyword arguments
    coref_layer.add_annotation( mention=(75, 88), entity=(43, 51) )
    coref_layer.add_annotation( mention=(133, 136), entity=(42, 52) )
    # Case 1: decompose into named span indexes
    segments, named_spans  = decompose_to_elementary_named_spans(coref_layer, text.text)
    assert segments == \
        [['Mari', [0, 1]],
        [' kirjeldas õhinal, kuidas ', []],
        ['ta', [2]],
        [' väiksena ', []],
        ['"', [3]], ['Sipsikut', [4, 5]], ['"', [6]],
        [' luges: "', []],
        ['Ma', [7]],
        [' ei suutnud ', []],
        ['seda raamatut', [8]],
        [' kohe kuidagi käest ära panna! Nii põnev oli ', []],
        ['see', [9]],
        ['!"', []]]
    named_spans_texts = [(ns.name, ns.text) for ns in named_spans]
    assert named_spans_texts == \
        [('entity', 'Mari'), ('entity', 'Mari'), 
         ('mention', 'ta'), 
         ('entity', '"Sipsikut"'), ('entity', '"Sipsikut"'), ('entity', 'Sipsikut'), ('entity', '"Sipsikut"'), 
         ('mention', 'Ma'), 
         ('mention', 'seda raamatut'), 
         ('mention', 'see')]
    
    # Case 2: decompose into named span indexes and relation id-s
    segments, named_spans  = decompose_to_elementary_named_spans(coref_layer, text.text, add_relation_ids=True)
    assert segments == \
        [['Mari', [(0, 0), (1, 1)]], 
         [' kirjeldas õhinal, kuidas ', []], 
         ['ta', [(2, 0)]], 
         [' väiksena ', []], 
         ['"', [(3, 3)]], ['Sipsikut', [(4, 3), (5, 2)]], ['"', [(6, 3)]], 
         [' luges: "', []], 
         ['Ma', [(7, 1)]], 
         [' ei suutnud ', []], 
         ['seda raamatut', [(8, 2)]], 
         [' kohe kuidagi käest ära panna! Nii põnev oli ', []], 
         ['see', [(9, 3)]], 
         ['!"', []]]
    named_spans_texts = [(ns.name, ns.text) for ns in named_spans]
    assert named_spans_texts == \
        [('entity', 'Mari'), ('entity', 'Mari'), 
         ('mention', 'ta'), 
         ('entity', '"Sipsikut"'), ('entity', '"Sipsikut"'), ('entity', 'Sipsikut'), ('entity', '"Sipsikut"'), 
         ('mention', 'Ma'), 
         ('mention', 'seda raamatut'), 
         ('mention', 'see')]