"""Scenario 3: the conditional edge after compiler_fixer must route to
script_generator on failure (under the cap), to renderer on success, and
to fail_node once the cap is hit - without ever crashing."""
from src.graph import route_after_compile, DEFAULT_MAX_FIX_ATTEMPTS
from src.schemas import CompileResult, CompileError


def _state(success: bool, attempts: int, max_attempts: int = DEFAULT_MAX_FIX_ATTEMPTS):
    errors = [] if success else [CompileError(message="x", error_type="type")]
    return {
        "compile_result": CompileResult(success=success, errors=errors, attempt_number=attempts),
        "fix_attempts": attempts,
        "max_fix_attempts": max_attempts,
    }


def test_routes_to_renderer_on_success():
    assert route_after_compile(_state(success=True, attempts=1)) == "renderer"


def test_routes_to_script_generator_on_failure_under_cap():
    assert route_after_compile(_state(success=False, attempts=1, max_attempts=3)) == "script_generator"


def test_routes_to_fail_node_once_cap_reached():
    assert route_after_compile(_state(success=False, attempts=3, max_attempts=3)) == "fail_node"


def test_never_exceeds_cap_even_if_attempts_overshoots():
    # defensive: if attempts somehow exceeds max (shouldn't happen), still fails safely
    assert route_after_compile(_state(success=False, attempts=5, max_attempts=3)) == "fail_node"
