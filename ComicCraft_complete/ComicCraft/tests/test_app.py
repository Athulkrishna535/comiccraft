import os
from pathlib import Path

os.environ.setdefault("IMAGE_PROVIDER", "placeholder")

from fastapi.testclient import TestClient
from app.main import app
from app.config import get_settings


client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_homepage():
    response = client.get("/")
    assert response.status_code == 200
    assert "ComicCraft" in response.text


def test_json_validation_rejects_blank_story():
    response = client.post("/generate-comic/json", json={
        "story_prompt": "",
        "character_name": "Fenn",
        "setting": "Forest",
        "tone": "dramatic",
        "art_style": "comic book",
        "panels": 5,
    })
    assert response.status_code == 422


def test_download_rejects_path_traversal():
    response = client.get("/download/../secret.pdf")
    assert response.status_code in (400, 404)


def test_placeholder_image():
    from app.services.image_generator import generate_image
    path = generate_image("A fox in a forest", 99, "test")
    assert path.startswith("/static/panels/")
    filename = Path(path).name
    assert (get_settings().panels_dir / filename).exists()
