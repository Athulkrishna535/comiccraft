import json
from google import genai
from ..config import get_settings
from ..schemas import ComicOutline, ComicStory, PromptRequest


def _client():
    settings = get_settings()
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")
    return genai.Client(api_key=settings.gemini_api_key)


def generate_story(request: PromptRequest, outline: ComicOutline) -> ComicStory:
    settings = get_settings()
    outline_json = outline.model_dump_json(indent=2)
    prompt = f'''
Expand the following comic outline into a polished comic script.

Story idea: {request.story_prompt}
Main character: {request.character_name}
Setting: {request.setting}
Tone: {request.tone}
Art style: {request.art_style}

Outline:
{outline_json}

Requirements:
- Keep exactly the same number and order of panels.
- Keep names, setting, continuity, and character actions consistent.
- For every panel provide a short caption, narration, and dialogue.
- Dialogue should be natural and brief enough for a comic speech bubble.
- Narration should advance the story rather than repeat the scene description.
- Return JSON only using the requested schema.
'''
    response = _client().models.generate_content(
        model=settings.gemini_story_model,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": ComicStory.model_json_schema(),
            "temperature": 0.85,
        },
    )
    raw = response.text or ""
    try:
        story = ComicStory.model_validate(json.loads(raw))
    except Exception as exc:
        raise RuntimeError(f"Gemini story response was not valid structured JSON: {exc}") from exc

    if len(story.panels) != len(outline.panels):
        raise RuntimeError("Gemini story panel count does not match the outline.")
    return story
