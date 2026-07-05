from __future__ import annotations
from src.schemas import RemotionScript, VideoIntent, Storyboard, CompileResult
from src.models.client import structured_call
from src.models.router import NODE_MODEL_MAP, model_for_fix_attempt
from src.rag.retriever import retrieve_remotion_api_context, retrieve_fix_context
from src.state import PipelineState

SYSTEM_TEMPLATE ="""You are the Script Generator.

Generate ONE complete, production-ready Remotion Composition.tsx file.

The output MUST be valid TypeScript and compile successfully with:

    npx tsc --noEmit -p .

STRICT REQUIREMENTS

1. Return ONLY the TypeScript code.
2. Do NOT include markdown.
3. Do NOT include explanations.
4. Do NOT include comments such as:
   // Example
   // Usage
   // Register like this
5. Do NOT wrap any code in /* ... */.
6. Do NOT omit required exports.

The file MUST export BOTH:

export const FotoOwlReel = ...

AND

export const RemotionRoot = () => (
  <>
    <Composition
      id="FotoOwlReel"
      component={{FotoOwlReel}}
      durationInFrames={{...}}
      fps={{30}}
      width={{1080}}
      height={{1920}}
    />
  </>
);

The file MUST:

- import React
- import Composition from remotion
- import Sequence
- import AbsoluteFill
- import Img
- import staticFile
- import interpolate
- import useCurrentFrame

Use staticFile() for every image.

Use Sequence for scene timing.

Implement the exact storyboard.

The generated code MUST compile without modification.

VideoIntent:
{intent}

Storyboard:
{storyboard}

Retrieved Remotion API reference:
{api_context}

{fix_context_block}
"""


def generate_script(
    intent: VideoIntent,
    storyboard: Storyboard,
    previous_compile_result: CompileResult | None = None,
    previous_script: RemotionScript | None = None,
) -> RemotionScript:
    api_context = retrieve_remotion_api_context(intent)

    fix_block = ""
    model = NODE_MODEL_MAP["script_generator"].value
    if previous_compile_result and not previous_compile_result.success:
        # Retry path: pull targeted context for the specific error(s), and
        # pass the previous script + structured errors back so the fix is
        # targeted rather than a blind regeneration.
        model = model_for_fix_attempt(previous_compile_result.attempt_number).value
        fix_snippets = []
        for err in previous_compile_result.errors:
            fix_snippets.extend(retrieve_fix_context(err))
        errors_text = "\n".join(
            f"- [{e.error_type}] {e.message} (line {e.line})"
            for e in previous_compile_result.errors
        )
        fix_block = f"""
This is a FIX attempt (#{previous_compile_result.attempt_number + 1}).
Previous script:
{previous_script.typescript_code if previous_script else ''}

Compile errors to fix:
{errors_text}

Targeted fix reference:
{chr(10).join(fix_snippets)}

Fix ONLY what's needed to resolve these specific errors. Do not rewrite
unrelated parts of the script.
"""

    system = SYSTEM_TEMPLATE.format(
        intent=intent.model_dump_json(indent=2),
        storyboard=storyboard.model_dump_json(indent=2),
        api_context="\n---\n".join(api_context),
        fix_context_block=fix_block,
    )
    return structured_call(
        model=model,
        system=system,
        user_content="""
    Generate ONLY the complete contents of Composition.tsx.

    The code must compile immediately.

    Do not output examples.
    Do not output comments.
    Do not output markdown.
    Do not wrap code in /* ... */.
    Do not omit the RemotionRoot export.
    """,
        response_model=RemotionScript,
    )


def script_generator_node(state: PipelineState) -> dict:
    script = generate_script(
        state["intent"],
        state["storyboard"],
        previous_compile_result=state.get("compile_result"),
        previous_script=state.get("script"),
    )
    return {
        "script": script,
        "node_trace": state.get("node_trace", []) + ["script_generator"],
    }
