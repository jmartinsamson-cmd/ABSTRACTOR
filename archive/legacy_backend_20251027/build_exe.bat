@echo off
REM Build Abstractor.exe - Windows Batch Script
REM
REM This script packages the Abstractor application into a standalone executable
REM
REM Usage: Double-click this file or run from command prompt

echo ============================================================
echo Abstractor - Executable Builder
echo ============================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.7 or later and try again.
    pause
    exit /b 1
)

echo Installing/Updating dependencies...
python -m pip install -r requirements_gui.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)
echo.

echo Building Abstractor.exe with PyInstaller...
echo.

pyinstaller --onefile ^
            --windowed ^
            --name=Abstractor ^
            --add-data=config.py;. ^
            --add-data=src;src ^
            --hidden-import=PyPDF2 ^
            --hidden-import=fitz ^
            --hidden-import=pytesseract ^
            --hidden-import=pdf2image ^
            --clean ^
            launch_gui.py

if errorlevel 1 (
    echo.
    echo ============================================================
    echo BUILD FAILED!
    echo ============================================================
    echo.
    echo Check the errors above and try again.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo BUILD SUCCESSFUL!
echo ============================================================
echo.
echo Executable created: dist\Abstractor.exe
echo.
echo To run: Double-click dist\Abstractor.exe
echo.
pause
