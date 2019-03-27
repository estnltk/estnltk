from collections import defaultdict

from estnltk import Text

from estnltk.taggers.morph_analysis.morf import VabamorfAnalyzer
from estnltk.taggers.morph_analysis.cb_disambiguator import CorpusBasedMorphDisambiguator
from estnltk.taggers.morph_analysis.cb_disambiguator import RemoveDuplicateAndProblematicAnalysesRetagger

from estnltk.taggers.morph_analysis.morf_common import _is_empty_annotation

# ----------------------------------
#   Helper functions
# ----------------------------------

def collect_ambiguities( docs ):
    # Collect and index all morphological ambiguities from 
    # the given document collection
    ambiguities = dict()
    for doc_id, doc in enumerate(docs):
        for wid, word in enumerate(doc['words']):
            analyses = [(a.root, a.partofspeech, a.form) for a in word.morph_analysis]
            ambiguities[(doc_id,wid)] = analyses
    return ambiguities

def find_ambiguities_diff( ambiguities_a, ambiguities_b ):
    # Finds a difference between ambiguities_a and ambiguities_b
    removed_ambiguities = defaultdict(list)
    added_ambiguities   = defaultdict(list)
    for key_a in ambiguities_a.keys():
        if key_a in ambiguities_b:
            # Check if any ambiguities were removed
            for analysis_a in ambiguities_a[key_a]:
                if analysis_a not in ambiguities_b[key_a]:
                    removed_ambiguities[key_a].append( analysis_a )
            # Check if any ambiguities were introduced
            for analysis_b in ambiguities_b[key_a]:
                if analysis_b not in ambiguities_a[key_a]:
                    added_ambiguities[key_a].append( analysis_b )
        else:
            # All analyses from a have been removed
            removed_ambiguities[key_a] = ambiguities_a[key_a]
    for key_b in ambiguities_b.keys():
        if key_b not in ambiguities_a:
            # All analyses from a have been newly added 
            added_ambiguities[key_b] = ambiguities_b[key_b]
    return removed_ambiguities, added_ambiguities

def count_analyses( docs ):
    # Finds count of all analyses, and how the counts distribute
    # between proper name analyses, and other analyses
    analyseCountTotal = 0
    analyseCountH     = 0
    analyseCountNotH  = 0
    for doc_id, doc in enumerate(docs):
        for wid, word in enumerate(doc['words']):
            for analysis in word.morph_analysis:
                if _is_empty_annotation(analysis):
                    raise Exception( '(!) Error: unexpectedly found an empty span: '+str(analysis) )
                analyseCountTotal += 1
                if analysis.partofspeech == 'H':
                    analyseCountH += 1
                else:
                    analyseCountNotH += 1
    return [analyseCountTotal, analyseCountH, analyseCountNotH]

morf_analyzer = VabamorfAnalyzer()

# ----------------------------------

def test_proper_names_disambiguation():
    # Case 1
    docs = [ Text('Perekonnanimi oli Nõmm.'), \
             Text('Kuidas seda hääldada: Nõmmil või Nõmmel?') ]
    for doc in docs:
        doc.tag_layer(['compound_tokens', 'words', 'sentences'])
        morf_analyzer.tag(doc)
    ambiguities_a = collect_ambiguities( docs )
    # Use corpus-based disambiguation:
    cb_disambiguator = CorpusBasedMorphDisambiguator()
    cb_disambiguator._test_predisambiguation(docs)
    # Find difference in ambiguities
    ambiguities_b = collect_ambiguities( docs )
    removed, added = find_ambiguities_diff( ambiguities_a, ambiguities_b )
    assert sorted(list(removed.items())) == [ ( (0, 0),[('Perekonna_nimi', 'H', 'sg n'),
                                                        ('Perekonnanim', 'H', 'adt'),
                                                        ('Perekonnanim', 'H', 'sg g'),
                                                        ('Perekonnanim', 'H', 'sg p'),
                                                        ('Perekonnanimi', 'H', 'sg g'),
                                                        ('Perekonnanimi', 'H', 'sg n')]),
                                              ( (0, 2), [('nõmm', 'S', 'sg n')]),
                                              ( (1, 4), [('Nõmmil', 'H', 'sg n'), ('Nõmmi', 'H', 'sg ad')]),
                                              ( (1, 6), [('nõmm', 'S', 'sg ad')]),
                                            ]
    assert list(added.items()) == []
    
    # Case 2
    docs = [ Text('Ott tahab võita ka Kuldgloobust.'), \
             Text('Kuidas see Otil õnnestub, ei tea. Aga Ott lubas pingutada.'), \
             Text('Võib-olla tuleks siiski teha Kuldgloobuse eesti variant.') ]
    for doc in docs:
        doc.tag_layer(['compound_tokens', 'words', 'sentences'])
        morf_analyzer.tag(doc)
    ambiguities_a = collect_ambiguities( docs )
    # Use corpus-based disambiguation:
    cb_disambiguator = CorpusBasedMorphDisambiguator()
    cb_disambiguator._test_predisambiguation(docs)
    # Find difference in ambiguities
    ambiguities_b = collect_ambiguities( docs )
    removed, added = find_ambiguities_diff( ambiguities_a, ambiguities_b )
    assert sorted(list(removed.items())) == [ ((0, 0), [('ott', 'S', 'sg n')]), \
                                              ((0, 4), [('kuld_gloobus', 'S', 'sg p')]),\
                                              ((1, 2), [('ott', 'S', 'sg ad')]), \
                                              ((1, 9), [('ott', 'S', 'sg n')]), \
                                              ((2, 4), [('kuld_gloobus', 'S', 'sg g')]), \
                                            ]
    assert list(added.items()) == []


def test_pre_disambiguation_ver_1_4():
    # Pre-disambiguation test from estnltk v1.4
    docs = [Text('Jänes oli parajasti põllu peal. Hunti nähes ta ehmus ja pani jooksu.'),\
            Text('Talupidaja Jänes kommenteeris, et hunte on viimasel ajal liiga palju siginenud. Tema naaber, talunik Lammas, nõustus sellega.'), \
            Text('Jänesele ja Lambale oli selge, et midagi tuleb ette võtta. Eile algatasid nad huntidevastase kampaania.')]
    for doc in docs:
        doc.tag_layer(['compound_tokens', 'words', 'sentences'])
        morf_analyzer.tag(doc)
    [countTotal, countH, countNonH] = count_analyses( docs )
    assert [countTotal, countH, countNonH] == [104, 19, 85]
    # Use corpus-based disambiguation:
    cb_disambiguator = CorpusBasedMorphDisambiguator()
    cb_disambiguator._test_predisambiguation(docs)
    [countTotal, countH, countNonH] = count_analyses( docs )
    assert [countTotal, countH, countNonH] == [85, 5, 80]



def test_remove_duplicate_and_problematic_analyses():
    # 
    #  Case 1: removing duplicate analyses (if any exists)
    #  
    duplicate_removal_tagger = RemoveDuplicateAndProblematicAnalysesRetagger()
    doc = Text('Konkreetne palk vs ümar palk')
    doc.tag_layer(['compound_tokens', 'words', 'sentences'])
    morf_analyzer.tag(doc)
    # TODO: could not find an example of 'palk/palgi/palga' ambiguity:
    #       it seems that the word 'palk' always has only a single 
    #       analysis
    [countTotal, countH, countNonH] = count_analyses( [doc] )
    assert [countTotal, countH, countNonH] == [7, 2, 5]
    duplicate_removal_tagger.retag( doc )
    [countTotal, countH, countNonH] = count_analyses( [doc] )
    assert [countTotal, countH, countNonH] == [7, 2, 5]
    for word in doc['words']:
        if word.text == 'palk':
            records = word.morph_analysis.to_records()
            for rec in records:
                del rec['start']
                del rec['end']
            assert records == [{'root': 'palk', 'partofspeech': 'S', 'ending': '0', 'form': 'sg n', 'lemma': 'palk', 'clitic': '', 'root_tokens': ('palk',)}]
    # 
    #  Case 2: removing 'tama' if verb contains both 'tama' and 'ma'
    #  
    doc = Text('Peaks kuulutama, kuulatama ja kajastama.')
    doc.tag_layer(['compound_tokens', 'words', 'sentences'])
    morf_analyzer.tag(doc)
    duplicate_removal_tagger.retag( doc )
    for word in doc['words']:
        if word.text.endswith('tama'):
            records = word.morph_analysis.to_records()
            for rec in records:
                del rec['start']
                del rec['end']
            if word.text == 'kuulutama':
                assert records == [{'root': 'kuuluta', 'lemma': 'kuulutama', 'ending': 'ma', 'partofspeech': 'V', 'root_tokens': ('kuuluta',), 'clitic': '', 'form': 'ma'}]
            if word.text == 'kuulatama':
                assert records == [{'root': 'kuulata', 'lemma': 'kuulatama', 'ending': 'ma', 'partofspeech': 'V', 'root_tokens': ('kuulata',), 'clitic': '', 'form': 'ma'}]
            if word.text == 'kajastama':
                assert records == [{'root': 'kajasta', 'lemma': 'kajastama', 'ending': 'ma', 'partofspeech': 'V', 'root_tokens': ('kajasta',), 'clitic': '', 'form': 'ma'}]

