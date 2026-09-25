"""Determining a word's morphological form from its possible replacements.

This is the indirect method the component exists for. Rather than asking a model
what case a word is in, it asks for words that would fit the same slot, analyses
each of those with Vabamorf, and reads the answer off the resulting distribution
of forms. Words that fit the same slot must agree in case, so the case the
replacements share is the case of the original.

The cost is one model call plus one Vabamorf analysis per candidate, so this is
worth reserving for words that are genuinely in doubt.
"""

from __future__ import annotations

from collections import defaultdict
from typing import List, Optional, Sequence, Tuple

from estnltk import Text
from estnltk.taggers import VabamorfAnalyzer

from estnltk_neural.taggers.neural_morph.llm_generator_based.word_filter import (
    WordFilter,
)
from estnltk_neural.taggers.neural_morph.llm_generator_based.word_replacement_generator import (
    Replacement,
    WordReplacementGenerator,
)

# FormDistribution entry = (form, share of the candidate weight, or None)
FormDistribution = List[Tuple[str, Optional[float]]]


class WordReplacementAnalyzer:
    """Turns candidate replacements into a distribution over morphological forms."""

    def __init__(
        self,
        generator: WordReplacementGenerator,
        word_filter: Optional[WordFilter] = None,
        vabamorf_analyzer: Optional[VabamorfAnalyzer] = None,
        split_pos_form: bool = False,
    ):
        """Initialise the analyzer.

        Parameters
        ----------
        generator:
            Proposes the replacement candidates.
        word_filter:
            Optional; drops candidates that do not fit the sentence.
        vabamorf_analyzer:
            Used to analyse each candidate. Defaults to a plain
            ``VabamorfAnalyzer``, which is not disambiguated, so a candidate that
            is itself ambiguous contributes to every form it could carry.
        split_pos_form:
            If ``True``, forms are reported as ``'partofspeech|form'`` rather
            than the form alone, which distinguishes e.g. a noun's ``sg g`` from
            an adjective's.
        """
        self.generator = generator
        self.word_filter = word_filter
        self.vabamorf_analyzer = vabamorf_analyzer or VabamorfAnalyzer()
        self.split_pos_form = split_pos_form

    def _forms_of_candidate(
        self, sentence: Sequence[str], loc: int, candidate: str
    ) -> List[str]:
        """Analyse ``candidate`` in place of the token at ``loc``, return its forms.

        The candidate is substituted token-for-token, so the target keeps its
        index and the surrounding context is unchanged.
        """
        tokens = list(sentence)
        tokens[loc] = candidate
        text = Text(" ".join(tokens))
        text.tag_layer(["words", "sentences"])
        self.vabamorf_analyzer.tag(text)

        # Locate the substituted token by index rather than by string: the same
        # word form may occur more than once in the sentence.
        spans = list(text[self.vabamorf_analyzer.output_layer])
        if loc >= len(spans):
            # Vabamorf's tokenisation split the candidate into several tokens, so
            # the indices no longer line up and the candidate cannot be scored.
            return []
        span = spans[loc]
        if span.text != candidate:
            return []

        forms = []
        for annotation in span.annotations:
            form = annotation.get("form")
            if form is None:
                continue
            if self.split_pos_form:
                forms.append(f"{annotation.get('partofspeech')}|{form}")
            else:
                forms.append(str(form))
        return forms

    def analyze(self, sentence: Sequence[str], loc: int) -> FormDistribution:
        """Return the distribution of forms over the candidate replacements.

        Parameters
        ----------
        sentence:
            The sentence as a list of tokens.
        loc:
            Index of the word whose form is in question.

        Returns
        -------
        list of (str, float)
            Forms with their share of the total candidate weight, most likely
            first. Empty if no candidate could be analysed.
        """
        candidates: List[Replacement] = self.generator.generate(sentence, loc)
        if self.word_filter is not None:
            candidates = self.word_filter.filter(sentence, loc, candidates)
        if not candidates:
            return []

        # A generator that reports no probabilities gets uniform weights, which
        # is how the thesis experiments treated LLM candidates.
        weights = [1.0 if score is None else float(score) for _, score in candidates]

        mass: defaultdict[str, float] = defaultdict(float)
        total = 0.0
        for (candidate, _), weight in zip(candidates, weights):
            forms = self._forms_of_candidate(sentence, loc, candidate)
            if not forms:
                continue
            # An ambiguous candidate splits its weight across its readings, so a
            # candidate with one clear reading counts for more than one with four.
            share = weight / len(forms)
            for form in forms:
                mass[form] += share
            total += weight

        if total <= 0:
            return []
        return sorted(
            ((form, weight / total) for form, weight in mass.items()),
            key=lambda pair: (-pair[1], pair[0]),
        )
