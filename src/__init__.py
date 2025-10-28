"""
ABSTRACTOR - Core processing modules

Convenience exports so callers can `import src` and access common utilities.
"""

# Legacy/primary parsers
from .parser import PDFParser
from .field_extractor import FieldExtractor

# Cover generation and assembly
from .cover_page_generator import BradleyAbstractCoverPage
from .pdf_assembler import PDFAssembler

# Schema, calibration, rendering, preview
from .schema_loader import load_schema, get_field_defs, apply_postprocess, validate_value
from .calibration import compute_page_transform
from .render import draw_text_in_box
from .preview import render_cover_preview_png

# Extraction and word indexing
from .extract import extract_fields_from_schema, FieldValue
from .word_index import collect_words_from_sources, ocr_available, ocr_environment_status

__all__ = [
	'PDFParser', 'FieldExtractor',
	'BradleyAbstractCoverPage', 'PDFAssembler',
	'load_schema', 'get_field_defs', 'apply_postprocess', 'validate_value',
	'compute_page_transform', 'draw_text_in_box', 'render_cover_preview_png',
	'extract_fields_from_schema', 'FieldValue',
	'collect_words_from_sources', 'ocr_available', 'ocr_environment_status',
]
