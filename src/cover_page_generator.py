"""
Bradley Abstract Cover Page Generator
Creates and fills the Bradley Abstract LLC Conveyance and Mortgage Certificate cover page
"""
from typing import Dict, Any, Optional
from pathlib import Path

try:
    import fitz  # PyMuPDF
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False


class CoverPageGenerator:
    """Generate and fill Bradley Abstract cover pages"""
    
    # Field coordinates (x, y) for form filling - based on letter size (8.5 x 11)
    FIELD_COORDS = {
        'for': (115, 645),           # FOR: field
        'file_number': (320, 645),    # FILE #: field
        'property_description': (210, 615),  # PROPERTY DESCRIPTION: field
        'period_of_search': (165, 590),      # PERIOD OF SEARCH: field
        'present_owners': (165, 560),        # PRESENT OWNER(S): field
        'names_searched': (100, 420),        # NAMES SEARCHED: section
        'conveyance_docs': (100, 350),       # CONVEYANCE DOCUMENTS: section
        'encumbrances': (100, 280),          # ENCUMBRANCES: section
    }
    
    def __init__(self, template_path: str = "templates/bradley_abstract_cover.pdf"):
        """
        Initialize CoverPageGenerator with template
        
        Args:
            template_path: Path to the Bradley Abstract cover template PDF
        """
        self.template_path = Path(template_path)
        
        if not DEPENDENCIES_AVAILABLE:
            raise ImportError(
                "Required dependencies not available. "
                "Install with: pip install PyMuPDF reportlab"
            )
        
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
    
    def fill_cover_page(
        self,
        output_path: str,
        for_field: str = "",
        file_number: str = "",
        property_description: str = "",
        period_of_search: str = "",
        present_owners: str = "",
        names_searched: str = "",
        conveyance_docs: str = "",
        encumbrances: str = "",
        verbose: bool = False
    ) -> bool:
        """
        Fill the Bradley Abstract cover page with provided data
        
        Args:
            output_path: Where to save the filled cover page
            for_field: Client/recipient name
            file_number: File/case number
            property_description: Property address or legal description
            period_of_search: Date range for the search
            present_owners: Current owner name(s)
            names_searched: Names searched in records
            conveyance_docs: Conveyance document details
            encumbrances: Encumbrance details
            verbose: Print detailed progress
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if verbose:
                print(f"Opening template: {self.template_path}")
            
            # Open the template
            doc = fitz.open(str(self.template_path))
            page = doc[0]

            # Schema-driven rendering
            from .schema_loader import load_schema, apply_postprocess, validate_value
            from .calibration import compute_page_transform
            from .render import draw_text_in_box

            schema = load_schema("bradley_cover_v1.yml")
            transform = compute_page_transform(doc, schema)

            # Map input args to schema field keys
            data_map = {
                "for_field": for_field,
                "file_number": file_number,
                "property_description": property_description,
                "period_of_search": period_of_search,
                "present_owners": present_owners,
                "names_searched": names_searched,
                "conveyance_documents": conveyance_docs,
                "encumbrances": encumbrances,
            }

            fields = schema.get("fields", {})
            validation_failures = []
            for key, fdef in fields.items():
                render_def = fdef.get("render", {})
                text_val = apply_postprocess(data_map.get(key, ""), fdef.get("postprocess"))
                ok, errs = validate_value(text_val, fdef.get("validate"))
                if not ok:
                    validation_failures.append({"field": key, "errors": errs})
                if render_def:
                    draw_text_in_box(
                        page,
                        text_val,
                        render_def.get("box", {}),
                        render_def.get("font", {}),
                        render_def.get("overflow", {}),
                        transform,
                    )

            # Save the filled form
            path_obj = Path(output_path)
            path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            doc.save(str(path_obj))
            doc.close()
            
            if verbose:
                if validation_failures:
                    print(f"Validation warnings: {validation_failures}")
                print(f"✓ Cover page saved to: {path_obj}")
            
            return True
            
        except Exception as e:
            print(f"Error filling cover page: {e}")
            return False
    
    def _add_multiline_text(self, page, text: str, field_name: str, fontsize: int, verbose: bool):
        """Add multi-line text to a section"""
        x, y = self.FIELD_COORDS[field_name]
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            if line.strip():
                point = fitz.Point(x, page.rect.height - (y + i * 15))  # 15pt line spacing
                if verbose:
                    print(f"Adding line to {field_name}: {line[:50]}...")
                page.insert_text(point, line, fontsize=fontsize, fontname="helv", color=(0, 0, 0))
    
    def create_fillable_form(self, output_path: str = "templates/bradley_abstract_cover_fillable.pdf") -> bool:
        """
        Deprecated stub: Creating interactive form fields is not supported in this build.
        Returns False to indicate no file created.
        """
        print("Creating interactive form fields is not supported in this build.")
        return False


def merge_cover_with_abstract(cover_path: str, abstract_path: str, output_path: str) -> bool:
    """
    Merge the cover page with the abstract PDF
    
    Args:
        cover_path: Path to the filled cover page
        abstract_path: Path to the abstract/main document
        output_path: Where to save the merged PDF
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Open both PDFs
        cover_doc = fitz.open(cover_path)
        abstract_doc = fitz.open(abstract_path)
        
        # Create new document with cover page first
        merged_doc = fitz.open()
        
        # Insert cover page
        merged_doc.insert_pdf(cover_doc)
        
        # Insert abstract pages
        merged_doc.insert_pdf(abstract_doc)
        
        # Save merged document
        path_obj = Path(output_path)
        path_obj.parent.mkdir(parents=True, exist_ok=True)
        merged_doc.save(str(path_obj))
        
        # Close all documents
        cover_doc.close()
        abstract_doc.close()
        merged_doc.close()
        
        print(f"✓ Merged document saved: {path_obj}")
        return True
        
    except Exception as e:
        print(f"Error merging PDFs: {e}")
        return False


# Compatibility wrapper expected by streamlit_app.py
class BradleyAbstractCoverPage:
    """
    Backwards-compatible adapter so streamlit_app.py can call:
        generator = BradleyAbstractCoverPage()
        generator.generate_cover_page(data, output_path)

    This maps the data dict to CoverPageGenerator.fill_cover_page signature.
    """

    def __init__(self, template_path: Optional[str] = None):
        # Resolve template relative to repository root (src/.. -> templates/...)
        if template_path:
            self.template_path = template_path
        else:
            repo_root = Path(__file__).resolve().parent.parent
            self.template_path = str(repo_root / "templates" / "bradley_abstract_cover.pdf")

    def generate_cover_page(self, data: Dict[str, Any], output_path: str, verbose: bool = False) -> bool:
        try:
            generator = CoverPageGenerator(self.template_path)
        except Exception as e:
            # Surface a concise error and return False per streamlit expectations
            print(f"Cover page generator init failed: {e}")
            return False

        # Map incoming fields with sensible defaults
        return generator.fill_cover_page(
            output_path=output_path,
            for_field=str(data.get("client_name", "")).strip(),
            file_number=str(data.get("file_number", "")).strip(),
            property_description=str(data.get("property_description", "")).strip(),
            period_of_search=str(data.get("period_of_search", "")).strip(),
            present_owners=str(data.get("present_owners", "")).strip(),
            names_searched=str(data.get("names_searched", "")).strip(),
            conveyance_docs=str(data.get("conveyance_documents", "")).strip(),
            encumbrances=str(data.get("encumbrances", "")).strip(),
            verbose=verbose,
        )
