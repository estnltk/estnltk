#
#  Default LayerResolver for EstNLTK v1.6
#
from estnltk_core.taggers import TaggerLoader
from estnltk_core.taggers_registry import TaggersRegistry
from estnltk_core.layer_resolver import LayerResolver

# Load default configuration for morph analyser
from .taggers.standard.morph_analysis.morf_common import DEFAULT_PARAM_DISAMBIGUATE, DEFAULT_PARAM_GUESS
from .taggers.standard.morph_analysis.morf_common import DEFAULT_PARAM_PROPERNAME, DEFAULT_PARAM_PHONETIC
from .taggers.standard.morph_analysis.morf_common import DEFAULT_PARAM_COMPOUND
from .taggers.standard.morph_analysis.morf_common import ESTNLTK_MORPH_ATTRIBUTES
from .taggers.standard.morph_analysis.morf_common import NORMALIZED_TEXT
from .taggers.standard.morph_analysis.morf_common import IGNORE_ATTR

def make_resolver(
                 disambiguate=DEFAULT_PARAM_DISAMBIGUATE,
                 guess       =DEFAULT_PARAM_GUESS,
                 propername  =DEFAULT_PARAM_PROPERNAME,
                 phonetic    =DEFAULT_PARAM_PHONETIC,
                 compound    =DEFAULT_PARAM_COMPOUND,
                 slang_lex   =False,
                 use_reorderer=True,
                 predisambiguate =False,
                 postdisambiguate=False):
    vabamorf_tagger_parameters = { \
        'disambiguate': disambiguate,
        'guess': guess,
        'propername': propername,
        'phonetic': phonetic,
        'compound': compound,
        'slang_lex': slang_lex,
        'use_reorderer': use_reorderer,
        'predisambiguate': predisambiguate,
        'postdisambiguate': postdisambiguate
    }
    vabamorf_tagger_output_attributes = (NORMALIZED_TEXT,) + ESTNLTK_MORPH_ATTRIBUTES
    if not disambiguate:
        vabamorf_tagger_output_attributes += (IGNORE_ATTR,)
    taggers = TaggersRegistry([
        # ==================================================
        #             The basic pipeline                    
        # ==================================================
        TaggerLoader( 'tokens', [], 
                      'estnltk.taggers.standard.text_segmentation.tokens_tagger.TokensTagger', 
                      output_attributes=() ),
        TaggerLoader( 'compound_tokens', ['tokens'], 
                      'estnltk.taggers.standard.text_segmentation.compound_token_tagger.CompoundTokenTagger', 
                      output_attributes=('type', 'normalized') ),
        TaggerLoader( 'words', ['tokens', 'compound_tokens'], 
                      'estnltk.taggers.standard.text_segmentation.word_tagger.WordTagger', 
                      output_attributes=('normalized_form',) ),
        TaggerLoader( 'sentences', ['compound_tokens', 'words'], 
                      'estnltk.taggers.standard.text_segmentation.sentence_tokenizer.SentenceTokenizer', 
                      output_attributes=() ),
        TaggerLoader( 'paragraphs', ['sentences'], 
                      'estnltk.taggers.standard.text_segmentation.paragraph_tokenizer.ParagraphTokenizer', 
                      output_attributes=() ),
        TaggerLoader( 'morph_analysis', ['compound_tokens', 'words', 'sentences'], 
                      'estnltk.taggers.standard.morph_analysis.morf.VabamorfTagger', 
                      output_attributes=vabamorf_tagger_output_attributes,
                      parameters=vabamorf_tagger_parameters ),
        TaggerLoader( 'clauses', ['words', 'sentences', 'morph_analysis'], 
                      'estnltk.taggers.standard.text_segmentation.clause_segmenter.ClauseSegmenter',  # Requires Java
                      output_attributes= ('clause_type',) ),
        # ==================================================
        #             Specific morph                        
        # ==================================================
        TaggerLoader( 'morph_analysis_est', ['morph_analysis'], 
                      'estnltk.taggers.standard.morph_analysis.vm_est_cat_names.VabamorfEstCatConverter', 
                      output_attributes=('normaliseeritud_sõne', 'algvorm', 'lõpp', 'sõnaliik', 'vormi_nimetus', 'kliitik') ),
        TaggerLoader( 'morph_extended', ['morph_analysis'], 
                      'estnltk.taggers.standard.syntax.preprocessing.morph_extended_tagger.MorphExtendedTagger', 
                      output_attributes= (NORMALIZED_TEXT,) + ESTNLTK_MORPH_ATTRIBUTES + \
                                         ('punctuation_type', 'pronoun_type', 'letter_case', \
                                          'fin', 'verb_extension_suffix', 'subcat') ),
        TaggerLoader( 'gt_morph_analysis', ['words', 'sentences', 'morph_analysis', 'clauses'], 
                      'estnltk.taggers.standard.morph_analysis.gt_morf.GTMorphConverter', 
                      output_attributes=(NORMALIZED_TEXT,) + ESTNLTK_MORPH_ATTRIBUTES ),
        TaggerLoader( 'hfst_gt_morph_analysis', ['words'], 
                      'estnltk.taggers.standard.morph_analysis.hfst.hfst_morph_analyser_cmd_line.HfstClMorphAnalyser',  # Requires HFST cmd 
                      output_attributes=('morphemes_lemmas', 'postags', 'forms', 'is_guessed', 'has_clitic', 'usage', 'weight') ),
        # ==================================================
        #             Information extraction                
        # ==================================================
        TaggerLoader( 'ner', ['morph_analysis', 'words', 'sentences'], 
                      'estnltk.taggers.standard.ner.ner_tagger.NerTagger', 
                      output_attributes=('nertag',) ),
        TaggerLoader( 'timexes', [], 
                      'estnltk.taggers.standard.timexes.timex_tagger.TimexTagger',  # Requires Java
                      output_attributes=('tid', 'type', 'value', 'temporal_function', 'anchor_time_id', \
                                         'mod', 'quant', 'freq', 'begin_point', 'end_point', 'part_of_interval' ) ),
        TaggerLoader( 'address_parts', ['words'], 
                      'estnltk.taggers.miscellaneous.address_tagger.AddressPartTagger', 
                      output_attributes=('grammar_symbol', 'type') ),
        TaggerLoader( 'addresses', ['address_parts'], 
                      'estnltk.taggers.miscellaneous.address_tagger.AddressGrammarTagger', 
                      output_attributes=('grammar_symbol', 'TÄNAV', 'MAJA', 'ASULA', 'MAAKOND', 'INDEKS') ),
        # ==================================================
        #             Default syntax                        
        # ==================================================
        TaggerLoader( 'maltparser_conll_morph', ['sentences', 'morph_analysis'], 
                      'estnltk.taggers.standard.syntax.conll_morph_tagger.ConllMorphTagger', 
                      output_attributes=('id', 'form', 'lemma', 'upostag', 'xpostag', 'feats', \
                                         'head', 'deprel', 'deps', 'misc'),
                      parameters={ 'output_layer': 'maltparser_conll_morph', 
                                   'morph_extended_layer': 'morph_analysis', 
                                   'no_visl': True} ),
        TaggerLoader( 'maltparser_syntax', ['words', 'sentences', 'maltparser_conll_morph'], 
                      'estnltk.taggers.standard.syntax.maltparser_tagger.maltparser_tagger.MaltParserTagger',  # Requires Java
                      output_attributes=('id', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', \
                                         'deps', 'misc', 'parent_span', 'children'),
                      parameters={ 'input_conll_morph_layer': 'maltparser_conll_morph', 
                                   'input_type': 'morph_analysis'} ),
        # ==================================================
        #             Experimental stuff                    
        # ==================================================
        TaggerLoader( 'verb_chains', ['words', 'sentences', 'morph_analysis', 'clauses'], 
                      'estnltk.taggers.miscellaneous.verb_chains.verbchain_detector_tagger.VerbChainDetector', 
                      output_attributes=('pattern', 'roots', 'word_ids', 'mood', 'polarity', 'tense', \
                                         'voice', 'remaining_verbs' ) ),
        TaggerLoader( 'np_chunks', ['words', 'sentences', 'morph_analysis', 'maltparser_syntax'], 
                      'estnltk.taggers.miscellaneous.np_chunker.NounPhraseChunker', 
                      output_attributes=(), parameters={'syntax_layer':'maltparser_syntax'} ),
    ])
    return LayerResolver( taggers, default_layers=('morph_analysis', 'sentences') )


DEFAULT_RESOLVER = make_resolver()
