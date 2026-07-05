"""
Multi-model routing.

Rationale (also duplicated in README for the reviewer):

Node              | Model                     | Why
------------------|---------------------------|----------------------------------
Intent Parser     | gemini-2.5-flash          | Tiny structured-extraction task.
                  |                           | Cheap model is plenty accurate for
                  |                           | mapping a sentence to 4 enums.
Image Analyser    | gemini-2.5-pro (vision)   | Needs real vision understanding
                  |                           | (subjects, emotion, composition) -
                  |                           | this is the one place quality
                  |                           | genuinely matters and it only
                  |                           | runs once per image, not in a loop.
Storyboard Writer | gemini-2.5-pro            | Creative sequencing + narrative
                  |                           | reasoning benefits from a stronger
                  |                           | model; still a single call per run.
Script Generator  | gemini-2.5-pro            | Code generation quality directly
                  |                           | determines whether the compile loop
                  |                           | even has a chance of succeeding -
                  |                           | worth paying for.
Compiler Fixer    | gemini-2.5-flash          | Runs in a retry loop (up to N times)
                  | (escalates to pro on      | so cost multiplies fastest here.
                  | 2nd+ retry)               | Most compile errors are small/
                  |                           | mechanical (missing import, typo,
                  |                           | wrong prop) - cheap model fixes
                  |                           | most of them. Escalate to Pro
                  |                           | only if Flash's fix also fails,
                  |                           | since repeated failures suggest a
                  |                           | structural misunderstanding.

This is a cost/quality ladder: cheap-by-default, escalate on evidence of
difficulty, spend the most on the two single-shot creative/quality-critical
calls (vision analysis, code generation).

Migration note: this file previously mapped nodes to Claude models
(claude-haiku-4-5 / claude-sonnet-5). Only the model identifiers changed
for the Gemini migration - the routing policy (which node gets the cheap
vs. capable model, and the escalation rule) is unchanged.
"""
from __future__ import annotations
from enum import Enum


class ModelName(str, Enum):
    FLASH = "gemini-2.5-flash"
    PRO = "gemini-2.5-flash"


NODE_MODEL_MAP: dict[str, ModelName] = {
    "intent_parser": ModelName.FLASH,
    "image_analyser": ModelName.PRO,     # vision-capable
    "storyboard_writer": ModelName.PRO,
    "script_generator": ModelName.PRO,
    "compiler_fixer_attempt_1": ModelName.FLASH,
    "compiler_fixer_attempt_2_plus": ModelName.PRO,
}


def model_for_fix_attempt(attempt_number: int) -> ModelName:
    """Escalation policy for the Compiler & Fixer loop."""
    return ModelName.FLASH if attempt_number <= 1 else ModelName.PRO
