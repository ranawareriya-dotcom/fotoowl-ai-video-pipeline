"""
LangGraph wiring.

Flow:
  intent_parser -> image_analyser -> storyboard_writer -> script_generator
       -> compiler_fixer --(fail, retries left)--> script_generator (loop)
       -> compiler_fixer --(success)--> renderer -> END
       -> compiler_fixer --(fail, retries exhausted)--> fail_node -> END

The retry loop is compiler_fixer <-> script_generator, NOT a self-loop on
compiler_fixer alone - the fix has to go back through generation because
the thing being changed is the script, and script_generator is what reads
the structured CompileError context (via retrieve_fix_context) to target
the fix. compiler_fixer's job is only to compile and classify errors, not
to author code.
"""
from __future__ import annotations
from langgraph.graph import StateGraph, END

from src.state import PipelineState
from src.intent_parser import parse_intent
from src.agents.image_analyser import image_analyser_node
from src.agents.storyboard_writer import storyboard_writer_node
from src.agents.script_generator import script_generator_node
from src.agents.compiler_fixer import compiler_fixer_node
from src.agents.renderer import renderer_node
from src.schemas import PipelineFailure

DEFAULT_MAX_FIX_ATTEMPTS = 3


def intent_parser_node(state: PipelineState) -> dict:
    intent = parse_intent(state["user_prompt"])
    return {
        "intent": intent,
        "max_fix_attempts": state.get("max_fix_attempts", DEFAULT_MAX_FIX_ATTEMPTS),
        "node_trace": ["intent_parser"],
    }


def fail_node(state: PipelineState) -> dict:
    compile_result = state["compile_result"]
    failure = PipelineFailure(
        failed_at_node="compiler_fixer",
        last_errors=compile_result.errors,
        attempts_made=state["fix_attempts"],
        suggestion=(
            "Retry limit reached. Most common remaining error type: "
            f"{compile_result.errors[0].error_type if compile_result.errors else 'unknown'}. "
            "Review sample_output/pipeline_state.json for the full error trace, "
            "or raise max_fix_attempts and re-run."
        ),
    )
    return {
        "failure": failure,
        "node_trace": state.get("node_trace", []) + ["fail_node"],
    }


def route_after_compile(state: PipelineState) -> str:
    """The conditional edge implementing the retry loop + hard cap."""
    result = state["compile_result"]
    if result.success:
        return "renderer"
    if state["fix_attempts"] >= state.get("max_fix_attempts", DEFAULT_MAX_FIX_ATTEMPTS):
        return "fail_node"
    return "script_generator"  # loop back with structured error context


def build_graph():
    graph = StateGraph(PipelineState)

    graph.add_node("intent_parser", intent_parser_node)
    graph.add_node("image_analyser", image_analyser_node)
    graph.add_node("storyboard_writer", storyboard_writer_node)
    graph.add_node("script_generator", script_generator_node)
    graph.add_node("compiler_fixer", compiler_fixer_node)
    graph.add_node("renderer", renderer_node)
    graph.add_node("fail_node", fail_node)

    graph.set_entry_point("intent_parser")
    graph.add_edge("intent_parser", "image_analyser")
    graph.add_edge("image_analyser", "storyboard_writer")
    graph.add_edge("storyboard_writer", "script_generator")
    graph.add_edge("script_generator", "compiler_fixer")

    graph.add_conditional_edges(
        "compiler_fixer",
        route_after_compile,
        {
            "renderer": "renderer",
            "script_generator": "script_generator",
            "fail_node": "fail_node",
        },
    )

    graph.add_edge("renderer", END)
    graph.add_edge("fail_node", END)

    return graph.compile()


def run_pipeline(image_folder: str, user_prompt: str, max_fix_attempts: int = DEFAULT_MAX_FIX_ATTEMPTS) -> PipelineState:
    app = build_graph()
    initial_state: PipelineState = {
        "image_folder": image_folder,
        "user_prompt": user_prompt,
        "max_fix_attempts": max_fix_attempts,
        "fix_attempts": 0,
        "node_trace": [],
    }
    return app.invoke(initial_state)


import os

def export_graph_mermaid(path):
    import os
    os.makedirs(os.path.dirname(path), exist_ok=True)

    graph_text = "graph TD; A-->B; B-->C;"  # example

    with open(path, "w") as f:
        f.write(graph_text)
