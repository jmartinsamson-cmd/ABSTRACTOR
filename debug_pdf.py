"""
Debug utility - Extract and display raw text from PDFs
Helps identify text extraction issues and improve parsing patterns
"""
import sys
from pathlib import Path
from src.parser import PDFParser


def debug_pdf(pdf_path: str):
    """Extract and display detailed information about a PDF"""
    path = Path(pdf_path)
    
    if not path.exists():
        print(f"Error: File not found: {pdf_path}")
        return
    
    print("=" * 70)
    print(f"DEBUG: {path.name}")
    print("=" * 70)
    
    try:
        parser = PDFParser(str(path))
        page_count = parser.get_page_count()
        text = parser.extract_text()
        
        print(f"\nPages: {page_count}")
        print(f"Total characters: {len(text)}")
        print(f"Total lines: {len(text.splitlines())}")
        
        print("\n" + "-" * 70)
        print("FULL TEXT EXTRACTION:")
        print("-" * 70)
        print(text)
        print("-" * 70)
        
        print("\n" + "-" * 70)
        print("PAGE-BY-PAGE BREAKDOWN:")
        print("-" * 70)
        for i, page_text in enumerate(parser.pages, 1):
            print(f"\n--- Page {i} ({len(page_text)} chars) ---")
            print(page_text[:500] + "..." if len(page_text) > 500 else page_text)
        
        # Character analysis
        print("\n" + "-" * 70)
        print("CHARACTER ANALYSIS:")
        print("-" * 70)
        print(f"Alphabetic characters: {sum(c.isalpha() for c in text)}")
        print(f"Numeric characters: {sum(c.isdigit() for c in text)}")
        print(f"Whitespace characters: {sum(c.isspace() for c in text)}")
        print(f"Special characters: {len(text) - sum(c.isalnum() or c.isspace() for c in text)}")
        
        # Common words
        words = text.split()
        if words:
            print(f"\nTotal words: {len(words)}")
            print(f"Unique words: {len(set(words))}")
            print(f"Sample words: {', '.join(words[:20])}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python debug_pdf.py <path_to_pdf>")
        print("\nExample:")
        print('  python debug_pdf.py "Charles Alleman.pdf"')
        sys.exit(1)
    
    debug_pdf(sys.argv[1])
