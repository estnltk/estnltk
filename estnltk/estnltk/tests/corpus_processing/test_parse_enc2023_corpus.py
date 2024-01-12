import os, os.path, tempfile

from estnltk.converters import layer_to_dict, dict_to_layer
from estnltk.corpus_processing.parse_enc import parse_enc_file_iterator

enc_2023_excerpt_1 = \
"""
<doc src="Literature Old 1864–1945" filename="b10500790" original_author="Anton Hansen Tammsaare" original_title="Kärbes" title="Kärbes" publisher="Maa" original_year="1917*" published_year="1917*" genre="fiction:Short story|fiction" genre_src="source" translated="no" isbn="Unknown">
<p>
<s>
Nüüd	D	nüüd-d		nüüd	nüüd	0						
kostis	V.s	kostma-v	s	kost	kost	is		mod_indic_impf_ps3_sg_ps_af			fin	Intr
tasane	A.sg.n	tasane-a	sg_n	tasane	tasane	0		pos_sg_nom				
naerukihin	S.sg.n	naerukihin-s	sg_n	naeru kihin	naeru_kihin	0		com_sg_nom				
<g/>
.	Z	.-z		.	.				Fst			
</s>
</p>
<p>
<s>
"	Z	"-z		"	"				Quo			
<g/>
Ah	I	ah-i		ah	ah	0						
sind	P.sg.p	sina-p	sg_p	sina	sina	d		sg_part		ps2		
wõrukaela	S.adt	wõrukael-s	adt	wõru kael	wõru_kael	0		com_sg_adit				
<g/>
!	Z	!-z		!	!				Exc			
</s>
<s>
Mina	P.sg.n	mina-p	sg_n	mina	mina	0		sg_nom		ps1		
tunnen	V.n	tundma-v	n	tund	tund	n		mod_indic_pres_ps1_sg_ps_af			fin	Part-P
<g/>
,	Z	,-z		,	,				Com			
et	J	et-j		et	et	0		sub_crd				
õhk	S.sg.n	õhk-s	sg_n	õhk	õhk	0		com_sg_nom				
pole	V.neg.o	olema-v	neg_o	ole	ole	0		aux_imper_pres_ps2_sg_ps_neg			fin	Intr
puhas	A.sg.n	puhas-a	sg_n	puhas	puhas	0		pos_sg_nom				
<g/>
.	Z	.-z		.	.				Fst			
<g/>
"	Z	"-z		"	"				Quo			
</s>
</p>
</doc>
<doc src="Literature Old 1864–1945" filename="b11422737" original_author="Eduard Bornhöhe" original_title="Tallinna narrid ja narrikesed" title="Tallinna narrid ja narrikesed" publisher="K. Busch" original_year="1892*" published_year="1892*" genre="fiction:Set of stories|fiction" genre_src="source" translated="no" isbn="Unknown">
<p>
<s>
Uulitsapoisid	S.pl.n	uulitsapoiss-s	pl_n	uulitsa poiss	uulitsa_poiss	d		com_pl_nom				
lakkusiwad	S.pl.n	lakkusiwa-s	pl_n	lakkusiwa	lakkusiwa	d		com_pl_nom				
ta	P.sg.g	tema-p	sg_g	tema	tema	0		sg_gen		ps3		
suure	A.sg.g	suur-a	sg_g	suur	suur	0		pos_sg_gen				
isuga	S.sg.kom	isu-s	sg_kom	isu	isu	ga		com_sg_kom				
puhtaks	A.sg.tr	puhas-a	sg_tr	puhas	puhas	ks		pos_sg_tr				
<g/>
.	Z	.-z		.	.				Fst			
</s>
<s>
Jaan	H.sg.n	Jaan-h	sg_n	Jaan	Jaan	0		prop_sg_nom				
läks	V.s	minema-v	s	mine	mine	s		mod_indic_impf_ps3_sg_ps_af			fin	
kolmandamast	S.sg.n	kolmandamast-s	sg_n	kolmanda mast	kolmanda_mast	0		com_sg_nom				
koolist	S.sg.el	kool-s	sg_el	kool	kool	st		com_sg_el				
suuremat	C.sg.p	suurem-c	sg_p	suurem	suurem	t		comp_sg_part				
õigust	S.sg.p	õigus-s	sg_p	õigus	õigus	t		com_sg_part				
ja	J	ja-j		ja	ja	0		sub_crd				
haridust	S.sg.p	haridus-s	sg_p	haridus	haridus	t		com_sg_part				
otsima	V.ma	otsima-v	ma	otsi	otsi	ma		mod_sup_ps_ill			inf	NGP-P
<g/>
.	Z	.-z		.	.				Fst			
</s>
</p>
</doc>
"""

# ===========================================================
#    Loading ENC 2023 corpus files
# ===========================================================

def test_parse_enc2023_file_iterator_w_original_tokenization():
    # Set up: Create an example file from the enc_2023_excerpt_1
    fp = tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', 
                                     prefix='enc_2023_excerpt_',
                                     suffix='.vert', delete=False)
    fp.write( enc_2023_excerpt_1 )
    fp.close()
    # Attempt to parse enc 2023 file
    try:
        texts = []
        for text_obj in parse_enc_file_iterator( fp.name, encoding='utf-8',\
                                                 tokenization='preserve'):
            texts.append( text_obj )
    finally:
        # clean up: remove temporary file
        os.remove(fp.name)

    # Make assertions
    assert len(texts) == 2
    # Check document metadata
    assert texts[0].meta == \
        {'src': 'Literature Old 1864–1945', 'filename': 'b10500790', 'original_author': 'Anton Hansen Tammsaare', 
         'original_title': 'Kärbes', 'title': 'Kärbes', 'publisher': 'Maa', 'original_year': '1917*', 'published_year': '1917*', 
         'genre': 'fiction:Short story|fiction', 'genre_src': 'source', 'translated': 'no', 'isbn': 'Unknown', 
         'id': '(doc@line:1)', 'autocorrected_paragraphs': False}
    assert texts[1].meta == \
        {'src': 'Literature Old 1864–1945', 'filename': 'b11422737', 'original_author': 'Eduard Bornhöhe', 
         'original_title': 'Tallinna narrid ja narrikesed', 'title': 'Tallinna narrid ja narrikesed', 'publisher': 'K. Busch', 
         'original_year': '1892*', 'published_year': '1892*', 'genre': 'fiction:Set of stories|fiction', 
         'genre_src': 'source', 'translated': 'no', 'isbn': 'Unknown', 'id': '(doc@line:38)', 
         'autocorrected_paragraphs': False}
    # Check for existence of tokenization layers
    for layer in ['original_paragraphs', 'original_words', 'original_compound_tokens', \
                  'original_sentences', 'original_tokens', 'original_word_chunks']:
        for text in texts:
            assert layer in text.layers
            assert len(layer) > 0 or layer in ['original_word_chunks', 'original_compound_tokens']
    # Check document contents
    assert texts[0]['original_words'].text == ['Nüüd', 'kostis', 'tasane', 'naerukihin', '.', '"', 'Ah', 'sind', 'wõrukaela', '!', 
                                               'Mina', 'tunnen', ',', 'et', 'õhk', 'pole', 'puhas', '.', '"']
    assert texts[1]['original_words'].text == ['Uulitsapoisid', 'lakkusiwad', 'ta', 'suure', 'isuga', 'puhtaks', '.', 
                                               'Jaan', 'läks', 'kolmandamast', 'koolist', 'suuremat', 'õigust', 'ja', 'haridust', 
                                               'otsima', '.']


def test_parse_enc2023_file_iterator_w_original_morph():
    # Set up: Create an example file from the enc_2023_excerpt_1
    fp = tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', 
                                     prefix='enc_2023_excerpt_',
                                     suffix='.vert', delete=False)
    fp.write( enc_2023_excerpt_1 )
    fp.close()
    try:
        # Parse ENC and restore only morph
        texts = []
        text_count = 0
        word_count = 0
        for text in parse_enc_file_iterator( fp.name, encoding='utf-8',\
                                             tokenization='preserve',
                                             restore_morph_analysis=True ):
            assert 'original_morph_analysis' in text.layers
            assert 'original_syntax' not in text.layers
            text_count += 1
            word_count += len(text['original_morph_analysis'])
            texts.append(text)
        assert text_count == 2
        assert word_count == 36
        word_count = 0
        #from pprint import pprint
        #pprint( layer_to_dict(texts[0]['original_morph_analysis']) )
        
        # Check morph layer content
        expected_doc1_morph_dict = \
            {'ambiguous': True,
             'attributes': ('lemma',
                            'root',
                            'root_tokens',
                            'ending',
                            'clitic',
                            'form',
                            'partofspeech'),
             'enveloping': None,
             'meta': {},
             'name': 'original_morph_analysis',
             'parent': 'original_words',
             'secondary_attributes': (),
             'serialisation_module': None,
             'spans': [{'annotations': [{'clitic': '',
                                         'ending': '0',
                                         'form': '',
                                         'lemma': 'nüüd',
                                         'partofspeech': 'D',
                                         'root': 'nüüd',
                                         'root_tokens': ('nüüd',)}],
                        'base_span': (0, 4)},
                       {'annotations': [{'clitic': '',
                                         'ending': 'is',
                                         'form': 's',
                                         'lemma': 'kostma',
                                         'partofspeech': 'V',
                                         'root': 'kost',
                                         'root_tokens': ('kost',)}],
                        'base_span': (5, 11)},
                       {'annotations': [{'clitic': '',
                                         'ending': '0',
                                         'form': 'sg n',
                                         'lemma': 'tasane',
                                         'partofspeech': 'A',
                                         'root': 'tasane',
                                         'root_tokens': ('tasane',)}],
                        'base_span': (12, 18)},
                       {'annotations': [{'clitic': '',
                                         'ending': '0',
                                         'form': 'sg n',
                                         'lemma': 'naerukihin',
                                         'partofspeech': 'S',
                                         'root': 'naeru_kihin',
                                         'root_tokens': ('naeru', 'kihin')}],
                        'base_span': (19, 29)},
                       {'annotations': [{'clitic': '',
                                         'ending': '',
                                         'form': '',
                                         'lemma': '.',
                                         'partofspeech': 'Z',
                                         'root': '.',
                                         'root_tokens': ('.',)}],
                        'base_span': (29, 30)},
                       {'annotations': [{'clitic': '',
                                         'ending': '',
                                         'form': '',
                                         'lemma': '"',
                                         'partofspeech': 'Z',
                                         'root': '"',
                                         'root_tokens': ('"',)}],
                        'base_span': (32, 33)},
                       {'annotations': [{'clitic': '',
                                         'ending': '0',
                                         'form': '',
                                         'lemma': 'ah',
                                         'partofspeech': 'I',
                                         'root': 'ah',
                                         'root_tokens': ('ah',)}],
                        'base_span': (33, 35)},
                       {'annotations': [{'clitic': '',
                                         'ending': 'd',
                                         'form': 'sg p',
                                         'lemma': 'sina',
                                         'partofspeech': 'P',
                                         'root': 'sina',
                                         'root_tokens': ('sina',)}],
                        'base_span': (36, 40)},
                       {'annotations': [{'clitic': '',
                                         'ending': '0',
                                         'form': 'adt',
                                         'lemma': 'wõrukael',
                                         'partofspeech': 'S',
                                         'root': 'wõru_kael',
                                         'root_tokens': ('wõru', 'kael')}],
                        'base_span': (41, 50)},
                       {'annotations': [{'clitic': '',
                                         'ending': '',
                                         'form': '',
                                         'lemma': '!',
                                         'partofspeech': 'Z',
                                         'root': '!',
                                         'root_tokens': ('!',)}],
                        'base_span': (50, 51)},
                       {'annotations': [{'clitic': '',
                                         'ending': '0',
                                         'form': 'sg n',
                                         'lemma': 'mina',
                                         'partofspeech': 'P',
                                         'root': 'mina',
                                         'root_tokens': ('mina',)}],
                        'base_span': (52, 56)},
                       {'annotations': [{'clitic': '',
                                         'ending': 'n',
                                         'form': 'n',
                                         'lemma': 'tundma',
                                         'partofspeech': 'V',
                                         'root': 'tund',
                                         'root_tokens': ('tund',)}],
                        'base_span': (57, 63)},
                       {'annotations': [{'clitic': '',
                                         'ending': '',
                                         'form': '',
                                         'lemma': ',',
                                         'partofspeech': 'Z',
                                         'root': ',',
                                         'root_tokens': (',',)}],
                        'base_span': (63, 64)},
                       {'annotations': [{'clitic': '',
                                         'ending': '0',
                                         'form': '',
                                         'lemma': 'et',
                                         'partofspeech': 'J',
                                         'root': 'et',
                                         'root_tokens': ('et',)}],
                        'base_span': (65, 67)},
                       {'annotations': [{'clitic': '',
                                         'ending': '0',
                                         'form': 'sg n',
                                         'lemma': 'õhk',
                                         'partofspeech': 'S',
                                         'root': 'õhk',
                                         'root_tokens': ('õhk',)}],
                        'base_span': (68, 71)},
                       {'annotations': [{'clitic': '',
                                         'ending': '0',
                                         'form': 'neg o',
                                         'lemma': 'olema',
                                         'partofspeech': 'V',
                                         'root': 'ole',
                                         'root_tokens': ('ole',)}],
                        'base_span': (72, 76)},
                       {'annotations': [{'clitic': '',
                                         'ending': '0',
                                         'form': 'sg n',
                                         'lemma': 'puhas',
                                         'partofspeech': 'A',
                                         'root': 'puhas',
                                         'root_tokens': ('puhas',)}],
                        'base_span': (77, 82)},
                       {'annotations': [{'clitic': '',
                                         'ending': '',
                                         'form': '',
                                         'lemma': '.',
                                         'partofspeech': 'Z',
                                         'root': '.',
                                         'root_tokens': ('.',)}],
                        'base_span': (82, 83)},
                       {'annotations': [{'clitic': '',
                                         'ending': '',
                                         'form': '',
                                         'lemma': '"',
                                         'partofspeech': 'Z',
                                         'root': '"',
                                         'root_tokens': ('"',)}],
                        'base_span': (83, 84)}]}

        assert texts[0]['original_morph_analysis'] == dict_to_layer(expected_doc1_morph_dict)
    finally:
        # clean up: remove temporary file
        os.remove(fp.name)

