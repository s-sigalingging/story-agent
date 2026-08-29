from typing import Dict, List, Optional

from pydantic import BaseModel, Field


# ================================================================
# WORLD ENTITY DEFINITIONS
# ================================================================


class CharacterDefinition(BaseModel):
    """
    Canonical definition of a character known to the world registry.

    Story-specific visual details can be added later without changing
    how entity identity works.
    """

    entity_id: str

    name: str

    aliases: List[str] = Field(
        default_factory=list
    )

    description: str = ""

    reference_path: Optional[str] = None


class LocationDefinition(BaseModel):
    """
    Canonical definition of a location.
    """

    entity_id: str

    name: str

    aliases: List[str] = Field(
        default_factory=list
    )

    description: str = ""

    reference_path: Optional[str] = None


class PropDefinition(BaseModel):
    """
    Canonical definition of a prop.
    """

    entity_id: str

    name: str

    aliases: List[str] = Field(
        default_factory=list
    )

    description: str = ""

    reference_path: Optional[str] = None


# ================================================================
# WORLD REGISTRY SNAPSHOT
# ================================================================


class WorldRegistrySnapshot(BaseModel):
    """
    Serializable snapshot of everything currently known by the
    registry.

    Dictionary keys are canonical entity IDs.
    """

    characters: Dict[
        str,
        CharacterDefinition
    ] = Field(
        default_factory=dict
    )

    locations: Dict[
        str,
        LocationDefinition
    ] = Field(
        default_factory=dict
    )

    props: Dict[
        str,
        PropDefinition
    ] = Field(
        default_factory=dict
    )


# ================================================================
# ENTITY ANALYSIS RESULTS
# ================================================================


class SceneEntityAnalysis(BaseModel):
    """
    Entity IDs resolved for one scene.
    """

    scene_number: int

    character_ids: List[str] = Field(
        default_factory=list
    )

    location_id: Optional[str] = None

    prop_ids: List[str] = Field(
        default_factory=list
    )


class EpisodeEntityAnalysis(BaseModel):
    """
    Entity resolution result for an entire episode.
    """

    status: str

    episode_id: str

    scenes: List[
        SceneEntityAnalysis
    ] = Field(
        default_factory=list
    )

    registry: WorldRegistrySnapshot