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
        
        # Create output
        output_data = {
            "source_file": pdf_path.name,
            "page_count": page_count,
            "ocr_used": parser.ocr_used,
            "confidence_score": round(confidence, 3),
            "extracted_fields": fields
        }
        
        # Save individual JSON
        output_file = output_dir / f"{pdf_path.stem}_extracted.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        ocr_indicator = " (OCR)" if parser.ocr_used else ""
        print(f"✓ Confidence: {confidence:.1%}{ocr_indicator}")
        print(f"✓ Saved to: {output_file.name}")
        
        return output_data
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def main():
    """Process all sample PDFs"""
    # Find PDFs in current directory
    current_dir = Path(__file__).parent
    pdf_files = [
        current_dir / "Charles Alleman.pdf",
        current_dir / "Charles Alleman docs.pdf"
    ]
    
    # Create output directory
    output_dir = current_dir / "output"
    output_dir.mkdir(exist_ok=True)
    
    print("=" * 60)
    print("PDF BATCH PROCESSOR")
    print("=" * 60)
    
    results = []
    for pdf_path in pdf_files:
        if pdf_path.exists():
            result = process_pdf(pdf_path, output_dir)
            if result:
                results.append(result)
        else:
            print(f"\n⚠ File not found: {pdf_path.name}")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"PROCESSED {len(results)} / {len(pdf_files)} FILES")
    print("=" * 60)
    
    for result in results:
        print(f"\n{result['source_file']}:")
        fields = result['extracted_fields']
        
        if fields.get('owner_name'):
            print(f"  Owner: {fields['owner_name']}")
        if fields.get('property_address'):
            print(f"  Address: {fields['property_address']}")
        if fields.get('parcel_number'):
            print(f"  Parcel: {fields['parcel_number']}")
    
    print("\n✓ All results saved to 'output/' directory")


if __name__ == "__main__":
    main()
