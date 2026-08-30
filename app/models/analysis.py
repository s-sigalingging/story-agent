from typing import List, Optional

from pydantic import BaseModel, Field


# ================================================================
# PROP / OBJECT ANALYSIS
# ================================================================


class PropCandidate(BaseModel):
    """
    Candidate prop/object extracted from scene semantics.

    This is not yet a canonical world entity.
    """

    name: str

    source: str

    confidence: float = 0.5

    visually_important: bool = False


class ScenePropAnalysis(BaseModel):
    """
    Prop/object analysis result for one scene.
    """

    scene_number: int

    explicit_props: List[str] = Field(
        default_factory=list
    )

    inferred_props: List[
        PropCandidate
    ] = Field(
        default_factory=list
    )

    resolved_props: List[str] = Field(
        default_factory=list
    )


class EpisodePropAnalysis(BaseModel):
    """
    Prop/object analysis for the full episode.
    """

    status: str

    episode_id: str

    scenes: List[
        ScenePropAnalysis
    ] = Field(
        default_factory=list
    )


# ================================================================
# PRODUCTION INTENT
# ================================================================


class ProductionBeatIntent(BaseModel):
    """
    Structured creative intent for one dramatic beat.
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