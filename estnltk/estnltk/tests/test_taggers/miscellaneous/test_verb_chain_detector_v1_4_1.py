# Tests for VerbChainDetector (which uses v1.4.1 source)
from estnltk import Text
from estnltk.taggers import VerbChainDetector


def test_verb_chain_detection_1():
    # Test detection of main verb chains
    vc_detector = VerbChainDetector()
    test_data = [
       { 'text': 'Hariduselt geograaf, sattus ta esimeste korda jääpangale, mis triivis juba Norra poole.',
         'vc_texts' : [['sattus'], ['triivis']],
         'patterns' : [['verb'],   ['verb']], 
         'roots'    : [['sattu'],  ['triivi']],
         'remaining_verbs': [False, False] },
       { 'text': 'Uudistes kõlasid just ütlused, milles seati kahtluse alla inimese roll kliima muutumises.',
         'vc_texts' : [['kõlasid'], ['seati']],
         'patterns' : [['verb'],   ['verb']], 
         'roots'    : [['kõla'],  ['sead']],
         'remaining_verbs': [False, False] },
       { 'text': 'Elron saab lõpuks osta portsu "porgandeid", aga kust minister ühtäkki selleks raha sai?',
         'vc_texts' : [['saab', 'osta'], ['sai']],
         'patterns' : [['verb', 'verb'], ['verb']], 
         'roots'    : [['saa', 'ost'],   ['saa']],
         'remaining_verbs': [False, False] },
       { 'text': 'Teadus on juba aastakümneid kliimamuutuse kohta kaalukaid fakte tõestuseks esitanud.',
         'vc_texts' : [['on', 'esitanud']],
         'patterns' : [['ole', 'verb']], 
         'roots'    : [['ole', 'esita']],
         'remaining_verbs': [False] },
       { 'text': 'Teadus on rääkinud, loodus on tugevaid signaale edastanud ja nüüd on pall poliitikute käes.',
         'vc_texts' : [['on', 'rääkinud'], ['on', 'edastanud'], ['on']],
         'patterns' : [['ole', 'verb'], ['ole', 'verb'], ['ole']], 
         'roots'    : [['ole', 'rääki'], ['ole', 'edasta'], ['ole']],
         'remaining_verbs': [False, False, False] },
       { 'text': 'Siin ei saa enam toetuda lihtsalt ühe inimese veendumusele.',
         'vc_texts' : [['ei', 'saa', 'toetuda']],
         'patterns' : [['ei', 'verb', 'verb']], 
         'roots'    : [['ei', 'saa', 'toetu']],
         'remaining_verbs': [False] },
       { 'text': 'Ei saa ju lihtsalt keelata autodega sõita või tuba soojaks kütta.',
         'vc_texts' : [['Ei', 'saa', 'keelata']],
         'patterns' : [['ei', 'verb', 'verb']], 
         'roots'    : [['ei', 'saa', 'keela']],
         'remaining_verbs': [True] },
    ]
    for test_text in test_data:
        # Prepare text. Add required layers
        text = Text(test_text['text'])
        text.tag_layer(['words', 'sentences', 'morph_analysis', 'clauses'])
        # Tag chains
        vc_detector.tag( text )
        # Check results 
        assert 'verb_chains' in text.layers
        verb_chains = text['verb_chains']
        assert len(test_text['vc_texts']) == len(verb_chains)
        verb_chain_texts = [vc.text for vc in verb_chains]
        assert verb_chain_texts == test_text['vc_texts']
        verb_chain_patterns = [vc.pattern for vc in verb_chains]
        assert verb_chain_patterns == test_text['patterns']
        verb_chain_roots = [vc.roots for vc in verb_chains]
        assert verb_chain_roots == test_text['roots']
        has_remaining_verbs = [vc.remaining_verbs for vc in verb_chains]
        assert has_remaining_verbs == test_text['remaining_verbs']


def test_verb_chain_detection_2():
    # Test detection of some rather long (and a bit complex) verb chains
    vc_detector = VerbChainDetector()
    test_data = [
       { 'text': 'Oluline on teada , et plaanis oli olla vaid kolm päeva ...',
         'vc_texts' : [['Oluline', 'on', 'teada'], ['plaanis', 'oli', 'olla']],
         'patterns' : [['ole', 'nom/adv', 'verb'], ['ole', 'nom/adv', 'ole']],
         'roots'    : [['ole', 'oluline', 'tead'], ['ole', 'plaan', 'ole']],
         'word_ids' : [[1, 0, 2], [6, 5, 7]],
       },
       { 'text': 'Abilinnapea tegi juba eelmise aasta lõpus ettepaneku leida linnaeelarvest võimalusi kainestusmaja luua .',
         'vc_texts' : [['tegi', 'ettepaneku', 'leida', 'võimalusi', 'luua']],
         'patterns' : [['verb', 'nom/adv', 'verb', 'nom/adv', 'verb']], 
         'roots'    : [['tege', 'ette_panek', 'leid', 'võimalus', 'loo']],
       },
       { 'text': 'See annab neile võimaluse suu väga pärani lahti ajada ning saagi küljest suuri tükke hammustada .',
         'vc_texts' : [['annab', 'võimaluse', 'ajada', 'ning', 'hammustada']],
         'patterns' : [['verb', 'nom/adv', 'verb', '&', 'verb']],
         'roots'    : [['and', 'võimalus', 'aja', 'ning', 'hammusta']],
       },
       { 'text': 'Und küll pole , aga ma ei näe põhjust öö läbi üleval olla .',
         'vc_texts' : [['pole'], ['ei', 'näe', 'põhjust', 'olla']],
         'patterns' : [['pole'], ['ei', 'verb', 'nom/adv', 'ole']],
         'roots'    : [['ole'], ['ei', 'näge', 'põhjus', 'ole']],
       },
       { 'text': 'Igaüks ajab oma rida ega ole püüdnudki milleski kokku leppida .',
         'vc_texts' : [['ajab'], ['ega', 'ole', 'püüdnudki', 'leppida']],
         'patterns' : [['verb'], ['ega', 'ole', 'verb', 'verb']],
         'roots'    : [['aja'], ['ega', 'ole', 'püüd', 'leppi']],
       },
       { 'text': 'Ära mine rikkaga riidlema ega vägevaga kohut käima .',
         'vc_texts' : [['Ära', 'mine', 'riidlema', 'ega', 'käima']],
         'patterns' : [['ära', 'verb', 'verb', '&', 'verb']],
         'roots'    : [['ära', 'mine', 'riidle', 'ega', 'käi']],
       },
       { 'text': 'Ma olen siiski teadlane, mitte kohvikutante, ega ole harjunud koguma või levitama kuuldusi.',
         'vc_texts' : [['olen'], ['ega', 'ole', 'harjunud', 'koguma', 'või', 'levitama']],
         'patterns' : [['ole'], ['ega', 'ole', 'verb', 'verb', '&', 'verb']],
         'roots'    : [['ole'], ['ega', 'ole', 'harju', 'kogu', 'või', 'levita']],
       },
    ]
    for test_text in test_data:
        # Prepare text. Add required layers
        text = Text(test_text['text'])
        text.tag_layer(['words', 'sentences', 'morph_analysis', 'clauses'])
        # Tag chains
        vc_detector.tag( text )
        # Check results
        verb_chains = text['verb_chains']
        verb_chain_texts = [vc.text for vc in verb_chains]
        assert verb_chain_texts == test_text['vc_texts']
        verb_chain_patterns = [vc.pattern for vc in verb_chains]
        assert verb_chain_patterns == test_text['patterns']
        verb_chain_roots = [vc.roots for vc in verb_chains]
        assert verb_chain_roots == test_text['roots']
        if 'word_ids' in test_text:
            verb_chain_word_ids = [vc.word_ids for vc in verb_chains]
            assert verb_chain_word_ids == test_text['word_ids']



def test_verb_chain_detection_from_v1_4():
    # Verb chain detection test texts from EstNLTK version 1.4
    vc_detector = VerbChainDetector()
    test_data = [
       { 'text': 'Kass, suur ja must, ei jooksnud üle tee.',
         'vc_texts'  : [['ei', 'jooksnud']],
         'patterns'  : [['ei', 'verb']], 
         'roots'     : [['ei', 'jooks']],
         'polarities': ['NEG'],
       },
       { 'text': 'Londoni lend pidi täna hommikul kell 4:30 Tallinna saabuma.',
         'vc_texts' : [['pidi', 'saabuma']],
         'patterns' : [['verb', 'verb']],
         'roots'    : [['pida', 'saabu']],
         'polarities': ['POS'],
       },
       { 'text': 'Lend oleks Tallinna pidanud juba öösel jõudma.',
         'vc_texts' : [['oleks', 'pidanud', 'jõudma']],
         'patterns' : [['ole', 'verb', 'verb']],
         'roots'    : [['ole', 'pida', 'jõud']],
         'polarities': ['POS'],
       },
       { 'text': 'Samas on selge, et senine korraldus jätkuda ei saa. Saaks ehk jätkuda teisiti.',
         'vc_texts' : [['on'],  ['jätkuda', 'ei', 'saa'], ['Saaks', 'jätkuda']],
         'patterns' : [['ole'], ['ei', 'verb', 'verb'], ['verb', 'verb']],
         'roots'    : [['ole'], ['ei', 'saa', 'jätku'], ['saa', 'jätku']],
         'polarities': ['POS', 'NEG', 'POS'],
       },
    ]
    for test_text in test_data:
        # Prepare text. Add required layers
        text = Text(test_text['text'])
        text.tag_layer(['words', 'sentences', 'morph_analysis', 'clauses'])
        # Tag chains
        vc_detector.tag( text )
        # Check results
        verb_chains = text['verb_chains']
        verb_chain_texts = [vc.text for vc in verb_chains]
        assert verb_chain_texts == test_text['vc_texts']
        verb_chain_patterns = [vc.pattern for vc in verb_chains]
        assert verb_chain_patterns == test_text['patterns']
        verb_chain_roots = [vc.roots for vc in verb_chains]
        assert verb_chain_roots == test_text['roots']
        verb_chain_polarities = [vc.polarity for vc in verb_chains]
        assert verb_chain_polarities == test_text['polarities']



def test_verb_chain_detection_3():
    # Tests that grammatical features of main verbs are correctly detected
    vc_detector = VerbChainDetector()
    test_data = [
       { 'text': 'Kass, suur ja must, ei jooksnud üle tee.',
         'vc_texts'  : [['ei', 'jooksnud']],
         'polarities': ['NEG'],
         'moods':['indic'],
         'voices':['personal'],
         'tenses':['imperfect'],
         'remaining_verbs':[False],
       },
       { 'text': 'Lend oleks Tallinna pidanud juba öösel jõudma.',
         'vc_texts' : [['oleks', 'pidanud', 'jõudma']],
         'polarities': ['POS'],
         'moods':['condit'],
         'voices':['personal'],
         'tenses':['past'],
         'remaining_verbs':[False],
       },
       { 'text': 'Ära mine rikkaga riidlema ega vägevaga kohut käima .',
         'vc_texts' : [['Ära', 'mine', 'riidlema', 'ega', 'käima']],
         'polarities': ['NEG'],
         'moods':['imper'],
         'voices':['personal'],
         'tenses':['present'],
         'remaining_verbs':[False],
       },
       { 'text': 'Teadus oli juba aastakümneid ülekaalukaid fakte tõestuseks esitanud. Aga ei midagi.',
         'vc_texts' : [['oli', 'esitanud']],
         'polarities': ['POS'],
         'moods':['indic'],
         'voices':['personal'],
         'tenses':['pluperfect'],
         'remaining_verbs': [False],
       },
    ]
    for test_text in test_data:
        # Prepare text. Add required layers
        text = Text(test_text['text'])
        text.tag_layer(['words', 'sentences', 'morph_analysis', 'clauses'])
        # Tag chains
        vc_detector.tag( text )
        # Check results
        verb_chains = text['verb_chains']
        verb_chain_texts = [vc.text for vc in verb_chains]
        assert verb_chain_texts == test_text['vc_texts']
        verb_chain_polarities = [vc.polarity for vc in verb_chains]
        assert verb_chain_polarities == test_text['polarities']
        verb_chain_moods = [vc.mood for vc in verb_chains]
        assert verb_chain_moods == test_text['moods']
        verb_chain_voices = [vc.voice for vc in verb_chains]
        assert verb_chain_voices == test_text['voices']
        verb_chain_tenses = [vc.tense for vc in verb_chains]
        assert verb_chain_tenses == test_text['tenses']
        remaining_verbs = [vc.remaining_verbs for vc in verb_chains]
        assert remaining_verbs == test_text['remaining_verbs']



def test_verb_chain_detection_customize_detector():
    # Tests that VerbChainDetector's detector component can be customized:
    # Use a detector that breaks chains on intervening punctuation
    from estnltk.taggers.miscellaneous.verb_chains.verbchain_detector_tagger import VERB_CHAIN_RES_PATH
    from estnltk.taggers.miscellaneous.verb_chains.v1_4_1.verbchain_detector import VerbChainDetectorV1_4
    vc_detector_customized = VerbChainDetector( vc_detector=VerbChainDetectorV1_4(resourcesPath=VERB_CHAIN_RES_PATH),
                                                breakOnPunctuation=True )
    test_data = [
       { 'text': 'Londoni lend pidi täna hommikul kell 4:30 Tallinna saabuma.',
         'vc_texts' : [['pidi']],
         'patterns' : [['verb']],
         'roots'    : [['pida']],
         'polarities': ['POS'],
       },
    ]
    for test_text in test_data:
        # Prepare text. Add required layers
        text = Text(test_text['text'])
        text.tag_layer(['words', 'sentences', 'morph_analysis', 'clauses'])
        # Tag chains
        vc_detector_customized.tag( text )
        # Check results
        verb_chains = text['verb_chains']
        verb_chain_texts = [vc.text for vc in verb_chains]
        assert verb_chain_texts == test_text['vc_texts']
        verb_chain_patterns = [vc.pattern for vc in verb_chains]
        assert verb_chain_patterns == test_text['patterns']
        verb_chain_roots = [vc.roots for vc in verb_chains]
        assert verb_chain_roots == test_text['roots']
        verb_chain_polarities = [vc.polarity for vc in verb_chains]
        assert verb_chain_polarities == test_text['polarities']

