from typing import Literal
from pydantic import BaseModel, Field, field_validator


Tone = Literal["light-hearted", "dramatic", "poetic", "funny"]
ArtStyle = Literal["anime", "pixel art", "comic book", "realistic"]


class PromptRequest(BaseModel):
    story_prompt: str = Field(min_length=5, max_length=2000)
    character_name: str = Field(min_length=1, max_length=80)
    setting: str = Field(min_length=1, max_length=120)
    tone: Tone = "dramatic"
    art_style: ArtStyle = "comic book"
    panels: int = Field(default=5, ge=1, le=8)

    @field_validator("story_prompt", "character_name", "setting")
    @classmethod
    def strip_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be blank.")
        return value


class ComicPanel(BaseModel):
    panel_number: int = Field(ge=1)
    title: str
    scene_description: str
    image_prompt: str


class ComicOutline(BaseModel):
    panels: list[ComicPanel]


class StoryPanel(BaseModel):
    panel_number: int
    title: str
    caption: str
    narration: str
    dialogue: str


class ComicStory(BaseModel):
    panels: list[StoryPanel]


class ComicPanelLayout(BaseModel):
    panel_number: int
    title: str
    image_path: str
    scene_description: str
    caption: str
    narration: str
    dialogue: str
    image_prompt: str
