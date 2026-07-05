"""
Mocking strategy: we monkeypatch `src.models.client.structured_call` -
the single choke point every agent uses to talk to an LLM. This means
every node's actual logic (prompt assembly, state shape, RAG retrieval,
routing) runs for real; only the network call is faked. That's a much
stronger test than mocking each agent function directly.
"""
from __future__ import annotations
from src.schemas import (
    VideoIntent, Pacing, VisualStyle, CaptionTone, TransitionPreference,
    ImageAnalysisBatch, ImageAnalysis, Storyboard, StoryboardScene,
    RemotionScript, CompileError,
)


def make_mock_intent(style: str = "cinematic") -> VideoIntent:
    presets = {
        "cinematic": VideoIntent(
            raw_prompt="Cinematic wedding reel, slow and emotional, warm tones, minimal text",
            pacing=Pacing.SLOW, visual_style=VisualStyle.CINEMATIC,
            caption_tone=CaptionTone.EMOTIONAL, transition_preference=TransitionPreference.CROSSFADE,
            target_duration_seconds=45, music_mood="soft piano",
            rationale="Prompt explicitly requests slow, emotional, minimal-text cinematic treatment.",
        ),
        "upbeat": VideoIntent(
            raw_prompt="Upbeat birthday reel, fast cuts, bold captions, energetic",
            pacing=Pacing.FAST, visual_style=VisualStyle.UPBEAT,
            caption_tone=CaptionTone.PLAYFUL, transition_preference=TransitionPreference.HARD_CUT,
            target_duration_seconds=25, music_mood="upbeat pop",
            rationale="Prompt explicitly requests fast, energetic, bold-caption treatment.",
        ),
    }
    return presets[style]


def make_mock_analyses(n: int = 5) -> list[ImageAnalysis]:
    return [
        ImageAnalysis(
            file_name=f"img_{i:02d}.jpg",
            description=f"Event photo {i}",
            detected_subjects=["people"],
            dominant_colors=["warm amber", "white"],
            estimated_emotion="joyful" if i % 2 == 0 else "candid",
            composition_quality=0.9 if i % 3 != 0 else 0.4,
            suggested_role=["opening", "climax", "closing", "filler"][i % 4],
        )
        for i in range(n)
    ]


def make_mock_storyboard(intent: VideoIntent, analyses: list[ImageAnalysis]) -> Storyboard:
    good = [a for a in analyses if a.composition_quality >= 0.5]
    scenes = [
        StoryboardScene(
            scene_index=i,
            file_name=a.file_name,
            duration_seconds=2.0 if intent.pacing == Pacing.FAST else 5.0,
            caption="Let's go!" if intent.caption_tone == CaptionTone.PLAYFUL else "the quiet before",
            transition_in=intent.transition_preference,
            camera_effect="ken_burns_zoom_in",
        )
        for i, a in enumerate(good)
    ]
    return Storyboard(
        scenes=scenes,
        total_duration_seconds=sum(s.duration_seconds for s in scenes),
        narrative_arc="arrival -> celebration -> closing",
        style_notes=f"Generated for {intent.visual_style.value} style.",
    )


def make_mock_script(valid: bool = True) -> RemotionScript:
    code = (
        "import {Composition, Sequence, AbsoluteFill, staticFile} from 'remotion';\n"
        "export const FotoOwlReel = () => (<AbsoluteFill><Sequence from={0} "
        "durationInFrames={90}><img src={staticFile('img_00.jpg')} /></Sequence></AbsoluteFill>);\n"
        "export const RemotionRoot = () => (<Composition id='FotoOwlReel' "
        "component={FotoOwlReel} durationInFrames={900} fps={30} width={1080} height={1920} />);\n"
    )
    if not valid:
        code = code.replace("durationInFrames={90}", "durationInFrames='ninety'")  # type error
    return RemotionScript(typescript_code=code)


def make_mock_compile_error() -> CompileError:
    return CompileError(
        message="Type 'string' is not assignable to type 'number'.",
        file="Composition.tsx", line=2, error_type="type",
    )
