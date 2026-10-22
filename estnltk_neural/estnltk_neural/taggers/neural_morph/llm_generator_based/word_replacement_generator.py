"""Interface for generating words that could replace a given word in a sentence. 

The point of generating replacements is indirect morphological analysis. Asking a
language model for a word's case directly has not worked well; asking it for words
that would fit the same slot, and then analysing those with Vabamorf, turns the
question into one the model answers well. See ``WordReplacementAnalyzer``.

A generator returns ``(word, score)`` pairs. The score is a probability where the
underlying model exposes one and ``None`` where it does not, which is the case for
a chat model asked for a list of words.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Sequence, Tuple

# Replacement = (word form, score or None)
Replacement = Tuple[str, Optional[float]]


class WordReplacementGenerator(ABC):
    """Proposes word forms that could replace the word at a given position."""

    @abstractmethod
    def generate(self, sentence: Sequence[str], loc: int) -> List[Replacement]:
        """Return candidate replacements for the token at ``loc``.

        Parameters
        ----------
        sentence:
            The sentence as a list of tokens.
        loc:
            Index of the token to replace.

        Returns
        -------
        list of (str, float or None)
            Candidate word forms, with a score where the model provides one.
        """

