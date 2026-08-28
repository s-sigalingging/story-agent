from pydantic import BaseModel
from typing import Dict, List


class CharacterState(BaseModel):
    entity_id: str
    name: str

    appearance: str
    wardrobe: str

    emotional_state: str
    physical_condition: str

    reference_required: bool = True
    master_character_required: bool = True


class LocationState(BaseModel):
    entity_id: str
    name: str

    time_of_day: str
    weather: str
    lighting: str
    atmosphere: str

    reference_required: bool = True


class PropState(BaseModel):
    entity_id: str
    name: str

    appearance: str
    state: str

    reference_required: bool = True


class SceneState(BaseModel):
    scene_number: int

    characters: Dict[str, CharacterState]

    location: LocationState

    props: Dict[str, PropState]

    active_characters: List[str]

    active_props: List[str]


class EpisodeState(BaseModel):
    episode_id: str
    title: str

    current_scene: int

    characters: Dict[str, CharacterState]

    locations: Dict[str, LocationState]

    props: Dict[str, PropState]

    scene_states: Dict[int, SceneState]