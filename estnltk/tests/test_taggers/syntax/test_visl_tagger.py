from estnltk import Text
from estnltk.converters import layer_to_dict
from estnltk.taggers import VislTagger


visl_dict = {'_base': 'words',
             'ambiguous': True,
             'attributes': ('visl',),
             'enveloping': None,
             'name': 'visl',
             'parent': 'words',
             'spans': [[{'_index_': 0,
                'end': 4,
                'start': 0,
                'visl': '"juba" L0 D cap @ADVL #1->3'}],
              [{'_index_': 1,
                'end': 10,
                'start': 5,
                'visl': '"taht" Lb V main indic pres ps3 sg ps af @FMV #2->0'}],
              [{'_index_': 2,
                'end': 16,
                'start': 11,
                'visl': '"saa" Lda V main inf @OBJ #3->2'}],
              [{'_index_': 3,
                'end': 25,
                'start': 17,
                'visl': '"pagar" Lks S com sg tr @ADVL #4->3'}],
              [{'_index_': 4, 'end': 26, 'start': 25, 'visl': '"!" Z Exc CLB #5->5'}],
              [{'_index_': 5,
                'end': 30,
                'start': 27,
                'visl': '"ise" L0 P pos det refl pl nom cap @ADVL #1->3'},
               {'_index_': 5,
                'end': 30,
                'start': 27,
                'visl': '"ise" L0 P pos det refl sg nom cap @ADVL #1->3'}],
              [{'_index_': 6, 'end': 36, 'start': 31, 'visl': '"alles" L0 D @ADVL #2->3'}],
              [{'_index_': 7,
                'end': 40,
                'start': 37,
                'visl': '"tee" L0 S com sg gen @NN> #3->0'},
               {'_index_': 7,
                'end': 40,
                'start': 37,
                'visl': '"tee" L0 S com sg gen @OBJ #3->0'}],
              [{'_index_': 8,
                'end': 49,
                'start': 41,
                'visl': '"esimene" Ll N ord sg ad l @AN> #4->5'}],
              [{'_index_': 9,
                'end': 56,
                'start': 50,
                'visl': '"pool" Ll S com sg ad @<NN @ADVL #5->3'}],
              [{'_index_': 10, 'end': 58, 'start': 57, 'visl': '"," Z Com #6->6'}],
              [{'_index_': 11,
                'end': 64,
                'start': 59,
                'visl': '"vaevu" L0 D @ADVL #7->3'}],
              [{'_index_': 12,
                'end': 82,
                'start': 65,
                'visl': '"kolme_kümne_kolmene" L0 A pos sg nom @ADVL #8->5'}],
              [{'_index_': 13, 'end': 84, 'start': 83, 'visl': '"." Z Fst CLB #9->9'}]]}


def test_visl_tagger():
    text = Text('Juba tahab saada pagariks! Ise alles tee esimesel poolel , vaevu kolmekümnekolmene .').tag_layer(['morph_extended'])

    tagger = VislTagger()
    tagger.tag(text)
    result = layer_to_dict(layer=text.visl, text=text)
    assert visl_dict == result
