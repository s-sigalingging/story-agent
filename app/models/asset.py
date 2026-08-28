from pydantic import BaseModel
from typing import List, Optional


class AssetReference(BaseModel):

    asset_id: str

    entity_id: str

    asset_type: str

    name: str

    purpose: str

    required: bool = True

    master_reference_required: bool = False

    reference_path: Optional[str] = None


class ShotAssetPlan(BaseModel):

    shot_id: str

    assets: List[AssetReference]


class SceneAssetPlan(BaseModel):

    scene_number: int

    assets: List[AssetReference]

    shots: List[ShotAssetPlan]


class AssetPlan(BaseModel):

    episode_id: str

    title: str

    assets: List[AssetReference]

    scenes: List[SceneAssetPlan]
