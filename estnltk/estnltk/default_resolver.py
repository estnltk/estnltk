#
#  Default LayerResolver for EstNLTK v1.6
#
from estnltk_core.taggers import TaggerLoader
from estnltk_core.taggers_registry import TaggersRegistry
from estnltk_core.layer_resolver import LayerResolver

# Load default configuration for morph analyser
from estnltk.common import DEFAULT_PARAM_DISAMBIGUATE, DEFAULT_PARAM_GUESS
from estnltk.common import DEFAULT_PARAM_PROPERNAME, DEFAULT_PARAM_PHONETIC
from estnltk.common import DEFAULT_PARAM_COMPOUND
from estnltk.common import ESTNLTK_MORPH_ATTRIBUTES
from estnltk.common import NORMALIZED_TEXT
from estnltk.common import IGNORE_ATTR

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
    """
    Creates and returns LayerResolver with EstNLTK's default NLP pipeline.

    Parameters change settings of Vabamorf's morphological analysis.

    **Warning**: changing Vabamorf's parameters `guess`, `propername`,
    `disambiguate`, `compound` and `phonetic` can tamper the quality of
    taggers that are dependent on morphological analysis, and some
    downstream taggers can also become non-functional (run into errors).
    So, you should not use downstream taggers if you change these
    parameters (unless you know what you are doing).

    Parameters
    ----------
    guess: boolean (default: True)
        Use guessing in case of unknown words (Vabamorf's parameter).
    propername: boolean (default: True)
        Propose additional analysis variants for proper names
        (a.k.a. proper name guessing) (Vabamorf's parameter).
    disambiguate: boolean (default: True)
        Disambiguate morphological analyses with Vabamorf's
        disambiguator.
    compound: boolean (default: True)
        Add compound word markers to root forms (Vabamorf's parameter).
    phonetic: boolean (default: False)
        Add phonetic information to root forms (Vabamorf's parameter).
    slang_lex: boolean (default: False)
        If True, then uses an extended version of Vabamorf's binary lexicon,
        which provides valid analyses to spoken and slang words, such as
        'kodukas', 'mõnsa', 'mersu', 'kippelt'. However, using "the slang
        lexicon" also hinders Vabamorf's ability to clearly distinguish
        between written language and slang words, and this is the reason
        that "the slang lexicon" is not switched on by default;
        Note: this only works if you leave the parameter vm_instance
        unspecified (Vabamorf's parameter);
    use_reorderer: boolean (default: True)
        Whether analysis_reorderer will be applied for re-arranging
        ambiguous morphological analyses after disambiguation.
        Note: reorderings made by the default analysis_reorderer will
        only have effect together with the default disambiguation
        (disambiguate=True). That's why iff disambiguate=False, then
        use_reorderer will be forced to False (Vabamorf's parameter).
    predisambiguate: boolean (default: False)
        Whether text-based predisambiguation of ambiguous proper name
        analyses will be applied before Vabamorf's morphological
        disambiguation.
    postdisambiguate: boolean (default: False)
        Whether text-based post-disambiguation of remaining ambiguous
        analyses will be applied after Vabamorf's morphological
        disambiguation.

    """
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
                      output_attributes=(),
                      description="Preprocessing for word segmentation: segments text into tokens." ),
        TaggerLoader( 'compound_tokens', ['tokens'], 
                      'estnltk.taggers.standard.text_segmentation.compound_token_tagger.CompoundTokenTagger', 
                      output_attributes=('type', 'normalized'),
                      description="Preprocessing for word segmentation: joins tokens into compound tokens." ),
        TaggerLoader( 'words', ['tokens', 'compound_tokens'], 
                      'estnltk.taggers.standard.text_segmentation.word_tagger.WordTagger', 
                      output_attributes=('normalized_form',),
                      description="Segments text into words." ),
        TaggerLoader( 'sentences', ['compound_tokens', 'words'], 
                      'estnltk.taggers.standard.text_segmentation.sentence_tokenizer.SentenceTokenizer', 
                      output_attributes=(),
                      description="Segments text into sentences." ),
        TaggerLoader( 'paragraphs', ['sentences'], 
                      'estnltk.taggers.standard.text_segmentation.paragraph_tokenizer.ParagraphTokenizer', 
                      output_attributes=(),
                      description="Segments text into paragraphs." ),
        TaggerLoader( 'morph_analysis', ['compound_tokens', 'words', 'sentences'], 
                      'estnltk.taggers.standard.morph_analysis.morf.VabamorfTagger', 
                      output_attributes=vabamorf_tagger_output_attributes,
                      parameters=vabamorf_tagger_parameters,
                      description="Tags morphological analysis with Vabamorf." ),
        TaggerLoader( 'clauses', ['words', 'sentences', 'morph_analysis'], 
                      'estnltk.taggers.standard.text_segmentation.clause_segmenter.ClauseSegmenter',  # Requires Java
                      output_attributes= ('clause_type',),
                      description="Segments sentences into clauses. (requires Java)" ),
        # ==================================================
        #             Specific morph                        
        # ==================================================
        TaggerLoader( 'morph_analysis_est', ['morph_analysis'], 
                      'estnltk.taggers.standard.morph_analysis.vm_est_cat_names.VabamorfEstCatConverter', 
                      output_attributes=('normaliseeritud_sõne', 'algvorm', 'lõpp', 'sõnaliik', 'vormi_nimetus', 'kliitik'),
                      description="Translates category names of Vabamorf's morphological analyses into Estonian"+
                                  " (for educational purposes)." ),
        TaggerLoader( 'morph_extended', ['morph_analysis'], 
                      'estnltk.taggers.standard.syntax.preprocessing.morph_extended_tagger.MorphExtendedTagger', 
                      output_attributes= (NORMALIZED_TEXT,) + ESTNLTK_MORPH_ATTRIBUTES + \
                                         ('punctuation_type', 'pronoun_type', 'letter_case', \
                                          'fin', 'verb_extension_suffix', 'subcat'),
                      description="Converts Vabamorf's morphological analyses to syntax preprocessing (CG3) format." ),
        TaggerLoader( 'gt_morph_analysis', ['words', 'sentences', 'morph_analysis', 'clauses'], 
                      'estnltk.taggers.standard.morph_analysis.gt_morf.GTMorphConverter', 
                      output_attributes=(NORMALIZED_TEXT,) + ESTNLTK_MORPH_ATTRIBUTES,
                      description="Converts Vabamorf's morphological analyses to giellatekno's (GT) format." ),
        # ==================================================
        #             Information extraction                
        # ==================================================
        TaggerLoader( 'ner', ['morph_analysis', 'words', 'sentences'], 
                      'estnltk.taggers.standard.ner.ner_tagger.NerTagger', 
                      output_attributes=('nertag',),
                      description='Detects named entities: person, location and organization names.' ),
        TaggerLoader( 'timexes', [], 
                      'estnltk.taggers.standard.timexes.timex_tagger.TimexTagger',  # Requires Java
                      output_attributes=('tid', 'type', 'value', 'temporal_function', 'anchor_time_id', \
                                         'mod', 'quant', 'freq', 'begin_point', 'end_point', 'part_of_interval' ),
                      description='Detects temporal expressions and normalizes to corresponding dates, '+\
                                  'times, durations and recurrences. (requires Java)' ),
        TaggerLoader( 'address_parts', ['words'], 
                      'estnltk.taggers.miscellaneous.address_tagger.AddressPartTagger', 
                      output_attributes=('grammar_symbol', 'type'),
                      description='Preprocessing for address detection.' ),
        TaggerLoader( 'addresses', ['address_parts'], 
                      'estnltk.taggers.miscellaneous.address_tagger.AddressGrammarTagger', 
                      output_attributes=('grammar_symbol', 'TÄNAV', 'MAJA', 'ASULA', 'MAAKOND', 'INDEKS'),
                      description='Detects addresses.' ),
        # ==================================================
        #             Default syntax                        
        # ==================================================
        TaggerLoader( 'maltparser_conll_morph', ['sentences', 'morph_analysis'], 
                      'estnltk.taggers.standard.syntax.conll_morph_tagger.ConllMorphTagger', 
                      output_attributes=('id', 'form', 'lemma', 'upostag', 'xpostag', 'feats', \
                                         'head', 'deprel', 'deps', 'misc'),
                      parameters={ 'output_layer': 'maltparser_conll_morph', 
                                   'morph_extended_layer': 'morph_analysis', 
                                   'no_visl': True},
                      description='Preprocessing for MaltParser based syntactic analysis.' ),
        TaggerLoader( 'maltparser_syntax', ['words', 'sentences', 'maltparser_conll_morph'], 
                      'estnltk.taggers.standard.syntax.maltparser_tagger.maltparser_tagger.MaltParserTagger',  # Requires Java
                      output_attributes=('id', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', \
                                         'deps', 'misc', 'parent_span', 'children'),
                      parameters={ 'input_conll_morph_layer': 'maltparser_conll_morph', 
                                   'input_type': 'morph_analysis'},
                      description='Tags dependency syntactic analysis with MaltParser. (requires Java)' ),
        # ==================================================
        #             Experimental stuff                    
        # ==================================================
        TaggerLoader( 'verb_chains', ['words', 'sentences', 'morph_analysis', 'clauses'], 
                      'estnltk.taggers.miscellaneous.verb_chains.verbchain_detector_tagger.VerbChainDetector', 
                      output_attributes=('pattern', 'roots', 'word_ids', 'mood', 'polarity', 'tense', \
                                         'voice', 'remaining_verbs' ),
                      description='Tags main verbs and their extensions (verb chains) in clauses. (experimental)' ),
        TaggerLoader( 'np_chunks', ['words', 'sentences', 'morph_analysis', 'maltparser_syntax'], 
                      'estnltk.taggers.miscellaneous.np_chunker.NounPhraseChunker', 
                      output_attributes=(), parameters={'syntax_layer':'maltparser_syntax'},
                      description='Tags noun phrase chunks in sentences. (experimental)' ),
    ])
    return LayerResolver( taggers, default_layers=('morph_analysis', 'sentences') )


DEFAULT_RESOLVER = make_resolver()
"""
LayerResolver with EstNLTK's default NLP pipeline.
"""