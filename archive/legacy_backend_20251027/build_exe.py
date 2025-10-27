# Build Abstractor.exe - Desktop Application Builder
# 
# This script packages the Abstractor PDF Form Processing application
# into a standalone Windows executable.
#
# Usage:
#   python build_exe.py
#
# Or manually run:
#   pyinstaller --onefile --windowed --name=Abstractor launch_gui.py

import subprocess
import sys
from pathlib import Path
import shutil

print("=" * 60)
print("Abstractor - Executable Builder")
print("=" * 60)
print()

# Check if pyinstaller is installed
try:
    import PyInstaller
    print(f"✓ PyInstaller found: {PyInstaller.__version__}")
except ImportError:
    print("✗ PyInstaller not found!")
    print()
    print("Installing PyInstaller...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
    print()

# Build command
build_cmd = [
    "pyinstaller",
    "--onefile",                    # Single executable file
    "--windowed",                   # No console window (GUI only)
    "--name=Abstractor",            # Output name
    "--add-data=config.py;.",       # Include config file
    "--add-data=src;src",           # Include src directory
    "--hidden-import=PyPDF2",       # Ensure dependencies are included
    "--hidden-import=fitz",
    "--hidden-import=pytesseract",
    "--hidden-import=pdf2image",
    "--clean",                      # Clean build
    "launch_gui.py"
]

print("Building Abstractor.exe...")
print()
print("Command:", " ".join(build_cmd))
print()

try:
    result = subprocess.run(build_cmd, check=True)
    
    print()
    print("=" * 60)
    print("✅ BUILD SUCCESSFUL!")
    print("=" * 60)
    print()
    print("Executable created:")
    print(f"  📦 dist/Abstractor.exe")
    print()
    print("To distribute:")
    print("  1. Copy dist/Abstractor.exe to any Windows PC")
    print("  2. Double-click to run - no installation needed!")
    print()
    print("Note: Users will need Tesseract OCR installed separately")
    print("      if processing scanned PDFs.")
    print()
    
except subprocess.CalledProcessError as e:
    print()
    print("=" * 60)
    print("❌ BUILD FAILED!")
    print("=" * 60)
    print()
    print(f"Error: {e}")
    print()
    print("Troubleshooting:")
    print("  1. Ensure all dependencies are installed:")
    print("     pip install -r requirements_gui.txt")
    print("  2. Check that all source files are present")
    print("  3. Review the build log above for specific errors")
    print()
    sys.exit(1)
