from pydantic import BaseModel
from typing import List, Optional


class CameraPlan(BaseModel):

    shot_type: str

    camera_movement: str

    framing: str

    composition: str


class CharacterAction(BaseModel):

    entity_id: str

    action: str

    gesture: Optional[str] = None

    facial_movement: Optional[str] = None


class PropAction(BaseModel):

    entity_id: str

    action: str


class ShotPlan(BaseModel):

    shot_id: str

    scene_number: int

    duration_seconds: int

    purpose: str

    characters: List[str]

    props: List[str]

    camera: CameraPlan

    character_actions: List[CharacterAction]

    prop_actions: List[PropAction]

    visual_constraints: List[str]

    dialogue: Optional[str] = None


class SceneProductionPlan(BaseModel):

    scene_number: int

    duration_seconds: int

    location_id: str

    shot_count: int

    shots: List[ShotPlan]


class ProductionPlan(BaseModel):

    episode_id: str

    title: str

    target_duration_seconds: int

    scenes: List[SceneProductionPlan]