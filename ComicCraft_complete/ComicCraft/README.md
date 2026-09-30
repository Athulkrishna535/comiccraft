# ComicCraft — AI Comic Story Creator

ComicCraft is a FastAPI + Jinja2 web application that turns a story idea into a panel-by-panel comic. It follows the supplied project documentation: structured outline generation, detailed narration/dialogue, image generation, preview, and PDF export.

## Architecture

- **Frontend:** HTML + CSS + Jinja2 + small JavaScript enhancement.
- **Backend:** FastAPI.
- **Story AI:** Google Gemini through the current `google-genai` SDK.
- **Image AI:** Hugging Face Inference Providers by default. A local Diffusers mode is also included.
- **PDF:** `fpdf2`.
- **Validation:** Pydantic.
- **Tests:** pytest + FastAPI TestClient.

The original documentation specifies Gemini Flash/Pro and Stable Diffusion. The default configuration keeps that conceptual split while using the current Google SDK and a hosted Hugging Face inference path, so users do not have to download a multi-gigabyte diffusion model just to start the project.

## Project structure

```text
ComicCraft/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── routes.py
│   ├── schemas.py
│   ├── services/
│   │   ├── gemini_flash.py
│   │   ├── gemini_pro.py
│   │   ├── image_generator.py
│   │   ├── layout_builder.py
│   │   └── exporters.py
│   └── models/
├── templates/
│   ├── index.html
│   ├── comic_preview.html
│   └── export_success.html
├── static/
│   ├── css/style.css
│   ├── js/app.js
│   ├── panels/
│   └── exports/
├── tests/
├── .env.example
├── requirements.txt
├── requirements-local-sd.txt
└── README.md
```

## VS Code setup

1. Open the `ComicCraft` folder in VS Code.
2. Open **Terminal → New Terminal**.
3. Create and activate a virtual environment:

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

4. Copy `.env.example` to `.env`.
5. Add your Gemini API key. If you want live images, add a Hugging Face token with inference permissions.
6. Run:

```bash
uvicorn app.main:app --reload
```

7. Open `http://127.0.0.1:8000`.
8. API documentation: `http://127.0.0.1:8000/docs`.

## API endpoints

- `GET /` — homepage
- `POST /generate` — browser form workflow
- `POST /generate-comic/json` — JSON API workflow
- `POST /test-image` — image-generation test
- `GET /download/{filename}` — PDF download
- `GET /export-success` — export confirmation
- `GET /health` — health/configuration check

## JSON example

```json
{
  "story_prompt": "A brave fox exploring an enchanted forest",
  "character_name": "Fenn",
  "setting": "Enchanted forest",
  "tone": "dramatic",
  "art_style": "comic book",
  "panels": 5
}
```

## Image providers

### Hugging Face (recommended)

Set:

```env
IMAGE_PROVIDER=hf
HF_TOKEN=...
HF_IMAGE_MODEL=black-forest-labs/FLUX.1-schnell
```

### Local Stable Diffusion

Install a suitable PyTorch build for your computer, then:

```bash
pip install -r requirements-local-sd.txt
```

Set:

```env
IMAGE_PROVIDER=local
LOCAL_IMAGE_MODEL=runwayml/stable-diffusion-v1-5
```

The first local run downloads the model and can require significant disk space/RAM/VRAM.

### Placeholder mode

For UI development without any image provider:

```env
IMAGE_PROVIDER=placeholder
```

This still exercises the complete FastAPI → Gemini → layout → PDF pipeline when Gemini is configured, while using generated SVG placeholder panels.

## Testing

Run:

```bash
pytest -q
```

The tests cover the health endpoint, form validation, JSON validation, and PDF download route without calling paid/external AI services.

## Notes

The source documentation mentions the older `google-generativeai` package and Gemini 1.5 model names. This implementation uses the newer `google-genai` SDK and configurable model IDs. Keep the model IDs in `.env` so they can be updated independently of application code.
