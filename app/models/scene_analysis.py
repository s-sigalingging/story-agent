from typing import List, Optional

from pydantic import BaseModel, Field


class EnvironmentAnalysis(BaseModel):
    """
    Production-oriented interpretation of the scene environment.

    UNKNOWN means that the story has not explicitly established
    a reliable value.
    """

    time_of_day: str = "UNKNOWN"

    weather: str = "UNKNOWN"

    lighting: str = "UNKNOWN"

    atmosphere: str = "NEUTRAL"


class CameraAnalysis(BaseModel):
    """
    High-level camera intent derived from story data.

    This is still provider-agnostic.
    """

    framing: str = "UNSPECIFIED"

    movement: str = "STATIC"

    focus: str = "SCENE"


class SceneAnalysis(BaseModel):
    """
    Generic analysis result for a single scene.

    Story-facing names are retained for readability.

    Stable entity IDs are stored separately for use by downstream
    production systems.
    """

    scene_number: int = Field(
        gt=0
    )

    narrative_function: str = (
        "DEVELOPMENT"
    )

    visual_intent: str = ""

    emotional_state: str = "NEUTRAL"

    character_actions: List[str] = Field(
        default_factory=list
    )

    # ============================================================
    # STORY-FACING ENTITIES
    # ============================================================

    characters: List[str] = Field(
        default_factory=list
    )

    location: str = ""

    props: List[str] = Field(
        default_factory=list
    )

    primary_subject: Optional[str] = None

    # ============================================================
    # ENGINE-FACING ENTITIES
    # ============================================================

    character_ids: List[str] = Field(
        default_factory=list
    )

    location_id: Optional[str] = None

    prop_ids: List[str] = Field(
        default_factory=list
    )

    primary_subject_id: Optional[str] = None

    # ============================================================
    # PRODUCTION INTERPRETATION
    # ============================================================

    environment: EnvironmentAnalysis = Field(
        default_factory=EnvironmentAnalysis
    )

    camera: CameraAnalysis = Field(
        default_factory=CameraAnalysis
    )

    visual_constraints: List[str] = Field(
        default_factory=list
    )


class EpisodeSceneAnalysis(BaseModel):
    """
    Scene analysis for an entire episode.
    """

    status: str

    episode_id: str

    scenes: List[SceneAnalysis] = Field(
        default_factory=list
    )