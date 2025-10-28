from __future__ import annotations
import os
from pathlib import Path
from typing import Any, Dict
import yaml

_DEFAULT_SCHEMA_NAME = "bradley_cover_v1.yml"


def load_schema(name: str | None = None) -> Dict[str, Any]:
    """Load a YAML schema from mappings/ directory.

    If name is None, loads the default bradley cover schema.
    Returns a dict with keys: template, calibration, fields.
    """
    repo_root = Path(__file__).resolve().parent.parent
    mappings_dir = repo_root / "mappings"
    if name is None:
        name = _DEFAULT_SCHEMA_NAME
    schema_path = mappings_dir / name if not name.endswith(".yml") else mappings_dir / name
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema not found: {schema_path}")
    with open(schema_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict) or "fields" not in data:
        raise ValueError(f"Invalid schema format in {schema_path}")
    return data


def get_field_defs(schema: Dict[str, Any]) -> Dict[str, Any]:
    return schema.get("fields", {})


def apply_postprocess(value: str, steps: list[str] | None) -> str:
    if value is None:
        return ""
    text = str(value)
    steps = steps or []
    for step in steps:
        if step == "trim":
            text = text.strip()
        elif step == "collapse_spaces":
            text = " ".join(text.split())
        elif step == "uppercase":
            text = text.upper()
        elif step == "lowercase":
            text = text.lower()
        elif step == "titlecase":
            try:
                text = text.title()
            except Exception:
                pass
        # More transforms can be added here
    return text


def validate_value(value: str, rules: list[dict] | None) -> tuple[bool, list[str]]:
    import re
    rules = rules or []
    errors: list[str] = []
    ok = True
    for rule in rules:
        rtype = rule.get("type")
        if rtype == "not_empty":
            if not value or not str(value).strip():
                ok = False
                errors.append("value required")
        elif rtype == "regex":
            pattern = rule.get("pattern", "")
            if pattern:
                if not re.match(pattern, str(value) or ""):
                    ok = False
                    errors.append("format mismatch")
        elif rtype == "min_len":
            n = int(rule.get("n", 0))
            if len(str(value) or "") < n:
                ok = False
                errors.append(f"min_len {n}")
        # Extendable for max_len, allowed_set, etc.
    return ok, errors
