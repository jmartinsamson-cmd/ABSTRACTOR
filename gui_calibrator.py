"""
GUI Coordinate Calibrator - Visual tool for calibrating form field coordinates

This GUI allows you to:
- Load and view PDF pages
- Click to capture exact coordinates
- Preview text placement in real-time
- Save coordinates directly to config.py
- Test field mappings visually

Usage:
    python gui_calibrator.py
    python gui_calibrator.py --template output/STEP2.pdf
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import json
from typing import Dict, Any, Optional
import sys

try:
    import fitz  # PyMuPDF
except ImportError as e:
    print(f"Error: Missing required package: {e}")
    print("Please install: pip install PyMuPDF")
    sys.exit(1)

# Try to import PIL, but work around corruption if needed
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    print("Warning: PIL/Pillow not available or corrupted. Using alternative rendering.")
    PIL_AVAILABLE = False
    # We'll use PPM format as fallback

import config


class CoordinateCalibrator(tk.Tk):
    """
    Visual GUI for calibrating form field coordinates.
    
    Features:
    - PDF viewer with zoom controls
    - Click-to-capture coordinates
    - Live text preview
    - Field list management
    - Auto-save to config.py
    """
    
    def __init__(self, template_path: str = "output/STEP2.pdf"):
        super().__init__()
        
        self.title("PDF Form Coordinate Calibrator")
        self.geometry("1400x900")
        
        # State variables
        self.template_path = template_path
        self.pdf_doc: Optional[fitz.Document] = None
        self.current_page = 0
        self.zoom_level = 1.0
        self.field_coordinates: Dict[str, Dict[str, Any]] = {}
        self.current_field: Optional[str] = None
        self.preview_mode = False
        self.sample_data: Dict[str, Any] = {}
        self.canvas_image = None
        self.photo_image = None
        self.markers: list = []
        
        # Load existing coordinates from config
        self.load_existing_coordinates()
        
        # Load sample data for preview
        self.load_sample_data()
        
        # Initialize UI
        self.setup_ui()
        
        # Load PDF if exists
        if Path(template_path).exists():
            self.load_pdf(template_path)
        else:
            messagebox.showwarning(
                "Template Not Found",
                f"Template PDF not found at:\n{template_path}\n\n"
                "Please use 'Load PDF' to select a template."
            )
    
    def load_existing_coordinates(self):
        """Load coordinates from config.py if they exist."""
        if hasattr(config, 'FORM_FIELD_COORDINATES'):
            self.field_coordinates = dict(config.FORM_FIELD_COORDINATES)
            print(f"Loaded {len(self.field_coordinates)} existing field coordinates")
        else:
            self.field_coordinates = {}
    
    def load_sample_data(self):
        """Load sample extracted data for preview."""
        # Try to load from existing extracted JSON
        output_dir = Path("output")
        if output_dir.exists():
            json_files = list(output_dir.glob("*_extracted.json"))
            if json_files:
                with open(json_files[0], 'r') as f:
                    self.sample_data = json.load(f)
                    print(f"Loaded sample data from {json_files[0].name}")
                    return
        
        # Fallback to dummy data
        self.sample_data = {
            "property_address": "153 CHARDONNAY DR",
            "parcel_number": "0604233210CAQ",
            "owner_name": "JOHN DOE",
            "legal_description": "LOT 100 OF SUBDIVISION XYZ",
            "county": "ASCENSION",
            "state": "LA",
            "lot_number": "100",
            "subdivision": "CHARDONNAY ESTATES",
            "deed_info": {
                "book": "ABC",
                "page": "1224480",
                "recorded_date": "12/23/2021"
            },
            "tax_info": {
                "year": "2021",
                "amount": "$2,500.00"
            }
        }
    
    def setup_ui(self):
        """Create the main UI layout."""
        # Menu bar
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load PDF...", command=self.browse_pdf)
        file_menu.add_command(label="Load Sample Data...", command=self.browse_sample_data)
        file_menu.add_separator()
        file_menu.add_command(label="Save Coordinates", command=self.save_coordinates)
        file_menu.add_command(label="Export Config", command=self.export_config)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Instructions", command=self.show_instructions)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Main container
        main_container = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - PDF viewer
        left_panel = ttk.Frame(main_container)
        main_container.add(left_panel, weight=3)
        self.setup_pdf_viewer(left_panel)
        
        # Right panel - Controls
        right_panel = ttk.Frame(main_container)
        main_container.add(right_panel, weight=1)
        self.setup_controls(right_panel)
        
        # Status bar
        self.status_bar = ttk.Label(
            self, 
            text="Ready. Load a PDF to begin.", 
            relief=tk.SUNKEN, 
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def setup_pdf_viewer(self, parent):
        """Setup the PDF viewer canvas."""
        # Toolbar
        toolbar = ttk.Frame(parent)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="Load PDF", command=self.browse_pdf).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="◀ Prev", command=self.prev_page).pack(side=tk.LEFT, padx=2)
        
        self.page_label = ttk.Label(toolbar, text="Page: 0/0")
        self.page_label.pack(side=tk.LEFT, padx=10)
        
        ttk.Button(toolbar, text="Next ▶", command=self.next_page).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        ttk.Button(toolbar, text="Zoom -", command=self.zoom_out).pack(side=tk.LEFT, padx=2)
        self.zoom_label = ttk.Label(toolbar, text="100%")
        self.zoom_label.pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Zoom +", command=self.zoom_in).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Reset", command=self.zoom_reset).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        self.preview_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            toolbar, 
            text="Preview Mode", 
            variable=self.preview_var,
            command=self.toggle_preview
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(toolbar, text="Clear Markers", command=self.clear_markers).pack(side=tk.LEFT, padx=2)
        
        # Canvas with scrollbars
        canvas_frame = ttk.Frame(parent)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.canvas = tk.Canvas(canvas_frame, bg="gray80", cursor="crosshair")
        
        v_scroll = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        h_scroll = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind click event
        self.canvas.bind("<Button-1>", self.on_canvas_click)
    
    def setup_controls(self, parent):
        """Setup the right panel controls."""
        # Notebook for tabs
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab 1: Field List
        fields_tab = ttk.Frame(notebook)
        notebook.add(fields_tab, text="Fields")
        self.setup_fields_tab(fields_tab)
        
        # Tab 2: Current Field
        current_tab = ttk.Frame(notebook)
        notebook.add(current_tab, text="Current Field")
        self.setup_current_field_tab(current_tab)
        
        # Tab 3: Sample Data
        data_tab = ttk.Frame(notebook)
        notebook.add(data_tab, text="Sample Data")
        self.setup_data_tab(data_tab)
    
    def setup_fields_tab(self, parent):
        """Setup the fields list tab."""
        ttk.Label(parent, text="Form Fields:", font=("", 10, "bold")).pack(pady=5)
        
        # Field list
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.field_listbox = tk.Listbox(
            list_frame, 
            yscrollcommand=scrollbar.set,
            selectmode=tk.SINGLE,
            font=("Consolas", 9)
        )
        self.field_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.field_listbox.yview)
        
        self.field_listbox.bind("<<ListboxSelect>>", self.on_field_select)
        
        # Buttons
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Add Field", command=self.add_field).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text="Remove Field", command=self.remove_field).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text="Refresh List", command=self.refresh_field_list).pack(fill=tk.X, pady=2)
        
        # Populate field list
        self.refresh_field_list()
    
    def setup_current_field_tab(self, parent):
        """Setup the current field editing tab."""
        # Field info
        info_frame = ttk.LabelFrame(parent, text="Field Information", padding=10)
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(info_frame, text="Field Name:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.field_name_var = tk.StringVar()
        self.field_name_label = ttk.Label(info_frame, textvariable=self.field_name_var, font=("", 9, "bold"))
        self.field_name_label.grid(row=0, column=1, sticky=tk.W, pady=2)
        
        ttk.Separator(info_frame, orient=tk.HORIZONTAL).grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)
        
        # Coordinates
        coord_frame = ttk.LabelFrame(parent, text="Coordinates", padding=10)
        coord_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(coord_frame, text="X:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.x_var = tk.IntVar(value=0)
        ttk.Spinbox(coord_frame, from_=0, to=1000, textvariable=self.x_var, width=10).grid(row=0, column=1, pady=2)
        
        ttk.Label(coord_frame, text="Y:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.y_var = tk.IntVar(value=0)
        ttk.Spinbox(coord_frame, from_=0, to=1000, textvariable=self.y_var, width=10).grid(row=1, column=1, pady=2)
        
        ttk.Label(coord_frame, text="Page:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.page_var = tk.IntVar(value=0)
        ttk.Spinbox(coord_frame, from_=0, to=100, textvariable=self.page_var, width=10).grid(row=2, column=1, pady=2)
        
        ttk.Label(coord_frame, text="Font Size:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.font_size_var = tk.IntVar(value=10)
        ttk.Spinbox(coord_frame, from_=6, to=24, textvariable=self.font_size_var, width=10).grid(row=3, column=1, pady=2)
        
        ttk.Label(coord_frame, text="Max Width:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.max_width_var = tk.IntVar(value=400)
        ttk.Spinbox(coord_frame, from_=50, to=600, textvariable=self.max_width_var, width=10).grid(row=4, column=1, pady=2)
        
        # Preview text
        preview_frame = ttk.LabelFrame(parent, text="Preview Text", padding=10)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.preview_text_var = tk.StringVar(value="Sample Text")
        ttk.Entry(preview_frame, textvariable=self.preview_text_var).pack(fill=tk.X, pady=5)
        
        # Action buttons
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(action_frame, text="Preview Placement", command=self.preview_placement).pack(fill=tk.X, pady=2)
        ttk.Button(action_frame, text="Save Field", command=self.save_current_field).pack(fill=tk.X, pady=2)
        ttk.Button(action_frame, text="Reset", command=self.reset_current_field).pack(fill=tk.X, pady=2)
        
        # Instructions
        inst_frame = ttk.LabelFrame(parent, text="Instructions", padding=5)
        inst_frame.pack(fill=tk.X, padx=5, pady=5)
        
        instructions = (
            "1. Select field from list\n"
            "2. Click on PDF where text should appear\n"
            "3. Adjust coordinates if needed\n"
            "4. Preview placement\n"
            "5. Save field coordinates"
        )
        ttk.Label(inst_frame, text=instructions, justify=tk.LEFT, font=("", 8)).pack()
    
    def setup_data_tab(self, parent):
        """Setup the sample data tab."""
        ttk.Label(parent, text="Sample Data (for preview):", font=("", 10, "bold")).pack(pady=5)
        
        self.data_text = scrolledtext.ScrolledText(parent, height=20, font=("Consolas", 9))
        self.data_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.refresh_sample_data()
        
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Load JSON...", command=self.browse_sample_data).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Refresh", command=self.refresh_sample_data).pack(side=tk.LEFT, padx=2)
    
    def refresh_sample_data(self):
        """Refresh the sample data display."""
        self.data_text.delete(1.0, tk.END)
        self.data_text.insert(1.0, json.dumps(self.sample_data, indent=2))
    
    def load_pdf(self, path: str):
        """Load a PDF file."""
        try:
            if self.pdf_doc:
                self.pdf_doc.close()
            
            self.pdf_doc = fitz.open(path)
            self.template_path = path
            self.current_page = 0
            self.zoom_level = 1.0
            
            self.update_status(f"Loaded: {Path(path).name} ({len(self.pdf_doc)} pages)")
            self.render_page()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load PDF:\n{e}")
    
    def render_page(self):
        """Render the current PDF page to canvas."""
        if not self.pdf_doc:
            return
        
        try:
            page = self.pdf_doc[self.current_page]
            
            # Get page as image
            mat = fitz.Matrix(self.zoom_level, self.zoom_level)
            pix = page.get_pixmap(matrix=mat)
            
            if PIL_AVAILABLE:
                # Use PIL if available
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                self.photo_image = ImageTk.PhotoImage(img)
            else:
                # Fallback: Use PPM format (Tkinter native)
                # Save pixmap to PPM bytes and load directly
                import io
                ppm_bytes = pix.pil_tobytes(format="PPM")
                self.photo_image = tk.PhotoImage(data=ppm_bytes)
            
            # Update canvas
            self.canvas.delete("all")
            self.markers.clear()
            
            self.canvas_image = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image)
            self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
            
            # Update page label
            self.page_label.config(text=f"Page: {self.current_page + 1}/{len(self.pdf_doc)}")
            
            # Render preview if enabled
            if self.preview_var.get():
                self.render_preview()
            
        except Exception as e:
            self.update_status(f"Error rendering page: {e}")
    
    def render_preview(self):
        """Render text preview overlays on the PDF."""
        if not self.pdf_doc or not self.preview_var.get():
            return
        
        try:
            # Create a temporary PDF with text overlays
            page = self.pdf_doc[self.current_page]
            
            # Draw markers for fields on current page
            for field_name, coords in self.field_coordinates.items():
                if coords.get('page', 0) == self.current_page:
                    x = coords['x']
                    y = coords['y']
                    
                    # Convert PDF coords to canvas coords
                    canvas_x = int(x * self.zoom_level)
                    canvas_y = int((page.rect.height - y) * self.zoom_level)
                    
                    # Draw marker
                    marker = self.canvas.create_oval(
                        canvas_x - 5, canvas_y - 5,
                        canvas_x + 5, canvas_y + 5,
                        fill="red", outline="white", width=2
                    )
                    self.markers.append(marker)
                    
                    # Draw label
                    label = self.canvas.create_text(
                        canvas_x + 10, canvas_y,
                        text=field_name,
                        fill="red",
                        font=("Arial", 8, "bold"),
                        anchor=tk.W
                    )
                    self.markers.append(label)
            
        except Exception as e:
            print(f"Error rendering preview: {e}")
    
    def on_canvas_click(self, event):
        """Handle canvas click to capture coordinates."""
        if not self.pdf_doc or not self.current_field:
            self.update_status("Select a field from the list first")
            return
        
        try:
            page = self.pdf_doc[self.current_page]
            
            # Get click position relative to canvas
            canvas_x = self.canvas.canvasx(event.x)
            canvas_y = self.canvas.canvasy(event.y)
            
            # Convert to PDF coordinates (accounting for zoom)
            pdf_x = int(canvas_x / self.zoom_level)
            pdf_y = int(page.rect.height - (canvas_y / self.zoom_level))
            
            # Update current field coordinates
            self.x_var.set(pdf_x)
            self.y_var.set(pdf_y)
            self.page_var.set(self.current_page)
            
            # Draw marker
            marker = self.canvas.create_oval(
                canvas_x - 5, canvas_y - 5,
                canvas_x + 5, canvas_y + 5,
                fill="blue", outline="white", width=2
            )
            self.markers.append(marker)
            
            self.update_status(f"Captured: {self.current_field} at ({pdf_x}, {pdf_y}) on page {self.current_page}")
            
            # Auto-save if enabled
            if messagebox.askyesno("Save Coordinates", 
                                  f"Save coordinates for '{self.current_field}'?\n\n"
                                  f"X: {pdf_x}, Y: {pdf_y}, Page: {self.current_page}"):
                self.save_current_field()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to capture coordinates:\n{e}")
    
    def on_field_select(self, event):
        """Handle field selection from list."""
        selection = self.field_listbox.curselection()
        if not selection:
            return
        
        field_name = self.field_listbox.get(selection[0])
        self.current_field = field_name
        self.field_name_var.set(field_name)
        
        # Load existing coordinates if available
        if field_name in self.field_coordinates:
            coords = self.field_coordinates[field_name]
            self.x_var.set(coords.get('x', 0))
            self.y_var.set(coords.get('y', 0))
            self.page_var.set(coords.get('page', 0))
            self.font_size_var.set(coords.get('font_size', 10))
            self.max_width_var.set(coords.get('max_width', 400))
            
            # Navigate to field's page
            if self.current_page != coords.get('page', 0):
                self.current_page = coords.get('page', 0)
                self.render_page()
        
        # Set preview text
        if field_name in self.sample_data:
            self.preview_text_var.set(str(self.sample_data[field_name]))
        
        self.update_status(f"Selected: {field_name}")
    
    def refresh_field_list(self):
        """Refresh the field listbox."""
        self.field_listbox.delete(0, tk.END)
        
        # Get all field names from sample data and existing coordinates
        all_fields = set(self.sample_data.keys()) | set(self.field_coordinates.keys())
        
        for field in sorted(all_fields):
            marker = "✓" if field in self.field_coordinates else "○"
            self.field_listbox.insert(tk.END, f"{marker} {field}")
    
    def add_field(self):
        """Add a new field."""
        dialog = tk.Toplevel(self)
        dialog.title("Add Field")
        dialog.geometry("300x100")
        
        ttk.Label(dialog, text="Field Name:").pack(pady=5)
        
        name_var = tk.StringVar()
        entry = ttk.Entry(dialog, textvariable=name_var, width=30)
        entry.pack(pady=5)
        entry.focus()
        
        def save():
            name = name_var.get().strip()
            if name:
                self.field_coordinates[name] = {
                    'x': 100, 'y': 700, 'page': 0,
                    'font_size': 10, 'max_width': 400
                }
                self.refresh_field_list()
                dialog.destroy()
        
        ttk.Button(dialog, text="Add", command=save).pack(pady=5)
        entry.bind("<Return>", lambda e: save())
    
    def remove_field(self):
        """Remove selected field."""
        selection = self.field_listbox.curselection()
        if not selection:
            return
        
        field_name = self.field_listbox.get(selection[0]).split(" ", 1)[1]
        
        if messagebox.askyesno("Confirm", f"Remove field '{field_name}'?"):
            if field_name in self.field_coordinates:
                del self.field_coordinates[field_name]
                self.refresh_field_list()
                self.update_status(f"Removed: {field_name}")
    
    def save_current_field(self):
        """Save current field coordinates."""
        if not self.current_field:
            messagebox.showwarning("No Field", "Please select a field first")
            return
        
        self.field_coordinates[self.current_field] = {
            'x': self.x_var.get(),
            'y': self.y_var.get(),
            'page': self.page_var.get(),
            'font_size': self.font_size_var.get(),
            'max_width': self.max_width_var.get()
        }
        
        self.refresh_field_list()
        self.update_status(f"Saved: {self.current_field}")
        
        # Re-render with updated coordinates
        if self.preview_var.get():
            self.render_page()
    
    def reset_current_field(self):
        """Reset current field to defaults."""
        self.x_var.set(100)
        self.y_var.set(700)
        self.page_var.set(0)
        self.font_size_var.set(10)
        self.max_width_var.set(400)
    
    def preview_placement(self):
        """Preview text placement on PDF."""
        if not self.current_field or not self.pdf_doc:
            return
        
        try:
            # Clear existing markers
            for marker in self.markers:
                self.canvas.delete(marker)
            self.markers.clear()
            
            page = self.pdf_doc[self.current_page]
            
            # Get coordinates
            x = self.x_var.get()
            y = self.y_var.get()
            text = self.preview_text_var.get()
            
            # Convert to canvas coords
            canvas_x = int(x * self.zoom_level)
            canvas_y = int((page.rect.height - y) * self.zoom_level)
            
            # Draw marker
            marker = self.canvas.create_oval(
                canvas_x - 5, canvas_y - 5,
                canvas_x + 5, canvas_y + 5,
                fill="green", outline="white", width=2
            )
            self.markers.append(marker)
            
            # Draw text preview
            text_marker = self.canvas.create_text(
                canvas_x, canvas_y,
                text=text[:50],  # Limit preview length
                fill="green",
                font=("Arial", int(self.font_size_var.get() * self.zoom_level), "bold"),
                anchor=tk.W
            )
            self.markers.append(text_marker)
            
            self.update_status(f"Preview: {self.current_field} at ({x}, {y})")
            
        except Exception as e:
            messagebox.showerror("Error", f"Preview failed:\n{e}")
    
    def clear_markers(self):
        """Clear all markers from canvas."""
        for marker in self.markers:
            self.canvas.delete(marker)
        self.markers.clear()
        self.update_status("Cleared markers")
    
    def toggle_preview(self):
        """Toggle preview mode."""
        self.preview_mode = self.preview_var.get()
        self.render_page()
    
    def save_coordinates(self):
        """Save all coordinates to config.py."""
        if not self.field_coordinates:
            messagebox.showwarning("No Data", "No coordinates to save")
            return
        
        try:
            # Read current config.py
            config_path = Path("config.py")
            with open(config_path, 'r') as f:
                content = f.read()
            
            # Format new coordinates
            coords_str = "FORM_FIELD_COORDINATES = {\n"
            for field_name, coords in sorted(self.field_coordinates.items()):
                coords_str += f'    "{field_name}": {{\n'
                coords_str += f'        "x": {coords["x"]},\n'
                coords_str += f'        "y": {coords["y"]},\n'
                coords_str += f'        "page": {coords["page"]},\n'
                coords_str += f'        "font_size": {coords["font_size"]},\n'
                coords_str += f'        "max_width": {coords["max_width"]}\n'
                coords_str += '    },\n'
            coords_str += "}\n"
            
            # Replace or append
            if "FORM_FIELD_COORDINATES" in content:
                # Find and replace existing definition
                import re
                pattern = r'FORM_FIELD_COORDINATES\s*=\s*\{[^}]*\}'
                content = re.sub(pattern, coords_str.strip(), content, flags=re.DOTALL)
            else:
                # Append to end
                content += f"\n# Form field coordinates\n{coords_str}"
            
            # Write back
            with open(config_path, 'w') as f:
                f.write(content)
            
            messagebox.showinfo("Success", 
                              f"Saved {len(self.field_coordinates)} field coordinates to config.py")
            self.update_status(f"Saved coordinates to {config_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save coordinates:\n{e}")
    
    def export_config(self):
        """Export coordinates to a JSON file."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filepath:
            try:
                with open(filepath, 'w') as f:
                    json.dump(self.field_coordinates, f, indent=2)
                
                messagebox.showinfo("Success", f"Exported coordinates to:\n{filepath}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Export failed:\n{e}")
    
    def browse_pdf(self):
        """Browse for PDF file."""
        filepath = filedialog.askopenfilename(
            title="Select PDF Template",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if filepath:
            self.load_pdf(filepath)
    
    def browse_sample_data(self):
        """Browse for sample JSON data."""
        filepath = filedialog.askopenfilename(
            title="Select Sample Data",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filepath:
            try:
                with open(filepath, 'r') as f:
                    self.sample_data = json.load(f)
                
                self.refresh_sample_data()
                self.refresh_field_list()
                messagebox.showinfo("Success", f"Loaded sample data from:\n{Path(filepath).name}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load sample data:\n{e}")
    
    def prev_page(self):
        """Go to previous page."""
        if self.pdf_doc and self.current_page > 0:
            self.current_page -= 1
            self.render_page()
    
    def next_page(self):
        """Go to next page."""
        if self.pdf_doc and self.current_page < len(self.pdf_doc) - 1:
            self.current_page += 1
            self.render_page()
    
    def zoom_in(self):
        """Zoom in."""
        self.zoom_level = min(3.0, self.zoom_level + 0.25)
        self.zoom_label.config(text=f"{int(self.zoom_level * 100)}%")
        self.render_page()
    
    def zoom_out(self):
        """Zoom out."""
        self.zoom_level = max(0.25, self.zoom_level - 0.25)
        self.zoom_label.config(text=f"{int(self.zoom_level * 100)}%")
        self.render_page()
    
    def zoom_reset(self):
        """Reset zoom."""
        self.zoom_level = 1.0
        self.zoom_label.config(text="100%")
        self.render_page()
    
    def update_status(self, message: str):
        """Update status bar."""
        self.status_bar.config(text=message)
        print(f"[STATUS] {message}")
    
    def show_instructions(self):
        """Show instruction dialog."""
        instructions = """
PDF Form Coordinate Calibrator - Quick Start

1. LOAD PDF
   • Use 'Load PDF' button or File → Load PDF
   • Select your form template (e.g., STEP2.pdf)

2. SELECT FIELD
   • Choose a field from the Fields tab
   • Fields marked with ✓ have coordinates
   • Fields marked with ○ need coordinates

3. CAPTURE COORDINATES
   • Click anywhere on the PDF canvas
   • Coordinates are automatically captured
   • A marker appears at click position

4. ADJUST & PREVIEW
   • Fine-tune coordinates in Current Field tab
   • Click 'Preview Placement' to see text position
   • Adjust font size and max width as needed

5. SAVE
   • Click 'Save Field' to save current field
   • Use File → Save Coordinates to update config.py
   • All changes persist to your configuration

TIPS:
• Enable 'Preview Mode' to see all field markers
• Use Zoom controls for precise positioning
• Load sample JSON data for realistic previews
• Clear markers to declutter the view
        """
        
        dialog = tk.Toplevel(self)
        dialog.title("Instructions")
        dialog.geometry("600x500")
        
        text = scrolledtext.ScrolledText(dialog, wrap=tk.WORD, font=("Consolas", 9))
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text.insert(1.0, instructions.strip())
        text.config(state=tk.DISABLED)
        
        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=5)
    
    def show_about(self):
        """Show about dialog."""
        about_text = """
PDF Form Coordinate Calibrator
Version 1.0

A visual tool for calibrating form field coordinates
for the PDF Form Abstractor project.

Features:
• Visual PDF viewer with zoom
• Click-to-capture coordinates
• Live text preview
• Auto-save to config.py
• Field management

Built with: Python, Tkinter, PyMuPDF
        """
        messagebox.showinfo("About", about_text.strip())


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Visual PDF coordinate calibrator")
    parser.add_argument(
        '--template', '-t',
        default='output/STEP2.pdf',
        help='Path to PDF template (default: output/STEP2.pdf)'
    )
    
    args = parser.parse_args()
    
    app = CoordinateCalibrator(args.template)
    app.mainloop()


if __name__ == "__main__":
    main()
