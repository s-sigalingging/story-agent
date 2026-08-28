from pydantic import BaseModel
from typing import List


class SceneStructure(BaseModel):
    scene_number: int

    narrative_function: str

    dramatic_role: str

    purpose: str

    information_revealed: List[str]

    open_questions: List[str]

    tension_level: int


class StoryStructure(BaseModel):
    status: str

    overall_arc: str

    scenes: List[SceneStructure]