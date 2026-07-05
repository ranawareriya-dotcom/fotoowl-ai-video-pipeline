"""
Exception hierarchy for the Gemini-backed LLM client.

Every failure mode the pipeline needs to handle explicitly (rate limits,
safety blocks, malformed/empty responses, generic API errors) gets its own
subclass so callers - and the LangGraph retry loop - can distinguish them
instead of catching a bare Exception.
"""
from __future__ import annotations


class LLMClientError(Exception):
    """Base class for every error this client layer raises."""


class LLMAPIError(LLMClientError):
    """Wraps a generic Gemini API failure (network, 5xx, malformed request)."""


class LLMRateLimitError(LLMClientError):
    """Raised on HTTP 429 / RESOURCE_EXHAUSTED responses from Gemini."""


class LLMSafetyBlockError(LLMClientError):
    """Raised when Gemini blocks a prompt or response on safety grounds
    (prompt_feedback.block_reason, or a candidate's finish_reason indicating
    SAFETY / PROHIBITED_CONTENT / BLOCKLIST / SPII / recitation, etc.)."""


class LLMEmptyResponseError(LLMClientError):
    """Raised when Gemini returns no candidates or no text content at all."""


class LLMInvalidJSONError(LLMClientError):
    """Raised when the model's response text isn't valid JSON, or doesn't
    validate against the expected Pydantic response_model."""
