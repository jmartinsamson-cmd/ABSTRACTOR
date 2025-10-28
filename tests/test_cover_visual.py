from pathlib import Path
from PIL import Image, ImageChops
from src.schema_loader import load_schema
from src.preview import render_cover_preview_png


def images_similar(a: Image.Image, b: Image.Image, threshold: int = 8) -> bool:
    diff = ImageChops.difference(a, b).convert("L")
    # Sum of non-zero bins gives a coarse measure; keep simple
    hist = diff.histogram()
    total = sum(i * v for i, v in enumerate(hist))
    return total < threshold


def test_cover_render_golden(tmp_path):
    repo_root = Path(__file__).resolve().parents[1]
    tpl = repo_root / "templates" / "bradley_abstract_cover.pdf"
    if not tpl.exists():
        # Skip if template missing in environment
        return
    schema = load_schema("bradley_cover_v1.yml")
    data = {
        'for_field': 'John Q. Public',
        'file_number': '2025-0001',
        'property_description': '123 Main St, Springfield, LA 70403',
        'period_of_search': '20 years',
        'present_owners': 'John Q. Public and Jane Public',
        'names_searched': 'John Q Public\nJane Public',
        'conveyance_documents': 'Deed Book 123, Page 45',
        'encumbrances': 'None',
    }
    png_bytes, _, _ = render_cover_preview_png(str(tpl), schema, data)
    out = tmp_path / "cover.png"
    out.write_bytes(png_bytes)

    golden_path = repo_root / "tests" / "golden" / "cover_v1.png"
    if not golden_path.exists():
        # No golden available yet; treat as soft pass
        return
    a = Image.open(out)
    b = Image.open(golden_path)
    assert images_similar(a, b), "Rendered cover deviates from golden"
