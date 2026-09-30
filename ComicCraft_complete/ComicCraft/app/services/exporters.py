from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from fpdf import FPDF

from ..config import get_settings
from ..schemas import ComicPanelLayout


class ComicPDF(FPDF):
    def footer(self):
        self.set_y(-14)
        self.set_font("Helvetica", size=8)
        self.cell(0, 8, f"ComicCraft • Page {self.page_no()}", align="C")


def _local_image_path(image_path: str) -> Path:
    settings = get_settings()
    name = Path(urlparse(image_path).path).name
    path = settings.panels_dir / name
    if not path.exists():
        raise FileNotFoundError(f"Panel image does not exist: {path}")
    return path


def save_pdf(layout: list[ComicPanelLayout]) -> str:
    settings = get_settings()
    filename = f"comiccraft-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}.pdf"
    output = settings.exports_dir / filename

    pdf = ComicPDF()
    pdf.set_auto_page_break(auto=True, margin=18)

    for panel in layout:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 18)
        pdf.cell(0, 12, f"Panel {panel.panel_number}: {panel.title}", new_x="LMARGIN", new_y="NEXT")

        image = _local_image_path(panel.image_path)
        # Keep image inside printable width while preserving aspect ratio.
        pdf.image(str(image), x=15, y=35, w=180)

        pdf.set_y(150)
        pdf.set_font("Helvetica", "I", 10)
        pdf.multi_cell(0, 6, panel.scene_description)

        pdf.ln(3)
        pdf.set_font("Helvetica", "B", 11)
        pdf.multi_cell(0, 6, f"Caption: {panel.caption}")

        pdf.set_font("Helvetica", size=11)
        pdf.multi_cell(0, 6, f"Narration: {panel.narration}")

        if panel.dialogue.strip():
            pdf.set_font("Helvetica", "B", 11)
            pdf.multi_cell(0, 6, f"Dialogue: {panel.dialogue}")

    pdf.output(str(output))
    return filename
