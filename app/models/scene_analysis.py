from typing import List, Optional

from pydantic import BaseModel, Field


class EnvironmentAnalysis(BaseModel):
    """
    Production-oriented interpretation of the scene environment.
    """

    time_of_day: str = "UNKNOWN"

    weather: str = "UNKNOWN"

    lighting: str = "UNKNOWN"

    atmosphere: str = "NEUTRAL"


class CameraAnalysis(BaseModel):
    """
    High-level provider-agnostic camera intent.
    """

    framing: str = "UNSPECIFIED"

    movement: str = "STATIC"

    focus: str = "SCENE"


class SceneCharacterRole(BaseModel):
    """
    Canonical character-role representation stored inside SceneAnalysis.
    """

    entity_id: str

    name: str

    role: str = "PARTICIPANT"

    interaction: str = "UNSPECIFIED"

    confidence: float = 0.5

    primary_candidate: bool = False

    evidence: str = ""


class ScenePropContent(BaseModel):
    """
    Canonical content semantics for one resolved scene prop.

    This is downstream-facing scene data.

    PropContentAnalyzer has its own analysis result model, while this
    model becomes part of the stable SceneAnalysis contract.
    """

    entity_id: str

    name: str

    content_modalities: List[str] = Field(
        default_factory=list
    )

    text_sensitive: bool = False

    readability_required: bool = False

    visual_detail_sensitive: bool = False

    confidence: float = 0.5

    evidence: List[str] = Field(
        default_factory=list
    )


class SceneAnalysis(BaseModel):
    """
    Generic semantic analysis result for a single scene.

    Human-readable story-facing names are preserved.

    Stable entity IDs and semantic data are stored separately for
    downstream production systems.
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
    # CHARACTER SEMANTICS
    # ============================================================

    character_roles: List[
        SceneCharacterRole
    ] = Field(
        default_factory=list
    )

    # ============================================================
    # PROP CONTENT SEMANTICS
    # ============================================================

    prop_content: List[
        ScenePropContent
    ] = Field(
        default_factory=list
    )

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

    scenes: List[
        SceneAnalysis
    ] = Field(
        default_factory=list
    )