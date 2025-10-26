"""
Form Filler - Populate PDF forms with extracted data using coordinate-based text overlay
"""
from typing import Dict, Any
from pathlib import Path

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

import config


class FormFiller:
    """Fill PDF forms with extracted field data using coordinate-based text overlay"""
    
    def __init__(self, template_path: str):
        """
        Initialize FormFiller with template PDF
        
        Args:
            template_path: Path to the template PDF (STEP2.pdf)
        """
        self.template_path = Path(template_path)
        
        if not PYMUPDF_AVAILABLE:
            raise ImportError(
                "PyMuPDF is required for form filling. "
                "Install it with: pip install PyMuPDF"
            )
        
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template PDF not found: {template_path}")
    
    def fill_form(self, data: Dict[str, Any], output_path: str, verbose: bool = False) -> bool:
        """
        Fill the form template with provided data using coordinate-based overlay
        
        Args:
            data: Dictionary of field names and values from extraction
            output_path: Where to save the filled form
            verbose: Print detailed progress information
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Map extracted fields to form coordinates
            mapped_data = self.map_fields(data)
            
            if verbose:
                print(f"\n{'='*70}")
                print("FILLING FORM: {}".format(self.template_path.name))
                print(f"{'='*70}")
                print(f"Mapped {len(mapped_data)} fields to form coordinates")
            
            # Open template PDF
            doc = fitz.open(str(self.template_path))
            
            # Add text overlays
            for field_key, value in mapped_data.items():
                coord_info = config.FORM_FIELD_COORDINATES.get(field_key)
                if not coord_info:
                    if verbose:
                        print(f"Warning: No coordinates defined for field '{field_key}'")
                    continue
                
                page_num = coord_info.get('page', 0)
                x = coord_info.get('x', 100)
                y = coord_info.get('y', 700)
                font_size = coord_info.get('font_size', 10)
                max_width = coord_info.get('max_width')
                
                # Get the page
                if page_num >= len(doc):
                    if verbose:
                        print(f"Warning: Page {page_num} not found in template")
                    continue
                
                page = doc[page_num]
                
                # PyMuPDF uses top-left origin, convert from bottom-left
                page_height = page.rect.height
                y_adjusted = page_height - y
                
                # Prepare text
                text = str(value)
                
                # Insert text
                point = fitz.Point(x, y_adjusted)
                
                # Handle long text with wrapping if max_width specified
                if max_width and len(text) * font_size * 0.6 > max_width:
                    # Simple word wrap
                    words = text.split()
                    lines = []
                    current_line = []
                    
                    for word in words:
                        test_line = ' '.join(current_line + [word])
                        if len(test_line) * font_size * 0.6 < max_width:
                            current_line.append(word)
                        else:
                            if current_line:
                                lines.append(' '.join(current_line))
                            current_line = [word]
                    
                    if current_line:
                        lines.append(' '.join(current_line))
                    
                    # Insert each line
                    for i, line in enumerate(lines):
                        line_point = fitz.Point(x, y_adjusted + (i * font_size * 1.2))
                        page.insert_text(
                            line_point,
                            line,
                            fontsize=font_size,
                            color=(0, 0, 0)
                        )
                else:
                    page.insert_text(
                        point,
                        text,
                        fontsize=font_size,
                        color=(0, 0, 0)
                    )
                
                if verbose:
                    print(f"  • {field_key}: '{value}' at ({x}, {y}) on page {page_num}")
            
            # Save filled form
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            doc.save(str(output_path))
            doc.close()
            
            if verbose:
                print(f"\n✓ Form filled successfully: {output_path}")
            
            return True
            
        except Exception as e:
            print(f"Error filling form: {e}")
            if verbose:
                import traceback
                traceback.print_exc()
            return False
    
    def map_fields(self, extracted_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Map extracted data to form field coordinates
        
        Args:
            extracted_data: Data from FieldExtractor
            
        Returns:
            Dictionary mapping coordinate keys to values
        """
        mapped = {}
        
        # Map simple fields
        for extracted_key, coord_key in config.FORM_FIELD_MAPPING.items():
            value = extracted_data.get(extracted_key)
            if value:
                mapped[coord_key] = str(value)
        
        # Map nested deed_info fields
        deed_info = extracted_data.get('deed_info', {})
        if isinstance(deed_info, dict):
            for deed_key, coord_key in config.DEED_INFO_MAPPING.items():
                value = deed_info.get(deed_key)
                if value:
                    mapped[coord_key] = str(value)
        
        # Map nested tax_info fields
        tax_info = extracted_data.get('tax_info', {})
        if isinstance(tax_info, dict):
            for tax_key, coord_key in config.TAX_INFO_MAPPING.items():
                value = tax_info.get(tax_key)
                if value:
                    mapped[coord_key] = str(value)
        
        return mapped
