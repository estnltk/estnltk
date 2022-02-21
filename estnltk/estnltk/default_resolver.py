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
        TaggerLoader( 'morph_analysis_est', ['morph_analysis'], 
                      'estnltk.taggers.standard.morph_analysis.vm_est_cat_names.VabamorfEstCatConverter', 
                      output_attributes=('normaliseeritud_sõne', 'algvorm', 'lõpp', 'sõnaliik', 'vormi_nimetus', 'kliitik') ),
        TaggerLoader( 'morph_extended', ['morph_analysis'], 
                      'estnltk.taggers.standard.syntax.preprocessing.morph_extended_tagger.MorphExtendedTagger', 
                      output_attributes= vabamorf_tagger_output_attributes + \
                                         ('punctuation_type', 'pronoun_type', 'letter_case', \
                                          'fin', 'verb_extension_suffix', 'subcat') ),
        TaggerLoader( 'clauses', ['words', 'sentences', 'morph_analysis'], 
                      'estnltk.taggers.standard.text_segmentation.clause_segmenter.ClauseSegmenter',  # Requires Java
                      output_attributes= ('clause_type',) )
    ])
    return LayerResolver( taggers, default_layers=('morph_analysis', 'sentences') )


DEFAULT_RESOLVER = make_resolver()
