from typing import Dict, List, Optional

from pydantic import BaseModel, Field


# ================================================================
# ASSET REFERENCES
# ================================================================


class PromptAssetReference(BaseModel):
    """
    Reference to an asset that should be supplied to the image/video
    generation system.

    The prompt layer does not decide whether an asset exists.
    It only receives resolved asset references from upstream planning.
    """

    asset_id: str

    entity_id: str

    asset_type: str

    name: str

    purpose: Optional[str] = None

    reference_path: Optional[str] = None

    required: bool = True

    master_reference_required: bool = False


# ================================================================
# PROMPT CONTEXT
# ================================================================


class PromptCameraContext(BaseModel):
    """
    Provider-agnostic camera context for prompt compilation.
    """

    shot_type: str = "UNSPECIFIED"

    camera_movement: str = "STATIC"

    framing: str = "UNSPECIFIED"

    composition: str = ""


class PromptCharacterPerformance(BaseModel):
    """
    Structured character performance used by image/video builders.
    """

    entity_id: str

    name: str = ""

    action: str = ""

    gesture: str = ""

    facial_movement: str = ""


class PromptPropPerformance(BaseModel):
    """
    Structured prop behavior used by prompt builders.
    """

    entity_id: str

    name: str = ""

    action: str = ""


class PromptEnvironmentContext(BaseModel):
    """
    Environment context available to the prompt compiler.

    UNKNOWN means upstream analysis did not establish the value.
    """

    location_id: Optional[str] = None

    location_name: str = ""

    time_of_day: str = "UNKNOWN"

    weather: str = "UNKNOWN"

    lighting: str = "UNKNOWN"

    atmosphere: str = "UNKNOWN"


class PromptStyleContext(BaseModel):
    """
    Story / series visual style context.

    This prevents prompt builders from hardcoding genre or rendering
    style inside Python source code.
    """

    tone: str = ""

    visual_style: str = ""

    additional_style_notes: List[str] = Field(
        default_factory=list
    )


class ShotPromptContext(BaseModel):
    """
    Complete provider-agnostic context for one production shot.

    Prompt builders should compile from this model instead of reading
    arbitrary upstream dictionaries or inventing missing story facts.
    """

    shot_id: str

    scene_number: int

    duration_seconds: int

    purpose: str

    style: PromptStyleContext = Field(
        default_factory=PromptStyleContext
    )

    camera: PromptCameraContext = Field(
        default_factory=PromptCameraContext
    )

    environment: PromptEnvironmentContext = Field(
        default_factory=PromptEnvironmentContext
    )

    characters: List[
        PromptCharacterPerformance
    ] = Field(
        default_factory=list
    )

    props: List[
        PromptPropPerformance
    ] = Field(
        default_factory=list
    )

    continuity_constraints: List[str] = Field(
        default_factory=list
    )

    assets: List[
        PromptAssetReference
    ] = Field(
        default_factory=list
    )

    dialogue: Optional[str] = None

    metadata: Dict[str, str] = Field(
        default_factory=dict
    )


# ================================================================
# COMPILED PROMPTS
# ================================================================


class ProductionPrompt(BaseModel):
    """
    Generated production prompt for a single shot.

    image_prompt:
        describes the approved still/keyframe target.

    video_prompt:
        describes motion from the approved keyframe.

    negative_prompt:
        contains shot-relevant exclusions only.
    """

    shot_id: str

    scene_number: int

    duration_seconds: int

    image_prompt: str

    video_prompt: str

    negative_prompt: Optional[str] = None

    assets: List[
        PromptAssetReference
    ] = Field(
        default_factory=list
    )

    dialogue: Optional[str] = None


class SceneProductionPrompts(BaseModel):
    """
    Collection of prompts generated for one scene.
    """

    scene_number: int

    prompts: List[
        ProductionPrompt
    ] = Field(
        default_factory=list
    )


class EpisodeProductionPrompts(BaseModel):
    """
    Complete production prompt package for an episode.
    """

    episode_id: str

    title: str

    target_duration_seconds: int

    scenes: List[
        SceneProductionPrompts
    ] = Field(
        default_factory=list
    )

    total_shots: int = 0