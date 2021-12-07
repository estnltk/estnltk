from collections import defaultdict
import pytest

from estnltk_core.converters import span_to_records
from estnltk_core.converters import layer_to_records

from estnltk import Text

from estnltk.taggers.standard.morph_analysis.morf import VabamorfAnalyzer, VabamorfDisambiguator
from estnltk.taggers.standard.morph_analysis.cb_disambiguator import CorpusBasedMorphDisambiguator
from estnltk.taggers.standard.morph_analysis.cb_disambiguator import RemoveDuplicateAndProblematicAnalysesRetagger
from estnltk.taggers.standard.morph_analysis.cb_disambiguator import IgnoredByPostDisambiguationTagger

from estnltk.taggers.standard.morph_analysis.morf_common import _is_empty_annotation

# ----------------------------------
#   Helper functions
# ----------------------------------

def _sort_morph_annotations( morph_annotations:list ):
    """Sorts morph_annotations. Sorting is required for comparing
       morph analyses of a word without setting any constraints 
       on their specific order."""
    sorted_records = sorted( morph_annotations, key = lambda x : \
        str(x['root'])+str(x['ending'])+str(x['clitic'])+\
        str(x['partofspeech'])+str(x['form']) )
    return sorted_records


def collect_analyses( docs, sort_analyses=True ):
    # Collect and index all morphological analyses from 
    # the given document collection
    all_analyses = dict()
    for doc_id, doc in enumerate(docs):
        for wid, word in enumerate(doc['words']):
            morph_annotations = word.morph_analysis.annotations
            if sort_analyses:
                # Sort analyses
                # ( so the order will be independent of the ordering used by 
                #   VabamorfAnalyzer & VabamorfDisambiguator )
                morph_annotations = _sort_morph_annotations( morph_annotations )
            analyses = [(a.root, a.partofspeech, a.form) for a in morph_annotations]
            all_analyses[(doc_id,wid)] = analyses
    return all_analyses


def collect_2nd_level_analyses( corpus, sort_analyses=True ):
    # Collect 2nd level analyses
    all_analyses = dict()
    for corp_id, docs in enumerate( corpus ):
        collected = collect_analyses( docs, sort_analyses=sort_analyses )
        for (k, v) in collected.items():
            k = (corp_id,) + k
            assert k not in all_analyses
            all_analyses[k] = v
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

def count_analyses( collection, skipEmptyAnalyses=True ):
    # Finds count of all analyses, and how the counts distribute
    # between proper name analyses, and other analyses
    analyseCountTotal = 0
    analyseCountH     = 0
    analyseCountNotH  = 0
    for item_id, item in enumerate(collection):
        sub_collection = None
        if isinstance(item, Text):
            sub_collection = [ item ]
        elif isinstance(item, list):
            sub_collection = item
        for doc_id, doc in enumerate(sub_collection):
            for wid, word in enumerate(doc['words']):
                for analysis in word.morph_analysis.annotations:
                    if _is_empty_annotation(analysis):
                        if skipEmptyAnalyses:
                            continue
                        else:
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
    cb_disambiguator.predisambiguate(docs)
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
    cb_disambiguator.predisambiguate(docs)
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
    cb_disambiguator.predisambiguate(docs)
    [countTotal, countH, countNonH] = count_analyses( docs )
    assert [countTotal, countH, countNonH] == [85, 5, 80]



def test_pre_disambiguation_quoted_and_enumrated_texts():
    # Pre-disambiguator should distinguish between sentence initial and sentence central proper names
    # even if the potential proper name is:
    #         1) after the sentence-initial quotation mark
    #         2) after the sentence-initial enumeration mark
    #
    # Case 1: Erroneous proper name analyses of 'Veel' and 'Eks' should 
    #         be deleted in the following corpus:
    #
    docs = [Text('" Veel üks Jänes pani jooksu!", ütles Hunt.'),\
            Text('1. Veel teinegi Jänes jooksu pani.'), \
            Text('Veel üks tekst. Jänesele ja Hundile on asi selge.'), \
            Text('Eks neid tekste siin vaikselt koguneb.'), \
            Text('" Eks jah, " ütles Hunt.') ]
    for doc in docs:
        doc.tag_layer(['compound_tokens', 'words', 'sentences'])
        morf_analyzer.tag(doc)
    analyses_a = collect_analyses( docs )
    cb_disambiguator = CorpusBasedMorphDisambiguator()
    cb_disambiguator.predisambiguate(docs)
    # Find difference in ambiguities
    analyses_b = collect_analyses( docs )
    removed, added = find_ambiguities_diff( analyses_a, analyses_b )
    #print( sorted(list(removed.items())) )
    assert sorted(list(removed.items())) == [ ((0, 1), [('Veel', 'H', 'sg n'), ('Vee', 'H', 'sg ad'), ('Vesi', 'H', 'sg ad')]), 
                                              ((0, 3), [('Jäne', 'H', 'sg in'), ('jänes', 'S', 'sg n')]), 
                                              ((0, 10), [('hunt', 'S', 'sg n')]), 
                                              ((1, 1), [('Veel', 'H', 'sg n'), ('Vee', 'H', 'sg ad'), ('Vesi', 'H', 'sg ad')]), 
                                              ((1, 3), [('Jäne', 'H', 'sg in'), ('jänes', 'S', 'sg n')]), 
                                              ((2, 0), [('Veel', 'H', 'sg n'), ('Vee', 'H', 'sg ad'), ('Vesi', 'H', 'sg ad')]), 
                                              ((2, 4), [('Jänese', 'H', 'sg all'), ('jänes', 'S', 'sg all')]), 
                                              ((2, 6), [('Hundile', 'H', 'sg g'), ('Hundile', 'H', 'sg n'), \
                                                        ('Hundi', 'H', 'sg all'), ('Hund', 'H', 'sg all'), ('hunt', 'S', 'sg all')]), 
                                              ((3, 0), [('Eks', 'H', 'sg n')]), 
                                              ((4, 1), [('Eks', 'H', 'sg n')]), 
                                              ((4, 6), [('hunt', 'S', 'sg n')]) 
    ]
    assert list(added.items()) == []



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
            records = span_to_records( word.morph_analysis )
            for rec in records:
                del rec['start']
                del rec['end']
            assert records == [{'normalized_text': 'palk', 'root': 'palk', 'partofspeech': 'S', 'ending': '0', 'form': 'sg n', 'lemma': 'palk', 'clitic': '', 'root_tokens': ['palk']}]
    # 
    #  Case 2: removing 'tama' if verb contains both 'tama' and 'ma'
    #  
    doc = Text('Peaks kuulutama, kuulatama ja kajastama.')
    doc.tag_layer(['compound_tokens', 'words', 'sentences'])
    morf_analyzer.tag(doc)
    duplicate_removal_tagger.retag( doc )
    for word in doc['words']:
        if word.text.endswith('tama'):
            records = span_to_records( word.morph_analysis )
            for rec in records:
                del rec['start']
                del rec['end']
            if word.text == 'kuulutama':
                assert records == [{'normalized_text': 'kuulutama', 'root': 'kuuluta', 'lemma': 'kuulutama', 'ending': 'ma', 'partofspeech': 'V', 'root_tokens': ['kuuluta'], 'clitic': '', 'form': 'ma'}]
            if word.text == 'kuulatama':
                assert records == [{'normalized_text': 'kuulatama', 'root': 'kuulata', 'lemma': 'kuulatama', 'ending': 'ma', 'partofspeech': 'V', 'root_tokens': ['kuulata'], 'clitic': '', 'form': 'ma'}]
            if word.text == 'kajastama':
                assert records == [{'normalized_text': 'kajastama', 'root': 'kajasta', 'lemma': 'kajastama', 'ending': 'ma', 'partofspeech': 'V', 'root_tokens': ['kajasta'], 'clitic': '', 'form': 'ma'}]



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
    assert disamb_ignore_tagger.output_layer in doc.layers
    #
    # 2) Collect results and make assertions
    #
    hidden_words_records = []
    hidden_words = []
    for hidden_word in doc[ disamb_ignore_tagger.output_layer ]:
        records = layer_to_records( hidden_word.morph_analysis )
        hidden_words_records.append( records[0] )
        hidden_words.append( hidden_word.text[0] )
    assert hidden_words == ['kõlanud', 'nagu', 'Mis', 'on', 'üks', 'ega', 'teine']
    expected_hidden_words_records = [
        [ {'normalized_text': 'kõlanud', 'lemma': 'kõlanud', 'form': '', 'partofspeech': 'A', 'root': 'kõla=nud', 'root_tokens': ['kõlanud',], 'end': 18, 'ending': '0', 'start': 11, 'clitic': ''},
          {'normalized_text': 'kõlanud', 'lemma': 'kõlanud', 'form': 'sg n', 'partofspeech': 'A', 'root': 'kõla=nud', 'root_tokens': ['kõlanud',], 'end': 18, 'ending': '0', 'start': 11, 'clitic': ''},
          {'normalized_text': 'kõlanud', 'lemma': 'kõlanu', 'form': 'pl n', 'partofspeech': 'S', 'root': 'kõla=nu', 'root_tokens': ['kõlanu',], 'end': 18, 'ending': 'd', 'start': 11, 'clitic': ''},
          {'normalized_text': 'kõlanud', 'lemma': 'kõlanud', 'form': 'pl n', 'partofspeech': 'A', 'root': 'kõla=nud', 'root_tokens': ['kõlanud',], 'end': 18, 'ending': 'd', 'start': 11, 'clitic': ''},
          {'normalized_text': 'kõlanud', 'lemma': 'kõlama', 'form': 'nud', 'partofspeech': 'V', 'root': 'kõla', 'root_tokens': ['kõla',], 'end': 18, 'ending': 'nud', 'start': 11, 'clitic': ''} ], \
        [ {'normalized_text': 'nagu', 'lemma': 'nagu', 'form': '', 'partofspeech': 'D', 'root': 'nagu', 'root_tokens': ['nagu',], 'end': 23, 'ending': '0', 'start': 19, 'clitic': ''},
          {'normalized_text': 'nagu', 'lemma': 'nagu', 'form': '', 'partofspeech': 'J', 'root': 'nagu', 'root_tokens': ['nagu',], 'end': 23, 'ending': '0', 'start': 19, 'clitic': ''} ], \
        [ {'normalized_text': 'Mis', 'lemma': 'mis', 'form': 'pl n', 'partofspeech': 'P', 'root': 'mis', 'root_tokens': ['mis',], 'end': 33, 'ending': '0', 'start': 30, 'clitic': ''},
          {'normalized_text': 'Mis', 'lemma': 'mis', 'form': 'sg n', 'partofspeech': 'P', 'root': 'mis', 'root_tokens': ['mis',], 'end': 33, 'ending': '0', 'start': 30, 'clitic': ''} ], \
        [ {'normalized_text': 'on', 'lemma': 'olema', 'form': 'b', 'partofspeech': 'V', 'root': 'ole', 'root_tokens': ['ole',], 'end': 36, 'ending': '0', 'start': 34, 'clitic': ''},
          {'normalized_text': 'on', 'lemma': 'olema', 'form': 'vad', 'partofspeech': 'V', 'root': 'ole', 'root_tokens': ['ole',], 'end': 36, 'ending': '0', 'start': 34, 'clitic': ''} ],
        [ {'normalized_text': 'üks', 'lemma': 'üks', 'form': 'sg n', 'partofspeech': 'N', 'root': 'üks', 'root_tokens': ['üks',], 'end': 50, 'ending': '0', 'start': 47, 'clitic': ''},
          {'normalized_text': 'üks', 'lemma': 'üks', 'form': 'sg n', 'partofspeech': 'P', 'root': 'üks', 'root_tokens': ['üks',], 'end': 50, 'ending': '0', 'start': 47, 'clitic': ''} ],
        [{'normalized_text': 'ega', 'lemma': 'ega', 'form': '', 'partofspeech': 'D', 'root': 'ega', 'root_tokens': ['ega',], 'end': 54, 'ending': '0', 'start': 51, 'clitic': ''}, 
         {'normalized_text': 'ega', 'lemma': 'ega', 'form': '', 'partofspeech': 'J', 'root': 'ega', 'root_tokens': ['ega',], 'end': 54, 'ending': '0', 'start': 51, 'clitic': ''}],
        [{'normalized_text': 'teine', 'lemma': 'teine', 'form': 'sg n', 'partofspeech': 'O', 'root': 'teine', 'root_tokens': ['teine',], 'end': 60, 'ending': '0', 'start': 55, 'clitic': ''}, 
         {'normalized_text': 'teine', 'lemma': 'teine', 'form': 'sg n', 'partofspeech': 'P', 'root': 'teine', 'root_tokens': ['teine',], 'end': 60, 'ending': '0', 'start': 55, 'clitic': ''}] ]
    # sort analyses of each and every word
    assert len(hidden_words_records) == len(expected_hidden_words_records)
    for wid in range(len(hidden_words_records)):
        hidden_words_rec = hidden_words_records[wid]
        expected_hidden_words_rec = expected_hidden_words_records[wid]
        hidden_words_records[wid] = _sort_morph_annotations( hidden_words_rec )
        expected_hidden_words_records[wid] = _sort_morph_annotations( expected_hidden_words_rec )
    assert hidden_words_records == expected_hidden_words_records



def test_postdisambiguation_one_level():
    #
    #  Tests the one level of lemma-based post-disambiguation
    #
    morf_analyzer2 = VabamorfAnalyzer(propername=False)
    docs = [Text('Esimesele kohale tuleb Jänes, kuigi tema punktide summa pole kõrgeim.'),\
            Text('Lõpparvestuses läks Konnale esimene koht. Teine koht seekord Jänesele. Uus võistlus toimub 2. mail.'), \
            Text('Konn paistis silma suurima punktide summaga. Uue võistluse toimumisajaks on 2. mai.'),
            Text('Kordame: summat, summat, summat.'),]
    for doc in docs:
        doc.tag_layer(['compound_tokens', 'words', 'sentences'])
        morf_analyzer2.tag( doc )  # Analyse without proper name guessing
    analyses_a = collect_analyses( docs )
    # Use corpus-based disambiguation:
    cb_disambiguator = CorpusBasedMorphDisambiguator()
    cb_disambiguator.postdisambiguate( docs )
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
    cb_disambiguator.postdisambiguate( [docs] )
    [countTotal, countH, countNonH] = count_analyses( docs )
    #print( [countTotal, countH, countNonH] )
    assert [countTotal, countH, countNonH] == [47, 0, 47]
    # 4) Nr of analyses after corpus-based pre-disambiguation, vm disambiguation and 
    #    post-disambiguation
    docs = [ Text(text) for text in corpus ]
    for doc in docs:
        doc.tag_layer(['compound_tokens', 'words', 'sentences'])
        morf_analyzer.tag(doc)
    cb_disambiguator.predisambiguate( docs )
    for doc in docs:
        vm_disamb.retag(doc)
    cb_disambiguator.postdisambiguate( docs )
    [countTotal, countH, countNonH] = count_analyses( docs )
    #print( [countTotal, countH, countNonH] )
    assert [countTotal, countH, countNonH] == [47, 4, 43]


def test_postdisambiguation_two_level():
    #
    #  Tests the two level of lemma-based post-disambiguation
    #  Basically, the corpus division is 2-level this time:
    #      a corpus consists of subsets, and each subset 
    #      contains a list of documents;
    #
    cb_disambiguator = CorpusBasedMorphDisambiguator()
    #
    #   TestCase 1
    #
    morf_analyzer2 = VabamorfAnalyzer(propername=False)
    corpus = [[Text('Esimesele kohale tuleb Jänes, kuigi tema punktide summa pole kõrgeim.'),\
               Text('Lõpparvestuses läks Konnale esimene koht. Teine koht seekord Jänesele. Uus võistlus toimub 2. mail.')], \
              [Text('Konn paistis silma suurima punktide summaga. Uue võistluse toimumisajaks on 2. mai.'),
               Text('Kordame: summat, summat, summat.')],]
    for docs in corpus:
        for doc in docs:
            doc.tag_layer(['compound_tokens', 'words', 'sentences'])
            morf_analyzer2.tag(doc)  # Analyse without proper name guessing
    # collect analyses from all subcorpora
    analyses_before = collect_2nd_level_analyses( corpus )
    # Use corpus-based disambiguation:
    cb_disambiguator.postdisambiguate( corpus )
    # Find difference in ambiguities
    analyses_after = collect_2nd_level_analyses( corpus )
    removed, added = find_ambiguities_diff( analyses_before, analyses_after )
    #for a in sorted(list(removed.items())):
    #    print( a )
    #print()
    assert sorted(list(removed.items())) == [ ((0, 0, 1), [('kohale', 'D', ''), ('kohale', 'K', ''), ('koha', 'S', 'sg all')]), \
                                              ((0, 0, 8), [('summa', 'S', 'sg g'), ('summa', 'S', 'sg n')]), \
                                              ((0, 1, 15), [('maa', 'S', 'pl ad'), ('mail', 'S', 'sg n')]), \
                                              ((1, 0, 2), [('silma', 'V', 'o')]), \
                                              ((1, 0, 5), [('summ', 'S', 'sg kom')]) 
                                            ]
    assert list(added.items()) == []
    #
    #   TestCase 2
    #
    morf_analyzer2 = VabamorfAnalyzer(propername=False)
    corpus = [[Text('Põhja suunas olla sõna läinud, et saak on suur.'),\
               Text('Oma või vaenlase saagist räägite?'),\
               Text('Kulda ja karda jätkus ning leidsime isegi talle.')], \
              [Text('Saagi koju vedanud, saatis ta sõna põhja: omi sõnu me ei söö!'),
               Text('Saak missugune, kulla ja karra tõime koju, tallesid samuti.')],]
    for docs in corpus:
        for doc in docs:
            doc.tag_layer(['compound_tokens', 'words', 'sentences'])
            morf_analyzer2.tag(doc)  # Analyse without proper name guessing
    # collect analyses from all subcorpora
    analyses_before = collect_2nd_level_analyses( corpus )
    # Use corpus-based disambiguation:
    cb_disambiguator.postdisambiguate( corpus )
    # Find difference in ambiguities
    analyses_after = collect_2nd_level_analyses( corpus )
    removed, added = find_ambiguities_diff( analyses_before, analyses_after )
    #for a in sorted(list(removed.items())):
    #    print( a )
    #print()
    #for a in sorted(list(analyses_before)):
    #    print(a, analyses_before[a], '|', analyses_after[a])
    assert sorted(list(removed.items())) == [ ((0, 0, 0), [('põhja', 'V', 'o')]), \
                                              ((0, 0, 3), [('sõna', 'V', 'o')]), \
                                              ((0, 1, 0), [('oma', 'V', 'o')]), \
                                              ((0, 1, 1), [('või', 'V', 'o')]), \
                                              ((0, 1, 3), [('saagis', 'S', 'sg p')]), \
                                              ((0, 2, 0), [('kulda', 'V', 'o')]), \
                                              ((0, 2, 2), [('kart', 'V', 'o')]), \
                                              ((0, 2, 7), [('tema', 'P', 'sg all')]), \
                                              ((1, 0, 0), [('saa', 'V', 'o'), ('saag', 'S', 'adt'), ('saag', 'S', 'sg p')]), \
                                              ((1, 0, 6), [('sõna', 'V', 'o')]), \
                                              ((1, 0, 7), [('põhja', 'V', 'o')]), \
                                              ((1, 0, 10), [('sõnu', 'V', 'o')]), \
                                              ((1, 1, 3), [('kulla', 'A', '')]), 
                                            ]
    assert list(added.items()) == []
    
    
    
def test_postdisambiguation_two_phase_count_position_duplicates_once():
    #
    #  Tests the two-phase of lemma-based post-disambiguation
    #      in which position duplicates will be counted only 
    #      once. For instance, if we have:
    #         põhja -> [ ('põhi', 'S', 'adt'), ('põhi', 'S', 'sg g'), 
    #                    ('põhi', 'S', 'sg p'), ('põhja', 'V', 'o') ]
    #      then counts will be: {'põhi': 1, 'põhja': 1}
    #  [ an experimental feature ]
    #
    cb_disambiguator = CorpusBasedMorphDisambiguator(count_position_duplicates_once=True)
    #
    #   TestCase 1
    #
    morf_analyzer2 = VabamorfAnalyzer(propername=False)
    corpus = [[Text('Põhja poole olla sõna läinud, et saak on suur.'),\
               Text('Oma või vaenlase saagist räägite?'),\
               Text('Kulda ja karda jätkus ning leidsime isegi talle.')], \
              [Text('Saagi koju vedanud, saatis ta sõna põhja poole: omi sõnu me ei söö!'),
               Text('Saak missugune, kulla ja karra tõime koju, tallesid samuti.')],]
    for docs in corpus:
        for doc in docs:
            doc.tag_layer(['compound_tokens', 'words', 'sentences'])
            morf_analyzer2.tag(doc)  # Analyse without proper name guessing
    # collect analyses from all subcorpora
    analyses_before = collect_2nd_level_analyses( corpus )
    # Use corpus-based disambiguation:
    cb_disambiguator.postdisambiguate( corpus )
    # Find difference in ambiguities
    analyses_after = collect_2nd_level_analyses( corpus )
    removed, added = find_ambiguities_diff( analyses_before, analyses_after )
    #for a in sorted(list(removed.items())):
    #    print( a )
    #print()
    #for a in sorted(list(analyses_before)):
    #    print(a, analyses_before[a], '|', analyses_after[a])
    assert sorted(list(removed.items())) == [ ((0, 0, 3), [('sõna', 'V', 'o')]),\
                                              ((0, 1, 0), [('oma', 'V', 'o')]),\
                                              ((0, 1, 3), [('saagis', 'S', 'sg p')]),\
                                              ((0, 2, 0), [('kulda', 'V', 'o')]),\
                                              ((0, 2, 2), [('kart', 'V', 'o')]),\
                                              ((0, 2, 7), [('tema', 'P', 'sg all')]),\
                                              ((1, 0, 0), [('saa', 'V', 'o'), ('saag', 'S', 'adt'), ('saag', 'S', 'sg p')]),\
                                              ((1, 0, 6), [('sõna', 'V', 'o')]),\
                                              ((1, 0, 11), [('sõnu', 'V', 'o')]),\
                                              ((1, 1, 3), [('kulla', 'A', '')]),\
                                            ]
    assert list(added.items()) == []



def test_postdisambiguation_count_inside_compounds():
    #
    #  Tests the post-disambiguation can use the heuristic 'disamb_compound_words':
    #        1) use the lemmas acquired from inside compounds to 
    #           reduce  ambiguities  inside  non-compound  words;
    #        2) use the lemmas acquired from non-compound words to 
    #           reduce  ambiguities  of  compound  words;
    #
    cb_disambiguator = CorpusBasedMorphDisambiguator(disamb_compound_words=True)
    #
    #   Test Case 1
    #
    morf_analyzer2 = VabamorfAnalyzer(propername=False)
    docs = [Text('Kolmas koht Kofu katserajal, edasipääs on sellega tagatud.'),\
            Text('Poolfinaali pääsu korral oleks ta esimene naissoost poolfinalist.'), \
            Text('Aga mida konkurendid rajal tagantvaates näha saavad? Mingi liikuriga ma ringrajale juba ei tule.'), \
            Text('See on nii omane õrnemale soole.'),]
    for doc in docs:
        doc.tag_layer(['compound_tokens', 'words', 'sentences'])
        morf_analyzer2.tag( doc )  # Analyse without proper name guessing
    analyses_a = collect_analyses( docs )
    # Use corpus-based disambiguation:
    cb_disambiguator.postdisambiguate( docs )
    # Find difference in ambiguities
    analyses_b = collect_analyses( docs )
    removed, added = find_ambiguities_diff( analyses_a, analyses_b )
    #for a in sorted(list(removed.items())):
    #    print( a )
    #print()
    assert sorted(list(removed.items())) == [ 
                    ((0, 3), [('katse_raja', 'S', 'sg ad')]),
                    ((1, 1), [('pääsu', 'S', 'sg g'), ('pääsu', 'S', 'sg n')]),
                    ((1, 2), [('kord', 'S', 'sg ad')]),
                    ((2, 3), [('raja', 'S', 'sg ad')]),
                    ((2, 6), [('saa', 'V', 'vad')]),
                    ((2, 8), [('mink', 'S', 'sg g'), ('minki', 'V', 'o')]),
                    ((3, 5), [('soo', 'S', 'sg all')])
    ]
    assert list(added.items()) == []
    #
    #   Test Case 2
    #
    docs = [Text('Mõisnikesoost mees sõitis juurviljalao juurde.'),\
            Text('Ladu langes. Mõisnikesugu irvitas. Ei, ma ei võta seda laest!'), \
            Text('Ta pärines tuntud kirjandusmehe soost ehk vahmiilist.'), \
            Text('Toalagi oli must -- alates saunalae kõrguselt.'),]
    for doc in docs:
        doc.tag_layer(['compound_tokens', 'words', 'sentences'])
        morf_analyzer2.tag( doc )  # Analyse without proper name guessing
    analyses_a = collect_analyses( docs )
    # Use corpus-based disambiguation:
    cb_disambiguator.postdisambiguate( docs )
    # Find difference in ambiguities
    analyses_b = collect_analyses( docs )
    removed, added = find_ambiguities_diff( analyses_a, analyses_b )
    #for a in sorted(list(removed.items())):
    #    print( a )
    #print()
    assert sorted(list(removed.items())) == [ 
                    ((0, 0), [('mõisnik+e_soo', 'S', 'sg el')]),
                    ((0, 1), [('mesi', 'S', 'sg in')]),
                    ((0, 3), [('juur_vilja_lagu', 'S', 'sg g')]),
                    ((0, 4), [('juur', 'S', 'adt')]),
                    ((1, 12), [('laad', 'S', 'sg el')]),
                    ((2, 4), [('soo', 'S', 'sg el')]),
                    ((3, 5), [('sauna_laad', 'S', 'sg g')])
    ]
    assert list(added.items()) == []



def test_pre_and_postdisambiguation_different_input_structures():
    #
    #  Tests the pre- and post-disambiguation works on different input structures
    #
    cb_disambiguator = CorpusBasedMorphDisambiguator()
    #
    #   TestCase 0 : a list with one Text object
    #
    docs0 = [ Text('Tahtis kulda. Aga sai kasside kulla.') ]
    for doc in docs0:
        doc.tag_layer(['compound_tokens', 'words', 'sentences'])
        morf_analyzer.tag( doc )
    cb_disambiguator.predisambiguate( docs0 )
    cb_disambiguator.postdisambiguate( docs0 )
    assert count_analyses( docs0 ) == [10, 0, 10]
    #
    #   TestCase 1 : list of Texts
    #
    docs = [ Text('Ott tahab võita ka Kuldgloobust ja kulda.'), \
             Text('Kuidas see Otil õnnestub, ei tea. Aga Ott lubas pingutada kulla nimel.'), \
             Text('Võib-olla tuleks siiski teha Kuldgloobuse eesti variant.') ]
    for doc in docs:
        doc.tag_layer(['compound_tokens', 'words', 'sentences'])
        morf_analyzer.tag( doc )
    cb_disambiguator.predisambiguate( docs )
    cb_disambiguator.postdisambiguate( docs )
    assert count_analyses( docs ) == [38, 5, 33]
    #
    #   TestCase 2 : list of lists of Texts
    #
    docs2 = [ [Text('Ott tahab võita ka Kuldgloobust ja kulda.')], \
              [Text('Kuidas see Otil õnnestub, ei tea. Aga Ott lubas pingutada kulla nimel.'), \
               Text('Võib-olla tuleks siiski teha Kuldgloobuse eesti variant.') ] ]
    for sub_docs in docs2:
        for doc in sub_docs:
            doc.tag_layer(['compound_tokens', 'words', 'sentences'])
            morf_analyzer.tag( doc )
    cb_disambiguator.predisambiguate( docs2 )
    cb_disambiguator.postdisambiguate( docs2 )
    assert count_analyses( docs2 ) == [38, 5, 33]
    #
    #   TestCase X : a list with an empty Text
    #
    docsx = [ Text('') ]
    for doc in docsx:
        doc.tag_layer(['compound_tokens', 'words', 'sentences'])
        morf_analyzer.tag( doc )
    cb_disambiguator.predisambiguate( docsx )
    cb_disambiguator.postdisambiguate( docsx )
    #
    #   TestCase Y : an empty list
    #
    docsy = []
    cb_disambiguator.predisambiguate( docsy )
    cb_disambiguator.postdisambiguate( docsy )
    #
    #   TestCase Z : a Text as input gives AssertionError
    #        ( a collection of Text-s is required )
    #
    
    # Giving Text as an input gives AssertionError: 
    #   a list of Texts is expected
    text = Text('Tahtis kulda. Aga sai kasside kulla.')
    with pytest.raises(AssertionError) as e1:
        cb_disambiguator.predisambiguate( text )
    with pytest.raises(AssertionError) as e2:
        cb_disambiguator.postdisambiguate( text )
    #
    #   TestCase Cthulhu : the pre- and post-disambiguation 
    #       raises an Exception if some of the required 
    #       layers are missing
    #
    text = Text('Tahtis kulda. Aga sai kasside kulla.')
    with pytest.raises(Exception) as ex1:
        cb_disambiguator.predisambiguate( [text] )
    with pytest.raises(Exception) as ex2:
        cb_disambiguator.postdisambiguate( [text] )


def test_cb_disambiguator_on_unknown_words():
    #
    #  Tests CorpusBasedMorphDisambiguator works (==does not fail) on texts
    #        that contain unknown words
    #
    cb_disambiguator = CorpusBasedMorphDisambiguator()
    morf_analyzer3 = VabamorfAnalyzer(guess= False, propername=False)
    docs = [Text('Mulll on yks hea netikeelelause'),
            Text('Davai siis, mul ka yks'), ]
    for doc in docs:
        doc.tag_layer(['compound_tokens', 'words', 'sentences'])
        # Analyse, but do not guess anything
        morf_analyzer3.tag( doc )
    #print ( count_analyses( docs ) )
    cb_disambiguator.predisambiguate( docs )
    cb_disambiguator.postdisambiguate( docs )
    # Assert that unknowns still exist
    unknowns = []
    for doc in docs:
        for word_analyses in doc.morph_analysis:
            for analysis in word_analyses.annotations:
                if _is_empty_annotation(analysis):
                    unknowns.append(word_analyses.text)
    assert unknowns == ['Mulll', 'yks', 'Davai', ',', 'yks']
    # Assert analysis count
    [countTotal, countH, countNonH] = count_analyses( docs )
    assert [countTotal, countH, countNonH] == [12, 0, 12]

