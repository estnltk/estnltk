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
        #pprint( layer_to_dict(texts[0]['original_morph_analysis'][:5]) )
        # Check morph layer content
        expected_doc1_morph_dict_first_5_words = \
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
             ]}
        # Validate content
        assert texts[0]['original_morph_analysis'][:5] == \
            dict_to_layer(expected_doc1_morph_dict_first_5_words)
        #
        # Parse ENC and restore morph extended
        #
        texts = []
        for text in parse_enc_file_iterator( fp.name, encoding='utf-8',\
                                             tokenization='preserve',
                                             restore_morph_analysis=True,
                                             extended_morph_form=True ):
            assert 'original_morph_analysis' in text.layers
            assert 'original_syntax' not in text.layers
            texts.append(text)
        #from pprint import pprint
        #pprint( layer_to_dict(texts[0]['original_morph_analysis'][:5]) )
        # Check morph layer content
        expected_doc1_morph_dict_first_5_words = \
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
                                         'form': 'mod indic impf ps3 sg ps af',
                                         'lemma': 'kostma',
                                         'partofspeech': 'V',
                                         'root': 'kost',
                                         'root_tokens': ('kost',)}],
                        'base_span': (5, 11)},
                       {'annotations': [{'clitic': '',
                                         'ending': '0',
                                         'form': 'pos sg nom',
                                         'lemma': 'tasane',
                                         'partofspeech': 'A',
                                         'root': 'tasane',
                                         'root_tokens': ('tasane',)}],
                        'base_span': (12, 18)},
                       {'annotations': [{'clitic': '',
                                         'ending': '0',
                                         'form': 'com sg nom',
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
                        'base_span': (29, 30)}]}
        # Validate content
        assert texts[0]['original_morph_analysis'][:5] == \
                dict_to_layer(expected_doc1_morph_dict_first_5_words)
    finally:
        # clean up: remove temporary file
        os.remove(fp.name)


enc_2023_excerpt_2_error_cases = \
'''
<doc src="Timestamped 2014–2023" feed_hostname="xn--snumid-pxa.ee" feed_country="Estonia" feed_latitude="59.0" feed_longitude="26.0" tags='Arvamus|“Terevisioon"' feed="http://newsfeed.ijs.si/feedns/1295563" url="https://xn--snumid-pxa.ee/2019/09/hea-voimalus-oma-kodu-ule-uhke-olla/" timestamp_year="2019" timestamp_month="2019-09" timestamp_quarter="2019q3" timestamp_date="2019-09-04" crawl_date="2019-09-04" dmoz_categories="Top/Society/Government/Defense_Ministries|Top/Business/Food_and_Related_Products/Marketing_and_Advertising|Top/Reference/Quotations/Wisdom|Top/Society/Genealogy/By_Ethnic_Group|Top/Shopping/Home_and_Garden/Swimming_Pools_and_Spas" dmoz_keywords="Society|Defense_Ministries|Government|Marketing_and_Advertising|Food_and_Related_Products|Business">
<p heading="1">
<s>
Hea	A.sg.n	hea-a	sg_n	hea	hea	0		pos_sg_nom				
võimalus	S.sg.n	võimalus-s	sg_n	võimalus	võimalus	0		com_sg_nom				
oma	P.sg.g	oma-p	sg_g	oma	oma	0		sg_gen		pos_det_refl		
kodu	S.sg.g	kodu-s	sg_g	kodu	kodu	0		com_sg_gen				
üle	K	üle-k		üle	üle	0		post				gen
uhke	A.sg.n	uhke-a	sg_n	uhke	uhke	0		pos_sg_nom				
olla	V.da	olema-v	da	ole	ole	a		mod_inf			inf	Intr
</s>
</p>
</doc>
<doc src="Timestamped 2014–2023" genre="periodicals" genre_src="site list" title="Ivi Eenmaa: \"Rahu, ainult rahu! Kõik, mis on tulnud Hiinast, ei kesta kaua!" url="https://elu.ohtuleht.ee/995275/ivi-eenmaa-rahu-ainult-rahu-koik-mis-on-tulnud-hiinast-ei-kesta-kaua" feed="https://www.ohtuleht.ee/rss" timestamp_year="2020" timestamp_month="2020-03" timestamp_quarter="2020q1" timestamp_date="2020-03-14" feed_fetched="2020-03-14" crawled_date="2020-03-14">
</s>
<p heading="0">
<s>
Eile	D	eile-d		eile	eile	0						
õhtul	S.sg.ad	õhtu-s	sg_ad	õhtu	õhtu	l		com_sg_ad				
lõppes	V.s	lõppema-v	s	lõppe	lõppe	s		mod_indic_impf_ps3_sg_ps_af			fin	Intr_Kom
meil	P.pl.ad	mina-p	pl_ad	mina	mina	l		pl_ad		ps1		
WC	Y.?	wc-y	?	wc	wc	0		nominal				
paber	S.sg.n	paber-s	sg_n	paber	paber	0		com_sg_nom				
-	Z	--z		-	-				Dsh			
poodides	S.pl.in	pood-s	pl_in	pood	pood	des		com_pl_in				
pole	V.neg.o	olema-v	neg_o	ole	ole	0		aux_imper_pres_ps2_sg_ps_neg			fin	Intr
ja	J	ja-j		ja	ja	0		sub_crd				
nr2	Y.?	nr2-y	?	nr2	nr2	0		nominal				
hüüab	V.b	hüüdma-v	b	hüüd	hüüd	b		mod_indic_pres_ps3_sg_ps_af			fin	NGP-P_All_Tr
tulles	V.des	tulema-v	des	tule	tule	es		mod_ger			inf	Intr
<g/>
.	Z	.-z		.	.				Fst			
</s>
</p>
</doc>
'''

def test_parse_enc2023_file_iterator_error_cases():
    # Test that fixed parse_enc can resolve error cases
    # Set up: Create an example file from the enc_2023_excerpt_2_error_case
    fp = tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', 
                                     prefix='enc_2023_excerpt_',
                                     suffix='.vert', delete=False)
    fp.write( enc_2023_excerpt_2_error_cases )
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
            text_count += 1
            word_count += len(text['original_morph_analysis'])
            texts.append(text)
        assert text_count == 2
        assert word_count == 7 + 14
        assert texts[1].meta == \
            {'src': 'Timestamped 2014–2023', 'genre': 'periodicals', 'genre_src': 'site list', 
             'title': 'Ivi Eenmaa: "Rahu, ainult rahu! Kõik, mis on tulnud Hiinast, ei kesta kaua!', 
             'url': 'https://elu.ohtuleht.ee/995275/ivi-eenmaa-rahu-ainult-rahu-koik-mis-on-tulnud-hiinast-ei-kesta-kaua', 
             'feed': 'https://www.ohtuleht.ee/rss', 'timestamp_year': '2020', 'timestamp_month': '2020-03', 
             'timestamp_quarter': '2020q1', 'timestamp_date': '2020-03-14', 'feed_fetched': '2020-03-14', 
             'crawled_date': '2020-03-14', 'id': 'https://elu.ohtuleht.ee/995275/ivi-eenmaa-rahu-ainult-rahu-koik-mis-on-tulnud-hiinast-ei-kesta-kaua(doc@line:14)', 
             'autocorrected_paragraphs': False}
    finally:
        # clean up: remove temporary file
        os.remove(fp.name)

