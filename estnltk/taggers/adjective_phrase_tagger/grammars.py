from estnltk import Postags, Regex, Intersection, Concatenation, Lemmas, Union

from .adverbs import ADJ_MODIFIERS
from .adverbs import COMP_MODIFIERS

adverb = Postags('D')
adjective = Postags('A')
comparative = Postags('C')

space = Regex('\s')

adj_modifier = Intersection(
        ADJ_MODIFIERS,
        Postags('D')
)

comp_modifier = Intersection(
        COMP_MODIFIERS,
        Postags('D')
)

adj_phrase = Concatenation(
        adj_modifier,
        space,
        adjective)

comp_phrase = Concatenation(
        comp_modifier,
        space,
        comparative)

adj_phrase_ja = Concatenation(
        adj_phrase,
        space,
        Lemmas("ja"),
        space,
        adjective)

comp_phrase_ja = Concatenation(
        comp_phrase,
        space,
        Lemmas("ja"),
        space,
        comparative)

adjective_phrases = Union(
        adj_phrase_ja,
        comp_phrase_ja,
        comp_phrase,
        adj_phrase,
        adjective,
        comparative,
        name='adjective_phrases'
)

# Participle phrases are initially tagged as a separate layer and afterwards included into adjective_phrases layer
part_phrase = Union(
        Concatenation(
                adverb,
                space,
                adjective),
                name='participle_phrases'
)
