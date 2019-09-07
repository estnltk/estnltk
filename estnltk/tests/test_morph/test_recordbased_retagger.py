from estnltk import Text

from estnltk.taggers.morph_analysis.morf import VabamorfAnalyzer
from estnltk.taggers.morph_analysis.recordbased_retagger import MorphAnalysisRecordBasedRetagger

# ----------------------------------
#   Helper functions
# ----------------------------------

def _sort_morph_analysis_records( morph_analysis_records:list ):
    '''Sorts sublists (lists of analyses of a single word) of 
       morph_analysis_records. Sorting is required for comparing
       morph analyses of a word without setting any constraints 
       on their specific order. '''
    for wrid, word_records_list in enumerate( morph_analysis_records ):
        sorted_records = sorted( word_records_list, key = lambda x : \
            str(x['root'])+str(x['ending'])+str(x['clitic'])+\
            str(x['partofspeech'])+str(x['form']) )
        morph_analysis_records[wrid] = sorted_records

morf_analyzer = VabamorfAnalyzer()

# ----------------------------------

class PickFirstAnalysisDisambiguator(MorphAnalysisRecordBasedRetagger):
    """ A naive morphological disambiguator that always picks the 
        first morphological analysis for each word.
    """
    def rewrite_words(self, words:list):
        new_word_records = []
        for word_morph in words:
            new_word_records.append([ word_morph[0] ])
        return new_word_records


def test_pick_first_analysis_with_record_retagger():
    # Tests that MorphAnalysisRecordBasedRetagger can be used to create a simple disambiguator:
    # for each word, pick the first analysis (and remove others)
    
    # Initialize tagger
    simple_disambiguator = PickFirstAnalysisDisambiguator()
    text=Text('Ma ei olnud sellisest masinavärgist veel kuulnudki.')
    text.tag_layer(['words','sentences'])
    morf_analyzer.tag(text)
    simple_disambiguator.retag(text)
    #print(text['morph_analysis'].to_records())
    expected_records = [
       [{'root': 'mina', 'ending': '0', 'form': 'sg n', 'lemma': 'mina', 'clitic': '', 'end': 2, 'start': 0, 'partofspeech': 'P', 'root_tokens': ('mina',)}],
       [{'root': 'ei', 'ending': '0', 'form': '', 'lemma': 'ei', 'clitic': '', 'end': 5, 'start': 3, 'partofspeech': 'D', 'root_tokens': ('ei',)}], 
       [{'root': 'ol=nud', 'ending': '0', 'form': '', 'lemma': 'olnud', 'clitic': '', 'end': 11, 'start': 6, 'partofspeech': 'A', 'root_tokens': ('olnud',)}],
       [{'root': 'selline', 'ending': 'st', 'form': 'sg el', 'lemma': 'selline', 'clitic': '', 'end': 21, 'start': 12, 'partofspeech': 'P', 'root_tokens': ('selline',)}], 
       [{'root': 'masina_värk', 'ending': 'st', 'form': 'sg el', 'lemma': 'masinavärk', 'clitic': '', 'end': 35, 'start': 22, 'partofspeech': 'S', 'root_tokens': ('masina', 'värk')}], 
       [{'root': 'veel', 'ending': '0', 'form': '', 'lemma': 'veel', 'clitic': '', 'end': 40, 'start': 36, 'partofspeech': 'D', 'root_tokens': ('veel',)}], 
       [{'root': 'kuulnu', 'ending': 'd', 'form': 'pl n', 'lemma': 'kuulnu', 'clitic': 'ki', 'end': 50, 'start': 41, 'partofspeech': 'S', 'root_tokens': ('kuulnu',)}], 
       [{'root': '.', 'ending': '', 'form': '', 'lemma': '.', 'clitic': '', 'end': 51, 'start': 50, 'partofspeech': 'Z', 'root_tokens': ('.',)}]]
    # Sort analyses (so that the order within a word is always the same)
    results_dict = text['morph_analysis'].to_records()
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    assert expected_records == results_dict
    
# ----------------------------------

class PickVerbForNudDisambiguator(MorphAnalysisRecordBasedRetagger):
    """ A naive morphological disambiguator that always picks the 
        verb form for 'nud'-ending words, but does not change any-
        thing else.
    """
    def rewrite_words(self, words:list):
        new_word_records = []
        changed_words = set()
        for wid, word_morph in enumerate(words):
            nud_index = -1
            for aid, analysis in enumerate( word_morph ):
                if analysis['partofspeech'] == 'V' and \
                   analysis['ending'] == 'nud':
                   nud_index = aid
            if nud_index != -1:
                new_word_records.append([ word_morph[nud_index] ])
                changed_words.add(wid)
            else:
                # do not change anything
                new_word_records.append(word_morph)
        return new_word_records, changed_words


def test_pick_verb_for_nud_with_record_retagger():
    # Tests that MorphAnalysisRecordBasedRetagger can be used to create a simple disambiguator:
    # for each nud-word, pick the verb analysis (even if it may not be correct)
    
    # Initialize tagger
    simple_disambiguator = PickVerbForNudDisambiguator()
    
    text=Text('Nad ei olnud loonud arenenud erakonnademokraatiat.')
    text.tag_layer(['words','sentences'])
    morf_analyzer.tag(text)
    simple_disambiguator.retag(text)
    #print(text['morph_analysis'].to_records())
    expected_records = [
         [{'end': 3, 'ending': 'd', 'start': 0, 'root': 'tema', 'clitic': '', 'root_tokens': ['tema'], 'partofspeech': 'P', 'lemma': 'tema', 'form': 'pl n'}], \
         [{'end': 6, 'ending': '0', 'start': 4, 'root': 'ei', 'clitic': '', 'root_tokens': ['ei',], 'partofspeech': 'D', 'lemma': 'ei', 'form': ''}, \
          {'end': 6, 'ending': '0', 'start': 4, 'root': 'ei', 'clitic': '', 'root_tokens': ['ei',], 'partofspeech': 'V', 'lemma': 'ei', 'form': 'neg'}], \
         [{'end': 12, 'ending': 'nud', 'start': 7, 'root': 'ole', 'clitic': '', 'root_tokens': ('ole',), 'partofspeech': 'V', 'lemma': 'olema', 'form': 'nud'}], \
         [{'end': 19, 'ending': 'nud', 'start': 13, 'root': 'loo', 'clitic': '', 'root_tokens': ('loo',), 'partofspeech': 'V', 'lemma': 'looma', 'form': 'nud'}], \
         [{'end': 28, 'ending': 'nud', 'start': 20, 'root': 'arene', 'clitic': '', 'root_tokens': ('arene',), 'partofspeech': 'V', 'lemma': 'arenema', 'form': 'nud'}], \
         [{'end': 49, 'ending': 't', 'start': 29, 'root': 'erakonna_demo_kraatia', 'clitic': '', 'root_tokens': ['erakonna', 'demo', 'kraatia'], 'partofspeech': 'S', 'lemma': 'erakonnademokraatia', 'form': 'sg p'}], \
         [{'end': 50, 'ending': '', 'start': 49, 'root': '.', 'clitic': '', 'root_tokens': ['.',], 'partofspeech': 'Z', 'lemma': '.', 'form': ''}]
    ]
    # Sort analyses (so that the order within a word is always the same)
    results_dict = text['morph_analysis'].to_records()
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    assert expected_records == results_dict


# ----------------------------------

class GiveSpecialPosTagsToEmoticonsTagger(MorphAnalysisRecordBasedRetagger):
    """ A naive morphological tagger that changes partofspeech of 
        emoticons :) :-) and :D to 'Emo' and fixes root/root_tokens
        of corresponding emoticons.
        Note: this is only for testing purposes, 'Emo' is actually not
        a legal partofspeech tag.
    """
    def __init__(self):
        # Require normalized word forms
        super().__init__(add_normalized_word_form=True)
    
    def rewrite_words(self, words:list):
        new_word_records = []
        changed_words = set()
        for wid, word_morph in enumerate(words):
            isEmoticon = False
            for aid, analysis in enumerate( word_morph ):
                if analysis['word_normal'] in [':)', ':-)', ':D']:
                   isEmoticon = True
                if isEmoticon:
                    analysis['partofspeech'] = 'Emo'
                    # Fix root/root_tokens
                    analysis['root'] = analysis['word_normal']
                    analysis['root_tokens'] = (analysis['word_normal'],)
            if isEmoticon:
                changed_words.add(wid)
            new_word_records.append(word_morph)
        return new_word_records, changed_words


def test_record_retagger_that_requires_normalized_word_forms():
    # Tests that MorphAnalysisRecordBasedRetagger can be used to create a tagger
    # that changes partofspeech of emoticons, and takes account of the normalized
    # word forms
    
    # Initialize tagger
    simple_disambiguator = GiveSpecialPosTagsToEmoticonsTagger()
    
    text=Text('Kas :- ) või hoopis :) ? Pigem :D')
    text.tag_layer(['words','sentences'])
    morf_analyzer.tag(text)
    simple_disambiguator.retag(text)
    #print(text['morph_analysis'].to_records())
    expected_records = [
        [{'end': 3, 'start': 0, 'partofspeech': 'D', 'root': 'kas', 'clitic': '', 'root_tokens': ['kas',], 'ending': '0', 'form': '', 'lemma': 'kas'}], \
        [{'end': 8, 'start': 4, 'partofspeech': 'Emo', 'root': ':-)', 'clitic': '', 'root_tokens': (':-)',), 'ending': '', 'form': '', 'lemma': ':-)'}], \
        [{'end': 12, 'start': 9, 'partofspeech': 'D', 'root': 'või', 'clitic': '', 'root_tokens': ['või',], 'ending': '0', 'form': '', 'lemma': 'või'}, \
         {'end': 12, 'start': 9, 'partofspeech': 'J', 'root': 'või', 'clitic': '', 'root_tokens': ['või',], 'ending': '0', 'form': '', 'lemma': 'või'}, \
         {'end': 12, 'start': 9, 'partofspeech': 'S', 'root': 'või', 'clitic': '', 'root_tokens': ['või',], 'ending': '0', 'form': 'sg g', 'lemma': 'või'}, \
         {'end': 12, 'start': 9, 'partofspeech': 'S', 'root': 'või', 'clitic': '', 'root_tokens': ['või',], 'ending': '0', 'form': 'sg n', 'lemma': 'või'}, \
         {'end': 12, 'start': 9, 'partofspeech': 'V', 'root': 'või', 'clitic': '', 'root_tokens': ['või',], 'ending': '0', 'form': 'o', 'lemma': 'võima'}], \
        [{'end': 19, 'start': 13, 'partofspeech': 'D', 'root': 'hoopis', 'clitic': '', 'root_tokens': ['hoopis',], 'ending': '0', 'form': '', 'lemma': 'hoopis'}], \
        [{'end': 22, 'start': 20, 'partofspeech': 'Emo', 'root': ':)', 'clitic': '', 'root_tokens': (':)',), 'ending': '', 'form': '', 'lemma': ':)'}], \
        [{'end': 24, 'start': 23, 'partofspeech': 'Z', 'root': '?', 'clitic': '', 'root_tokens': ['?',], 'ending': '', 'form': '', 'lemma': '?'}], \
        [{'end': 30, 'start': 25, 'partofspeech': 'D', 'root': 'pigem', 'clitic': '', 'root_tokens': ['pigem',], 'ending': '0', 'form': '', 'lemma': 'pigem'}], \
        [{'end': 33, 'start': 31, 'partofspeech': 'Emo', 'root': ':D', 'clitic': '', 'root_tokens': (':D',), 'ending': '0', 'form': '?', 'lemma': 'D'}]
    ]
    # Sort analyses (so that the order within a word is always the same)
    results_dict = text['morph_analysis'].to_records()
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    assert expected_records == results_dict

# ----------------------------------

class DeleteSentenceInitialProperNamesDisambiguator(MorphAnalysisRecordBasedRetagger):
    """ A naive morphological disambiguator that removes all proper 
        name analyses that appear in the beginning of a sentence.
    """
    def __init__(self):
        # Require sentence_id-s
        super().__init__(add_sentence_ids=True)
    
    def rewrite_words(self, words:list):
        new_word_records = []
        changed_words = set()
        last_sent_id = -1
        for wid, word_morph in enumerate(words):
            toDelete = []
            for aid, analysis in enumerate( word_morph ):
                cur_sent_id = analysis['sentence_id']
                if cur_sent_id != last_sent_id:
                    # We are in the beginning of a sentence
                    if analysis['partofspeech'] == 'H':
                        toDelete.append( analysis )
            if toDelete:
                for analysis in toDelete:
                    word_morph.remove(analysis)
                changed_words.add(wid)
            new_word_records.append(word_morph)
            last_sent_id = cur_sent_id
        return new_word_records, changed_words


def test_record_retagger_that_requires_sentence_ids():
    # Tests that MorphAnalysisRecordBasedRetagger can be used to create a tagger
    # that naively deletes all sentence-initial proper names
    
    # Initialize tagger
    simple_disambiguator = DeleteSentenceInitialProperNamesDisambiguator()
    
    text=Text('Jänese Haak? Kapsa Mari!')
    text.tag_layer(['words','sentences'])
    morf_analyzer.tag(text)
    simple_disambiguator.retag(text)
    #print(text['morph_analysis'].to_records())
    expected_records = [
        [{'clitic': '', 'lemma': 'jänes', 'root_tokens': ('jänes',), 'partofspeech': 'S', 'root': 'jänes', 'form': 'sg g', 'start': 0, 'ending': '0', 'end': 6}], \
        [{'clitic': '', 'lemma': 'Haak', 'root_tokens': ['Haak',], 'partofspeech': 'H', 'root': 'Haak', 'form': 'sg n', 'start': 7, 'ending': '0', 'end': 11}, \
         {'clitic': '', 'lemma': 'haak', 'root_tokens': ['haak',], 'partofspeech': 'S', 'root': 'haak', 'form': 'sg n', 'start': 7, 'ending': '0', 'end': 11}], \
        [{'clitic': '', 'lemma': '?', 'root_tokens': ['?',], 'partofspeech': 'Z', 'root': '?', 'form': '', 'start': 11, 'ending': '', 'end': 12}], \
        [{'clitic': '', 'lemma': 'kapsama', 'root_tokens': ('kapsa',), 'partofspeech': 'V', 'root': 'kapsa', 'form': 'o', 'start': 13, 'ending': '0', 'end': 18}, \
         {'clitic': '', 'lemma': 'kapsas', 'root_tokens': ('kapsas',), 'partofspeech': 'S', 'root': 'kapsas', 'form': 'sg g', 'start': 13, 'ending': '0', 'end': 18}], \
        [{'clitic': '', 'lemma': 'Mari', 'root_tokens': ['Mari',], 'partofspeech': 'H', 'root': 'Mari', 'form': 'sg g', 'start': 19, 'ending': '0', 'end': 23}, \
         {'clitic': '', 'lemma': 'Mari', 'root_tokens': ['Mari',], 'partofspeech': 'H', 'root': 'Mari', 'form': 'sg n', 'start': 19, 'ending': '0', 'end': 23}, \
         {'clitic': '', 'lemma': 'mari', 'root_tokens': ['mari',], 'partofspeech': 'S', 'root': 'mari', 'form': 'sg g', 'start': 19, 'ending': '0', 'end': 23}, \
         {'clitic': '', 'lemma': 'mari', 'root_tokens': ['mari',], 'partofspeech': 'S', 'root': 'mari', 'form': 'sg n', 'start': 19, 'ending': '0', 'end': 23}, \
         {'clitic': '', 'lemma': 'mari', 'root_tokens': ['mari',], 'partofspeech': 'S', 'root': 'mari', 'form': 'sg p', 'start': 19, 'ending': '0', 'end': 23}], \
        [{'clitic': '', 'lemma': '!', 'root_tokens': ['!',], 'partofspeech': 'Z', 'root': '!', 'form': '', 'start': 23, 'ending': '', 'end': 24}]
    ]
    # Sort analyses (so that the order within a word is always the same)
    results_dict = text['morph_analysis'].to_records()
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    assert expected_records == results_dict
