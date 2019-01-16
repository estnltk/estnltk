from estnltk import Text

from estnltk.taggers.morph_analysis.morf import VabamorfAnalyzer
from estnltk.taggers.morph_analysis.record_based_retagger import MorphAnalysisRecordBasedRetagger

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

class PickFirstAnalysisDisambiguator(MorphAnalysisRecordBasedRetagger):
    """ A naive morphological disambiguator that always picks the 
        first morphological analysis for each word.
    """
    def rewrite_words(self, words:list):
        new_word_records = []
        for word_morph in words:
            new_word_records.append([ word_morph[0] ])
        return new_word_records

morf_analyzer = VabamorfAnalyzer()

# ----------------------------------

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