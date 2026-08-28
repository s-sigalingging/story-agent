from pydantic import BaseModel
from typing import List


class CharacterState(BaseModel):
    name: str
    appearance: str
    wardrobe: str
    emotional_state: str
    physical_condition: str


class LocationState(BaseModel):
    name: str
    time_of_day: str
    weather: str
    lighting: str
    atmosphere: str


class PropState(BaseModel):
    name: str
    appearance: str
    state: str


class SceneContinuity(BaseModel):
    scene_number: int

    inherited_from_previous_scene: bool

    characters: List[CharacterState]

    location: LocationState

    props: List[PropState]

    continuity_requirements: List[str]

    changes_from_previous_scene: List[str]


class EpisodeContinuity(BaseModel):
    status: str

    scenes: List[SceneContinuity]