from __future__ import annotations
from typing import Dict, Any
import fitz


def compute_page_transform(doc: fitz.Document, schema: Dict[str, Any]) -> Dict[str, Any]:
    """Compute translation and uniform scale using anchor text on the actual template.

    Returns dict: {dx, dy, scale, status}
    Coordinates are measured in PDF points from top-left in the schema; convert accordingly.
    """
    try:
        page_idx = int(schema.get("template", {}).get("page", 1)) - 1
        page = doc.load_page(page_idx)
        anchor_text = schema.get("calibration", {}).get("anchor_text", "")
        if not anchor_text:
            return {"dx": 0.0, "dy": 0.0, "scale": 1.0, "status": "no_anchor"}
        found = page.search_for(anchor_text)
        if not found:
            return {"dx": 0.0, "dy": 0.0, "scale": 1.0, "status": "anchor_not_found"}
        (x0, y0, x1, y1) = found[0]
        ex = schema.get("calibration", {}).get("anchor_box_expected", {"x": 0, "y": 0, "w": 0, "h": 0})
        # Expected y provided from top-left; convert to bottom-left for comparison if needed
        # However, we only use height to compute scale which is invariant to origin.
        scale = (y1 - y0) / (ex.get("h", 1) or 1)
        dx = x0 - float(ex.get("x", 0))
        dy = y0 - float(ex.get("y", 0))
        return {"dx": dx, "dy": dy, "scale": scale, "status": "ok"}
    except Exception:
        return {"dx": 0.0, "dy": 0.0, "scale": 1.0, "status": "error"}
