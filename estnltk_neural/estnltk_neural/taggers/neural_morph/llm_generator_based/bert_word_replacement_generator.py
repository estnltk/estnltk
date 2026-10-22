"""Uses Bert model's masked language modelling to generate words that could 
replace a given word in a sentence. 

The point of generating replacements is indirect morphological analysis. Asking a 
language model for a word's case directly has not worked well; asking it for words 
that would fit the same slot, and then analysing those with Vabamorf, turns the 
question into one the model answers well. See ``WordReplacementAnalyzer``. 
"""
from typing import List, Sequence, Optional, Dict

from copy import deepcopy

from estnltk_neural.taggers.neural_morph.llm_generator_based.word_replacement_generator import Replacement
from estnltk_neural.taggers.neural_morph.llm_generator_based.word_replacement_generator import WordReplacementGenerator


class BertWordReplacementGenerator(WordReplacementGenerator):
    """Asks Bert language model for word replacements in sentence via ``AutoModelForMaskedLM``.
    """

    # Revisions pinned for specific HuggingFace models. Used whenever the
    # caller does not pass model_revision explicitly.
    # EMBEDDIA/est-roberta: the model at the default location (main) is
    # malfunctioning; this commit contains the fix.
    # (this logic was provided by Claude Opus 5.5)
    DEFAULT_MODEL_REVISIONS: Dict[str, str] = {
        'EMBEDDIA/est-roberta': 'eb8131e56a9a92a78187d8cbf50c8258bcb253b9',
    }

    def __init__(
        self, 
        model_name: str = 'EMBEDDIA/est-roberta', 
        model_revision: Optional[str] = None,
        n_candidates: int = 10,
        device: str = "cpu"
    ):
        """Initialise the Bert based word replacement generator.

        Parameters
        ----------
        model_name: str
            Full path to a directory containing a Bert model or a repo_id of a model 
            available from huggingface.com. 
            Default: 'EMBEDDIA/est-roberta'
        model_revision: str
            Model version, branch name or repository commit hash. Optional. Only works
            if model_name corresponds to a repo_id of a model available from
            huggingface.com. If not given, a known working revision is looked up from
            BertWordReplacementGenerator.DEFAULT_MODEL_REVISIONS; for models not listed 
            there, the latest version (main) is used. To use the latest version of a 
            listed model, pass 'main'.
            Default: None
        n_candidates: int
            How many replacements will be generated for the word in the sentence. Default: 10.
        device: int
            The device argument to be passed to transformers.pipeline. Optional, defaults to -1. 
            According to transformers' documentation: "Device ordinal for CPU/GPU supports. Setting 
            this to -1 will leverage CPU, a positive will run the model on the associated CUDA 
            device id. You can pass native `torch.device` or a `str` too."
        """
        from transformers import pipeline
        from transformers import AutoModelForMaskedLM, AutoTokenizer
        if model_revision is None:
            model_revision = self.DEFAULT_MODEL_REVISIONS.get(model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name, revision=model_revision)
        model = AutoModelForMaskedLM.from_pretrained(model_name, return_dict=True, revision=model_revision)
        self.mask_filler = pipeline("fill-mask", model=model, tokenizer=tokenizer, device=device)
        self.mask = self.mask_filler.tokenizer.mask_token
        assert n_candidates > 0
        self.n_candidates = n_candidates


    def generate(self, sentence: Sequence[str], loc: int) -> List[Replacement]:
        assert loc >= 0 and loc < len(sentence), \
            f'(!) Index loc={loc} is out of range (0, {len(sentence)-1})'
        assert self.mask not in sentence, \
            f'(!) Unexpectedly, the mask token "{self.mask}" is in {sentence!r}'
        sentence_text = deepcopy(sentence)
        sentence_text[loc] = self.mask
        results = self.mask_filler(' '.join(sentence_text), top_k=self.n_candidates)
        candidates = []
        for result_dict in sorted(results, key=lambda x:x['score'], reverse=True):
            assert 'score' in result_dict
            assert 'token_str' in result_dict
            candidates.append( (result_dict['token_str'], result_dict['score']) )
        return candidates
