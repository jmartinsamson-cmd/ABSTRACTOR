# Quick Tesseract Installer for Windows
# Run this script in PowerShell as Administrator

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Tesseract OCR Installer" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "⚠️  This script requires administrator privileges." -ForegroundColor Yellow
    Write-Host "Please right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit
}

Write-Host "Step 1: Downloading Tesseract OCR..." -ForegroundColor Green

# Tesseract download URL (latest stable version)
$tesseractUrl = "https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231005.exe"
$installerPath = "$env:TEMP\tesseract-installer.exe"

try {
    Invoke-WebRequest -Uri $tesseractUrl -OutFile $installerPath -UseBasicParsing
    Write-Host "✓ Download complete" -ForegroundColor Green
} catch {
    Write-Host "✗ Download failed: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please download manually from:" -ForegroundColor Yellow
    Write-Host "https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Step 2: Installing Tesseract..." -ForegroundColor Green
Write-Host "Please follow the installation wizard." -ForegroundColor Yellow
Write-Host "IMPORTANT: Note the installation path (default: C:\Program Files\Tesseract-OCR)" -ForegroundColor Yellow
Write-Host ""

# Run installer
Start-Process -FilePath $installerPath -Wait

# Check common installation paths
$possiblePaths = @(
    "C:\Program Files\Tesseract-OCR",
    "C:\Program Files (x86)\Tesseract-OCR",
    "$env:LOCALAPPDATA\Programs\Tesseract-OCR"
)

$tesseractPath = $null
foreach ($path in $possiblePaths) {
    if (Test-Path "$path\tesseract.exe") {
        $tesseractPath = $path
        break
    }
}

if ($tesseractPath) {
    Write-Host "✓ Tesseract found at: $tesseractPath" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "Step 3: Adding to PATH..." -ForegroundColor Green
    
    # Get current PATH
    $currentPath = [Environment]::GetEnvironmentVariable("Path", [System.EnvironmentVariableTarget]::Machine)
    
    # Check if already in PATH
    if ($currentPath -notlike "*$tesseractPath*") {
        try {
            $newPath = $currentPath + ";$tesseractPath"
            [Environment]::SetEnvironmentVariable("Path", $newPath, [System.EnvironmentVariableTarget]::Machine)
            Write-Host "✓ Added to system PATH" -ForegroundColor Green
        } catch {
            Write-Host "⚠️  Could not add to PATH automatically" -ForegroundColor Yellow
            Write-Host "Please add manually: $tesseractPath" -ForegroundColor Yellow
        }
    } else {
        Write-Host "✓ Already in PATH" -ForegroundColor Green
    }
    
    Write-Host ""
    Write-Host "==================================" -ForegroundColor Cyan
    Write-Host "Installation Complete!" -ForegroundColor Green
    Write-Host "==================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Close and reopen your terminal/IDE" -ForegroundColor White
    Write-Host "2. Test with: tesseract --version" -ForegroundColor White
    Write-Host "3. Run: python main.py -i 'Charles Alleman.pdf' -o output/ocr_test.json -v" -ForegroundColor White
    Write-Host ""
    
} else {
    Write-Host "⚠️  Could not find Tesseract installation" -ForegroundColor Yellow
    Write-Host "Please verify installation completed successfully" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "If installed to a custom location, update config.py:" -ForegroundColor Yellow
    Write-Host "TESSERACT_PATH = r'C:\Your\Custom\Path\tesseract.exe'" -ForegroundColor White
}

# Clean up
Remove-Item $installerPath -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
