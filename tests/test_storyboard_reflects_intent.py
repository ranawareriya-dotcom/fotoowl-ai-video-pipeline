"""Scenario 2: storyboard generation must (a) select a subset, not all
images, when quality varies, and (b) produce scenes whose timing/captions
differ based on VideoIntent alone."""
from tests.mocks import make_mock_intent, make_mock_analyses, make_mock_storyboard


def test_storyboard_selects_subset_not_all_images():
    intent = make_mock_intent("cinematic")
    analyses = make_mock_analyses(n=6)  # includes some low-quality (i % 3 == 0) images
    storyboard = make_mock_storyboard(intent, analyses)

    assert len(storyboard.scenes) < len(analyses)
    used_files = {s.file_name for s in storyboard.scenes}
    low_quality_files = {a.file_name for a in analyses if a.composition_quality < 0.5}
    assert used_files.isdisjoint(low_quality_files)


def test_pacing_changes_scene_duration():
    analyses = make_mock_analyses(n=6)
    slow = make_mock_storyboard(make_mock_intent("cinematic"), analyses)
    fast = make_mock_storyboard(make_mock_intent("upbeat"), analyses)

    assert slow.scenes[0].duration_seconds > fast.scenes[0].duration_seconds


def test_caption_tone_changes_caption_style():
    analyses = make_mock_analyses(n=6)
    cinematic = make_mock_storyboard(make_mock_intent("cinematic"), analyses)
    upbeat = make_mock_storyboard(make_mock_intent("upbeat"), analyses)

    assert cinematic.scenes[0].caption != upbeat.scenes[0].caption
