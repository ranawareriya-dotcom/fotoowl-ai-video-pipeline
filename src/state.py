"""
The single shared state object every LangGraph node reads from and writes to.

Design note: we keep this flat and typed (TypedDict) rather than nested,
because LangGraph merges partial updates per-key. Nesting mutable lists
inside a single key makes partial updates from parallel branches unsafe.
"""
from __future__ import annotations
from typing import Optional, TypedDict
from src.schemas import (
    VideoIntent,
    ImageAnalysis,
    Storyboard,
    RemotionScript,
    CompileResult,
    RenderResult,
    PipelineFailure,
)


class PipelineState(TypedDict, total=False):
    # inputs
    image_folder: str
    user_prompt: str

    # stage outputs (each populated by one node)
    intent: VideoIntent
    image_analyses: list[ImageAnalysis]
    selected_images: list[str]          # subset chosen for the reel
    storyboard: Storyboard
    script: RemotionScript

    # compile/fix loop
    compile_result: CompileResult
    fix_attempts: int
    max_fix_attempts: int

    # terminal states
    render_result: RenderResult
    failure: PipelineFailure

    # trace / observability (dumped to sample_output/pipeline_state.json)
    node_trace: list[str]
