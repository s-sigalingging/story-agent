from typing import List, Optional

from pydantic import BaseModel, Field


class PromptAssetReference(BaseModel):
    """
    Reference to an asset that should be supplied to the image/video generator.
    """

    asset_id: str
    entity_id: str
    asset_type: str
    name: str

    purpose: Optional[str] = None
    reference_path: Optional[str] = None

    required: bool = True
    master_reference_required: bool = False


class ProductionPrompt(BaseModel):
    """
    Generated production prompt for a single shot.

    The image prompt describes the visual keyframe.
    The video prompt describes how the keyframe should move.
    """

    shot_id: str
    scene_number: int

    duration_seconds: int

    image_prompt: str
    video_prompt: str

    negative_prompt: Optional[str] = None

    assets: List[PromptAssetReference] = Field(default_factory=list)

    dialogue: Optional[str] = None


class SceneProductionPrompts(BaseModel):
    """
    Collection of prompts generated for one scene.
    """

    scene_number: int
    prompts: List[ProductionPrompt] = Field(default_factory=list)


class EpisodeProductionPrompts(BaseModel):
    """
    Complete production prompt package for an episode.
    """

    episode_id: str
    title: str

    target_duration_seconds: int

    scenes: List[SceneProductionPrompts] = Field(default_factory=list)

    total_shots: int = 0