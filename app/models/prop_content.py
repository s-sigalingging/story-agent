from typing import List

from pydantic import BaseModel, Field


class PropContentSemantics(BaseModel):
    """
    Semantic description of content carried by one physical prop.

    A prop may carry more than one modality.

    Examples:
        printed letter
            -> TEXT

        photograph
            -> IMAGE

        identification card
            -> TEXT + IMAGE + MARKING

        ordinary cup
            -> no content modality
    """

    entity_id: str

    name: str

    content_modalities: List[str] = Field(
        default_factory=list
    )

    text_sensitive: bool = False

    readability_required: bool = False

    visual_detail_sensitive: bool = False

    confidence: float = 0.5

    evidence: List[str] = Field(
        default_factory=list
    )


class ScenePropContentAnalysis(BaseModel):
    """
    Content semantics for all resolved props in one scene.
    """

    scene_number: int

    props: List[
        PropContentSemantics
    ] = Field(
        default_factory=list
    )


class EpisodePropContentAnalysis(BaseModel):
    """
    Prop-content analysis for an entire episode.
    """

    status: str

    episode_id: str

    scenes: List[
        ScenePropContentAnalysis
    ] = Field(
        default_factory=list
    )