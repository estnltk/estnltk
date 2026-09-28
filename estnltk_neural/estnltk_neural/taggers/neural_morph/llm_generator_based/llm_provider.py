"""Provider adapters for LLM-based word replacement generation.

The adapter is the only place that knows how a particular provider is called and
how it is asked for structured output. Everything above it works with a plain
``dict`` parsed from the model's JSON response, so adding a provider means adding
one subclass rather than touching the generators or the retagger.

Only Azure OpenAI is implemented. Other providers differ mainly in how a JSON
schema is requested -- OpenAI takes a ``json_schema`` response format, Anthropic
expresses it as a tool definition, Gemini as a ``response_schema`` -- which is
exactly the difference this class is meant to absorb.
"""

from __future__ import annotations

import json
import os
import random
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class LLMBudgetExceededError(Exception):
    """Raised when the estimated spend for a run passes its ceiling."""


class LLMProvider(ABC):
    """Asks a language model for a JSON object matching a schema."""

    @abstractmethod
    def complete_json(
        self,
        messages: List[Dict[str, str]],
        schema: Dict[str, Any],
        schema_name: str = "response",
        max_tokens: int = 512,
    ) -> Dict[str, Any]:
        """Return the parsed JSON object the model produced.

        Parameters
        ----------
        messages:
            Chat messages, each ``{'role': ..., 'content': ...}``.
        schema:
            JSON schema the response must satisfy.
        schema_name:
            Name for the schema, as some providers require one.
        max_tokens:
            Ceiling on the response length.

        Raises
        ------
        ValueError
            If the model's response is not JSON matching the schema. Failing
            here rather than further along matters: a malformed response would
            otherwise surface as a puzzling morphological result much later.
        """

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Identifier of the model being called, for logging and cost lookup."""


class AzureOpenAIProvider(LLMProvider):
    """Azure OpenAI chat completions with a strict JSON schema response.

    Carries the request pacing, retries and spend ceiling that the experiments
    this component came from needed in practice: a corpus-sized run makes one
    request per word, so a rate limit or a silent cost blow-up is a question of
    when rather than whether.
    """

    # Published per-token prices, only used for the spend estimate.
    DEFAULT_COSTS = {
        "gpt-4o": {"input": 2.50 / 1_000_000, "output": 10.00 / 1_000_000},
    }

    def __init__(
        self,
        deployment: str = "EstNLTK-gpt-4o",
        endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        api_version: str = "2024-12-01-preview",
        model_name: str = "gpt-4o",
        requests_per_minute: int = 1080,
        jitter_seconds: float = 0.1,
        max_attempts: int = 5,
        backoff_base_seconds: float = 2.0,
        max_cost_usd: Optional[float] = None,
        costs: Optional[Dict[str, Dict[str, float]]] = None,
    ):
        """Initialise the adapter.

        Parameters
        ----------
        deployment:
            Azure deployment name, which is what the API calls a model.
        endpoint, api_key:
            Read from ``AZURE_ENDPOINT`` and ``OPENAI_API_KEY`` when not given.
        requests_per_minute:
            Used to space requests out. The default matches the rate limit the
            experiments ran against.
        max_attempts:
            Attempts per request, with exponential backoff between them.
        max_cost_usd:
            Stop the run once the estimated spend passes this. ``None`` disables
            the ceiling, which is reasonable interactively and not for a corpus.
        """
        endpoint = endpoint or os.getenv("AZURE_ENDPOINT")
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not endpoint or not api_key:
            raise ValueError(
                "(!) Azure OpenAI needs an endpoint and an API key. Pass them "
                "explicitly, or set AZURE_ENDPOINT and OPENAI_API_KEY."
            )

        try:
            from openai import AzureOpenAI
        except ImportError as exc:
            raise ImportError(
                "(!) The 'openai' package is required for AzureOpenAIProvider. "
                "Install it with: pip install openai"
            ) from exc

        self._client = AzureOpenAI(
            api_version=api_version, azure_endpoint=endpoint, api_key=api_key
        )
        self._deployment = deployment
        self._model_name = model_name
        self._min_interval = 60.0 / requests_per_minute if requests_per_minute else 0.0
        self._jitter = jitter_seconds
        self._max_attempts = max_attempts
        self._backoff_base = backoff_base_seconds
        self._max_cost = max_cost_usd
        self._costs = costs or self.DEFAULT_COSTS
        self._spent_usd = 0.0
        self._last_request_at = 0.0

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def spent_usd(self) -> float:
        """Estimated spend so far, from the token counts the API reports."""
        return self._spent_usd

    def _pace(self) -> None:
        """Space requests out so a long run does not trip the rate limit."""
        if self._min_interval <= 0:
            return
        elapsed = time.monotonic() - self._last_request_at
        wait = self._min_interval - elapsed
        if wait > 0:
            time.sleep(wait + random.uniform(0, self._jitter))
        self._last_request_at = time.monotonic()

    def _record_cost(self, response: Any) -> None:
        """Add one response's estimated cost, and stop if the ceiling is passed."""
        usage = getattr(response, "usage", None)
        if usage is None:
            return
        prices = self._costs.get(self._model_name)
        if prices is None:
            return
        self._spent_usd += (
            getattr(usage, "prompt_tokens", 0) * prices["input"]
            + getattr(usage, "completion_tokens", 0) * prices["output"]
        )
        if self._max_cost is not None and self._spent_usd > self._max_cost:
            raise LLMBudgetExceededError(
                f"(!) Estimated spend ${self._spent_usd:.4f} passed the "
                f"${self._max_cost:.2f} ceiling. Raise max_cost_usd to continue."
            )

    def complete_json(
        self,
        messages: List[Dict[str, str]],
        schema: Dict[str, Any],
        schema_name: str = "response",
        max_tokens: int = 512,
    ) -> Dict[str, Any]:
        response_format = {
            "type": "json_schema",
            "json_schema": {"name": schema_name, "strict": True, "schema": schema},
        }

        last_error: Optional[Exception] = None
        for attempt in range(self._max_attempts):
            if attempt:
                # Exponential backoff. Retries cover transient faults: rate
                # limiting, a dropped connection, a content filter hiccup.
                time.sleep(self._backoff_base**attempt + random.uniform(0, self._jitter))
            self._pace()
            try:
                response = self._client.chat.completions.create(
                    messages=messages,
                    model=self._deployment,
                    response_format=response_format,
                    max_completion_tokens=max_tokens,
                    top_p=0.95,
                )
            except LLMBudgetExceededError:
                raise
            except Exception as exc:  # provider SDKs raise a wide range here
                last_error = exc
                continue

            self._record_cost(response)
            content = response.choices[0].message.content
            if not content:
                last_error = ValueError("empty response content")
                continue
            try:
                parsed = json.loads(content)
            except json.JSONDecodeError as exc:
                # With strict schema output this should not happen, so treat it
                # as a contract breach rather than something to paper over.
                last_error = ValueError(f"response was not JSON: {exc}")
                continue
            if not isinstance(parsed, dict):
                last_error = ValueError(
                    f"expected a JSON object, got {type(parsed).__name__}"
                )
                continue
            return parsed

        raise ValueError(
            f"(!) Could not get a valid JSON response after "
            f"{self._max_attempts} attempts. Last error: {last_error}"
        )
