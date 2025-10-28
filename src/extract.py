from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple
import re

try:
    from rapidfuzz import fuzz
except Exception:
    class _F:
        @staticmethod
        def token_set_ratio(a, b):
            return 100 if a.lower() == b.lower() else 0
    fuzz = _F()


@dataclass
class FieldValue:
    value: str
    confidence: float
    source: str  # "zone_text", "regex_text", "ocr_zone", "manual"
    notes: List[str]


def fuzzy_label_match(label: str, candidates: List[str]) -> Tuple[str, float]:
    if not candidates:
        return label, 0.0
    best = max(candidates, key=lambda c: fuzz.token_set_ratio(label, c))
    score = float(fuzz.token_set_ratio(label, best)) / 100.0
    return best, score


def extract_zone_text(words: List[Dict[str, Any]], anchor: str, offset: Dict[str, float]) -> Tuple[str, float, List[str]]:
    """Extract text from a box offset relative to the first matching anchor word."""
    anchors = [w for w in words if anchor.lower() in (w.get("text", "").lower())]
    if not anchors:
        return "", 0.0, ["anchor_not_found"]
    ax0, ay0, ax1, ay1 = anchors[0].get("bbox", (0, 0, 0, 0))
    # Offset box to the right by default (coordinates assumed bottom-origin for words; keep simple bounding)
    zx0 = ax1 + float(offset.get("x", 0))
    zy0 = ay0 + float(offset.get("y", 0))
    zx1 = zx0 + float(offset.get("w", 0))
    zy1 = zy0 + float(offset.get("h", 0))
    in_box = [w for w in words if zx0 <= w.get("bbox", (0, 0, 0, 0))[0] <= zx1 and zy0 <= w.get("bbox", (0, 0, 0, 0))[1] <= zy1]
    text = " ".join(w.get("text", "") for w in in_box).strip()
    confs = [w.get("conf", 0.9) for w in in_box] or [0.0]
    return text, sum(confs) / len(confs), []


def extract_with_regex(text: str, pattern: str) -> str:
    m = re.search(pattern, text or "", re.IGNORECASE | re.MULTILINE)
    if not m:
        return ""
    if "value" in m.groupdict():
        return (m.group("value") or "").strip()
    # else first capture group
    if m.groups():
        return (m.group(1) or "").strip()
    return (m.group(0) or "").strip()


def score_confidence(source: str, base: float, label_score: float) -> float:
    if source == "regex_text":
        c = 0.6
    elif source == "zone_text":
        c = 0.8
    elif source == "ocr_zone":
        c = 0.7 * base
    else:  # manual/edit
        c = base
    # bump by fuzzy label match closeness
    if label_score > 0.95:
        c += 0.05
    elif label_score < 0.6:
        c -= 0.05
    return max(0.0, min(1.0, c))


def extract_fields_from_schema(words: List[Dict[str, Any]], full_text: str, schema: Dict[str, Any]) -> Dict[str, FieldValue]:
    """Use schema's extract rules (zone then regex) to produce FieldValue per field."""
    results: Dict[str, FieldValue] = {}
    field_defs = schema.get("fields", {})
    for key, fdef in field_defs.items():
        label_syns = fdef.get("label_synonyms", [])
        best_label, label_score = fuzzy_label_match(key, label_syns)
        value = ""
        source = ""
        base_conf = 0.9
        # Try zone first if provided
        ex = fdef.get("extract", {})
        if isinstance(ex, dict) and "zone" in ex:
            z = ex.get("zone", {})
            a = z.get("anchor") or best_label or key
            text, ocr_avg, _ = extract_zone_text(words, a, z.get("offset", {}))
            if text:
                value = text
                source = "zone_text"
                base_conf = ocr_avg if ocr_avg else 0.8
        # Fallback regex
        if not value and isinstance(ex, dict) and ex.get("regex"):
            rx = ex.get("regex")
            if isinstance(rx, str) and rx:
                text = extract_with_regex(full_text or "", rx)
            else:
                text = ""
            if text:
                value = text
                source = "regex_text"
                base_conf = 0.6
        if not value:
            results[key] = FieldValue("", 0.0, source or "", ["not_found"])
            continue
        # Postprocess & compute confidence
        from schema_loader import apply_postprocess, validate_value
        value_pp = apply_postprocess(value, fdef.get("postprocess"))
        ok, errs = validate_value(value_pp, fdef.get("validate"))
        conf = score_confidence(source, base_conf, label_score)
        if not ok:
            conf = min(conf, 0.55)  # force red
        results[key] = FieldValue(value_pp, conf, source, errs)
    return results
