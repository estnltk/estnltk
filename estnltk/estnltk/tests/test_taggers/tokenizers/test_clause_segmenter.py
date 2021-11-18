import pytest

from estnltk import Text
from estnltk.taggers import WordTagger
from estnltk.taggers import SentenceTokenizer
from estnltk.taggers import ClauseSegmenter
from estnltk.taggers import VabamorfTagger


def test_clause_segmenter_1():
    # Initialize segmenter's context
    with ClauseSegmenter() as segmenter:
        test_texts = [ 
            { 'text': 'Igaüks, kes traktori eest miljon krooni lauale laob, on huvitatud sellest, '+\
                      'et traktor meenutaks lisavõimaluste poolest võimalikult palju kosmoselaeva.',
              'expected_clause_word_texts': [['Igaüks', 'on', 'huvitatud', 'sellest', ','],
                                             [',', 'kes', 'traktori', 'eest', 'miljon', 'krooni', 'lauale', 'laob', ','],
                                             ['et', 'traktor', 'meenutaks', 'lisavõimaluste', 'poolest', 'võimalikult', 'palju', 'kosmoselaeva', '.']] },
            { 'text': 'Kõrred, millel on toitunud viljasääse vastsed, jäävad õhukeseks.',
              'expected_clause_word_texts': [['Kõrred', 'jäävad', 'õhukeseks', '.'],
                                             [',', 'millel', 'on', 'toitunud', 'viljasääse', 'vastsed', ',']] },
            { 'text': 'Sest mis sa ikka ütled, kui seisad tükk aega kinniste tõkkepuude taga, ootad ja ootad, aga rongi ei tulegi.',
              'expected_clause_word_texts': [['Sest', 'mis', 'sa', 'ikka', 'ütled', ','],
                                             ['kui', 'seisad', 'tükk', 'aega', 'kinniste', 'tõkkepuude', 'taga', ','],
                                             ['ootad', 'ja'],
                                             ['ootad', ','],
                                             ['aga', 'rongi', 'ei', 'tulegi', '.']] },
            { 'text': 'Pankurid Arti (LHV) ja Juri (Citadele) tulevad ja räägivad sellest, mida pank mõtleb laenu andmise juures.',
              'expected_clause_word_texts': [['Pankurid', 'Arti', 'ja', 'Juri', 'tulevad', 'ja'],
                                             ['(', 'LHV', ')'],
                                             ['(', 'Citadele', ')'],
                                             ['räägivad', 'sellest', ','],
                                             ['mida', 'pank', 'mõtleb', 'laenu', 'andmise', 'juures', '.']] },
        ]
        for test_text in test_texts:
            text = Text( test_text['text'] )
            # Perform analysis
            text.tag_layer(['words', 'sentences', 'morph_analysis'])
            segmenter.tag(text)
            # Collect results 
            clause_word_texts = \
                [[word.text for word in clause.words] for clause in text['clauses']]
            #print( clause_word_texts )
            # Check results
            assert clause_word_texts == test_text['expected_clause_word_texts']


def test_clause_segmenter_2_missing_commas():
    # Initialize segmenter that is insensitive to missing commas
    with ClauseSegmenter(ignore_missing_commas=True) as segmenter:
        test_texts = [ 
            { 'text': 'Keegi teine ka siin ju kirjutas et ütles et saab ise asjadele järgi minna aga '+
                      'vastust seepeale ei tulnudki.', \
              'expected_clause_word_texts': [['Keegi', 'teine', 'ka', 'siin', 'ju', 'kirjutas'],\
                                             ['et', 'ütles'], \
                                             ['et', 'saab', 'ise', 'asjadele', 'järgi', 'minna'], \
                                             ['aga', 'vastust', 'seepeale', 'ei', 'tulnudki', '.']] }, \
            { 'text': 'Pritsimehed leidsid eest lõõmava kapotialusega auto mida läheduses parkinud masinate sohvrid eemale '+
                      'üritasid lükata kuid esialgu see ei õnnestunud sest autol oli käik sees.', \
              'expected_clause_word_texts': [['Pritsimehed', 'leidsid', 'eest', 'lõõmava', 'kapotialusega', 'auto'], \
                                             ['mida', 'läheduses', 'parkinud', 'masinate', 'sohvrid', 'eemale', 'üritasid', 'lükata'], \
                                             ['kuid', 'esialgu', 'see', 'ei', 'õnnestunud'], \
                                             ['sest', 'autol', 'oli', 'käik', 'sees', '.']] }, \
        ]
        for test_text in test_texts:
            text = Text( test_text['text'] )
            # Perform analysis
            text.tag_layer(['words', 'sentences', 'morph_analysis'])
            segmenter.tag(text)
            # Collect results 
            clause_word_texts = \
                [[word.text for word in clause.words] for clause in text['clauses']]
            #print( clause_word_texts )
            # Check results
            assert clause_word_texts == test_text['expected_clause_word_texts']


def test_apply_clause_segmenter_on_empty_text():
    # Applying clause segmenter on empty text should not produce any errors
    text = Text( '' )
    text.tag_layer(['words', 'sentences', 'morph_analysis'])
    
    with ClauseSegmenter() as segmenter:
        segmenter.tag(text)
    
    assert len(text.words) == 0
    assert len(text.sentences) == 0
    assert len(text.clauses) == 0


def test_change_input_output_layer_names_of_clause_segmenter():
    # Tests that names of input / output layers of ClauseSegmenter can be changed
    word_tagger        = WordTagger(output_layer='my_words')
    sentence_tokenizer = SentenceTokenizer(input_words_layer='my_words', 
                                           output_layer='my_sentences')
    morftagger = VabamorfTagger(input_words_layer     ='my_words',
                                input_sentences_layer ='my_sentences',
                                output_layer          ='my_morf')
    with ClauseSegmenter(input_words_layer          ='my_words',
                         input_sentences_layer      ='my_sentences',
                         input_morph_analysis_layer ='my_morf',
                         output_layer          ='my_clauses') as segmenter:
        test_texts = [ 
            { 'text': 'Igaüks, kes traktori eest miljon krooni lauale laob, on huvitatud sellest, '+\
                      'et traktor meenutaks lisavõimaluste poolest võimalikult palju kosmoselaeva.',\
              'expected_clause_word_texts': [['Igaüks', 'on', 'huvitatud', 'sellest', ','], \
                                             [',', 'kes', 'traktori', 'eest', 'miljon', 'krooni', 'lauale', 'laob', ','], \
                                             ['et', 'traktor', 'meenutaks', 'lisavõimaluste', 'poolest', 'võimalikult', 'palju', 'kosmoselaeva', '.']] }, \
        ]
        for test_text in test_texts:
            text = Text( test_text['text'] )
            # Perform analysis
            text.tag_layer(['tokens', 'compound_tokens'])
            word_tagger.tag( text )
            sentence_tokenizer.tag( text )
            morftagger.tag( text )
            segmenter.tag( text )
            # Initial assertions
            assert 'my_clauses' in text.layers
            assert 'clauses' not in text.layers
            # Collect results 
            clause_word_texts = \
                [[word.text for word in clause.spans] for clause in text['my_clauses']]
            #print( clause_word_texts )
            # Check results
            assert clause_word_texts == test_text['expected_clause_word_texts']


def test_clause_segmenter_context_set_up_and_tear_down():
    # Tests ClauseSegmenter's java process will be initialized in correct context;
    # Tests after exiting ClauseSegmenter's context manager, the process has been 
    # torn down and no longer available
    text = Text( 'Testimise tekst.' )
    text.tag_layer(['words', 'sentences', 'morph_analysis'])
    # 1) Apply segmenter as a context manager
    with ClauseSegmenter() as segmenter:
        # Check: Inside the with context, the java process 
        # should already be initialized
        assert segmenter._java_process._process is not None
        # Check: the process should be up and running
        assert segmenter._java_process._process.poll() is None
        # Apply segmenter
        segmenter.tag(text)
    # Check: polling the process should not return None
    assert segmenter._java_process._process.poll() is not None
    # Check: After context has been torn down, we should get an assertion error
    with pytest.raises(AssertionError) as e1:
        segmenter.tag(text)
    
    # Test different ways how ClauseSegmenter can be ended manually:
    
    # 2) Create segmenter outside with, and use the __exit__() method
    segmenter2 = ClauseSegmenter()
    # Check that there is no process at first (lazy initialization)
    # [if ClauseSegmenter() is created outside the with context, java 
    #     should not be initiated before calling the tag() method]
    assert segmenter2._java_process._process is None
    text = Text( 'Testimise tekst.' )
    text.tag_layer(['words', 'sentences', 'morph_analysis'])
    segmenter2.tag(text)
    # Check that the process is up and running after calling tag()
    assert segmenter2._java_process._process.poll() is None
    # Terminate the process "manually"
    segmenter2.__exit__()
    # Check that the process is terminated
    assert segmenter2._java_process._process.poll() is not None
    
    # 3) Create segmenter outside with, and use the close() method
    segmenter3 = ClauseSegmenter()
    # Check that there is no process at first (lazy initialization)
    assert segmenter3._java_process._process is None
    text = Text( 'Testimise tekst.' )
    text.tag_layer(['words', 'sentences', 'morph_analysis'])
    segmenter3.tag(text)
    # Check that the process is running
    assert segmenter3._java_process._process.poll() is None
    # Terminate the process "manually"
    segmenter3.close()
    # Check that the process is terminated
    assert segmenter3._java_process._process.poll() is not None

    # 4) Create segmenter outside with, and simply delete it
    #segmenter4 = ClauseSegmenter()
    # Check that the process is running
    #assert segmenter4._java_process._process.poll() is None
    #java_process = segmenter4._java_process
    # Terminate the process "manually"
    #del segmenter4
    # Check that the process is terminated
    #assert java_process._process.poll() is not None
    #
    # TODO: this option is currently not available, because__del__ 
    #       method causes some irregular and wierd subprocess errors 
    #       during pytest; needs further investigation;


def test_clause_segmenter_no_java_initialization_in_make_resolver():
    # Test that the ClauseSegmenter's java process will not be 
    # initialized during the creation of the default resolver 
    # (the initialization should occur later, only after the tag() 
    #  method is called )
    from estnltk.default_resolver import make_resolver
    new_default_resolver = make_resolver()
    segmenter = new_default_resolver.get_tagger('clauses')
    assert isinstance(segmenter, ClauseSegmenter)
    # Check that there is no process at first (lazy initialization)
    assert segmenter._java_process._process is None

