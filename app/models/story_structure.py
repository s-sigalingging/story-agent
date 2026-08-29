from typing import List

from pydantic import BaseModel, Field


class SceneStructure(BaseModel):
    scene_number: int = Field(gt=0)

    narrative_function: str

    dramatic_role: str

    purpose: str

    information_revealed: List[str] = Field(
        default_factory=list
    )

    open_questions: List[str] = Field(
        default_factory=list
    )

    tension_level: int = Field(
        ge=0,
        le=10,
    )


class StoryStructure(BaseModel):
    status: str

    overall_arc: str

    scenes: List[SceneStructure] = Field(
        default_factory=list
    )