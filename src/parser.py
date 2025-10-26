"""
PDF Parser - Extract text and structure from PDF documents
"""
from PyPDF2 import PdfReader
from pathlib import Path
from typing import List, Optional
import os

# OCR imports (optional - graceful degradation if not available)
try:
    from pdf2image import convert_from_path
    from PIL import Image
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("Warning: OCR libraries not available. Install pytesseract and pdf2image for scanned PDF support.")


class PDFParser:
    """Handles PDF text extraction and basic preprocessing"""
    
    def __init__(self, pdf_path: str, use_ocr: bool = True):
        self.pdf_path = Path(pdf_path)
        self.text = ""
        self.pages = []
        self.use_ocr = use_ocr and OCR_AVAILABLE
        self.ocr_used = False
        
    def extract_text(self) -> str:
        """Extract all text from the PDF, using OCR if needed"""
        try:
            reader = PdfReader(self.pdf_path)
            self.pages = []
            
            # Try normal text extraction first
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    self.pages.append(page_text)
            
            self.text = "\n\n".join(self.pages)
            
            # Check if we got meaningful text
            if self._is_text_quality_low(self.text) and self.use_ocr:
                print(f"Low quality text detected. Attempting OCR...")
                return self._extract_with_ocr()
            
            return self.text
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def extract_tables(self) -> List[List[List[str]]]:
        """Extract tables from the PDF (basic implementation)"""
        # PyPDF2 doesn't have native table extraction
        # This is a placeholder for future enhancement
        print("Table extraction not available with PyPDF2")
        return []
    
    def get_page_count(self) -> int:
        """Get the number of pages in the PDF"""
        try:
            reader = PdfReader(self.pdf_path)
            return len(reader.pages)
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
    
    def get_text_by_page(self, page_num: int) -> Optional[str]:
        """Get text from a specific page (0-indexed)"""
        if not self.pages:
            self.extract_text()
        
        if 0 <= page_num < len(self.pages):
            return self.pages[page_num]
        return None
    
    def _is_text_quality_low(self, text: str) -> bool:
        """
        Determine if extracted text quality is too low
        Indicators: too short, too many special chars, low word count
        """
        if not text or len(text.strip()) < 50:
            return True
        
        # Check ratio of alphanumeric to total characters
        alphanumeric = sum(c.isalnum() or c.isspace() for c in text)
        total = len(text)
        
        if total > 0:
            ratio = alphanumeric / total
            # If less than 60% alphanumeric, likely garbled
            if ratio < 0.6:
                return True
        
        # Check word count
        words = text.split()
        # If very few words relative to character count, likely garbled
        if len(words) < len(text) / 50:
            return True
        
        return False
    
    def _extract_with_ocr(self) -> str:
        """Extract text using OCR (for scanned PDFs)"""
        if not OCR_AVAILABLE:
            print("⚠️  OCR libraries not available.")
            print("Install with: pip install pytesseract pdf2image Pillow")
            return self.text
        
        try:
            print("Converting PDF to images...")
            # Convert PDF pages to images
            images = convert_from_path(
                self.pdf_path,
                dpi=300,  # Higher DPI = better quality
                fmt='jpeg'
            )
            
            print(f"Running OCR on {len(images)} page(s)...")
            self.pages = []
            
            for i, image in enumerate(images):
                print(f"  Processing page {i+1}/{len(images)}...")
                # Perform OCR on the image
                page_text = pytesseract.image_to_string(
                    image,
                    config='--psm 1'  # Automatic page segmentation with OSD
                )
                self.pages.append(page_text)
            
            self.text = "\n\n".join(self.pages)
            self.ocr_used = True
            print(f"✓ OCR complete! Extracted {len(self.text)} characters")
            
            return self.text
            
        except FileNotFoundError as e:
            if 'tesseract' in str(e).lower():
                print("\n⚠️  Tesseract OCR is not installed!")
                print("\nTo enable OCR for scanned PDFs:")
                print("  1. Run: install_tesseract.ps1 (as Administrator)")
                print("  2. Or download from: https://github.com/UB-Mannheim/tesseract/wiki")
                print("  3. See OCR_SETUP.md for detailed instructions\n")
            else:
                print(f"⚠️  OCR failed: {str(e)}")
            return self.text
            
        except Exception as e:
            print(f"⚠️  OCR failed: {str(e)}")
            if 'poppler' in str(e).lower():
                print("\nPoppler is required for PDF to image conversion.")
                print("See OCR_SETUP.md for installation instructions.")
            # Fall back to original text
            return self.text
