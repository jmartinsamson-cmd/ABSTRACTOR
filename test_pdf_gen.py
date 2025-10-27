#!/usr/bin/env python3
"""Test PDF generation workflow"""

import sys
from pathlib import Path
from src.parser import PDFParser
from src.field_extractor import FieldExtractor
from src.form_filler import FormFiller
import json
import tempfile

def test_pdf_generation(input_pdf_path):
    """Test the complete PDF generation workflow"""
    
    print("=" * 60)
    print("ABSTRACTOR PDF Generation Test")
    print("=" * 60)
    
    # Step 1: Extract text
    print(f"\n📖 Step 1: Extracting text from {Path(input_pdf_path).name}...")
    parser = PDFParser(input_pdf_path)
    text = parser.extract_text()
    print(f"✅ Extracted {len(text):,} characters")
    
    if len(text.strip()) < 100:
        print("⚠️  Low text detected, trying OCR...")
        parser_ocr = PDFParser(input_pdf_path, use_ocr=True)
        text = parser_ocr.extract_text()
        print(f"✅ OCR extracted {len(text):,} characters")
    
    # Step 2: Extract fields
    print("\n🔎 Step 2: Extracting fields...")
    extractor = FieldExtractor(text)
    extracted_data = extractor.extract_all_fields()
    print(f"✅ Extracted {len(extracted_data)} fields:")
    for key, value in extracted_data.items():
        if isinstance(value, dict):
            print(f"  - {key}: {value}")
        else:
            print(f"  - {key}: {value[:50] if value and len(str(value)) > 50 else value}")
    
    # Step 3: Extract images
    print("\n🖼️  Step 3: Extracting images...")
    try:
        images = parser.get_largest_images(min_width=150, min_height=150, max_count=5)
        print(f"✅ Extracted {len(images)} images")
        for i, img in enumerate(images):
            print(f"  - Image {i+1}: {img['width']}x{img['height']}px")
    except Exception as e:
        print(f"⚠️  Image extraction failed: {e}")
        images = []
    
    # Step 4: Fill form
    print("\n✍️  Step 4: Filling form template...")
    template_path = "templates/STEP2.pdf"
    
    if not Path(template_path).exists():
        print(f"❌ Template not found: {template_path}")
        return False
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "STEP2_filled.pdf"
            
            filler = FormFiller(template_path)
            filler.fill_form(
                extracted_data,
                str(output_file),
                verbose=True,
                images=images
            )
            
            # Check if file was created
            if output_file.exists():
                file_size = output_file.stat().st_size
                print(f"\n✅ SUCCESS! PDF generated: {file_size:,} bytes")
                
                # Save to output folder
                output_dir = Path("output")
                output_dir.mkdir(exist_ok=True)
                final_output = output_dir / "test_STEP2_filled.pdf"
                
                with open(output_file, 'rb') as f_in:
                    with open(final_output, 'wb') as f_out:
                        f_out.write(f_in.read())
                
                print(f"📁 Saved to: {final_output.absolute()}")
                return True
            else:
                print("❌ Output file was not created")
                return False
                
    except Exception as e:
        print(f"❌ Error filling form: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_file = r"c:\Users\jsamb\OneDrive\Desktop\B & P 712- docs.pdf"
    
    if not Path(test_file).exists():
        print(f"❌ Test file not found: {test_file}")
        sys.exit(1)
    
    success = test_pdf_generation(test_file)
    sys.exit(0 if success else 1)
