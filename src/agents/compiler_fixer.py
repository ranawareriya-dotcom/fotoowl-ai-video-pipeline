from __future__ import annotations
import os
import subprocess
from src.schemas import CompileResult, CompileError
from src.models.client import structured_call
from src.models.router import ModelName
from src.state import PipelineState

REMOTION_PROJECT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "remotion")

_ERROR_PARSE_SYSTEM = """Convert this raw TypeScript/Remotion compiler output
into a structured list of CompileError objects. Merge duplicate errors.
If the output indicates success with no errors, return an empty list."""


class _CompileErrorList:
    """Local wrapper so structured_call has a single pydantic root model."""
    pass


def _write_script_to_disk(typescript_code: str) -> str:
    path = os.path.join(REMOTION_PROJECT_DIR, "src", "Composition.tsx")
    with open(path, "w") as f:
        f.write(typescript_code)
    return path

def _run_typecheck():
    print("=" * 80)
    print("REMOTION_PROJECT_DIR =", REMOTION_PROJECT_DIR)
    print("Exists:", os.path.exists(REMOTION_PROJECT_DIR))
    print("=" * 80)

    result = subprocess.run(
        "npx tsc --noEmit -p .",
        cwd=REMOTION_PROJECT_DIR,
        shell=True,
        capture_output=True,
        text=True,
        timeout=120,
    )

    return result.returncode == 0, result.stdout + result.stderr



def compile_script(typescript_code: str, attempt_number: int) -> CompileResult:
    _write_script_to_disk(typescript_code)
    success, raw_output = _run_typecheck()

    if success:
        return CompileResult(success=True, stdout=raw_output, attempt_number=attempt_number)

    from pydantic import BaseModel

    class _ErrorsWrapper(BaseModel):
        errors: list[CompileError]

    parsed = structured_call(
        model=ModelName.FLASH.value,   # cheap: this is a mechanical extraction task
        system=_ERROR_PARSE_SYSTEM,
        user_content=raw_output[:4000],
        response_model=_ErrorsWrapper,
    )
    return CompileResult(
        success=False,
        errors=parsed.errors,
        stdout=raw_output,
        attempt_number=attempt_number,
    )


def compiler_fixer_node(state: PipelineState) -> dict:
    attempt = state.get("fix_attempts", 0) + 1
    result = compile_script(state["script"].typescript_code, attempt_number=attempt)
    return {
        "compile_result": result,
        "fix_attempts": attempt,
        "node_trace": state.get("node_trace", []) + ["compiler_fixer"],
    }
