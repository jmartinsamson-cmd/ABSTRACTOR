"""
Bradley Abstract Cover Page Generator
Creates and fills the Bradley Abstract LLC Conveyance and Mortgage Certificate cover page
"""
from typing import Dict, Any, Optional
from pathlib import Path
import io

try:
    import fitz  # PyMuPDF
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False


class BradleyAbstractCoverPage:
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
            
            # Font settings
            fontsize = 11
            fontname = "helv"  # Helvetica
            
            # Fill in the fields
            fields_to_fill = {
                'for': for_field,
                'file_number': file_number,
                'property_description': property_description,
                'period_of_search': period_of_search,
                'present_owners': present_owners,
            }
            
            for field_name, value in fields_to_fill.items():
                if value:
                    x, y = self.FIELD_COORDS[field_name]
                    # Convert coordinates (PyMuPDF uses bottom-left origin)
                    point = fitz.Point(x, page.rect.height - y)
                    
                    if verbose:
                        print(f"Adding {field_name}: {value} at ({x}, {y})")
                    
                    page.insert_text(
                        point,
                        value,
                        fontsize=fontsize,
                        fontname=fontname,
                        color=(0, 0, 0)
                    )
            
            # Handle multi-line sections
            if names_searched:
                self._add_multiline_text(page, names_searched, 'names_searched', fontsize, verbose)
            
            if conveyance_docs:
                self._add_multiline_text(page, conveyance_docs, 'conveyance_docs', fontsize, verbose)
            
            if encumbrances:
                self._add_multiline_text(page, encumbrances, 'encumbrances', fontsize, verbose)
            
            # Save the filled form
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            doc.save(str(output_path))
            doc.close()
            
            if verbose:
                print(f"✓ Cover page saved to: {output_path}")
            
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
        Create a fillable PDF form version with interactive form fields
        
        Args:
            output_path: Where to save the fillable form
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Open the template
            doc = fitz.open(str(self.template_path))
            page = doc[0]
            
            # Define form fields
            fields = [
                {"name": "for_field", "rect": [115, 640, 300, 655], "type": "text"},
                {"name": "file_number", "rect": [320, 640, 450, 655], "type": "text"},
                {"name": "property_description", "rect": [210, 610, 550, 625], "type": "text"},
                {"name": "period_of_search", "rect": [165, 585, 400, 600], "type": "text"},
                {"name": "present_owners", "rect": [165, 555, 550, 570], "type": "text"},
                {"name": "names_searched", "rect": [100, 350, 550, 415], "type": "textarea"},
                {"name": "conveyance_docs", "rect": [100, 280, 550, 345], "type": "textarea"},
                {"name": "encumbrances", "rect": [100, 210, 550, 275], "type": "textarea"},
            ]
            
            # Add form fields to the PDF
            for field in fields:
                widget = fitz.Widget()
                widget.field_name = field["name"]
                widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
                widget.rect = fitz.Rect(field["rect"])
                widget.text_fontsize = 11
                page.add_widget(widget)
            
            # Save the fillable form
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            doc.save(str(output_path))
            doc.close()
            
            print(f"✓ Fillable form created: {output_path}")
            return True
            
        except Exception as e:
            print(f"Error creating fillable form: {e}")
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
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        merged_doc.save(str(output_path))
        
        # Close all documents
        cover_doc.close()
        abstract_doc.close()
        merged_doc.close()
        
        print(f"✓ Merged document saved: {output_path}")
        return True
        
    except Exception as e:
        print(f"Error merging PDFs: {e}")
        return False
