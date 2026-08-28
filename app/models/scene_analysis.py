from pydantic import BaseModel
from typing import List


class EnvironmentAnalysis(BaseModel):
    time_of_day: str
    weather: str
    lighting: str
    atmosphere: str


class CameraAnalysis(BaseModel):
    framing: str
    movement: str
    focus: str


class SceneAnalysis(BaseModel):
    scene_number: int

    narrative_function: str

    visual_intent: str

    emotional_state: str

    character_actions: List[str]

    characters: List[str]

    location: str

    props: List[str]

    environment: EnvironmentAnalysis

    camera: CameraAnalysis

    visual_constraints: List[str]


class EpisodeSceneAnalysis(BaseModel):
    status: str

    scenes: List[SceneAnalysis]