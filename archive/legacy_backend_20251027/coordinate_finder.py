"""
PDF Coordinate Finder - Interactive tool to find exact coordinates for form filling

Click on a PDF page to get coordinates. Use this to calibrate FORM_FIELD_COORDINATES in config.py.

Usage:
    python coordinate_finder.py "output/STEP2.pdf"
    python coordinate_finder.py "output/STEP2.pdf" --page 0
    python coordinate_finder.py "output/STEP2.pdf" --grid
"""
import argparse
import fitz  # PyMuPDF
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from pathlib import Path


class CoordinateFinder:
    """Interactive PDF coordinate finder with click-to-get-coordinates"""
    
    def __init__(self, pdf_path: str, page_num: int = 0, show_grid: bool = False):
        self.pdf_path = Path(pdf_path)
        self.page_num = page_num
        self.show_grid = show_grid
        self.coordinates = []
        
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        # Open PDF
        self.doc = fitz.open(str(self.pdf_path))
        
        if page_num >= len(self.doc):
            raise ValueError(f"Page {page_num} not found. PDF has {len(self.doc)} pages.")
        
        self.page = self.doc[page_num]
        self.page_height = self.page.rect.height
        self.page_width = self.page.rect.width
        
        print(f"\n{'='*70}")
        print(f"PDF COORDINATE FINDER")
        print(f"{'='*70}")
        print(f"File: {self.pdf_path.name}")
        print(f"Page: {page_num} of {len(self.doc)-1}")
        print(f"Size: {self.page_width:.0f} x {self.page_height:.0f} points")
        print(f"{'='*70}\n")
    
    def show_interactive(self):
        """Display PDF page with interactive coordinate finding"""
        # Render page to image
        zoom = 2  # Higher quality
        mat = fitz.Matrix(zoom, zoom)
        pix = self.page.get_pixmap(matrix=mat)
        img = pix.samples
        
        # Convert to numpy array for matplotlib
        import numpy as np
        img_array = np.frombuffer(img, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 16))
        ax.imshow(img_array)
        ax.set_title(f'{self.pdf_path.name} - Page {self.page_num}\nClick to get coordinates (close window when done)')
        
        # Add grid if requested
        if self.show_grid:
            self._add_grid_overlay(ax, zoom)
        
        # Add axis labels with coordinates
        ax.set_xlabel('X coordinate (points)')
        ax.set_ylabel('Y coordinate from top (points)')
        
        # Convert pixel coordinates to PDF points
        def on_click(event):
            if event.inaxes:
                # Convert matplotlib pixel coords to PDF points
                x_pdf = event.xdata / zoom
                # Convert from top-origin (matplotlib) to bottom-origin (PDF)
                y_from_top = event.ydata / zoom
                y_from_bottom = self.page_height - y_from_top
                
                self.coordinates.append((x_pdf, y_from_bottom))
                
                # Display coordinates
                print(f"\n{'─'*70}")
                print(f"Click #{len(self.coordinates)}")
                print(f"{'─'*70}")
                print(f"  X: {x_pdf:.1f}")
                print(f"  Y (from bottom): {y_from_bottom:.1f}")
                print(f"  Y (from top): {y_from_top:.1f}")
                print(f"  Page: {self.page_num}")
                print(f"\nAdd to config.py:")
                print(f'  "field_name": {{"x": {x_pdf:.0f}, "y": {y_from_bottom:.0f}, "page": {self.page_num}, "font_size": 10}},')
                
                # Mark the point on the image
                ax.plot(event.xdata, event.ydata, 'r+', markersize=15, markeredgewidth=2)
                ax.text(event.xdata + 10, event.ydata - 10, f'({x_pdf:.0f}, {y_from_bottom:.0f})', 
                       color='red', fontsize=10, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
                fig.canvas.draw()
        
        # Connect click event
        fig.canvas.mpl_connect('button_press_event', on_click)
        
        print("\n📍 INSTRUCTIONS:")
        print("  1. Click anywhere on the PDF to get coordinates")
        print("  2. Coordinates will be shown in terminal")
        print("  3. Copy the config.py snippet for each field")
        print("  4. Close the window when done")
        print(f"\n{'='*70}\n")
        
        plt.tight_layout()
        plt.show()
        
        self._print_summary()
    
    def _add_grid_overlay(self, ax, zoom: float):
        """Add grid lines to help with coordinate finding"""
        grid_spacing = 50  # Grid every 50 points
        
        # Vertical lines
        for x in range(0, int(self.page_width), grid_spacing):
            ax.axvline(x * zoom, color='cyan', alpha=0.3, linewidth=0.5, linestyle='--')
            if x % 100 == 0:  # Label every 100 points
                ax.text(x * zoom, 10, str(x), color='cyan', fontsize=8, alpha=0.7)
        
        # Horizontal lines (from top)
        for y in range(0, int(self.page_height), grid_spacing):
            ax.axhline(y * zoom, color='cyan', alpha=0.3, linewidth=0.5, linestyle='--')
            if y % 100 == 0:  # Label every 100 points
                y_from_bottom = self.page_height - y
                ax.text(10, y * zoom, f'{y_from_bottom:.0f}', color='cyan', fontsize=8, alpha=0.7)
    
    def _print_summary(self):
        """Print summary of all clicked coordinates"""
        if not self.coordinates:
            print("\nNo coordinates captured.")
            return
        
        print(f"\n{'='*70}")
        print(f"SUMMARY - {len(self.coordinates)} coordinates captured")
        print(f"{'='*70}\n")
        print("Add these to config.py FORM_FIELD_COORDINATES:\n")
        
        for i, (x, y) in enumerate(self.coordinates, 1):
            print(f'    "field_{i}": {{"x": {x:.0f}, "y": {y:.0f}, "page": {self.page_num}, "font_size": 10}},')
        
        print(f"\n{'='*70}\n")
    
    def generate_grid_pdf(self, output_path: str = None):
        """Generate a PDF with coordinate grid overlay for reference"""
        if output_path is None:
            output_path = str(self.pdf_path.parent / f"{self.pdf_path.stem}_grid.pdf")
        
        print(f"\nGenerating grid overlay PDF...")
        
        # Create a copy of the document
        grid_doc = fitz.open(str(self.pdf_path))
        page = grid_doc[self.page_num]
        
        # Grid settings
        grid_spacing = 50
        color_major = (0, 0.7, 0.7)  # Cyan for major grid (every 100)
        color_minor = (0.8, 0.8, 0.8)  # Light gray for minor grid
        
        # Draw vertical lines
        for x in range(0, int(self.page_width), grid_spacing):
            is_major = x % 100 == 0
            color = color_major if is_major else color_minor
            width = 1.5 if is_major else 0.5
            
            # Draw line
            p1 = fitz.Point(x, 0)
            p2 = fitz.Point(x, self.page_height)
            page.draw_line(p1, p2, color=color, width=width)
            
            # Add label for major lines
            if is_major:
                text_point = fitz.Point(x + 2, 15)
                page.insert_text(text_point, str(x), fontsize=8, color=color)
        
        # Draw horizontal lines
        for y in range(0, int(self.page_height), grid_spacing):
            is_major = y % 100 == 0
            color = color_major if is_major else color_minor
            width = 1.5 if is_major else 0.5
            
            # Draw line
            p1 = fitz.Point(0, y)
            p2 = fitz.Point(self.page_width, y)
            page.draw_line(p1, p2, color=color, width=width)
            
            # Add label for major lines (show Y from bottom)
            if is_major:
                y_from_bottom = self.page_height - y
                text_point = fitz.Point(5, y - 2)
                page.insert_text(text_point, f'{y_from_bottom:.0f}', fontsize=8, color=color)
        
        # Add info text in corner
        info_text = f"Grid spacing: {grid_spacing} points | Page {self.page_num} | Size: {self.page_width:.0f}x{self.page_height:.0f}"
        info_point = fitz.Point(10, self.page_height - 10)
        page.insert_text(info_point, info_text, fontsize=10, color=(0, 0, 1))
        
        # Save
        grid_doc.save(output_path)
        grid_doc.close()
        
        print(f"✓ Grid overlay PDF created: {output_path}")
        print(f"  Open this file to see coordinate grid")
        print(f"  Use it as reference when adjusting config.py\n")
        
        return output_path
    
    def close(self):
        """Close the PDF document"""
        self.doc.close()


def main():
    parser = argparse.ArgumentParser(
        description="Interactive PDF coordinate finder for form filling calibration"
    )
    parser.add_argument(
        "pdf",
        help="Path to PDF file (e.g., output/STEP2.pdf)"
    )
    parser.add_argument(
        "--page",
        type=int,
        default=0,
        help="Page number to analyze (default: 0)"
    )
    parser.add_argument(
        "--grid",
        action="store_true",
        help="Show coordinate grid overlay on interactive view"
    )
    parser.add_argument(
        "--generate-grid",
        action="store_true",
        help="Generate a PDF with grid overlay (no interactive mode)"
    )
    parser.add_argument(
        "--output",
        help="Output path for grid PDF (default: <input>_grid.pdf)"
    )
    
    args = parser.parse_args()
    
    try:
        finder = CoordinateFinder(args.pdf, args.page, args.grid)
        
        if args.generate_grid:
            # Just generate grid PDF and exit
            finder.generate_grid_pdf(args.output)
        else:
            # Interactive mode
            finder.show_interactive()
            
            # Optionally generate grid PDF after interactive session
            print("\nGenerate grid PDF for reference? (y/n): ", end="")
            response = input().strip().lower()
            if response == 'y':
                finder.generate_grid_pdf(args.output)
        
        finder.close()
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
