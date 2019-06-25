# Test VerbChainDetector (which uses v1.4.1 source)
#
from estnltk import Text
from estnltk.taggers.verb_chains import VerbChainDetector


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
        assert 'verb_chains' in text.layers.keys()
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
       }
       
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
