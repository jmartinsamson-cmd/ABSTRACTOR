from __future__ import annotations
from typing import Dict, Any, Tuple, Optional
import fitz
from schema_loader import get_field_defs, apply_postprocess, validate_value
from calibration import compute_page_transform
from render import draw_text_in_box


def _box_to_rect(page: fitz.Page, box: dict, transform: dict) -> fitz.Rect:
    x = (box["x"] + transform.get("dx", 0.0)) * transform.get("scale", 1.0)
    y_top = (box["y"] + transform.get("dy", 0.0)) * transform.get("scale", 1.0)
    w = box["w"] * transform.get("scale", 1.0)
    h = box.get("h", 14) * transform.get("scale", 1.0)
    page_h = page.rect.height
    y = page_h - y_top
    return fitz.Rect(x, y - h, x + w, y)


def render_cover_preview_png(template_path: str, schema: Dict[str, Any], data: Dict[str, str], confidences: Optional[Dict[str, float]] = None) -> Tuple[bytes, Dict[str, Dict[str, Any]], Dict[str, float]]:
    """Render the cover with provided data into a PNG and return per-field statuses.

    Returns (png_bytes, field_status, transform) where field_status[field] = {ok, errors, confidence, color}
    """
    # Open template and make a working copy in memory
    doc = fitz.open(template_path)
    page = doc[0]
    transform = compute_page_transform(doc, schema)
    fields = get_field_defs(schema)

    statuses: Dict[str, Dict[str, Any]] = {}

    for key, fdef in fields.items():
        render_def = fdef.get("render", {})
        value = apply_postprocess(data.get(key, ""), fdef.get("postprocess"))
        ok, errs = validate_value(value, fdef.get("validate"))
        # Confidence: combine extraction confidence (if any) with validation heuristic
        base = 0.9 if ok else 0.5
        if confidences and key in confidences:
            conf = max(confidences[key], base)
        else:
            conf = base
        color = "green" if conf >= 0.85 else ("yellow" if conf >= 0.6 else "red")
        statuses[key] = {"ok": ok, "errors": errs, "confidence": conf, "color": color}
        # Draw overlay first
        if render_def:
            rect = _box_to_rect(page, render_def.get("box", {}), transform)
            if color == "green":
                stroke = (0, 0.6, 0)
            elif color == "yellow":
                stroke = (0.9, 0.7, 0)
            else:
                stroke = (0.9, 0, 0)
            page.draw_rect(rect, color=stroke, width=0.8)
            # Render value
            draw_text_in_box(
                page,
                value,
                render_def.get("box", {}),
                render_def.get("font", {}),
                render_def.get("overflow", {}),
                transform,
            )

    # Rasterize to PNG
    pix = page.get_pixmap(dpi=144)
    img_bytes = pix.tobytes("png")
    doc.close()
    return img_bytes, statuses, transform
