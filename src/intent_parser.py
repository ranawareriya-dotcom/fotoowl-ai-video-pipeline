from __future__ import annotations
from src.schemas import VideoIntent
from src.models.client import structured_call
from src.models.router import NODE_MODEL_MAP

SYSTEM = """You convert a free-text video style brief into a structured VideoIntent.
Infer sensible values for every field even if the prompt doesn't mention it
explicitly (e.g. a wedding-themed prompt with no stated pacing -> slow).
Always fill target_duration_seconds with a reasonable value for a short
personalised event reel (typically 20-60s)."""


def parse_intent(user_prompt: str) -> VideoIntent:
    return structured_call(
        model=NODE_MODEL_MAP["intent_parser"].value,
        system=SYSTEM,
        user_content=f"User prompt: {user_prompt!r}",
        response_model=VideoIntent,
    )
