"""
Quick Coordinate Calibration Tool - Test and adjust field positions

This tool helps you quickly test coordinate adjustments without modifying config.py.
Once you're happy with the positions, it generates the final config.py snippet.

Usage:
    python calibrate_coordinates.py
"""
import json
from pathlib import Path
from src.form_filler import FormFiller


def load_sample_data():
    """Load sample extracted data for testing"""
    json_files = list(Path("output").glob("*_extracted.json"))
    
    if not json_files:
        print("No extracted JSON files found. Run batch_process.py first.")
        return None
    
    # Use the first file with highest confidence
    best_file = None
    best_confidence = 0
    
    for json_file in json_files:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            confidence = data.get('confidence_score', 0)
            if confidence > best_confidence:
                best_confidence = confidence
                best_file = json_file
    
    if best_file:
        with open(best_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"Loaded sample data from: {best_file.name}")
        print(f"Confidence: {best_confidence:.0%}\n")
        return data.get('extracted_fields', {})
    
    return None


def test_coordinates(template_path: str, sample_data: dict, test_coords: dict):
    """Test form filling with specific coordinates"""
    import config
    
    # Temporarily override coordinates
    original_coords = config.FORM_FIELD_COORDINATES.copy()
    config.FORM_FIELD_COORDINATES.update(test_coords)
    
    try:
        filler = FormFiller(template_path)
        output_path = "calibration_test.pdf"
        
        success = filler.fill_form(sample_data, output_path, verbose=True)
        
        if success:
            print(f"\n✓ Test form created: {output_path}")
            print("  Open this file to check field positions")
            return True
        else:
            print("\n✗ Form filling failed")
            return False
    
    finally:
        # Restore original coordinates
        config.FORM_FIELD_COORDINATES = original_coords


def interactive_calibration():
    """Interactive coordinate calibration"""
    print("\n" + "="*70)
    print("COORDINATE CALIBRATION TOOL")
    print("="*70)
    print("\nThis tool helps you fine-tune field coordinates.\n")
    
    # Load sample data
    sample_data = load_sample_data()
    if not sample_data:
        return
    
    template_path = "output/STEP2.pdf"
    if not Path(template_path).exists():
        print(f"Template not found: {template_path}")
        return
    
    print("Available fields in sample data:")
    for i, (key, value) in enumerate(sample_data.items(), 1):
        if isinstance(value, dict):
            print(f"  {i}. {key}: {list(value.keys())}")
        else:
            display_value = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
            print(f"  {i}. {key}: {display_value}")
    
    print("\n" + "="*70)
    print("CALIBRATION WORKFLOW:")
    print("="*70)
    print("1. Use coordinate_finder.py to get exact coordinates:")
    print("   python coordinate_finder.py output/STEP2.pdf --grid")
    print("\n2. Test coordinates here before updating config.py")
    print("\n3. Enter field coordinates below (or 'done' to finish)")
    print("="*70 + "\n")
    
    test_coords = {}
    
    while True:
        print("\nEnter field name (or 'done' to test, 'skip' to test current): ", end="")
        field_name = input().strip()
        
        if field_name.lower() == 'done':
            break
        
        if field_name.lower() == 'skip':
            if test_coords:
                break
            else:
                print("No coordinates entered yet!")
                continue
        
        print(f"Enter X coordinate for '{field_name}': ", end="")
        try:
            x = float(input().strip())
        except ValueError:
            print("Invalid number, skipping...")
            continue
        
        print(f"Enter Y coordinate (from bottom) for '{field_name}': ", end="")
        try:
            y = float(input().strip())
        except ValueError:
            print("Invalid number, skipping...")
            continue
        
        print(f"Enter font size (default 10): ", end="")
        font_input = input().strip()
        font_size = int(font_input) if font_input else 10
        
        print(f"Enter page number (default 0): ", end="")
        page_input = input().strip()
        page = int(page_input) if page_input else 0
        
        test_coords[field_name] = {
            "x": x,
            "y": y,
            "page": page,
            "font_size": font_size
        }
        
        print(f"\n✓ Added: {field_name} at ({x}, {y}) on page {page}")
    
    if test_coords:
        print(f"\n{'='*70}")
        print("Testing coordinates...")
        print(f"{'='*70}\n")
        
        success = test_coordinates(template_path, sample_data, test_coords)
        
        if success:
            print("\n" + "="*70)
            print("ADD TO config.py FORM_FIELD_COORDINATES:")
            print("="*70 + "\n")
            
            for field_name, coords in test_coords.items():
                print(f'    "{field_name}": {{"x": {coords["x"]:.0f}, "y": {coords["y"]:.0f}, "page": {coords["page"]}, "font_size": {coords["font_size"]}}},')
            
            print("\n" + "="*70 + "\n")
    else:
        print("\nNo coordinates to test.")


def quick_test_all():
    """Quick test with current config.py coordinates"""
    print("\n" + "="*70)
    print("QUICK TEST - Using current config.py coordinates")
    print("="*70 + "\n")
    
    sample_data = load_sample_data()
    if not sample_data:
        return
    
    template_path = "output/STEP2.pdf"
    if not Path(template_path).exists():
        print(f"Template not found: {template_path}")
        return
    
    filler = FormFiller(template_path)
    output_path = "calibration_test.pdf"
    
    success = filler.fill_form(sample_data, output_path, verbose=True)
    
    if success:
        print(f"\n✓ Test form created: {output_path}")
        print("  Open this file to check if coordinates are correct")


def main():
    print("\nCOORDINATE CALIBRATION OPTIONS:")
    print("="*70)
    print("1. Interactive calibration (enter coordinates manually)")
    print("2. Quick test with current config.py coordinates")
    print("3. Exit")
    print("="*70)
    print("\nChoice (1/2/3): ", end="")
    
    choice = input().strip()
    
    if choice == "1":
        interactive_calibration()
    elif choice == "2":
        quick_test_all()
    else:
        print("Exiting...")


if __name__ == "__main__":
    main()
