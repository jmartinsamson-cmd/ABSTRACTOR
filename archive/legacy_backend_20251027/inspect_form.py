"""
Form Field Inspector - Analyze PDF form fields in STEP2.pdf
This helps identify field names for mapping extracted data
"""
import sys
from pathlib import Path
from PyPDF2 import PdfReader


def inspect_form_fields(pdf_path: str):
    """Extract and display all form fields from a PDF"""
    path = Path(pdf_path)
    
    if not path.exists():
        print(f"Error: File not found: {pdf_path}")
        return
    
    print("=" * 70)
    print(f"FORM FIELD INSPECTOR: {path.name}")
    print("=" * 70)
    
    try:
        reader = PdfReader(path)
        
        # Check if PDF has form fields
        if reader.get_fields() is None:
            print("\n⚠️  This PDF does not contain interactive form fields.")
            print("\nPossible solutions:")
            print("1. The form might be a static PDF - you'll need to use")
            print("   coordinate-based text overlay instead of form filling")
            print("2. Try using reportlab to create a new PDF with filled data")
            print("3. Use a PDF template library like fillpdf or pdfrw")
            return
        
        fields = reader.get_fields()
        print(f"\n✓ Found {len(fields)} form fields\n")
        print("-" * 70)
        
        # Display each field
        for field_name, field_info in fields.items():
            print(f"\nField Name: {field_name}")
            
            # Get field properties
            if hasattr(field_info, '/FT'):
                field_type = field_info['/FT']
                print(f"  Type: {field_type}")
            
            if hasattr(field_info, '/T'):
                print(f"  Title: {field_info['/T']}")
            
            if hasattr(field_info, '/V'):
                print(f"  Value: {field_info.get('/V', 'None')}")
            
            if hasattr(field_info, '/DV'):
                print(f"  Default: {field_info.get('/DV', 'None')}")
            
            print("-" * 70)
        
        # Create a sample mapping template
        print("\n" + "=" * 70)
        print("SUGGESTED FIELD MAPPING (for config.py):")
        print("=" * 70)
        print("\nFORM_FIELD_MAPPING = {")
        
        sample_mappings = {
            "owner_name": "# Update with actual field name",
            "property_address": "# Update with actual field name",
            "parcel_number": "# Update with actual field name",
            "legal_description": "# Update with actual field name",
        }
        
        for key, comment in sample_mappings.items():
            # Try to find a matching field
            matching_field = None
            for field_name in fields.keys():
                if any(keyword in field_name.lower() for keyword in key.split('_')):
                    matching_field = field_name
                    break
            
            if matching_field:
                print(f'    "{key}": "{matching_field}",')
            else:
                print(f'    "{key}": "",  {comment}')
        
        print("}")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python inspect_form.py <path_to_pdf_form>")
        print("\nExample:")
        print('  python inspect_form.py "STEP2.pdf"')
        sys.exit(1)
    
    inspect_form_fields(sys.argv[1])
