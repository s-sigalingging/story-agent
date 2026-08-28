from typing import List

from pydantic import BaseModel, Field


class Scene(BaseModel):
    scene_number: int = Field(gt=0)

    duration_seconds: int = Field(gt=0)

    location: str

    characters: List[str] = Field(default_factory=list)

    dialogue: str = ""

    visual_description: str = ""

    narrative_purpose: str = ""

    camera_direction: str = ""

    continuity_notes: str = ""


class Episode(BaseModel):
    episode_id: str

    title: str

    target_duration_seconds: int = Field(gt=0)

    scenes: List[Scene] = Field(default_factory=list)

    story_summary: str = ""

    opening_hook: str = ""

    ending_hook: str = ""

    tone: str = ""

    visual_style: str = ""