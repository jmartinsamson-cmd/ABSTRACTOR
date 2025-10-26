"""
Batch Form Filler - Fill multiple STEP2.pdf forms from extracted JSON files with images
"""
import json
from pathlib import Path
from src.form_filler import FormFiller
from src.parser import PDFParser


def main():
    # Configuration
    template_path = "templates/STEP2.pdf"  # Updated path
    input_dir = Path("input")  # Source PDFs
    output_json_dir = Path("output")  # JSON data
    output_dir = Path("filled_forms")
    
    # Create output directory
    output_dir.mkdir(exist_ok=True)
    
    # Find all JSON files with extracted data
    json_files = list(output_json_dir.glob("*_extracted.json"))
    
    if not json_files:
        print("No extracted JSON files found in output/")
        print("Run batch_process.py first to extract data from PDFs")
        return
    
    # Check template exists
    if not Path(template_path).exists():
        print(f"Error: Template not found: {template_path}")
        print("Please ensure STEP2.pdf is in the templates/ folder")
        return
    
    print(f"\n{'='*70}")
    print(f"BATCH FORM FILLING WITH IMAGES")
    print(f"{'='*70}")
    print(f"Template: {template_path}")
    print(f"Input:    {output_json_dir}/*_extracted.json")
    print(f"Output:   {output_dir}/")
    print(f"Found {len(json_files)} JSON file(s) to process")
    print(f"{'='*70}\n")
    
    # Process each JSON file
    filler = FormFiller(template_path)
    success_count = 0
    failed_count = 0
    
    for json_file in json_files:
        # Load data
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        extracted_fields = data.get('extracted_fields', {})
        source_file = data.get('source_file', json_file.stem)
        confidence = data.get('confidence_score', 0)
        
        # Generate output filename
        base_name = json_file.stem.replace("_extracted", "")
        output_path = output_dir / f"{base_name}_filled.pdf"
        
        # Find and extract images from source PDF
        source_pdf = input_dir / f"{base_name}.pdf"
        images = []
        
        if source_pdf.exists():
            try:
                parser = PDFParser(str(source_pdf))
                # Get largest images only (photos, IDs, etc.)
                images = parser.get_largest_images(min_width=150, min_height=150, max_count=5)
                print(f"  Extracted {len(images)} image(s) from source PDF")
            except Exception as e:
                print(f"  Warning: Could not extract images: {e}")
        
        # Fill form
        print(f"Processing: {json_file.name}")
        print(f"  Source: {source_file}")
        print(f"  Confidence: {confidence:.0%}")
        print(f"  Fields: {len(extracted_fields)}")
        print(f"  Images: {len(images)}")
        
        try:
            success = filler.fill_form(
                extracted_fields, 
                str(output_path), 
                verbose=False,
                images=images if images else None
            )
            
            if success:
                print(f"  ✓ Filled: {output_path.name}\n")
                success_count += 1
            else:
                print(f"  ✗ Failed to fill form\n")
                failed_count += 1
                
        except Exception as e:
            print(f"  ✗ Error: {e}\n")
            failed_count += 1
    
    # Summary
    print(f"{'='*70}")
    print(f"BATCH FORM FILLING COMPLETE")
    print(f"{'='*70}")
    print(f"✓ Successful: {success_count}")
    print(f"✗ Failed:     {failed_count}")
    print(f"{'='*70}")
    
    if success_count > 0:
        print(f"\nFilled forms saved to: {output_dir}/")


if __name__ == "__main__":
    main()
