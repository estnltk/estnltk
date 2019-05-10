from collections import defaultdict

from estnltk import Text

from estnltk.taggers.morph_analysis.morf import VabamorfAnalyzer, VabamorfDisambiguator
from estnltk.taggers.morph_analysis.cb_disambiguator import CorpusBasedMorphDisambiguator
from estnltk.taggers.morph_analysis.cb_disambiguator import RemoveDuplicateAndProblematicAnalysesRetagger
from estnltk.taggers.morph_analysis.cb_disambiguator import IgnoredByPostDisambiguationTagger

from estnltk.taggers.morph_analysis.morf_common import _is_empty_annotation

# ----------------------------------
#   Helper functions
# ----------------------------------

def collect_analyses( docs ):
    # Collect and index all morphological analyses from 
    # the given document collection
    all_analyses = dict()
    for doc_id, doc in enumerate(docs):
        for wid, word in enumerate(doc['words']):
            analyses = [(a.root, a.partofspeech, a.form) for a in word.morph_analysis]
            all_analyses[(doc_id,wid)] = analyses
    return all_analyses

def find_ambiguities_diff( analyses_a, analyses_b ):
    # Finds a difference between analyses_a and analyses_b:
    #  *) which ambiguities were removed;
    #  *) which ambiguities were added;
    removed_ambiguities = defaultdict(list)
    added_ambiguities   = defaultdict(list)
    for key_a in analyses_a.keys():
        if key_a in analyses_b:
            # Check if any ambiguities were removed
            for analysis_a in analyses_a[key_a]:
                if analysis_a not in analyses_b[key_a]:
                    removed_ambiguities[key_a].append( analysis_a )
            # Check if any ambiguities were introduced
            for analysis_b in analyses_b[key_a]:
                if analysis_b not in analyses_a[key_a]:
                    added_ambiguities[key_a].append( analysis_b )
        else:
            # All analyses from a have been removed
            removed_ambiguities[key_a] = analyses_a[key_a]
    for key_b in analyses_b.keys():
        if key_b not in analyses_a:
            # All analyses from a have been newly added 
            added_ambiguities[key_b] = analyses_b[key_b]
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


# -------------------------------------------------------
#     Corpus-based pre-disambiguation of proper names    
# -------------------------------------------------------

def test_proper_names_disambiguation():
    # Case 1
    docs = [ Text('Perekonnanimi oli Nõmm.'), \
             Text('Kuidas seda hääldada: Nõmmil või Nõmmel?') ]
    for doc in docs:
        doc.tag_layer(['compound_tokens', 'words', 'sentences'])
        morf_analyzer.tag(doc)
    analyses_a = collect_analyses( docs )
    # Use corpus-based disambiguation:
    cb_disambiguator = CorpusBasedMorphDisambiguator()
    cb_disambiguator._test_predisambiguation(docs)
    # Find difference in ambiguities
    analyses_b = collect_analyses( docs )
    removed, added = find_ambiguities_diff( analyses_a, analyses_b )
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
    analyses_a = collect_analyses( docs )
    # Use corpus-based disambiguation:
    cb_disambiguator = CorpusBasedMorphDisambiguator()
    cb_disambiguator._test_predisambiguation(docs)
    # Find difference in ambiguities
    analyses_b = collect_analyses( docs )
    removed, added = find_ambiguities_diff( analyses_a, analyses_b )
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


# -------------------------------------------------------
#     Corpus-based post-disambiguation
# -------------------------------------------------------

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



def test_mark_ambiguities_to_be_ignored():
    #  Tests that IgnoredByPostDisambiguationTagger can be used to mark 
    #  ambiguities that should be ignored by the post disambiguation
    #
    # 1) Create text and add pre-requisite layers
    #
    doc = Text('Kõigepealt kõlanud nagu kong. Mis on, aga pole üks ega teine.')
    doc.tag_layer(['compound_tokens', 'words', 'sentences'])
    morf_analyzer.tag( doc )
    disamb_ignore_tagger = IgnoredByPostDisambiguationTagger()
    disamb_ignore_tagger.tag( doc )
    assert disamb_ignore_tagger.output_layer in doc.layers.keys()
    #
    # 2) Collect results and make assertions
    #
    hidden_words_records = []
    hidden_words = []
    for hidden_word in doc[ disamb_ignore_tagger.output_layer ]:
        records = hidden_word.morph_analysis.to_records()
        hidden_words_records.append( records[0] )
        hidden_words.append( hidden_word.text[0] )
    assert hidden_words == ['kõlanud', 'nagu', 'Mis', 'on', 'üks', 'ega', 'teine']
    expected_hidden_words_records = [
        [ {'lemma': 'kõlanud', 'form': '', 'partofspeech': 'A', 'root': 'kõla=nud', 'root_tokens': ('kõlanud',), 'end': 18, 'ending': '0', 'start': 11, 'clitic': ''}, 
          {'lemma': 'kõlanud', 'form': 'sg n', 'partofspeech': 'A', 'root': 'kõla=nud', 'root_tokens': ('kõlanud',), 'end': 18, 'ending': '0', 'start': 11, 'clitic': ''}, 
          {'lemma': 'kõlanu', 'form': 'pl n', 'partofspeech': 'S', 'root': 'kõla=nu', 'root_tokens': ('kõlanu',), 'end': 18, 'ending': 'd', 'start': 11, 'clitic': ''}, 
          {'lemma': 'kõlanud', 'form': 'pl n', 'partofspeech': 'A', 'root': 'kõla=nud', 'root_tokens': ('kõlanud',), 'end': 18, 'ending': 'd', 'start': 11, 'clitic': ''}, 
          {'lemma': 'kõlama', 'form': 'nud', 'partofspeech': 'V', 'root': 'kõla', 'root_tokens': ('kõla',), 'end': 18, 'ending': 'nud', 'start': 11, 'clitic': ''} ], \
        [ {'lemma': 'nagu', 'form': '', 'partofspeech': 'D', 'root': 'nagu', 'root_tokens': ('nagu',), 'end': 23, 'ending': '0', 'start': 19, 'clitic': ''}, 
          {'lemma': 'nagu', 'form': '', 'partofspeech': 'J', 'root': 'nagu', 'root_tokens': ('nagu',), 'end': 23, 'ending': '0', 'start': 19, 'clitic': ''} ], \
        [ {'lemma': 'mis', 'form': 'pl n', 'partofspeech': 'P', 'root': 'mis', 'root_tokens': ('mis',), 'end': 33, 'ending': '0', 'start': 30, 'clitic': ''}, 
          {'lemma': 'mis', 'form': 'sg n', 'partofspeech': 'P', 'root': 'mis', 'root_tokens': ('mis',), 'end': 33, 'ending': '0', 'start': 30, 'clitic': ''} ], \
        [ {'lemma': 'olema', 'form': 'b', 'partofspeech': 'V', 'root': 'ole', 'root_tokens': ('ole',), 'end': 36, 'ending': '0', 'start': 34, 'clitic': ''}, 
          {'lemma': 'olema', 'form': 'vad', 'partofspeech': 'V', 'root': 'ole', 'root_tokens': ('ole',), 'end': 36, 'ending': '0', 'start': 34, 'clitic': ''} ],
        [ {'lemma': 'üks', 'form': 'sg n', 'partofspeech': 'N', 'root': 'üks', 'root_tokens': ('üks',), 'end': 50, 'ending': '0', 'start': 47, 'clitic': ''}, 
          {'lemma': 'üks', 'form': 'sg n', 'partofspeech': 'P', 'root': 'üks', 'root_tokens': ('üks',), 'end': 50, 'ending': '0', 'start': 47, 'clitic': ''} ],
        [{'lemma': 'ega', 'form': '', 'partofspeech': 'D', 'root': 'ega', 'root_tokens': ('ega',), 'end': 54, 'ending': '0', 'start': 51, 'clitic': ''}, {'lemma': 'ega', 'form': '', 'partofspeech': 'J', 'root': 'ega', 'root_tokens': ('ega',), 'end': 54, 'ending': '0', 'start': 51, 'clitic': ''}],
        [{'lemma': 'teine', 'form': 'sg n', 'partofspeech': 'O', 'root': 'teine', 'root_tokens': ('teine',), 'end': 60, 'ending': '0', 'start': 55, 'clitic': ''}, {'lemma': 'teine', 'form': 'sg n', 'partofspeech': 'P', 'root': 'teine', 'root_tokens': ('teine',), 'end': 60, 'ending': '0', 'start': 55, 'clitic': ''}] ]
    assert hidden_words_records == expected_hidden_words_records



def test_postdisambiguation_first_phase():
    #
    #  Tests the 1st phase of lemma-based post-disambiguation
    #
    docs = [Text('Esimesele kohale tuleb Jänes, kuigi tema punktide summa pole kõrgeim.'),\
            Text('Lõpparvestuses läks Konnale esimene koht. Teine koht seekord Jänesele. Uus võistlus toimub 2. mail.'), \
            Text('Konn paistis silma suurima punktide summaga. Uue võistluse toimumisajaks on 2. mai.'),
            Text('Kordame: summat, summat, summat.'),]
    for doc in docs:
        doc.tag_layer(['compound_tokens', 'words', 'sentences'])
        morf_analyzer.tag(doc, propername=False)  # Analyse without proper name guessing
    analyses_a = collect_analyses( docs )
    # Use corpus-based disambiguation:
    cb_disambiguator = CorpusBasedMorphDisambiguator()
    cb_disambiguator._test_postdisambiguation( [docs] )
    # Find difference in ambiguities
    analyses_b = collect_analyses( docs )
    removed, added = find_ambiguities_diff( analyses_a, analyses_b )
    #for a in sorted(list(removed.items())):
    #    print( a )
    #print()
    assert sorted(list(removed.items())) == [ ( (0, 1), [('kohale', 'D', ''), ('kohale', 'K', ''), ('koha', 'S', 'sg all')] ), \
                                              ( (0, 8), [('summ', 'S', 'adt'), ('summ', 'S', 'sg g'), ('summ', 'S', 'sg p')] ), \
                                              ( (1, 15), [('maa', 'S', 'pl ad'), ('mail', 'S', 'sg n')] ), \
                                              ( (2, 2), [('silma', 'V', 'o')] ), \
                                              ( (2, 5), [('summ', 'S', 'sg kom')] )
                                            ]
    assert list(added.items()) == []



def test_post_disambiguation_ver_1_4():
    # A post-disambiguation test from estnltk v1.4
    corpus = ['Esimesele kohale tuleb Jänes, kuigi tema punktide summa pole kõrgeim.',\
              'Lõpparvestuses läks Konnale esimene koht. Teise koha sai seekord Jänes. Uus võistlus toimub 2. mail.', \
              'Konn paistis silma suurima punktide summaga. Uue võistluse toimumisajaks on 2. mai.']
    vm_disamb = VabamorfDisambiguator()
    cb_disambiguator = CorpusBasedMorphDisambiguator()
    # 1) Nr of analyses without disamb
    docs = [ Text(text) for text in corpus ]
    for doc in docs:
        doc.tag_layer(['compound_tokens', 'words', 'sentences'])
        morf_analyzer.tag(doc)
    [countTotal, countH, countNonH] = count_analyses( docs )
    assert [countTotal, countH, countNonH] == [88, 17, 71]
    # 2) Nr of analyses after vm disambiguation
    docs = [ Text(text) for text in corpus ]
    for doc in docs:
        doc.tag_layer(['compound_tokens', 'words', 'sentences'])
        morf_analyzer.tag(doc)
        vm_disamb.retag(doc)
    [countTotal, countH, countNonH] = count_analyses( docs )
    #print( [countTotal, countH, countNonH] )
    assert [countTotal, countH, countNonH] == [51, 0, 51]
    # 3) Nr of analyses after vm disambiguation and corpus-based post-disambiguation
    docs = [ Text(text) for text in corpus ]
    for doc in docs:
        doc.tag_layer(['compound_tokens', 'words', 'sentences'])
        morf_analyzer.tag(doc)
        vm_disamb.retag(doc)
    cb_disambiguator._test_postdisambiguation( [docs] )
    [countTotal, countH, countNonH] = count_analyses( docs )
    #print( [countTotal, countH, countNonH] )
    assert [countTotal, countH, countNonH] == [47, 0, 47]
    # 4) Nr of analyses after corpus-based pre-disambiguation, vm disambiguation and 
    #    post-disambiguation
    docs = [ Text(text) for text in corpus ]
    for doc in docs:
        doc.tag_layer(['compound_tokens', 'words', 'sentences'])
        morf_analyzer.tag(doc)
    cb_disambiguator._test_predisambiguation( docs )
    for doc in docs:
        vm_disamb.retag(doc)
    cb_disambiguator._test_postdisambiguation( [docs] )
    [countTotal, countH, countNonH] = count_analyses( docs )
    #print( [countTotal, countH, countNonH] )
    assert [countTotal, countH, countNonH] == [47, 4, 43]

