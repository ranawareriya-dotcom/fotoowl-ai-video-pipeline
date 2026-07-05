from __future__ import annotations
from src.schemas import Storyboard, VideoIntent, ImageAnalysis
from src.models.client import structured_call
from src.models.router import NODE_MODEL_MAP
from src.rag.retriever import retrieve_style_context
from src.state import PipelineState

SYSTEM_TEMPLATE = """You are the Storyboard Writer. You sequence a subset of
analysed images into a narrative arc for a personalised event video.

Rules:
- You do not need to use every image. Prefer higher composition_quality
  images and a coherent narrative_arc over including everything.
- Every scene's duration, caption tone, and transition MUST reflect the
  VideoIntent below - do not invent your own style.
- Use the retrieved style guide context to inform concrete choices
  (e.g. exact seconds-per-scene, caption phrasing register, transition type).

VideoIntent:
{intent}

Retrieved style guide context:
{style_context}
"""


def write_storyboard(intent: VideoIntent, analyses: list[ImageAnalysis]) -> Storyboard:
    style_context = retrieve_style_context(intent)
    system = SYSTEM_TEMPLATE.format(
        intent=intent.model_dump_json(indent=2),
        style_context="\n---\n".join(style_context),
    )
    images_summary = "\n".join(
        f"- {a.file_name}: {a.description} | subjects={a.detected_subjects} "
        f"| emotion={a.estimated_emotion} | quality={a.composition_quality} "
        f"| role={a.suggested_role}"
        for a in analyses
    )
    return structured_call(
        model=NODE_MODEL_MAP["storyboard_writer"].value,
        system=system,
        user_content=f"Analysed images:\n{images_summary}",
        response_model=Storyboard,
    )


def storyboard_writer_node(state: PipelineState) -> dict:
    storyboard = write_storyboard(state["intent"], state["image_analyses"])
    return {
        "storyboard": storyboard,
        "selected_images": [s.file_name for s in storyboard.scenes],
        "node_trace": state.get("node_trace", []) + ["storyboard_writer"],
    }
