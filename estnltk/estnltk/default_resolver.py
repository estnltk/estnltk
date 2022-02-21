#
#  Default LayerResolver for EstNLTK v1.6
#
from estnltk_core.taggers_registry import TaggersRegistry
from estnltk_core.layer_resolver import LayerResolver

from .taggers.standard.text_segmentation.tokens_tagger import TokensTagger
from .taggers.standard.text_segmentation.word_tagger import WordTagger
from .taggers.standard.text_segmentation.compound_token_tagger import CompoundTokenTagger
from .taggers.standard.text_segmentation.sentence_tokenizer import SentenceTokenizer
from .taggers.standard.text_segmentation.paragraph_tokenizer import ParagraphTokenizer
from .taggers.standard.morph_analysis.morf import VabamorfTagger
from .taggers.standard.morph_analysis.vm_est_cat_names import VabamorfEstCatConverter
from .taggers.standard.syntax.preprocessing.morph_extended_tagger import MorphExtendedTagger
from .taggers.standard.text_segmentation.clause_segmenter import ClauseSegmenter    # Requires Java

# Load default configuration for morph analyser
from .taggers.standard.morph_analysis.morf_common import DEFAULT_PARAM_DISAMBIGUATE, DEFAULT_PARAM_GUESS
from .taggers.standard.morph_analysis.morf_common import DEFAULT_PARAM_PROPERNAME, DEFAULT_PARAM_PHONETIC
from .taggers.standard.morph_analysis.morf_common import DEFAULT_PARAM_COMPOUND


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
    vabamorf_tagger = VabamorfTagger(
                                     disambiguate=disambiguate,
                                     guess=guess,
                                     propername=propername,
                                     phonetic=phonetic,
                                     compound=compound,
                                     slang_lex=slang_lex,
                                     use_reorderer=use_reorderer,
                                     predisambiguate =predisambiguate,
                                     postdisambiguate=postdisambiguate
                                     )

    taggers = TaggersRegistry([TokensTagger(), WordTagger(), CompoundTokenTagger(),
                       SentenceTokenizer(), ParagraphTokenizer(),
                       vabamorf_tagger, MorphExtendedTagger(), ClauseSegmenter(),
                       VabamorfEstCatConverter()])
    return LayerResolver( taggers, default_layers=('morph_analysis', 'sentences') )


DEFAULT_RESOLVER = make_resolver()
