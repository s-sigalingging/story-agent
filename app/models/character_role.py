from typing import List, Optional

from pydantic import BaseModel, Field


class CharacterRoleAnalysis(BaseModel):
    """
    Semantic role assigned to one character inside one scene.
    """

    entity_id: str

    name: str

    role: str = "PARTICIPANT"

    interaction: str = "UNSPECIFIED"

    confidence: float = 0.5

    primary_candidate: bool = False

    evidence: str = ""


class SceneCharacterRoleAnalysis(BaseModel):
    """
    Character-role analysis for one scene.
    """

    scene_number: int

    characters: List[
        CharacterRoleAnalysis
    ] = Field(
        default_factory=list
    )

    primary_subject_id: Optional[str] = None

    primary_subject_name: Optional[str] = None


class EpisodeCharacterRoleAnalysis(BaseModel):
    """
    Character-role analysis for an entire episode.
    """

    status: str

    episode_id: str

    scenes: List[
        SceneCharacterRoleAnalysis
    ] = Field(
        default_factory=list
    )