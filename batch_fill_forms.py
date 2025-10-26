"""
Batch Form Filler - Fill multiple STEP2.pdf forms from extracted JSON files
"""
import json
from pathlib import Path
from src.form_filler import FormFiller


def main():
    # Configuration
    template_path = "output/STEP2.pdf"
    input_dir = Path("output")
    output_dir = Path("filled_forms")
    
    # Create output directory
    output_dir.mkdir(exist_ok=True)
    
    # Find all JSON files with extracted data
    json_files = list(input_dir.glob("*_extracted.json"))
    
    if not json_files:
        print("No extracted JSON files found in output/")
        print("Run batch_process.py first to extract data from PDFs")
        return
    
    # Check template exists
    if not Path(template_path).exists():
        print(f"Error: Template not found: {template_path}")
        print("Please ensure STEP2.pdf is in the output/ folder")
        return
    
    print(f"\n{'='*70}")
    print(f"BATCH FORM FILLING")
    print(f"{'='*70}")
    print(f"Template: {template_path}")
    print(f"Input:    {input_dir}/*_extracted.json")
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
        
        # Fill form
        print(f"Processing: {json_file.name}")
        print(f"  Source: {source_file}")
        print(f"  Confidence: {confidence:.0%}")
        print(f"  Fields: {len(extracted_fields)}")
        
        try:
            success = filler.fill_form(extracted_fields, str(output_path), verbose=False)
            
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
