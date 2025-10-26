"""
Main entry point for the PDF Form Abstractor
"""
import argparse
import json
from pathlib import Path
from src.parser import PDFParser
from src.field_extractor import FieldExtractor


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description="Extract structured data from property/abstract PDF documents"
    )
    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Path to input PDF file"
    )
    parser.add_argument(
        "--output",
        "-o",
        required=True,
        help="Path to output JSON file"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print extracted text to console"
    )
    
    args = parser.parse_args()
    
    # Validate input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        return 1
    
    if not input_path.suffix.lower() == ".pdf":
        print(f"Error: Input file must be a PDF")
        return 1
    
    # Create output directory if needed
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Processing PDF: {input_path}")
    print("-" * 60)
    
    # Step 1: Parse the PDF
    try:
        pdf_parser = PDFParser(str(input_path))
        text = pdf_parser.extract_text()
        page_count = pdf_parser.get_page_count()
        
        if pdf_parser.ocr_used:
            print(f"✓ OCR was used to extract text from {page_count} page(s)")
        else:
            print(f"✓ Extracted text from {page_count} page(s)")
        
        if args.verbose:
            print("\n--- EXTRACTED TEXT ---")
            print(text[:1000] + "..." if len(text) > 1000 else text)
            print("--- END EXTRACTED TEXT ---\n")
        
    except Exception as e:
        print(f"✗ Error parsing PDF: {e}")
        return 1
    
    # Step 2: Extract structured fields
    try:
        field_extractor = FieldExtractor(text)
        fields = field_extractor.extract_all_fields()
        confidence = field_extractor.get_confidence_score()
        
        print(f"✓ Extracted structured fields (confidence: {confidence:.1%})")
        
    except Exception as e:
        print(f"✗ Error extracting fields: {e}")
        return 1
    
    # Step 3: Prepare output data
    output_data = {
        "source_file": str(input_path.name),
        "processed_date": None,  # Could add datetime if needed
        "page_count": page_count,
        "confidence_score": round(confidence, 3),
        "extracted_fields": fields
    }
    
    # Step 4: Write to JSON
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Saved results to: {output_path}")
        
    except Exception as e:
        print(f"✗ Error writing output: {e}")
        return 1
    
    # Display summary
    print("\n" + "=" * 60)
    print("EXTRACTION SUMMARY")
    print("=" * 60)
    
    for field_name, field_value in fields.items():
        if field_name == "additional_fields":
            if field_value:
                print(f"\nAdditional Fields:")
                for k, v in field_value.items():
                    print(f"  {k}: {v}")
        elif isinstance(field_value, dict):
            print(f"\n{field_name.replace('_', ' ').title()}:")
            for k, v in field_value.items():
                if v:
                    print(f"  {k}: {v}")
        elif field_value:
            print(f"{field_name.replace('_', ' ').title()}: {field_value}")
    
    print("\n" + "=" * 60)
    print(f"Processing complete! Confidence: {confidence:.1%}")
    
    return 0


if __name__ == "__main__":
    exit(main())
