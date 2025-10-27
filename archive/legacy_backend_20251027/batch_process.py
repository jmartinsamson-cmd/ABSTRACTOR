"""
Batch processor - Process multiple PDFs at once
"""
import sys
from pathlib import Path
from src.parser import PDFParser
from src.field_extractor import FieldExtractor
import json


def process_pdf(pdf_path: Path, output_dir: Path) -> dict:
    """Process a single PDF and return extracted data"""
    print(f"\nProcessing: {pdf_path.name}")
    print("-" * 60)
    
    try:
        # Parse PDF
        parser = PDFParser(str(pdf_path))
        text = parser.extract_text()
        page_count = parser.get_page_count()

        # Extract fields
        extractor = FieldExtractor(text)
        fields = extractor.extract_all_fields()
        confidence = extractor.get_confidence_score()

        # Extract images and save them
        images_output_dir = output_dir / "images"
        images = parser.extract_images(output_dir=images_output_dir)

        # Remove raw bytes from image dicts for JSON serialization
        images_for_json = []
        for img in images:
            img_copy = dict(img)
            if 'data' in img_copy:
                del img_copy['data']
            images_for_json.append(img_copy)

        # Print summary of images
        if images_for_json:
            print(f"✓ Extracted {len(images_for_json)} images:")
            for img in images_for_json:
                print(f"  - Page {img['page']+1}, Index {img['index']+1}, Size {img['width']}x{img['height']}, Path: {img.get('path','(not saved)')}")
        else:
            print("✓ No images found in PDF.")

        # Create output
        output_data = {
            "source_file": pdf_path.name,
            "page_count": page_count,
            "ocr_used": parser.ocr_used,
            "confidence_score": round(confidence, 3),
            "extracted_fields": fields,
            "extracted_images": images_for_json
        }

        # Save individual JSON
        output_file = output_dir / f"{pdf_path.stem}_extracted.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

            # Surface warning if confidence is under 0.3
            if confidence < 0.3:
                print(f"⚠️  WARNING: Extraction confidence is very low ({confidence:.1%}). Results may be incomplete or unreliable.")

            ocr_indicator = " (OCR)" if parser.ocr_used else ""
            print(f"✓ Confidence: {confidence:.1%}{ocr_indicator}")
            print(f"✓ Saved to: {output_file.name}")

        return output_data

    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def main():
    """Process all sample PDFs"""
    # Find PDFs in ExamplePDFin directory
    current_dir = Path(__file__).parent
    input_dir = current_dir / "ExamplePDFin"
    pdf_files = list(input_dir.glob("*.pdf"))

    # Create output directory
    output_dir = current_dir / "output"
    output_dir.mkdir(exist_ok=True)

    print("=" * 60)
    print("PDF BATCH PROCESSOR")
    print("=" * 60)
    print(f"Scanning for PDFs in: {input_dir}")
    print(f"Found {len(pdf_files)} PDF(s) to process.")

    results = []
    for pdf_path in pdf_files:
        print(f"\nProcessing file: {pdf_path.name}")
        result = process_pdf(pdf_path, output_dir)
        if result:
            results.append(result)

    # Summary
    print("\n" + "=" * 60)
    print(f"PROCESSED {len(results)} / {len(pdf_files)} FILES")
    print("=" * 60)

    for result in results:
        print(f"\n{result['source_file']}:")
        fields = result['extracted_fields']
        images = result.get('extracted_images', [])

        if fields.get('owner_name'):
            print(f"  Owner: {fields['owner_name']}")
        if fields.get('property_address'):
            print(f"  Address: {fields['property_address']}")
        if fields.get('parcel_number'):
            print(f"  Parcel: {fields['parcel_number']}")
        print(f"  Images extracted: {len(images)}")

    print(f"\n✓ All results saved to '{output_dir}/' directory")
    print(f"✓ All images saved to '{output_dir}/images/' directory")


if __name__ == "__main__":
    main()
