"""
PDF Parser - Extract text, images, and structure from PDF documents
"""
from PyPDF2 import PdfReader
from pathlib import Path
from typing import List, Optional, Dict, Tuple
import os
import io

# Image extraction with PyMuPDF (fitz)
try:
    import fitz  # PyMuPDF
    FITZ_AVAILABLE = True
except ImportError:
    FITZ_AVAILABLE = False
    print("Warning: PyMuPDF not available. Image extraction will be limited.")

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
    def _preprocess_image_for_ocr(self, image):
        """Apply basic pre-processing: grayscale, sharpen, autocontrast."""
        from PIL import ImageFilter, ImageOps
        # Convert to grayscale
        image = image.convert('L')
        # Apply autocontrast
        image = ImageOps.autocontrast(image)
        # Apply sharpening filter
        image = image.filter(ImageFilter.SHARPEN)
        # (Optional) Deskew: Pillow does not have native deskew, but Tesseract can handle some skew
        return image

    def extract_raw_ocr_text(self) -> str:
        """Extract raw OCR text from all pages and return as a string (for debugging)"""
        if not OCR_AVAILABLE:
            return "OCR libraries not available."
        try:
            images = convert_from_path(
                self.pdf_path,
                dpi=300,
                fmt='jpeg'
            )
            ocr_text = []
            for i, image in enumerate(images):
                pre_image = self._preprocess_image_for_ocr(image)
                page_text = pytesseract.image_to_string(
                    pre_image,
                    config='--psm 1'
                )
                ocr_text.append(f"--- Page {i+1} ---\n{page_text.strip()}\n")
            return "\n".join(ocr_text)
        except Exception as e:
            return f"OCR extraction failed: {str(e)}"
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
            print("Continuing with regular text extraction...")
            return self.text
        try:
            print("Converting PDF to images...")
            images = convert_from_path(
                self.pdf_path,
                dpi=300,
                fmt='jpeg'
            )
            print(f"Running OCR on {len(images)} page(s)...")
            self.pages = []
            for i, image in enumerate(images):
                print(f"  Processing page {i+1}/{len(images)}...")
                pre_image = self._preprocess_image_for_ocr(image)
                page_text = pytesseract.image_to_string(
                    pre_image,
                    config='--psm 1'
                )
                self.pages.append(page_text)
            self.text = "\n\n".join(self.pages)
            self.ocr_used = True
            print(f"✓ OCR complete! Extracted {len(self.text)} characters")
            return self.text
        except Exception as e:
            # Catch all OCR errors (including poppler not found)
            error_msg = str(e).lower()
            if 'tesseract' in error_msg:
                print("\n⚠️  Tesseract OCR is not installed!")
                print("\nTo enable OCR for scanned PDFs:")
                print("  1. Run: install_tesseract.ps1 (as Administrator)")
                print("  2. Or download from: https://github.com/UB-Mannheim/tesseract/wiki")
            elif 'poppler' in error_msg or 'page count' in error_msg:
                print("\n⚠️  Poppler is not installed!")
                print("\nPoppler is required for OCR functionality.")
                print("For now, continuing with regular text extraction...")
            else:
                print(f"⚠️  OCR failed: {str(e)}")
            print("Continuing with regular text extraction...")
            return self.text
    
    def extract_images(self, output_dir: Optional[Path] = None) -> List[Dict[str, any]]:
        """
        Extract all images from the PDF document
        
        Args:
            output_dir: Optional directory to save extracted images
            
        Returns:
            List of dictionaries containing image info:
            {
                'page': page number (0-indexed),
                'index': image index on page,
                'width': image width,
                'height': image height,
                'data': image bytes,
                'ext': image extension (png, jpg, etc),
                'path': saved file path (if output_dir provided)
            }
        """
        if not FITZ_AVAILABLE:
            print("Warning: PyMuPDF not available. Cannot extract images.")
            return []
        
        try:
            import fitz  # Import here to use it
            doc = fitz.open(str(self.pdf_path))
            images = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                image_list = page.get_images(full=True)
                
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    width = base_image["width"]
                    height = base_image["height"]
                    
                    image_info = {
                        'page': page_num,
                        'index': img_index,
                        'width': width,
                        'height': height,
                        'data': image_bytes,
                        'ext': image_ext,
                        'xref': xref
                    }
                    
                    # Save image if output directory provided
                    if output_dir:
                        output_dir = Path(output_dir)
                        output_dir.mkdir(parents=True, exist_ok=True)
                        
                        image_filename = f"page{page_num + 1}_img{img_index + 1}.{image_ext}"
                        image_path = output_dir / image_filename
                        
                        with open(image_path, "wb") as img_file:
                            img_file.write(image_bytes)
                        
                        image_info['path'] = str(image_path)
                    
                    images.append(image_info)
            
            doc.close()
            print(f"✓ Extracted {len(images)} images from PDF")
            return images
            
        except Exception as e:
            print(f"⚠️  Error extracting images: {str(e)}")
            return []
    
    def get_largest_images(self, min_width: int = 200, min_height: int = 200, max_count: int = 10) -> List[Dict[str, any]]:
        """
        Extract only the largest/most significant images from the PDF
        Useful for forms with photos (passport, ID, etc.)
        
        Args:
            min_width: Minimum image width in pixels
            min_height: Minimum image height in pixels
            max_count: Maximum number of images to return
            
        Returns:
            List of largest images sorted by size (descending)
        """
        all_images = self.extract_images()

        # Lower min size for single-page docs and signatures/stamps
        min_width = min_width if min_width < 200 else 50
        min_height = min_height if min_height < 200 else 50

        filtered_images = [
            img for img in all_images
            if img['width'] >= min_width and img['height'] >= min_height
        ]

        # If no images meet threshold, fallback to all images
        if not filtered_images and all_images:
            filtered_images = all_images

        # Always return at least one image if present
        if not filtered_images and all_images:
            filtered_images = [all_images[0]]

        # Sort by area (width * height) in descending order
        filtered_images.sort(key=lambda x: x['width'] * x['height'], reverse=True)

        # Return top N images
        return filtered_images[:max_count]
