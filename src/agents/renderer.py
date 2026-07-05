from __future__ import annotations

import os
import subprocess
import time

from src.schemas import RenderResult
from src.state import PipelineState

REMOTION_PROJECT_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "remotion"
)
OUTPUT_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "sample_output"
)


def render_video(composition_id: str = "FotoOwlReel") -> RenderResult:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    output_path = os.path.join(OUTPUT_DIR, f"{composition_id}.mp4")
    start = time.time()

    try:
        result = subprocess.run(
            [
                "npx",
                "remotion",
                "render",
                "src/index.ts",
                composition_id,
                output_path,
            ],
            cwd=REMOTION_PROJECT_DIR,
            capture_output=True,
            text=True,
            timeout=600,
            shell=True,
        )

        if result.returncode != 0:
            return RenderResult(
                success=False,
                error_message=(result.stdout + result.stderr)[-3000:],
            )

        return RenderResult(
            success=True,
            output_path=output_path,
            duration_seconds=time.time() - start,
        )

    except Exception as e:
        return RenderResult(
            success=False,
            error_message=str(e),
        )


def renderer_node(state: PipelineState) -> dict:
    result = render_video(state["script"].composition_id)

    return {
        "render_result": result,
        "node_trace": state.get("node_trace", []) + ["renderer"],
    }