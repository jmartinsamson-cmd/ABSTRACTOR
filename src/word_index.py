from __future__ import annotations
from typing import List, Dict, Any, Union
from pathlib import Path
import shutil
import fitz

try:
    from pdf2image.pdf2image import convert_from_path  # explicit module path
    import pytesseract
except Exception:
    convert_from_path = None
    pytesseract = None


def words_from_pdf_text_layer(pdf_path: Union[str, Path]) -> List[Dict[str, Any]]:
    """Extract word boxes using PyMuPDF's text layer (no confidence available)."""
    path = str(pdf_path)
    doc = fitz.open(path)
    words: List[Dict[str, Any]] = []
    for pno in range(len(doc)):
        page = doc[pno]
        for w in page.get_text("words"):
            x0, y0, x1, y1, text, *_ = w
            words.append({"text": text, "bbox": (x0, y0, x1, y1), "conf": 0.9, "page": pno})
    doc.close()
    return words


essential_ocr_note = "ocr_unavailable"

def words_from_pdf_ocr(pdf_path: Union[str, Path]) -> List[Dict[str, Any]]:
    """Fallback OCR: rasterize pages and use Tesseract to get word boxes with confidences.
    Coordinates are converted from pixels to PDF points assuming 72 dpi baseline.
    """
    if convert_from_path is None or pytesseract is None:
        return []
    try:
        images = convert_from_path(str(pdf_path), dpi=200)
    except Exception:
        # Missing poppler/pdfinfo or tesseract env; gracefully skip OCR
        return []
    results: List[Dict[str, Any]] = []
    for idx, img in enumerate(images):
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        w_img, h_img = img.size
        # scale factor from pixels to points: at 200 dpi, 1 inch = 200 px = 72 pt => 72/200 per px
        s = 72.0 / 200.0
        n = len(data.get("text", []))
        for i in range(n):
            txt = data["text"][i]
            if not txt or txt.strip() == "":
                continue
            x = data["left"][i] * s
            y = (h_img - data["top"][i]) * s  # invert y origin to bottom-left
            w = data["width"][i] * s
            h = data["height"][i] * s
            conf = float(data.get("conf", [0])[i])
            conf = 0.0 if conf == -1 else conf / 100.0
            results.append({
                "text": txt,
                "bbox": (x, y - h, x + w, y),
                "conf": conf,
                "page": idx,
            })
    return results


def collect_words_from_sources(pdf_paths: List[Union[str, Path]], prefer_ocr: bool = False) -> List[Dict[str, Any]]:
    """Aggregate words from each PDF.

    - If prefer_ocr=True, try OCR first then fall back to text layer.
    - If prefer_ocr=False, try text layer first then fall back to OCR.
    """
    all_words: List[Dict[str, Any]] = []
    for p in pdf_paths:
        if prefer_ocr:
            ocr_words = words_from_pdf_ocr(p)
            if ocr_words:
                all_words.extend(ocr_words)
                continue
            txt_words = words_from_pdf_text_layer(p)
            all_words.extend(txt_words)
        else:
            txt_words = words_from_pdf_text_layer(p)
            if txt_words:
                all_words.extend(txt_words)
                continue
            ocr_words = words_from_pdf_ocr(p)
            all_words.extend(ocr_words)
    return all_words


def ocr_available() -> bool:
    """Return True if OCR libraries are importable and poppler/tesseract binaries seem present."""
    if convert_from_path is None or pytesseract is None:
        return False
    # tesseract binary
    t_ok = shutil.which("tesseract") is not None
    # poppler's pdfinfo binary for pdf2image
    p_ok = shutil.which("pdfinfo") is not None
    return t_ok and p_ok


def ocr_environment_status() -> Dict[str, bool]:
    """Detailed environment check for UI messaging."""
    return {
        "pytesseract": pytesseract is not None,
        "pdf2image": convert_from_path is not None,
        "tesseract_bin": shutil.which("tesseract") is not None,
        "poppler_pdfinfo": shutil.which("pdfinfo") is not None,
    }
