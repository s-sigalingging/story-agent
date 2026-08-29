from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class CharacterContinuityState(BaseModel):
    """
    Continuity state for one character.

    Values should only contain information that is explicitly known
    or inherited from a previous scene.

    UNKNOWN means no reliable state has been established yet.
    """

    entity_id: str

    name: str = ""

    appearance: str = "UNKNOWN"

    wardrobe: str = "UNKNOWN"

    physical_condition: str = "UNKNOWN"

    emotional_state: str = "UNKNOWN"

    position: str = "UNKNOWN"

    notes: List[str] = Field(
        default_factory=list
    )


class LocationContinuityState(BaseModel):
    """
    Continuity state for a location.
    """

    entity_id: str

    name: str = ""

    time_of_day: str = "UNKNOWN"

    weather: str = "UNKNOWN"

    lighting: str = "UNKNOWN"

    atmosphere: str = "UNKNOWN"

    notes: List[str] = Field(
        default_factory=list
    )


class PropContinuityState(BaseModel):
    """
    Continuity state for a prop.
    """

    entity_id: str

    name: str = ""

    appearance: str = "UNKNOWN"

    condition: str = "UNKNOWN"

    position: str = "UNKNOWN"

    holder_id: Optional[str] = None

    notes: List[str] = Field(
        default_factory=list
    )


class SceneContinuity(BaseModel):
    """
    Continuity snapshot for one scene.
    """

    scene_number: int

    inherited_from_previous_scene: bool = False

    character_states: List[
        CharacterContinuityState
    ] = Field(
        default_factory=list
    )

    location_state: Optional[
        LocationContinuityState
    ] = None

    prop_states: List[
        PropContinuityState
    ] = Field(
        default_factory=list
    )

    continuity_notes: List[str] = Field(
        default_factory=list
    )


class EpisodeContinuity(BaseModel):
    """
    Continuity analysis result for an entire episode.
    """

    status: str

    episode_id: str

    scenes: List[
        SceneContinuity
    ] = Field(
        default_factory=list
    )

    final_character_states: Dict[
        str,
        CharacterContinuityState
    ] = Field(
        default_factory=dict
    )

    final_location_states: Dict[
        str,
        LocationContinuityState
    ] = Field(
        default_factory=dict
    )

    final_prop_states: Dict[
        str,
        PropContinuityState
    ] = Field(
        default_factory=dict
    )