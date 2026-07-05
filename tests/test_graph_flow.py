"""End-to-end graph test: patches every node's underlying model/subprocess
call so the whole StateGraph can run with no API keys and no Node/Remotion
installed, while still exercising real routing logic."""
from unittest.mock import patch
from src.graph import build_graph, DEFAULT_MAX_FIX_ATTEMPTS
from src.schemas import CompileResult, CompileError, RenderResult
from tests.mocks import (
    make_mock_intent, make_mock_analyses, make_mock_storyboard, make_mock_script,
)


def test_pipeline_recovers_from_one_compile_failure_then_succeeds():
    intent = make_mock_intent("cinematic")
    analyses = make_mock_analyses(5)
    storyboard = make_mock_storyboard(intent, analyses)
    bad_script = make_mock_script(valid=False)
    good_script = make_mock_script(valid=True)

    compile_calls = {"n": 0}

    def fake_compile_script(typescript_code, attempt_number):
        compile_calls["n"] += 1
        if attempt_number == 1:
            return CompileResult(success=False, attempt_number=1,
                                  errors=[CompileError(message="type error", error_type="type")])
        return CompileResult(success=True, attempt_number=attempt_number)

    script_calls = {"n": 0}

    def fake_generate_script(intent_, storyboard_, previous_compile_result=None, previous_script=None):
        script_calls["n"] += 1
        return bad_script if script_calls["n"] == 1 else good_script

    with patch("src.graph.parse_intent", return_value=intent), \
         patch("src.agents.image_analyser.analyse_images", return_value=analyses), \
         patch("src.agents.storyboard_writer.write_storyboard", return_value=storyboard), \
         patch("src.agents.script_generator.generate_script", side_effect=fake_generate_script), \
         patch("src.agents.compiler_fixer.compile_script", side_effect=fake_compile_script), \
         patch("src.agents.renderer.render_video", return_value=RenderResult(success=True, output_path="out.mp4")):

        app = build_graph()
        final_state = app.invoke({
            "image_folder": "images/", "user_prompt": intent.raw_prompt,
            "max_fix_attempts": DEFAULT_MAX_FIX_ATTEMPTS, "fix_attempts": 0, "node_trace": [],
        })

    assert script_calls["n"] == 2          # generated once, fixed once
    assert compile_calls["n"] == 2
    assert final_state["render_result"].success is True
    assert "fail_node" not in final_state["node_trace"]


def test_pipeline_exits_gracefully_after_exhausting_retries():
    intent = make_mock_intent("upbeat")
    analyses = make_mock_analyses(5)
    storyboard = make_mock_storyboard(intent, analyses)
    bad_script = make_mock_script(valid=False)

    def always_fails(typescript_code, attempt_number):
        return CompileResult(success=False, attempt_number=attempt_number,
                              errors=[CompileError(message="persistent error", error_type="unknown")])

    with patch("src.graph.parse_intent", return_value=intent), \
         patch("src.agents.image_analyser.analyse_images", return_value=analyses), \
         patch("src.agents.storyboard_writer.write_storyboard", return_value=storyboard), \
         patch("src.agents.script_generator.generate_script", return_value=bad_script), \
         patch("src.agents.compiler_fixer.compile_script", side_effect=always_fails):

        app = build_graph()
        final_state = app.invoke({
            "image_folder": "images/", "user_prompt": intent.raw_prompt,
            "max_fix_attempts": 2, "fix_attempts": 0, "node_trace": [],
        })

    assert "failure" in final_state
    assert final_state["failure"].attempts_made == 2
    assert "render_result" not in final_state
    assert final_state["node_trace"][-1] == "fail_node"
