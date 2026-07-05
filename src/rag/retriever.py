from __future__ import annotations
from src.rag.vectorstore import get_client, seed_collections
from src.schemas import VideoIntent, CompileError


def _client():
    c = get_client()
    seed_collections(c)
    return c


def retrieve_style_context(intent: VideoIntent, n_results: int = 4) -> list[str]:
    """Storyboard Writer calls this before generating the storyboard.
    Query is built from the intent object, not the raw prompt -
    downstream agents read structured intent only."""
    col = _client().get_collection("style_guides")
    query = (f"{intent.visual_style.value} style pacing {intent.pacing.value}, "
             f"caption tone {intent.caption_tone.value}, "
             f"transitions {intent.transition_preference.value}")
    results = col.query(query_texts=[query], n_results=n_results)
    return results["documents"][0]


def retrieve_remotion_api_context(intent: VideoIntent, n_results: int = 5) -> list[str]:
    """Script Generator calls this before writing code."""
    col = _client().get_collection("remotion_snippets")
    query = f"remotion components for {intent.transition_preference.value} transitions and captions"
    results = col.query(query_texts=[query], n_results=n_results)
    return results["documents"][0]


def retrieve_fix_context(error: CompileError, n_results: int = 2) -> list[str]:
    """Compiler & Fixer calls this on retry, targeting the specific error type
    rather than re-fetching generic Remotion docs.

    Note: we bias the query text with the error_type token rather than using
    a metadata `where` filter, because Chroma's default metadata filtering
    doesn't do substring/contains matching on comma-joined string fields
    reliably across versions. A cleaner follow-up (documented in README's
    "known limitations") would store error_types as a proper multi-value
    field or use a separate small collection per error type."""
    col = _client().get_collection("remotion_snippets")
    query = f"{error.error_type} {error.error_type} error fix: {error.message}"
    results = col.query(query_texts=[query], n_results=n_results)
    return results["documents"][0]
