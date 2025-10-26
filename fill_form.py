"""
Single Form Filler - Fill one STEP2.pdf form from extracted JSON data
"""
import argparse
import json
from pathlib import Path
from src.form_filler import FormFiller


def main():
    parser = argparse.ArgumentParser(
        description="Fill STEP2.pdf form with extracted data from JSON file"
    )
    parser.add_argument(
        "-i", "--input",
        required=True,
        help="Path to JSON file with extracted data"
    )
    parser.add_argument(
        "-t", "--template",
        default="output/STEP2.pdf",
        help="Path to STEP2.pdf template (default: output/STEP2.pdf)"
    )
    parser.add_argument(
        "-o", "--output",
        help="Path for filled PDF (default: auto-generated from input name)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print detailed progress information"
    )
    
    args = parser.parse_args()
    
    # Load extracted data
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {args.input}")
        return 1
    
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Get extracted fields
    extracted_fields = data.get('extracted_fields', {})
    
    if not extracted_fields:
        print(f"Warning: No extracted fields found in {args.input}")
        if args.verbose:
            print(f"Data keys: {list(data.keys())}")
    
    # Determine output path
    if args.output:
        output_path = args.output
    else:
        # Auto-generate: input_pdfs/Charles_Alleman_extracted.json -> filled_forms/Charles_Alleman_filled.pdf
        output_dir = Path("filled_forms")
        base_name = input_path.stem.replace("_extracted", "")
        output_path = output_dir / f"{base_name}_filled.pdf"
    
    # Check template exists
    template_path = Path(args.template)
    if not template_path.exists():
        print(f"Error: Template not found: {args.template}")
        print("Please ensure STEP2.pdf is in the correct location")
        return 1
    
    if args.verbose:
        print(f"\n{'='*70}")
        print(f"FORM FILLING CONFIGURATION")
        print(f"{'='*70}")
        print(f"Input JSON:    {input_path}")
        print(f"Template PDF:  {template_path}")
        print(f"Output PDF:    {output_path}")
        print(f"Fields to fill: {len(extracted_fields)}")
    
    # Fill the form
    try:
        filler = FormFiller(str(template_path))
        success = filler.fill_form(extracted_fields, str(output_path), verbose=args.verbose)
        
        if success:
            print(f"\n✓ Form filled successfully!")
            print(f"  Output: {output_path}")
            return 0
        else:
            print(f"\n✗ Form filling failed")
            return 1
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
