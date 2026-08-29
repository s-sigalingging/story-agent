from typing import List, Optional

from pydantic import BaseModel, Field


class ProductionBeatIntent(BaseModel):
    """
    Structured creative intent for one dramatic beat.

    This model describes what a shot sequence should communicate,
    without deciding provider-specific prompt syntax.
    """

    beat_type: str

    purpose: str

    primary_subject_id: Optional[str] = None

    supporting_subject_ids: List[str] = Field(
        default_factory=list
    )

    important_prop_ids: List[str] = Field(
        default_factory=list
    )

    emphasis: str = "NORMAL"


class SceneProductionIntent(BaseModel):
    """
    Creative production intent for one scene.

    This sits between SceneAnalysis and ShotPlanner.
    """

    scene_number: int

    narrative_function: str

    primary_subject_id: Optional[str] = None

    supporting_subject_ids: List[str] = Field(
        default_factory=list
    )

    important_prop_ids: List[str] = Field(
        default_factory=list
    )

    dialogue_present: bool = False

    visual_priority: str = "CHARACTER"

    pacing: str = "MODERATE"

    beats: List[
        ProductionBeatIntent
    ] = Field(
        default_factory=list
    )


class EpisodeProductionIntent(BaseModel):
    """
    Production intent for an entire episode.
    """

    status: str

    episode_id: str

    scenes: List[
        SceneProductionIntent
    ] = Field(
        default_factory=list
    )