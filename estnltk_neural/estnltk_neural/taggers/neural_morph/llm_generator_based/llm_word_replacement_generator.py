"""Uses LLM prompting to generate words that could replace a given word in a sentence. 

The point of generating replacements is indirect morphological analysis. Asking a
language model for a word's case directly has not worked well; asking it for words
that would fit the same slot, and then analysing those with Vabamorf, turns the
question into one the model answers well. See ``WordReplacementAnalyzer``.
"""

from typing import Any, Dict, List, Optional, Sequence

from estnltk_neural.common import LLMProvider
from estnltk_neural.taggers.neural_morph.llm_generator_based.word_replacement_generator import Replacement
from estnltk_neural.taggers.neural_morph.llm_generator_based.word_replacement_generator import WordReplacementGenerator


# The prompt the thesis experiments used, kept as-is: the candidate quality this
# component depends on was measured with this wording.
DEFAULT_SYSTEM_PROMPT = """You are an Estonian sentence rewriting assistant.

Replace exactly one marked token in angle brackets <...> with a context-appropriate alternative.

Rules:
- Preserve tense, number, case, agreement, capitalisation, punctuation, and word order as much as possible.
- Infer the token's grammatical role and morphology from the sentence context.
- Generate 10 alternatives that fit the context and use only these cases: nominative, genitive, partitive, or additive/illative (both fit the same role in this task).
- If the token is a proper name, replace it with another plausible proper name that still fits the required case.
- Do not repeat the original token unless it is the only valid option.
"""

# A worked example, which anchors the output format and the kind of alternative
# wanted. Without it the model tends to drift towards synonyms of the whole
# phrase rather than single words in the same case.
DEFAULT_ONE_SHOT_USER = "Sentence: Ma näen <maja>."
DEFAULT_ONE_SHOT_CANDIDATES = [
    "ehitist", "hoonet", "elamut", "rajatist", "korterit",
    "kodu", "eluaset", "hoonestust", "majapidamist", "maja",
]


def mark_target_word(sentence: Sequence[str], loc: int) -> str:
    """Join tokens into a sentence with the token at ``loc`` in angle brackets.

    Raises
    ------
    IndexError
        If ``loc`` is not a valid index into ``sentence``.
    """
    if not 0 <= loc < len(sentence):
        raise IndexError(
            f"(!) loc {loc} is out of range for a sentence of {len(sentence)} tokens."
        )
    marked = list(sentence)
    marked[loc] = f"<{marked[loc]}>"
    return " ".join(marked)


class LLMWordReplacementGenerator(WordReplacementGenerator):
    """Asks a language model for replacements, via an ``LLMProvider``.

    Scores are always ``None``: a chat model returns a list of words with no
    probabilities attached. Callers that need weights should treat the candidates
    as equally likely, which is what the thesis experiments did.
    """

    def __init__(
        self,
        provider: LLMProvider,
        n_candidates: int = 10,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        one_shot_user: Optional[str] = DEFAULT_ONE_SHOT_USER,
        one_shot_candidates: Optional[List[str]] = None,
        max_tokens: int = 512,
    ):
        """Initialise the generator.

        Parameters
        ----------
        provider:
            The adapter that performs the call.
        n_candidates:
            How many replacements to ask for. The schema requires exactly this
            many, so the model cannot quietly return fewer.
        one_shot_user, one_shot_candidates:
            A worked example prepended to the conversation. Pass ``None`` for
            ``one_shot_user`` to leave it out.
        """
        self.provider = provider
        self.n_candidates = n_candidates
        self.system_prompt = system_prompt
        self.one_shot_user = one_shot_user
        self.one_shot_candidates = (
            one_shot_candidates
            if one_shot_candidates is not None
            else DEFAULT_ONE_SHOT_CANDIDATES
        )
        self.max_tokens = max_tokens

    @property
    def response_schema(self) -> Dict[str, Any]:
        """JSON schema the provider must hold the response to."""
        return {
            "type": "object",
            "properties": {
                "candidates": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": self.n_candidates,
                    "maxItems": self.n_candidates,
                }
            },
            "required": ["candidates"],
            "additionalProperties": False,
        }

    def _build_messages(self, sentence: Sequence[str], loc: int) -> List[Dict[str, str]]:
        import json

        messages = [{"role": "system", "content": self.system_prompt}]
        if self.one_shot_user is not None:
            messages.append({"role": "user", "content": self.one_shot_user})
            messages.append(
                {
                    "role": "assistant",
                    "content": json.dumps(
                        {"candidates": self.one_shot_candidates}, ensure_ascii=False
                    ),
                }
            )
        messages.append(
            {"role": "user", "content": f"Sentence: {mark_target_word(sentence, loc)}"}
        )
        return messages

    def generate(self, sentence: Sequence[str], loc: int) -> List[Replacement]:
        parsed = self.provider.complete_json(
            messages=self._build_messages(sentence, loc),
            schema=self.response_schema,
            schema_name="candidates",
            max_tokens=self.max_tokens,
        )
        candidates = parsed.get("candidates")
        if not isinstance(candidates, list):
            raise ValueError(
                f"(!) Expected a 'candidates' list in the response, got "
                f"{type(candidates).__name__}. The provider should have held the "
                f"response to the schema."
            )
        return [(str(word), None) for word in candidates if str(word).strip()]
