"""
Bradley Abstract Cover Page Generator
Creates and fills the Bradley Abstract LLC Conveyance and Mortgage Certificate cover page
"""
from typing import Dict, Any, Optional, Tuple, TYPE_CHECKING
from pathlib import Path
import io

try:
    import fitz  # type: ignore[import-untyped]
    from reportlab.pdfgen import canvas  # type: ignore[import-untyped]
    from reportlab.lib.pagesizes import letter  # type: ignore[import-untyped]
    from reportlab.lib.units import inch  # type: ignore[import-untyped]
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False


class BradleyAbstractCoverPage:
    """Generate and fill Bradley Abstract cover pages"""
    
    # Field coordinates (x, y) measured from the top-left corner of the page (letter size 8.5 x 11)
    FIELD_COORDS: Dict[str, Tuple[float, float]] = {
        'for': (110, 130),
        'file_number': (330, 130),
        'property_description': (110, 175),
        'period_of_search': (110, 205),
        'present_owners': (110, 235),
        'names_searched': (70, 360),
        'conveyance_docs': (70, 433),
        'encumbrances': (70, 506),
        'tax_information': (70, 585),
    }

    # Width and height of the text boxes for each field (in points)
    FIELD_RECT_SIZES: Dict[str, Tuple[float, float]] = {
        'for': (190, 18),
        'file_number': (190, 18),
        'property_description': (450, 32),
        'period_of_search': (450, 32),
        'present_owners': (450, 32),
        'names_searched': (475, 65),
        'conveyance_docs': (475, 80),
        'encumbrances': (475, 90),
        'tax_information': (475, 18),
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
        tax_information: str = "",
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
                'names_searched': names_searched,
                'conveyance_docs': conveyance_docs,
                'encumbrances': encumbrances,
                'tax_information': tax_information,
            }

            for field_name, value in fields_to_fill.items():
                if value:
                    self._add_text_to_field(page, field_name, value, fontsize, fontname, verbose)
            
            # Save the filled form
            output_path_path = Path(output_path)
            output_path_path.parent.mkdir(parents=True, exist_ok=True)
            
            doc.save(str(output_path_path))
            doc.close()
            
            if verbose:
                print(f"✓ Cover page saved to: {output_path}")
            
            return True
            
        except Exception as e:
            print(f"Error filling cover page: {e}")
            return False
    
    def _add_text_to_field(
        self,
        page,
        field_name: str,
        text: str,
        fontsize: int,
        fontname: str,
        verbose: bool
    ) -> None:
        """Render text inside the configured rectangle for a given field"""
        coords = self.FIELD_COORDS.get(field_name)
        size = self.FIELD_RECT_SIZES.get(field_name)
        if not coords or not size:
            if verbose:
                print(f"Skipping unknown field '{field_name}'")
            return

        x, y = coords
        width, height = size
        rect = self._make_rect(page, x, y, width, height)
        cleaned_text = text.replace('\r\n', '\n').strip()
        if not cleaned_text:
            return

        if verbose:
            print(f"Adding {field_name}: '{cleaned_text[:60]}' into rect {rect}")

        leftover = page.insert_textbox(
            rect,
            cleaned_text,
            fontsize=fontsize,
            fontname=fontname,
            color=(0, 0, 0),
            align=fitz.TEXT_ALIGN_LEFT
        )

        if leftover and verbose:
            print(f"Warning: text truncated for field '{field_name}'")

    def _make_rect(self, page, x: float, y: float, width: float, height: float) -> fitz.Rect:
        """Convert top-left coordinates to a PyMuPDF rectangle"""
        top = page.rect.height - y
        bottom = top - height
        return fitz.Rect(x, bottom, x + width, top)
    
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
            # Add form fields to the PDF based on configured coordinates
            for field_name, (x, y) in self.FIELD_COORDS.items():
                width, height = self.FIELD_RECT_SIZES.get(field_name, (400, 18))
                rect = self._make_rect(page, x, y, width, height)

                widget = fitz.Widget()
                widget.field_name = field_name
                widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
                widget.rect = rect
                widget.text_fontsize = 11

                if field_name in {"names_searched", "conveyance_docs", "encumbrances", "property_description", "period_of_search", "present_owners"}:
                    widget.field_flags = fitz.PDF_WIDGET_FLAG_MULTILINE

                page.add_widget(widget)
            
            # Save the fillable form
            output_path_path = Path(output_path)
            output_path_path.parent.mkdir(parents=True, exist_ok=True)
            doc.save(str(output_path_path))
            doc.close()
            
            print(f"✓ Fillable form created: {output_path_path}")
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
        output_path_path = Path(output_path)
        output_path_path.parent.mkdir(parents=True, exist_ok=True)
        merged_doc.save(str(output_path_path))
        
        # Close all documents
        cover_doc.close()
        abstract_doc.close()
        merged_doc.close()
        
        print(f"✓ Merged document saved: {output_path_path}")
        return True
        
    except Exception as e:
        print(f"Error merging PDFs: {e}")
        return False
