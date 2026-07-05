from __future__ import annotations

import os

from src.schemas import ImageAnalysis, ImageAnalysisBatch, VideoIntent
from src.models.client import structured_call, image_to_content_block
from src.models.router import NODE_MODEL_MAP
from src.state import PipelineState

SYSTEM = """You analyse event photos for a personalised video reel pipeline.
For each image, describe it, list detected subjects, dominant colors,
estimate the emotional tone, score composition quality 0-1, and suggest
which narrative role it best serves (opening / climax / closing / filler).

Be honest about composition_quality - blurry or awkwardly framed images
should score low so the storyboard writer can deprioritize them.
"""


def analyse_images(image_folder: str, intent: VideoIntent) -> list[ImageAnalysis]:
    files = sorted(
        f for f in os.listdir(image_folder)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    )

    print(f"Analysing {len(files)} images in one Gemini request...")

    contents = []

    # Send filename followed by image
    for file in files:
        contents.append(
            {
                "type": "text",
                "text": f"Filename: {file}",
            }
        )

        contents.append(
            image_to_content_block(
                os.path.join(image_folder, file)
            )
        )

    contents.append(
        {
            "type": "text",
            "text": f"""
You have been given {len(files)} images.

Analyse EVERY image.

Return a JSON object:

{{
  "analyses": [
    ...
  ]
}}

Rules:

- Return EXACTLY {len(files)} ImageAnalysis objects.
- One object per image.
- Preserve the same order as the uploaded images.
- The file_name field MUST exactly match the filename provided before each image.
- NEVER invent filenames.
- NEVER rename images.

Visual style:
{intent.visual_style.value}
""",
        }
    )

    result = structured_call(
        model=NODE_MODEL_MAP["image_analyser"].value,
        system=SYSTEM,
        user_content=contents,
        response_model=ImageAnalysisBatch,
    )

    return result.analyses


def image_analyser_node(state: PipelineState) -> dict:
    analyses = analyse_images(
        image_folder=state["image_folder"],
        intent=state["intent"],
    )

    return {
        "image_analyses": analyses,
    }
 