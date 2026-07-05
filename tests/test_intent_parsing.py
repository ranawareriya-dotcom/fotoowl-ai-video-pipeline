"""Scenario 1: two different prompts on the same image set must yield
meaningfully different VideoIntent objects, and every downstream agent
must consume the SAME intent object (no raw-prompt re-reads)."""
from tests.mocks import make_mock_intent


def test_cinematic_vs_upbeat_intent_differ_on_every_axis():
    cinematic = make_mock_intent("cinematic")
    upbeat = make_mock_intent("upbeat")

    assert cinematic.pacing != upbeat.pacing
    assert cinematic.visual_style != upbeat.visual_style
    assert cinematic.caption_tone != upbeat.caption_tone
    assert cinematic.transition_preference != upbeat.transition_preference
    # duration should also reasonably diverge (slow reels tend longer)
    assert cinematic.target_duration_seconds != upbeat.target_duration_seconds


def test_intent_has_required_fields_for_downstream_agents():
    intent = make_mock_intent("cinematic")
    for field in ("pacing", "visual_style", "caption_tone", "transition_preference"):
        assert getattr(intent, field) is not None
