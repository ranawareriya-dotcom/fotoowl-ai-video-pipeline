"""
Entry point.

Usage:
    python main.py --images ./images --prompt "Cinematic wedding reel, slow and emotional, warm tones, minimal text"

Requires GEMINI_API_KEY in the environment (see .env.example).
Dumps the full final pipeline state to sample_output/pipeline_state.json
so the run can be reviewed without re-running it.
"""
from __future__ import annotations
import argparse
import json
import os
from dotenv import load_dotenv

from src.graph import run_pipeline, export_graph_mermaid


def main():
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--images", default="images", help="Folder of input images")
    parser.add_argument("--prompt", required=True, help="Free-text style brief")
    parser.add_argument("--max-fix-attempts", type=int, default=3)
    parser.add_argument("--out", default="sample_output/pipeline_state.json")
    args = parser.parse_args()

    export_graph_mermaid("sample_output/graph.mmd")

    final_state = run_pipeline(args.images, args.prompt, args.max_fix_attempts)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(_to_jsonable(final_state), f, indent=2, default=str)

    if "failure" in final_state:
        print("Pipeline ended in structured failure:")
        print(final_state["failure"].model_dump_json(indent=2))
    else:
        print("Pipeline succeeded:")
        print(final_state["render_result"].model_dump_json(indent=2))


def _to_jsonable(state: dict) -> dict:
    out = {}
    for k, v in state.items():
        out[k] = v.model_dump() if hasattr(v, "model_dump") else v
    return out


if __name__ == "__main__":
    main()
