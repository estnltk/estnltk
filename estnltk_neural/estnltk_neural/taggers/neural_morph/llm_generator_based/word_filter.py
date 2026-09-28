"""Filtering a list of candidate word forms down to those that fit a sentence.

A filter is optional in the pipeline. It exists because a generator that proposes
many candidates cheaply -- a masked language model, say -- tends to include forms
that do not fit the sentence at all, and those distort the form distribution the
analyser computes. A language model is good at rejecting them.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Sequence

from estnltk_neural.taggers.neural_morph.llm_generator_based.llm_provider import (
    LLMProvider,
)
from estnltk_neural.taggers.neural_morph.llm_generator_based.word_replacement_generator import (
    Replacement,
    mark_target_word,
)

DEFAULT_FILTER_SYSTEM_PROMPT = """You are an Estonian sentence rewriting assistant.
Your task is to select the best candidates from the provided list to replace the marked word <...> in the sentence.

Rules:
- Do not invent new candidates.
- Preserve the word's tense, number, case agreement, punctuation, and capitalisation.
- Return candidates that fit naturally and grammatically in one of these cases: nominative, genitive, partitive, or additive/illative.
- For proper names, keep only proper-name candidates that fit the same grammatical context.
- If fewer valid candidates exist than requested, return as many as possible.
- Order candidates from best to worst fit.
- Do not repeat the original word unless it is the only valid option.
"""


class WordFilter(ABC):
    """Removes candidate word forms that do not fit the sentence."""

    @abstractmethod
    def filter(
        self, sentence: Sequence[str], loc: int, words: List[Replacement]
    ) -> List[Replacement]:
        """Return the subset of ``words`` that fits the sentence at ``loc``.

        Scores are carried through unchanged from the input, so a filter narrows
        the candidate set without reweighting it.
        """


class LLMWordFilter(WordFilter):
    """Asks a language model which of the given candidates fit."""

    def __init__(
        self,
        provider: LLMProvider,
        keep_n: int = 5,
        system_prompt: str = DEFAULT_FILTER_SYSTEM_PROMPT,
        max_tokens: int = 512,
    ):
        """Initialise the filter.

        Parameters
        ----------
        keep_n:
            Upper bound on how many candidates to keep. The model may return
            fewer, and the schema allows that: forcing it to return exactly
            ``keep_n`` would make it pad the list with forms it just rejected.
        """
        self.provider = provider
        self.keep_n = keep_n
        self.system_prompt = system_prompt
        self.max_tokens = max_tokens

    def _schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "candidates": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 0,
                    "maxItems": self.keep_n,
                }
            },
            "required": ["candidates"],
            "additionalProperties": False,
        }

    def filter(
        self, sentence: Sequence[str], loc: int, words: List[Replacement]
    ) -> List[Replacement]:
        if not words:
            return []

        offered = [word for word, _ in words]
        user = (
            f"Sentence: {mark_target_word(sentence, loc)}\n"
            f"Candidates: {', '.join(offered)}\n"
            f"Select at most {self.keep_n}."
        )
        parsed = self.provider.complete_json(
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user},
            ],
            schema=self._schema(),
            schema_name="candidates",
            max_tokens=self.max_tokens,
        )
        kept = parsed.get("candidates")
        if not isinstance(kept, list):
            raise ValueError(
                f"(!) Expected a 'candidates' list in the response, got "
                f"{type(kept).__name__}."
            )

        # Keep the caller's scores, and ignore anything the model invented: the
        # prompt forbids new candidates, but a filter that silently accepted them
        # would turn a prompt violation into a wrong form distribution.
        scores = {word: score for word, score in words}
        return [(word, scores[word]) for word in map(str, kept) if word in scores]
