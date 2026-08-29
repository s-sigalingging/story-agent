from typing import Dict, List, Optional

from pydantic import BaseModel, Field


# ================================================================
# CANONICAL ENTITY STATES
# ================================================================


class CharacterState(BaseModel):
    """
    Canonical production state for one character.

    This state may survive across scenes and episodes.
    """

    entity_id: str

    name: str

    appearance: str = "UNKNOWN"

    wardrobe: str = "UNKNOWN"

    emotional_state: str = "UNKNOWN"

    physical_condition: str = "UNKNOWN"

    position: str = "UNKNOWN"

    notes: List[str] = Field(
        default_factory=list
    )

    reference_required: bool = True

    master_character_required: bool = True


class LocationState(BaseModel):
    """
    Canonical production state for one location.
    """

    entity_id: str

    name: str

    time_of_day: str = "UNKNOWN"

    weather: str = "UNKNOWN"

    lighting: str = "UNKNOWN"

    atmosphere: str = "UNKNOWN"

    notes: List[str] = Field(
        default_factory=list
    )

    reference_required: bool = True


class PropState(BaseModel):
    """
    Canonical production state for one prop.
    """

    entity_id: str

    name: str

    appearance: str = "UNKNOWN"

    state: str = "UNKNOWN"

    position: str = "UNKNOWN"

    holder_id: Optional[str] = None

    notes: List[str] = Field(
        default_factory=list
    )

    reference_required: bool = True


# ================================================================
# WORLD STATE
# ================================================================


class WorldStateSnapshot(BaseModel):
    """
    Persistent canonical state of the story world.

    This model is intentionally episode-agnostic.

    It represents everything that is currently known about
    characters, locations, and props after an episode has finished.
    """

    version: int = 1

    last_episode_id: Optional[str] = None

    characters: Dict[
        str,
        CharacterState
    ] = Field(
        default_factory=dict
    )

    locations: Dict[
        str,
        LocationState
    ] = Field(
        default_factory=dict
    )

    props: Dict[
        str,
        PropState
    ] = Field(
        default_factory=dict
    )


# ================================================================
# SCENE STATE
# ================================================================


class SceneState(BaseModel):
    """
    Production state visible during one scene.
    """

    scene_number: int

    characters: Dict[
        str,
        CharacterState
    ] = Field(
        default_factory=dict
    )

    location: Optional[
        LocationState
    ] = None

    props: Dict[
        str,
        PropState
    ] = Field(
        default_factory=dict
    )

    active_characters: List[str] = Field(
        default_factory=list
    )

    active_props: List[str] = Field(
        default_factory=list
    )


# ================================================================
# EPISODE STATE
# ================================================================


class EpisodeState(BaseModel):
    """
    Complete production state generated for one episode.

    The final_world_state can be persisted and supplied as the
    initial world state of the next episode.
    """

    episode_id: str

    title: str

    current_scene: int = 0

    characters: Dict[
        str,
        CharacterState
    ] = Field(
        default_factory=dict
    )

    locations: Dict[
        str,
        LocationState
    ] = Field(
        default_factory=dict
    )

    props: Dict[
        str,
        PropState
    ] = Field(
        default_factory=dict
    )

    scene_states: Dict[
        int,
        SceneState
    ] = Field(
        default_factory=dict
    )

    inherited_world_state: bool = False

    source_episode_id: Optional[str] = None

    final_world_state: WorldStateSnapshot = Field(
        default_factory=WorldStateSnapshot
    )