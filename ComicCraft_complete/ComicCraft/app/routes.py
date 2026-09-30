from pathlib import Path
from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from .config import get_settings
from .schemas import PromptRequest
from .services.gemini_flash import generate_outline
from .services.gemini_pro import generate_story
from .services.image_generator import generate_image
from .services.layout_builder import build_comic_layout
from .services.exporters import save_pdf

router = APIRouter()
settings = get_settings()
templates = Jinja2Templates(directory=str(settings.templates_dir))


def _run_generation(payload: PromptRequest):
    outline = generate_outline(payload)
    story = generate_story(payload, outline)

    image_paths = []
    for panel in outline.panels:
        visual_prompt = (
            f"{panel.image_prompt}. Clean comic composition, consistent character design, "
            f"no text, no watermark, high visual clarity."
        )
        image_paths.append(generate_image(visual_prompt, panel.panel_number, panel.title))

    layout = build_comic_layout(outline, story, image_paths)
    pdf_filename = save_pdf(layout)
    return outline, story, layout, pdf_filename


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"max_panels": settings.max_panels, "default_panels": settings.default_panels},
    )


@router.post("/generate", response_class=HTMLResponse)
async def generate(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form("dramatic"),
    art_style: str = Form("comic book"),
    panels: int = Form(5),
):
    try:
        payload = PromptRequest(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
            panels=panels,
        )
        outline, story, layout, pdf_filename = _run_generation(payload)
        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "layout": layout,
                "pdf_filename": pdf_filename,
                "request_data": payload.model_dump(),
            },
        )
    except Exception as exc:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            status_code=500,
            context={
                "max_panels": settings.max_panels,
                "default_panels": settings.default_panels,
                "error": str(exc),
                "form": {
                    "story_prompt": story_prompt,
                    "character_name": character_name,
                    "setting": setting,
                    "tone": tone,
                    "art_style": art_style,
                    "panels": panels,
                },
            },
        )


@router.post("/generate-comic/json")
async def generate_comic_json(payload: PromptRequest):
    try:
        outline, story, layout, pdf_filename = _run_generation(payload)
        return {
            "success": True,
            "request": payload.model_dump(),
            "outline": outline.model_dump(),
            "story": story.model_dump(),
            "layout": [panel.model_dump() for panel in layout],
            "pdf_url": f"/download/{pdf_filename}",
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/test-image")
async def test_image(prompt: str = Form(...)):
    try:
        path = generate_image(prompt, 1, "test-image")
        return {"success": True, "image_url": path}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/download/{filename}")
async def download_pdf(filename: str):
    safe_name = Path(filename).name
    if safe_name != filename or not safe_name.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid filename.")
    path = settings.exports_dir / safe_name
    if not path.exists():
        raise HTTPException(status_code=404, detail="PDF not found.")
    return FileResponse(
        path,
        media_type="application/pdf",
        filename=safe_name,
    )


@router.get("/export-success", response_class=HTMLResponse)
async def export_success(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={},
    )


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "gemini_configured": bool(settings.gemini_api_key),
        "image_provider": settings.image_provider,
        "hf_configured": bool(settings.hf_token),
    }
