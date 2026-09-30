import json
from google import genai
from ..config import get_settings
from ..schemas import ComicOutline, PromptRequest


def _client():
    settings = get_settings()
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")
    return genai.Client(api_key=settings.gemini_api_key)


def generate_outline(request: PromptRequest) -> ComicOutline:
    settings = get_settings()
    prompt = f'''
Create a coherent {request.panels}-panel comic outline.

User story idea: {request.story_prompt}
Main character: {request.character_name}
Setting: {request.setting}
Tone: {request.tone}
Art style: {request.art_style}

Requirements:
- Exactly {request.panels} panels.
- Maintain the same main character and visual identity across panels.
- Each panel needs a concise title, scene description, and a detailed image-generation prompt.
- The image prompt must describe composition, environment, character action, lighting, camera framing,
  and the requested art style.
- Do not put speech text inside the image prompt.
- Return JSON matching the requested schema only.
'''
    response = _client().models.generate_content(
        model=settings.gemini_outline_model,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": ComicOutline.model_json_schema(),
            "temperature": 0.9,
        },
    )
    raw = response.text or ""
    try:
        data = json.loads(raw)
        outline = ComicOutline.model_validate(data)
    except Exception as exc:
        raise RuntimeError(f"Gemini outline response was not valid structured JSON: {exc}") from exc

    if len(outline.panels) != request.panels:
        raise RuntimeError(
            f"Gemini returned {len(outline.panels)} panels; expected {request.panels}."
        )
    return outline
