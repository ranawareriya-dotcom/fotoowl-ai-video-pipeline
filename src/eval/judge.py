from __future__ import annotations
from pydantic import BaseModel, Field
from src.schemas import Storyboard
from src.models.client import structured_call
from src.models.router import ModelName


class NarrativeCoherenceJudgment(BaseModel):
    coherence_score: float = Field(ge=0, le=1, description="0=disjointed, 1=strong narrative arc")
    reasoning: str
    flagged_issues: list[str] = Field(default_factory=list)


JUDGE_SYSTEM = """You are evaluating whether a video storyboard has a coherent
narrative arc - does the scene order, pacing, and captions build a sensible
story rather than a random sequence of images? Score 0-1 and explain briefly."""


def judge_narrative_coherence(storyboard: Storyboard) -> NarrativeCoherenceJudgment:
    return structured_call(
        model=ModelName.FLASH.value,  # judging is a cheap, bounded classification task
        system=JUDGE_SYSTEM,
        user_content=storyboard.model_dump_json(indent=2),
        response_model=NarrativeCoherenceJudgment,
    )
