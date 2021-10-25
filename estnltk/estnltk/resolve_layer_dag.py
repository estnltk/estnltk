from typing import List
import networkx as nx

from estnltk_core.resolve_layer_dag import TaggersRegistry, Resolver

from .taggers.text_segmentation.tokens_tagger import TokensTagger
from .taggers.text_segmentation.word_tagger import WordTagger
from .taggers.text_segmentation.compound_token_tagger import CompoundTokenTagger
from .taggers.text_segmentation.sentence_tokenizer import SentenceTokenizer
from .taggers.text_segmentation.paragraph_tokenizer import ParagraphTokenizer
from .taggers.morph_analysis.morf import VabamorfTagger
from .taggers.morph_analysis.vm_est_cat_names import VabamorfEstCatConverter
from .taggers.syntax_preprocessing.morph_extended_tagger import MorphExtendedTagger
from .taggers.text_segmentation.clause_segmenter import ClauseSegmenter    # Requires Java

# Load default configuration for morph analyser
from .taggers.morph_analysis.morf_common import DEFAULT_PARAM_DISAMBIGUATE, DEFAULT_PARAM_GUESS
from .taggers.morph_analysis.morf_common import DEFAULT_PARAM_PROPERNAME, DEFAULT_PARAM_PHONETIC
from .taggers.morph_analysis.morf_common import DEFAULT_PARAM_COMPOUND


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
    return Resolver(taggers)


DEFAULT_RESOLVER = make_resolver()
