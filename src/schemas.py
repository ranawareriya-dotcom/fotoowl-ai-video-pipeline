"""
Structured data contracts for the whole pipeline.

Every LLM call in this project returns one of these Pydantic models
(via `.with_structured_output()` / tool-calling), never raw text that
gets regex-parsed. This is what satisfies the "no free-text parsing"
requirement in the task brief.
"""
from __future__ import annotations
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# 1. User intent (produced once, read by every downstream agent)
# ---------------------------------------------------------------------------

class Pacing(str, Enum):
    SLOW = "slow"
    MODERATE = "moderate"
    FAST = "fast"


class VisualStyle(str, Enum):
    CINEMATIC = "cinematic"
    UPBEAT = "upbeat"
    CORPORATE = "corporate"
    MINIMAL = "minimal"


class CaptionTone(str, Enum):
    EMOTIONAL = "emotional"
    PLAYFUL = "playful"
    PROFESSIONAL = "professional"
    MINIMAL = "minimal"


class TransitionPreference(str, Enum):
    CROSSFADE = "crossfade"
    HARD_CUT = "hard_cut"
    SLIDE = "slide"
    ZOOM = "zoom"


class VideoIntent(BaseModel):
    """The parsed creative brief. This is the single source of truth
    for style — no downstream node re-reads the raw prompt string."""
    raw_prompt: str
    pacing: Pacing
    visual_style: VisualStyle
    caption_tone: CaptionTone
    transition_preference: TransitionPreference
    target_duration_seconds: int = Field(ge=10, le=120)
    music_mood: Optional[str] = None
    rationale: str = Field(description="1-2 sentences: why this reading of the prompt")


# ---------------------------------------------------------------------------
# 2. Image Analyser output
# ---------------------------------------------------------------------------

class ImageAnalysis(BaseModel):
    file_name: str
    description: str
    detected_subjects: list[str]
    dominant_colors: list[str]
    estimated_emotion: str  # e.g. "joyful", "solemn", "candid"
    composition_quality: float = Field(ge=0, le=1, description="0-1 usability score")
    suggested_role: str  # e.g. "opening", "climax", "closing", "filler"


class ImageAnalysisBatch(BaseModel):
    analyses: list[ImageAnalysis]


# ---------------------------------------------------------------------------
# 3. Storyboard Writer output
# ---------------------------------------------------------------------------

class StoryboardScene(BaseModel):
    scene_index: int
    file_name: str
    duration_seconds: float = Field(ge=0.5, le=15)
    caption: str
    transition_in: TransitionPreference
    camera_effect: str  # e.g. "ken_burns_zoom_in", "pan_left", "static"


class Storyboard(BaseModel):
    scenes: list[StoryboardScene]
    total_duration_seconds: float
    narrative_arc: str = Field(description="e.g. 'arrival -> ceremony -> celebration -> farewell'")
    style_notes: str = Field(description="style-guide-informed notes passed to the script generator")


# ---------------------------------------------------------------------------
# 4. Script Generator output
# ---------------------------------------------------------------------------

class RemotionScript(BaseModel):
    file_name: str = "Composition.tsx"
    typescript_code: str
    fps: int = 30
    width: int = 1080
    height: int = 1920
    composition_id: str = "FotoOwlReel"


# ---------------------------------------------------------------------------
# 5. Compiler & Fixer output
# ---------------------------------------------------------------------------

class CompileError(BaseModel):
    message: str
    file: Optional[str] = None
    line: Optional[int] = None
    error_type: str  # "syntax" | "type" | "missing_import" | "remotion_api" | "unknown"


class CompileResult(BaseModel):
    success: bool
    errors: list[CompileError] = []
    stdout: str = ""
    attempt_number: int = 1


# ---------------------------------------------------------------------------
# 6. Renderer output
# ---------------------------------------------------------------------------

class RenderResult(BaseModel):
    success: bool
    output_path: Optional[str] = None
    duration_seconds: Optional[float] = None
    error_message: Optional[str] = None


class PipelineFailure(BaseModel):
    """Structured failure report returned when retries are exhausted."""
    failed_at_node: str
    last_errors: list[CompileError]
    attempts_made: int
    suggestion: str
