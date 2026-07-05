"""Scenario 5 (LLM-as-judge, required by the brief): mocks structured_call
so no API key is needed, but exercises the real judge() function and its
prompt-assembly + parsing path."""
from unittest.mock import patch
from src.eval.judge import judge_narrative_coherence, NarrativeCoherenceJudgment
from tests.mocks import make_mock_intent, make_mock_analyses, make_mock_storyboard


def _fake_judge_call(model, system, user_content, response_model, max_tokens=2048):
    # Simulate the judge reacting to arc quality found in the storyboard JSON
    # passed as user_content, without hitting a real model.
    if "arrival -> celebration -> closing" in user_content:
        return NarrativeCoherenceJudgment(
            coherence_score=0.85,
            reasoning="Clear beginning-middle-end structure with consistent pacing.",
            flagged_issues=[],
        )
    return NarrativeCoherenceJudgment(
        coherence_score=0.2,
        reasoning="Scenes appear in no discernible order.",
        flagged_issues=["no narrative_arc description", "inconsistent pacing"],
    )


@patch("src.eval.judge.structured_call", side_effect=_fake_judge_call)
def test_judge_scores_coherent_storyboard_highly(mock_call):
    intent = make_mock_intent("cinematic")
    analyses = make_mock_analyses(6)
    storyboard = make_mock_storyboard(intent, analyses)

    judgment = judge_narrative_coherence(storyboard)

    assert judgment.coherence_score >= 0.7
    assert judgment.flagged_issues == []
    mock_call.assert_called_once()


@patch("src.eval.judge.structured_call", side_effect=_fake_judge_call)
def test_judge_flags_incoherent_storyboard(mock_call):
    from src.schemas import Storyboard, StoryboardScene, TransitionPreference

    broken = Storyboard(
        scenes=[StoryboardScene(scene_index=0, file_name="x.jpg", duration_seconds=1,
                                 caption="", transition_in=TransitionPreference.HARD_CUT,
                                 camera_effect="static")],
        total_duration_seconds=1,
        narrative_arc="",
        style_notes="",
    )
    judgment = judge_narrative_coherence(broken)

    assert judgment.coherence_score < 0.5
    assert len(judgment.flagged_issues) > 0
