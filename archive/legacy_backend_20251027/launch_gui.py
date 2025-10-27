"""
Abstractor - PDF Form Processing Desktop Application

A desktop GUI for the PDF Form Abstractor project.
Provides one-click processing of property PDFs with extraction,
OCR, and automatic form filling.

Usage:
    python launch_gui.py
    
Or run as executable:
    Abstractor.exe
"""

try:
    import FreeSimpleGUI as sg
except ImportError:
    try:
        import PySimpleGUI as sg
    except ImportError:
        print("Error: FreeSimpleGUI not installed!")
        print("Please install: pip install FreeSimpleGUI")
        import sys
        sys.exit(1)

import subprocess
import sys
from pathlib import Path
import threading
import queue
from typing import List, Optional
import traceback

# Application metadata
APP_NAME = "Abstractor"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "PDF Form Processing & Auto-Fill"

# Set theme (with fallback for older versions)
try:
    sg.theme('DarkBlue3')
except (AttributeError, KeyError):
    try:
        sg.ChangeLookAndFeel('DarkBlue3')
    except (AttributeError, KeyError):
        pass  # Use default theme

# Queue for thread communication
progress_queue = queue.Queue()


class AbstractorGUI:
    """Main GUI application for PDF form processing."""
    
    def __init__(self):
        self.window: Optional[sg.Window] = None
        self.processing = False
        self.selected_files: List[str] = []
        
        # Paths
        self.project_root = Path(__file__).parent
        self.output_dir = self.project_root / "output"
        self.filled_forms_dir = self.project_root / "filled_forms"
        
        # Ensure directories exist
        self.output_dir.mkdir(exist_ok=True)
        self.filled_forms_dir.mkdir(exist_ok=True)
    
    def create_layout(self):
        """Create the GUI layout."""
        
        # Header section
        header = [
            [sg.Text(APP_NAME, font=("Helvetica", 28, "bold"), 
                    justification='center', expand_x=True)],
            [sg.Text(APP_DESCRIPTION, font=("Helvetica", 12), 
                    justification='center', expand_x=True)],
            [sg.HorizontalSeparator()],
        ]
        
        # File selection section
        file_section = [
            [sg.Text("Select PDF Files to Process:", font=("Helvetica", 11, "bold"))],
            [sg.Listbox(values=[], size=(80, 8), key='-FILE_LIST-', 
                       enable_events=True, select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED)],
            [
                sg.Button("Add Files", key='-ADD_FILES-', size=(12, 1)),
                sg.Button("Add Folder", key='-ADD_FOLDER-', size=(12, 1)),
                sg.Button("Clear All", key='-CLEAR_FILES-', size=(12, 1)),
                sg.Text("", expand_x=True),  # Spacer
                sg.Text("", key='-FILE_COUNT-', font=("Helvetica", 10))
            ],
        ]
        
        # Processing options section
        options_section = [
            [sg.Text("Processing Options:", font=("Helvetica", 11, "bold"))],
            [
                sg.Checkbox("Enable OCR for scanned PDFs", default=True, key='-OCR_ENABLED-'),
                sg.Text("  "),
                sg.Checkbox("Fill forms automatically", default=True, key='-FILL_FORMS-'),
            ],
            [sg.Text("Template PDF:", size=(12, 1)), 
             sg.Input(default_text="templates/STEP2.pdf", key='-TEMPLATE_PATH-', size=(40, 1)),
             sg.FileBrowse(file_types=(("PDF Files", "*.pdf"),))],
        ]
        
        # Progress section
        progress_section = [
            [sg.Text("Status:", font=("Helvetica", 11, "bold"))],
            [sg.Multiline(default_text="Ready to process files.\n", 
                         size=(80, 10), key='-OUTPUT-', 
                         autoscroll=True, disabled=True,
                         font=("Consolas", 9))],
            [sg.ProgressBar(100, orientation='h', size=(67, 20), 
                          key='-PROGRESS-', bar_color=('green', 'white'))],
        ]
        
        # Action buttons
        action_section = [
            [
                sg.Button("Process Files", key='-PROCESS-', 
                         size=(15, 1), button_color=('white', 'green'),
                         font=("Helvetica", 11, "bold")),
                sg.Button("Open Output Folder", key='-OPEN_OUTPUT-', size=(15, 1)),
                sg.Button("Open Filled Forms", key='-OPEN_FILLED-', size=(15, 1)),
                sg.Text("", expand_x=True),  # Spacer
                sg.Button("Exit", key='-EXIT-', size=(10, 1)),
            ],
        ]
        
        # Footer
        footer = [
            [sg.HorizontalSeparator()],
            [sg.Text(f"Version {APP_VERSION}", font=("Helvetica", 8), 
                    text_color='gray', justification='center', expand_x=True)],
        ]
        
        # Combine all sections
        layout = [
            *header,
            [sg.Frame("Input Files", file_section, expand_x=True, font=("Helvetica", 10))],
            [sg.Frame("Options", options_section, expand_x=True, font=("Helvetica", 10))],
            [sg.Frame("Progress", progress_section, expand_x=True, font=("Helvetica", 10))],
            *action_section,
            *footer,
        ]
        
        return layout
    
    def create_window(self):
        """Create the main window."""
        layout = self.create_layout()
        
        self.window = sg.Window(
            APP_NAME,
            layout,
            finalize=True,
            resizable=False,
            enable_close_attempted_event=True,
            icon=None,  # Can add icon later
        )
        
        self.update_file_count()
    
    def log(self, message: str, end: str = "\n"):
        """Add a message to the output log."""
        if self.window:
            current = self.window['-OUTPUT-'].get()
            self.window['-OUTPUT-'].update(current + message + end)
    
    def update_progress(self, percent: int):
        """Update the progress bar."""
        if self.window:
            self.window['-PROGRESS-'].update(percent)
    
    def update_file_count(self):
        """Update the file count display."""
        count = len(self.selected_files)
        if self.window:
            self.window['-FILE_COUNT-'].update(f"{count} file(s) selected")
    
    def add_files(self, files: List[str]):
        """Add files to the selection list."""
        for file in files:
            if file and file not in self.selected_files:
                if Path(file).suffix.lower() == '.pdf':
                    self.selected_files.append(file)
        
        self.window['-FILE_LIST-'].update(
            [Path(f).name for f in self.selected_files]
        )
        self.update_file_count()
    
    def clear_files(self):
        """Clear all selected files."""
        self.selected_files = []
        self.window['-FILE_LIST-'].update([])
        self.update_file_count()
    
    def run_processing(self):
        """Run the processing pipeline in a background thread."""
        try:
            self.log("=" * 60)
            self.log("Starting PDF Processing Pipeline")
            self.log("=" * 60 + "\n")
            
            total_steps = len(self.selected_files) * 2 if self.window['-FILL_FORMS-'].get() else len(self.selected_files)
            current_step = 0
            
            # Step 1: Copy files to input directory
            self.log("Step 1: Preparing files...")
            input_dir = self.project_root / "input"
            input_dir.mkdir(exist_ok=True)
            
            for file_path in self.selected_files:
                src = Path(file_path)
                dst = input_dir / src.name
                
                # Copy file
                import shutil
                shutil.copy2(src, dst)
                self.log(f"  Copied: {src.name}")
            
            progress_queue.put(('progress', 10))
            self.log("\n✓ Files prepared\n")
            
            # Step 2: Run extraction
            self.log("Step 2: Extracting data from PDFs...")
            self.log("  Running batch_process.py...\n")
            
            try:
                python_exe = sys.executable
                result = subprocess.run(
                    [python_exe, "batch_process.py"],
                    cwd=str(self.project_root),
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                if result.returncode == 0:
                    # Parse output for progress
                    for line in result.stdout.split('\n'):
                        if line.strip():
                            self.log(f"  {line}")
                            progress_queue.put(('log', f"  {line}"))
                    
                    progress_queue.put(('progress', 50))
                    self.log("\n✓ Extraction complete\n")
                else:
                    error_msg = result.stderr if result.stderr else "Unknown error"
                    raise Exception(f"Extraction failed: {error_msg}")
                
            except subprocess.TimeoutExpired:
                raise Exception("Extraction timed out after 5 minutes")
            
            # Step 3: Fill forms (if enabled)
            if self.window['-FILL_FORMS-'].get():
                self.log("Step 3: Filling forms...")
                self.log("  Running batch_fill_forms.py...\n")
                
                try:
                    result = subprocess.run(
                        [python_exe, "batch_fill_forms.py"],
                        cwd=str(self.project_root),
                        capture_output=True,
                        text=True,
                        timeout=300
                    )
                    
                    if result.returncode == 0:
                        for line in result.stdout.split('\n'):
                            if line.strip():
                                self.log(f"  {line}")
                                progress_queue.put(('log', f"  {line}"))
                        
                        progress_queue.put(('progress', 90))
                        self.log("\n✓ Form filling complete\n")
                    else:
                        error_msg = result.stderr if result.stderr else "Unknown error"
                        raise Exception(f"Form filling failed: {error_msg}")
                
                except subprocess.TimeoutExpired:
                    raise Exception("Form filling timed out after 5 minutes")
            
            # Completion
            progress_queue.put(('progress', 100))
            self.log("=" * 60)
            self.log("✅ PROCESSING COMPLETE!")
            self.log("=" * 60 + "\n")
            
            # Count outputs
            extracted_files = list(self.output_dir.glob("*_extracted.json"))
            filled_files = list(self.filled_forms_dir.glob("*_filled.pdf"))
            
            self.log(f"Results:")
            self.log(f"  • Extracted data: {len(extracted_files)} JSON files in output/")
            if self.window['-FILL_FORMS-'].get():
                self.log(f"  • Filled forms: {len(filled_files)} PDFs in filled_forms/")
            self.log("")
            
            progress_queue.put(('complete', True))
            
        except Exception as e:
            error_msg = f"Error: {str(e)}\n\n{traceback.format_exc()}"
            progress_queue.put(('error', error_msg))
            self.log(f"\n❌ ERROR: {str(e)}\n")
    
    def start_processing(self):
        """Start the processing in a background thread."""
        if not self.selected_files:
            sg.popup_error("No files selected", 
                          "Please select at least one PDF file to process.",
                          title="No Files")
            return
        
        if self.processing:
            sg.popup_warning("Already processing", 
                           "Please wait for current processing to complete.",
                           title="Busy")
            return
        
        # Disable process button
        self.window['-PROCESS-'].update(disabled=True)
        self.processing = True
        
        # Clear previous output
        self.window['-OUTPUT-'].update("")
        self.update_progress(0)
        
        # Start processing thread
        thread = threading.Thread(target=self.run_processing, daemon=True)
        thread.start()
    
    def open_folder(self, folder: Path):
        """Open a folder in file explorer."""
        if folder.exists():
            import os
            import platform
            
            if platform.system() == "Windows":
                os.startfile(folder)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", str(folder)])
            else:  # Linux
                subprocess.run(["xdg-open", str(folder)])
        else:
            sg.popup_error("Folder not found", 
                          f"The folder does not exist:\n{folder}",
                          title="Error")
    
    def run(self):
        """Run the main event loop."""
        self.create_window()
        
        while True:
            event, values = self.window.read(timeout=100)
            
            # Handle window close
            if event in (sg.WINDOW_CLOSE_ATTEMPTED_EVENT, '-EXIT-'):
                if self.processing:
                    response = sg.popup_yes_no(
                        "Processing in progress",
                        "Are you sure you want to exit?\nProcessing will be interrupted.",
                        title="Confirm Exit"
                    )
                    if response == "Yes":
                        break
                else:
                    break
            
            # Handle events
            if event == '-ADD_FILES-':
                files = sg.popup_get_file(
                    "Select PDF files",
                    multiple_files=True,
                    file_types=(("PDF Files", "*.pdf"), ("All Files", "*.*")),
                    title="Select PDFs"
                )
                if files:
                    if isinstance(files, str):
                        files = [files]
                    self.add_files(files)
            
            elif event == '-ADD_FOLDER-':
                folder = sg.popup_get_folder(
                    "Select folder containing PDFs",
                    title="Select Folder"
                )
                if folder:
                    pdf_files = list(Path(folder).glob("*.pdf"))
                    self.add_files([str(f) for f in pdf_files])
            
            elif event == '-CLEAR_FILES-':
                self.clear_files()
            
            elif event == '-PROCESS-':
                self.start_processing()
            
            elif event == '-OPEN_OUTPUT-':
                self.open_folder(self.output_dir)
            
            elif event == '-OPEN_FILLED-':
                self.open_folder(self.filled_forms_dir)
            
            # Check for progress updates from worker thread
            try:
                while True:
                    msg_type, msg_data = progress_queue.get_nowait()
                    
                    if msg_type == 'progress':
                        self.update_progress(msg_data)
                    elif msg_type == 'log':
                        self.log(msg_data)
                    elif msg_type == 'complete':
                        self.processing = False
                        self.window['-PROCESS-'].update(disabled=False)
                        sg.popup_auto_close(
                            "✅ Processing Complete!\n\n"
                            f"Forms saved to: {self.filled_forms_dir}\n\n"
                            "This window will close in 5 seconds.",
                            title="Success",
                            auto_close_duration=5,
                            button_type=sg.POPUP_BUTTONS_OK
                        )
                    elif msg_type == 'error':
                        self.processing = False
                        self.window['-PROCESS-'].update(disabled=False)
                        sg.popup_error(
                            "Processing failed!\n\n"
                            "See the log for details.",
                            title="Error"
                        )
                    
            except queue.Empty:
                pass
        
        self.window.close()


def main():
    """Main entry point."""
    print(f"{APP_NAME} v{APP_VERSION}")
    print(f"Starting GUI...")
    
    app = AbstractorGUI()
    app.run()
    
    print("Application closed.")


if __name__ == "__main__":
    main()
