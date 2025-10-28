from __future__ import annotations
from typing import Dict, Any
import fitz


def _schema_box_to_rect(page: fitz.Page, box: Dict[str, float], transform: Dict[str, float]) -> fitz.Rect:
    """Convert a schema box (x,y from top-left) to a fitz.Rect with transform applied."""
    x = (box["x"] + transform.get("dx", 0.0)) * transform.get("scale", 1.0)
    y_top = (box["y"] + transform.get("dy", 0.0)) * transform.get("scale", 1.0)
    # Convert top-origin y to bottom-origin y for fitz
    page_h = page.rect.height
    y = page_h - y_top
    w = box["w"] * transform.get("scale", 1.0)
    h = box.get("h", 14) * transform.get("scale", 1.0)
    # fitz.Rect expects bottom-left origin with y increasing upwards
    # so rect = (x, y-h, x+w, y)
    return fitz.Rect(x, y - h, x + w, y)


def draw_text_in_box(
    page: fitz.Page,
    text: str,
    box: Dict[str, float],
    font: Dict[str, Any],
    overflow: Dict[str, Any],
    transform: Dict[str, float],
):
    """Render text inside a box with autoshrink and optional wrap.

    - Schema coords are x,y from top-left.
    - overflow.mode: 'wrap' or 'autoshrink_min'
    - For 'wrap', use insert_textbox. For single-line, try shrinking to fit width.
    """
    rect = _schema_box_to_rect(page, box, transform)
    fontname = font.get("name", "helv")
    leading = font.get("leading", font.get("size", 11) + 1)
    max_size = float(font.get("size", 11))
    mode = (overflow or {}).get("mode", "autoshrink_min")
    min_size = float((overflow or {}).get("min_size", max_size))

    text = str(text or "").replace("\r", " ").replace("\t", " ").strip()

    if mode == "wrap":
        # render wrapped into the rectangle; fitz will clip extra lines
        page.insert_textbox(
            rect,
            text,
            fontname=fontname,
            fontsize=max_size,
            align=0,
            lineheight=leading / max_size if max_size else 1.2,
        )
        return

    # single-line autoshrink to fit width
    size = max_size
    while size >= min_size:
        # Use module-level get_text_length (Page method not available in this PyMuPDF)
        tw = fitz.get_text_length(text, fontname=fontname, fontsize=size)
        if tw <= rect.width - 0.5:  # small tolerance
            break
        size -= 0.5
    # Align to baseline at rect top (since rect defined from top-left schema)
    # We'll place text at left, vertically within rect from its top
    page.insert_text(
        fitz.Point(rect.x0, rect.y1),
        text,
        fontname=fontname,
        fontsize=size,
        color=(0, 0, 0),
    )
