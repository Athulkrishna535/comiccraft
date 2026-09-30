import html
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from huggingface_hub import InferenceClient

from ..config import get_settings


def _safe_name(text: str, index: int) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()[:50] or "panel"
    return f"{index:02d}-{slug}.png"


def _placeholder(prompt: str, path: Path, index: int) -> None:
    # A deterministic, dependency-light fallback for UI/PDF testing.
    image = Image.new("RGB", (1024, 768), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((25, 25, 999, 743), outline="black", width=5)
    draw.text((55, 60), f"ComicCraft — Panel {index}", fill="black")
    lines = [prompt[i:i+70] for i in range(0, min(len(prompt), 420), 70)]
    y = 130
    for line in lines:
        draw.text((55, y), line, fill="black")
        y += 35
    draw.text((55, 650), "IMAGE_PROVIDER=placeholder", fill="black")
    image.save(path)


def _hf_image(prompt: str, path: Path) -> None:
    settings = get_settings()
    if not settings.hf_token:
        raise RuntimeError("HF_TOKEN is not configured for Hugging Face image generation.")
    client = InferenceClient(provider="auto", api_key=settings.hf_token)
    image = client.text_to_image(
        prompt=prompt,
        model=settings.hf_image_model,
    )
    image.save(path)


def _local_image(prompt: str, path: Path) -> None:
    try:
        from diffusers import StableDiffusionPipeline
        import torch
    except ImportError as exc:
        raise RuntimeError(
            "Local image mode requires requirements-local-sd.txt and a suitable PyTorch install."
        ) from exc

    settings = get_settings()
    dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    pipe = StableDiffusionPipeline.from_pretrained(settings.local_image_model, torch_dtype=dtype)
    if torch.cuda.is_available():
        pipe = pipe.to("cuda")
    result = pipe(prompt, num_inference_steps=25, guidance_scale=7.0).images[0]
    result.save(path)


def generate_image(prompt: str, index: int, title: str) -> str:
    settings = get_settings()
    filename = _safe_name(title, index)
    path = settings.panels_dir / filename

    if settings.image_provider.lower() == "placeholder":
        _placeholder(prompt, path, index)
    elif settings.image_provider.lower() == "local":
        _local_image(prompt, path)
    elif settings.image_provider.lower() == "hf":
        _hf_image(prompt, path)
    else:
        raise RuntimeError(
            f"Unsupported IMAGE_PROVIDER={settings.image_provider}. Use hf, local, or placeholder."
        )

    return f"/static/panels/{filename}"
