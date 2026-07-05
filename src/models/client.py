"""
Thin wrapper around the Gemini API (google-genai SDK) that forces
structured JSON output validated against a Pydantic model, so no agent
ever regex-parses free text.

Every agent module imports `structured_call` from here and NOTHING ELSE
talks to the network. That single choke point is what makes the whole
pipeline mockable in tests without API keys (see tests/mocks.py - we
monkeypatch this one function) and is also what made this file the only
one that needed to change for the Anthropic -> Gemini migration.

Public API is intentionally unchanged from the Anthropic version so every
agent works without modification:
    _get_client()
    structured_call(model, system, user_content, response_model, max_tokens)
    image_to_content_block(path)
"""
from __future__ import annotations

import base64
import json
import os
from typing import Type, TypeVar

from google import genai
from google.genai import types
from google.genai import errors as genai_errors
from pydantic import BaseModel, ValidationError

from src.models.exceptions import (
    LLMAPIError,
    LLMRateLimitError,
    LLMSafetyBlockError,
    LLMEmptyResponseError,
    LLMInvalidJSONError,
)

T = TypeVar("T", bound=BaseModel)

_client: genai.Client | None = None

# Finish reasons that mean "the model refused / was blocked", as opposed to
# a normal stop or a length cutoff. Anything in here is a safety block, not
# a retryable API error.
_SAFETY_FINISH_REASONS = {
    types.FinishReason.SAFETY,
    types.FinishReason.PROHIBITED_CONTENT,
    types.FinishReason.BLOCKLIST,
    types.FinishReason.SPII,
    types.FinishReason.RECITATION,
    types.FinishReason.IMAGE_SAFETY,
    types.FinishReason.IMAGE_PROHIBITED_CONTENT,
    types.FinishReason.IMAGE_RECITATION,
}


def _get_client() -> genai.Client:
    """Lazily builds and caches the module-level Gemini client, same
    lazy-singleton pattern the Anthropic version used."""
    global _client
    if _client is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise LLMAPIError(
                "GEMINI_API_KEY is not set. Copy .env.example to .env and "
                "add your key, or export it in your shell."
            )
        _client = genai.Client(api_key=api_key)
    return _client


def _image_block_to_part(block: dict) -> types.Part:
    """Converts our internal image-block dict (see image_to_content_block)
    into a genai Part carrying inline image bytes."""
    source = block["source"]
    raw_bytes = base64.b64decode(source["data"])
    return types.Part.from_bytes(data=raw_bytes, mime_type=source["media_type"])


def _build_contents(user_content: str | list[dict]) -> str | list[types.Part]:
    """Translates the Anthropic-shaped `user_content` (a plain string, or a
    list of {"type": "image"|"text", ...} blocks) into what genai's
    generate_content expects. Agents never see this - they keep building
    content the same way they always did."""
    if isinstance(user_content, str):
        return user_content

    parts: list[types.Part] = []
    for block in user_content:
        block_type = block.get("type")
        if block_type == "image":
            parts.append(_image_block_to_part(block))
        elif block_type == "text":
            parts.append(types.Part.from_text(text=block["text"]))
        else:
            raise LLMAPIError(f"Unsupported content block type: {block_type!r}")
    return parts


def _check_for_safety_block(response) -> None:
    """Raises LLMSafetyBlockError if Gemini blocked the prompt outright, or
    if the returned candidate was cut off for safety reasons."""
    prompt_feedback = getattr(response, "prompt_feedback", None)
    block_reason = getattr(prompt_feedback, "block_reason", None)
    if block_reason and block_reason != types.BlockedReason.BLOCKED_REASON_UNSPECIFIED:
        raise LLMSafetyBlockError(f"Prompt was blocked by Gemini: {block_reason}")

    candidates = getattr(response, "candidates", None) or []
    for candidate in candidates:
        finish_reason = getattr(candidate, "finish_reason", None)
        if finish_reason in _SAFETY_FINISH_REASONS:
            raise LLMSafetyBlockError(
                f"Gemini response was blocked/withheld (finish_reason={finish_reason})"
            )


def structured_call(
    model: str,
    system: str,
    user_content: str | list[dict],
    response_model: Type[T],
    max_tokens: int = 32768,
) -> T:
    """
    Calls Gemini in JSON mode with `response_schema` set to the given
    Pydantic model, then validates the returned JSON against that same
    model and returns the parsed object - functionally identical contract
    to the Anthropic tool-calling version this replaces.
    """
    client = _get_client()
    contents = _build_contents(user_content)

    config = types.GenerateContentConfig(
        system_instruction=system,
        response_mime_type="application/json",
        response_schema=response_model,
        max_output_tokens=max_tokens,
    )

    try:
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=config,
        )
    except genai_errors.ClientError as e:
        status_code = getattr(e, "code", None) or getattr(e, "status_code", None)
        if status_code == 429:
            raise LLMRateLimitError(f"Gemini rate limit hit: {e}") from e
        raise LLMAPIError(f"Gemini rejected the request ({status_code}): {e}") from e
    except genai_errors.ServerError as e:
        raise LLMAPIError(f"Gemini server error: {e}") from e
    except genai_errors.APIError as e:
        raise LLMAPIError(f"Gemini API error: {e}") from e

    _check_for_safety_block(response)

    raw_text = getattr(response, "text", None)

    if raw_text is None:
        raise LLMEmptyResponseError(
            f"Gemini returned no text content for model={model!r}."
        )

    raw_text = raw_text.strip()

    if raw_text.startswith("```"):
        raw_text = raw_text.split("\n", 1)[1]
        raw_text = raw_text.rsplit("```", 1)[0].strip()

    print("=" * 80)
    print(raw_text)
    print("=" * 80)
    print("Response Length:", len(raw_text))

    if not raw_text:
        raise LLMEmptyResponseError(
            f"Gemini returned no text content for model={model!r}. "
            f"Full response: {response!r}"
        )

    try:
        parsed_json = json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise LLMInvalidJSONError(
            f"Gemini response was not valid JSON for model={model!r}: {e}\n"
            f"Raw text: {raw_text[:500]}"
        ) from e

    try:
        return response_model.model_validate(parsed_json)
    except ValidationError as e:
        raise LLMInvalidJSONError(
            f"Gemini's JSON did not match {response_model.__name__} schema: {e}\n"
            f"Raw JSON: {parsed_json}"
        ) from e


def image_to_content_block(path: str) -> dict:
    """Reads an image off disk into the same block shape the rest of the
    pipeline has always used: {"type": "image", "source": {...}}. This
    keeps every agent (image_analyser.py in particular) unchanged - only
    _build_contents(), above, knows this needs to become a genai Part."""
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    ext = path.rsplit(".", 1)[-1].lower()
    media_type = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"
    return {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": data}}