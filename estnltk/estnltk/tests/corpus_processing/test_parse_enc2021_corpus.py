import os, os.path, tempfile

from estnltk.converters import layer_to_dict, dict_to_layer
from estnltk.corpus_processing.parse_enc import parse_enc_file_iterator

enc_2021_excerpt_1 = \
"""
<doc id="3489541" src="Wikipedia Talk 2017" genre="forums" genre_src="source" domain_distance="0" url="https://et.wikipedia.org/wiki/Talk:”Ei_se_mitään!”_sanoi_Eemeli" title="Talk:”Ei_se_mitään!”_sanoi_Eemeli" wiki_categories="" wiki_translations="0" paragraphs="3" chars="358" crawl_date="2017-11-15 17:47" lang_scores="Estonian: 236.11, Russian: 0.00, English: 83.11, Finnish: 98.10, Ukrainian: 0.00, Belarusian: 0.00, Serbian: 0.00, Bulgarian: 0.00, Macedonian: 0.00" lang_old2="estonian" lang_scores="estonian: 156.65, finnish: 64.30, english: 56.98, arabic: 0.00, chinese: 0.00, danish: 51.69, french: 46.40, german: 46.96, hindi: 0.00, italian: 41.85, japanese: 0.00, korean: 0.00, polish: 41.61, portuguese: 41.00, russian: 0.00, spanish: 47.91, swedish: 45.60">
<p>
<s>
Kas	D	kas-d		kas	kas	0							1	9	advmod	keeles	keel	S	sg_in	root
filmide	S.pl.g	film-s	pl_g	film	film	de		com_pl_gen					2	3	nmod	pealkirjad	pealkiri	S	pl_n	nsubj:cop
pealkirjad	S.pl.n	pealkiri-s	pl_n	peal kiri	peal_kiri	d		com_pl_nom					3	9	nsubj:cop	keeles	keel	S	sg_in	root
ei	V.neg	ei-v	neg	ei	ei	0		aux_neg			inf		4	9	aux	keeles	keel	S	sg_in	root
pea	V.o	pidama-v	o	pida	pida	0		mod_indic_pres_ps_neg			fin	NGP-P	5	9	aux	keeles	keel	S	sg_in	root
siis	D	siis-d		siis	siis	0							6	9	advmod	keeles	keel	S	sg_in	root
olema	V.ma	olema-v	ma	ole	ole	ma		mod_sup_ps_ill			inf	Intr	7	9	cop	keeles	keel	S	sg_in	root
eesti	G	eesti-g		eesti	eesti	0							8	9	amod	keeles	keel	S	sg_in	root
keeles	S.sg.in	keel-s	sg_in	keel	keel	s		com_sg_in					9	0	root					
<g/>
?	Z	?-z		?	?				Int				10	9	punct	keeles	keel	S	sg_in	root
</s>
<s>
Kumb	P.sg.n	kumb-p	sg_n	kumb	kumb	0		sg_nom		rel			1	3	nsubj:cop	õige	õige	A	sg_n	root
on	V.b	olema-v	b	ole	ole	0		mod_indic_pres_ps3_sg_ps_af			fin	Intr	2	3	cop	õige	õige	A	sg_n	root
õige	A.sg.n	õige-a	sg_n	õige	õige	0		pos_sg_nom					3	0	root					
<g/>
?	Z	?-z		?	?				Int				4	3	punct	õige	õige	A	sg_n	root
</s>
</p>
</doc>
<doc id="3336603" src="Wikipedia Talk 2017" genre="forums" genre_src="source" domain_distance="0" url="https://et.wikipedia.org/wiki/Talk:Carl_Ludvig_Engel" title="Talk:Carl_Ludvig_Engel" wiki_categories="" wiki_translations="0" paragraphs="2" chars="275" crawl_date="2017-11-08 00:22" lang_scores="Estonian: 133.62, Russian: 0.00, English: 31.96, Finnish: 49.22, Ukrainian: 0.00, Belarusian: 0.00, Serbian: 0.00, Bulgarian: 0.00, Macedonian: 0.00" lang_old2="estonian" lang_scores="estonian: 133.62, finnish: 49.22, english: 31.96, arabic: 0.00, chinese: 0.00, danish: 29.82, french: 30.04, german: 32.27, hindi: 0.00, italian: 22.93, japanese: 0.00, korean: 0.00, polish: 33.80, portuguese: 23.54, russian: 0.00, spanish: 23.95, swedish: 30.08">
<p>
<s>
Küsimus	S.sg.n	küsimus-s	sg_n	küsimus	küsimus	0		com_sg_nom					1	4	nsubj:cop	avalikkusele	avalikkus	S	sg_all	root
oligi	V.s	olema-v	s	ole	ole	i	gi	mod_indic_impf_ps3_sg_ps_af			fin	Intr	2	4	cop	avalikkusele	avalikkus	S	sg_all	root
laiemale	C.sg.all	laiem-c	sg_all	laiem	laiem	le		comp_sg_all					3	4	amod	avalikkusele	avalikkus	S	sg_all	root
avalikkusele	S.sg.all	avalikkus-s	sg_all	avalikkus	avalikkus	le		com_sg_all					4	0	root					
<g/>
.	Z	.-z		.	.				Fst				5	4	punct	avalikkusele	avalikkus	S	sg_all	root
</s>
</p>
</doc>
"""

# ===========================================================
#    Loading ENC 2021 corpus files
# ===========================================================

def test_parse_enc2021_file_iterator_w_original_tokenization():
    # Set up: Create an example file from the enc_2021_excerpt_1
    fp = tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', 
                                     prefix='enc_2021_excerpt_',
                                     suffix='.vert', delete=False)
    fp.write( enc_2021_excerpt_1 )
    fp.close()
    # Attempt to parse enc 2021 file
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
        {'id': '3489541', 'src': 'Wikipedia Talk 2017', 'genre': 'forums', 'genre_src': 'source', 
         'domain_distance': '0', 'url': 'https://et.wikipedia.org/wiki/Talk:”Ei_se_mitään!”_sanoi_Eemeli', 
         'title': 'Talk:”Ei_se_mitään!”_sanoi_Eemeli', 'wiki_translations': '0', 
         'paragraphs': '3', 'chars': '358', 'crawl_date': '2017-11-15 17:47', 
         'lang_scores': 'Estonian: 236.11, Russian: 0.00, English: 83.11, Finnish: 98.10, Ukrainian: 0.00, Belarusian: 0.00, '+\
                        'Serbian: 0.00, Bulgarian: 0.00, Macedonian: 0.00',
         'lang_scores2': 'estonian: 156.65, finnish: 64.30, english: 56.98, arabic: 0.00, chinese: 0.00, danish: 51.69, '+\
                        'french: 46.40, german: 46.96, hindi: 0.00, italian: 41.85, japanese: 0.00, korean: 0.00, polish: 41.61, '+\
                        'portuguese: 41.00, russian: 0.00, spanish: 47.91, swedish: 45.60', 
         'lang_old2': 'estonian'}
    assert texts[1].meta == \
        {'id': '3336603', 'src': 'Wikipedia Talk 2017', 'genre': 'forums', 'genre_src': 'source', 
         'domain_distance': '0', 'url': 'https://et.wikipedia.org/wiki/Talk:Carl_Ludvig_Engel', 
         'title': 'Talk:Carl_Ludvig_Engel', 'wiki_translations': '0', 'paragraphs': '2', 'chars': '275', 
         'crawl_date': '2017-11-08 00:22', 'lang_scores': 'Estonian: 133.62, Russian: 0.00, English: 31.96, Finnish: 49.22, '+\
         'Ukrainian: 0.00, Belarusian: 0.00, Serbian: 0.00, Bulgarian: 0.00, Macedonian: 0.00', 
         'lang_scores2': 'estonian: 133.62, finnish: 49.22, english: 31.96, arabic: 0.00, '+\
         'chinese: 0.00, danish: 29.82, french: 30.04, german: 32.27, hindi: 0.00, italian: 22.93, japanese: 0.00, korean: 0.00, '+\
         'polish: 33.80, portuguese: 23.54, russian: 0.00, spanish: 23.95, swedish: 30.08', 'lang_old2': 'estonian'}
    # Check for existence of tokenization layers
    for layer in ['original_paragraphs', 'original_words', 'original_compound_tokens', \
                  'original_sentences', 'original_tokens', 'original_word_chunks']:
        for text in texts:
            assert layer in text.layers
            assert len(layer) > 0 or layer in ['original_word_chunks', 'original_compound_tokens']
    # Check document contents
    assert texts[0]['original_words'].text == ['Kas', 'filmide', 'pealkirjad', 'ei', 'pea', 'siis', 'olema', 'eesti', 'keeles', '?', \
                                               'Kumb', 'on', 'õige', '?']
    assert texts[1]['original_words'].text == ['Küsimus', 'oligi', 'laiemale', 'avalikkusele', '.']


def test_parse_enc2021_file_iterator_w_original_morph_and_syntax():
    # Set up: Create an example file from the enc_2021_excerpt_1
    fp = tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', 
                                     prefix='enc_2021_excerpt_',
                                     suffix='.vert', delete=False)
    fp.write( enc_2021_excerpt_1 )
    fp.close()
    try:
        # Parse ENC and restore only morph
        text_count = 0
        word_count = 0
        for text in parse_enc_file_iterator( fp.name, encoding='utf-8',\
                                             tokenization='preserve',
                                             restore_morph_analysis=True ):
            assert 'original_morph_analysis' in text.layers
            assert 'original_syntax' not in text.layers
            text_count += 1
            word_count += len(text['original_morph_analysis'])
        assert text_count == 2
        assert word_count == 19
        word_count = 0
        texts = []
        # Parse ENC and restore morph and syntax
        for text in parse_enc_file_iterator( fp.name, encoding='utf-8',\
                                             tokenization='preserve',
                                             restore_morph_analysis=True,
                                             restore_syntax=True ):
            assert 'original_morph_analysis' in text.layers
            assert 'original_syntax' in text.layers
            assert len(text['original_morph_analysis']) == len(text['original_syntax'])
            word_count += len(text['original_syntax'])
            texts.append(text)
        assert len(texts) == 2
        assert word_count == 19
        # Check morph layer content
        expected_doc2_morph_dict = \
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
                                         'form': 'sg n',
                                         'lemma': 'küsimus',
                                         'partofspeech': 'S',
                                         'root': 'küsimus',
                                         'root_tokens': ('küsimus',)}],
                        'base_span': (0, 7)},
                       {'annotations': [{'clitic': 'gi',
                                         'ending': 'i',
                                         'form': 's',
                                         'lemma': 'olema',
                                         'partofspeech': 'V',
                                         'root': 'ole',
                                         'root_tokens': ('ole',)}],
                        'base_span': (8, 13)},
                       {'annotations': [{'clitic': '',
                                         'ending': 'le',
                                         'form': 'sg all',
                                         'lemma': 'laiem',
                                         'partofspeech': 'C',
                                         'root': 'laiem',
                                         'root_tokens': ('laiem',)}],
                        'base_span': (14, 22)},
                       {'annotations': [{'clitic': '',
                                         'ending': 'le',
                                         'form': 'sg all',
                                         'lemma': 'avalikkus',
                                         'partofspeech': 'S',
                                         'root': 'avalikkus',
                                         'root_tokens': ('avalikkus',)}],
                        'base_span': (23, 35)},
                       {'annotations': [{'clitic': '',
                                         'ending': '',
                                         'form': '',
                                         'lemma': '.',
                                         'partofspeech': 'Z',
                                         'root': '.',
                                         'root_tokens': ('.',)}],
                        'base_span': (35, 36)}]}
        #from pprint import pprint
        #pprint( layer_to_dict(texts[1]['original_morph_analysis']) )
        assert texts[1]['original_morph_analysis'] == dict_to_layer(expected_doc2_morph_dict)
    finally:
        # clean up: remove temporary file
        os.remove(fp.name)


def test_parse_enc2021_file_iterator_w_original_syntax():
    # Set up: Create an example file from the enc_2021_excerpt_1
    fp = tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', 
                                     prefix='enc_2021_excerpt_',
                                     suffix='.vert', delete=False)
    fp.write( enc_2021_excerpt_1 )
    fp.close()
    try:
        word_count = 0
        texts = []
        # Parse ENC and restore only syntax
        for text in parse_enc_file_iterator( fp.name, encoding='utf-8',\
                                             tokenization='preserve',
                                             restore_morph_analysis=False,
                                             restore_syntax=True ):
            assert 'original_morph_analysis' not in text.layers
            assert 'original_syntax' in text.layers
            assert len(text['original_words']) == len(text['original_syntax'])
            texts.append(text)
            word_count += len(text['original_syntax'])
        assert len(texts) == 2
        assert word_count == 19
        # Check syntax layer content
        expected_doc2_syntax_dict = \
            {'ambiguous': True,
             'attributes': ('id', 'head', 'lemma', 'xpostag', 'feats', 'deprel'),
             'enveloping': None,
             'meta': {},
             'name': 'original_syntax',
             'parent': 'original_words',
             'secondary_attributes': (),
             'serialisation_module': None,
             'spans': [{'annotations': [{'deprel': 'nsubj:cop',
                                         'feats': 'com sg nom',
                                         'head': 4,
                                         'id': 1,
                                         'lemma': 'küsimus',
                                         'xpostag': 'S'}],
                        'base_span': (0, 7)},
                       {'annotations': [{'deprel': 'cop',
                                         'feats': 'mod indic impf ps3 sg ps af',
                                         'head': 4,
                                         'id': 2,
                                         'lemma': 'olema',
                                         'xpostag': 'V'}],
                        'base_span': (8, 13)},
                       {'annotations': [{'deprel': 'amod',
                                         'feats': 'comp sg all',
                                         'head': 4,
                                         'id': 3,
                                         'lemma': 'laiem',
                                         'xpostag': 'C'}],
                        'base_span': (14, 22)},
                       {'annotations': [{'deprel': 'root',
                                         'feats': 'com sg all',
                                         'head': 0,
                                         'id': 4,
                                         'lemma': 'avalikkus',
                                         'xpostag': 'S'}],
                        'base_span': (23, 35)},
                       {'annotations': [{'deprel': 'punct',
                                         'feats': '',
                                         'head': 4,
                                         'id': 5,
                                         'lemma': '.',
                                         'xpostag': 'Z'}],
                        'base_span': (35, 36)}]}
        #from pprint import pprint
        #pprint( layer_to_dict(texts[1]['original_syntax']) )
        assert texts[1]['original_syntax'] == dict_to_layer(expected_doc2_syntax_dict)
    finally:
        # clean up: remove temporary file
        os.remove(fp.name)

