"""
Generates sample_output/ contents using the mock fixtures, so the repo
ships with example artifacts even without spending API credits. When run
for real (via main.py with a real key), main.py overwrites these with
genuine model output in the same shape.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tests.mocks import make_mock_intent, make_mock_analyses, make_mock_storyboard, make_mock_script
from src.schemas import CompileResult, RenderResult, PipelineFailure, CompileError

OUT = os.path.join(os.path.dirname(__file__), "..", "sample_output")
os.makedirs(OUT, exist_ok=True)

for style in ("cinematic", "upbeat"):
    intent = make_mock_intent(style)
    analyses = make_mock_analyses(8)
    storyboard = make_mock_storyboard(intent, analyses)
    script = make_mock_script(valid=True)

    with open(os.path.join(OUT, f"intent_{style}.json"), "w") as f:
        f.write(intent.model_dump_json(indent=2))
    with open(os.path.join(OUT, f"storyboard_{style}.json"), "w") as f:
        f.write(storyboard.model_dump_json(indent=2))
    with open(os.path.join(OUT, f"remotion_script_{style}.tsx"), "w") as f:
        f.write(script.typescript_code)

# a full pipeline_state.json for the cinematic run, success path
intent = make_mock_intent("cinematic")
analyses = make_mock_analyses(8)
storyboard = make_mock_storyboard(intent, analyses)
script = make_mock_script(valid=True)
compile_result = CompileResult(success=True, attempt_number=1, stdout="tsc: no errors")
render_result = RenderResult(success=True, output_path="sample_output/FotoOwlReel.mp4", duration_seconds=12.4)

pipeline_state = {
    "image_folder": "images/",
    "user_prompt": intent.raw_prompt,
    "intent": intent.model_dump(),
    "image_analyses": [a.model_dump() for a in analyses],
    "selected_images": [s.file_name for s in storyboard.scenes],
    "storyboard": storyboard.model_dump(),
    "script": script.model_dump(),
    "compile_result": compile_result.model_dump(),
    "fix_attempts": 1,
    "max_fix_attempts": 3,
    "render_result": render_result.model_dump(),
    "node_trace": ["intent_parser", "image_analyser", "storyboard_writer",
                    "script_generator", "compiler_fixer", "renderer"],
}
with open(os.path.join(OUT, "pipeline_state_success_example.json"), "w") as f:
    json.dump(pipeline_state, f, indent=2)

# a failure-path example, retries exhausted
failure = PipelineFailure(
    failed_at_node="compiler_fixer",
    last_errors=[CompileError(message="Cannot find module 'remotion'", error_type="missing_import")],
    attempts_made=3,
    suggestion="Persistent missing_import error after 3 fix attempts - likely a "
               "structural issue (wrong import path) rather than a typo. "
               "Review sample_output/remotion_script_cinematic.tsx and the "
               "retrieved API context for remotion_composition_registration.",
)
failure_state = dict(pipeline_state)
failure_state.pop("render_result")
failure_state["compile_result"] = CompileResult(
    success=False, attempt_number=3,
    errors=failure.last_errors,
).model_dump()
failure_state["fix_attempts"] = 3
failure_state["failure"] = failure.model_dump()
failure_state["node_trace"] = ["intent_parser", "image_analyser", "storyboard_writer",
                                "script_generator", "compiler_fixer", "script_generator",
                                "compiler_fixer", "script_generator", "compiler_fixer", "fail_node"]
with open(os.path.join(OUT, "pipeline_state_failure_example.json"), "w") as f:
    json.dump(failure_state, f, indent=2)

print("Sample outputs written to", OUT)
