# Quick Reference - PDF Form Abstractor with OCR

## 🚀 Common Commands

```bash
# Process single PDF
python main.py -i "document.pdf" -o "output/result.json"

# Process with verbose output
python main.py -i "document.pdf" -o "output/result.json" -v

# Process all PDFs in current directory
python batch_process.py

# Debug text extraction
python debug_pdf.py "document.pdf"

# Analyze form fields
python inspect_form.py "form.pdf"
```

## 🔧 OCR Setup (One-Time)

```powershell
# Quick install (Run as Administrator)
.\install_tesseract.ps1

# Verify installation
tesseract --version

# Test OCR
python main.py -i "Charles Alleman.pdf" -o "output/test.json" -v
```

## 📊 Understanding Output

### JSON Structure
```json
{
  "source_file": "document.pdf",
  "page_count": 21,
  "ocr_used": false,                    // OCR was/wasn't used
  "confidence_score": 0.54,             // 0.0 to 1.0
  "extracted_fields": {
    "owner_name": "John Doe",
    "property_address": "123 Main St",
    "parcel_number": "12-345-678",
    ...
  }
}
```

### Confidence Scores
- **0-30%**: Poor extraction, check PDF quality
- **30-60%**: Moderate, review fields manually
- **60-90%**: Good extraction quality
- **90-100%**: Excellent, high confidence

## 🎯 OCR Status Indicators

### Console Output
```
✓ Extracted text from 2 page(s)           // Normal extraction
✓ OCR was used (300 DPI)                  // OCR was triggered
✓ Confidence: 54.0% (OCR)                 // Batch mode with OCR
```

### When OCR Activates
- Text < 50 characters
- < 60% alphanumeric characters
- Low word density (garbled text)

## ⚙️ Configuration (config.py)

```python
# OCR Settings
OCR_ENABLED = True          # Enable/disable OCR
OCR_DPI = 300               # 200=fast, 300=balanced, 400=quality
OCR_LANGUAGE = 'eng'        # Language code

# Quality Thresholds
MIN_TEXT_LENGTH = 50
MIN_ALPHANUMERIC_RATIO = 0.6
MIN_WORD_DENSITY = 50
```

## 🐛 Troubleshooting

### OCR Not Working
```bash
# Check Tesseract
tesseract --version

# Not installed? Run installer
.\install_tesseract.ps1

# Or set path in config.py
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### Low Confidence
```bash
# See raw text
python main.py -i "file.pdf" -o "out.json" -v

# Debug extraction
python debug_pdf.py "file.pdf"

# Increase OCR quality
# Edit config.py: OCR_DPI = 400
```

### Slow Processing
```bash
# Reduce OCR quality for speed
# Edit config.py: OCR_DPI = 200

# Or disable OCR
# Edit config.py: OCR_ENABLED = False
```

## 📁 Project Structure

```
ABSTRACTOR/
├── main.py                 # Single file processor
├── batch_process.py        # Batch processor
├── debug_pdf.py           # Debug utility
├── inspect_form.py        # Form analyzer
├── install_tesseract.ps1  # OCR installer
├── config.py              # Configuration
├── src/
│   ├── parser.py          # PDF extraction + OCR
│   ├── field_extractor.py # Pattern matching
│   └── form_filler.py     # Form filling (TBD)
└── output/                # Generated JSON files
```

## 📚 Documentation

- **README.md** - Project overview
- **QUICKSTART.md** - Get started in 3 steps
- **OCR_SETUP.md** - Detailed OCR installation
- **OCR_COMPLETE.md** - OCR implementation details
- **GETTING_STARTED.md** - Full setup guide
- **PROJECT_SUMMARY.md** - Complete documentation
- **WORKFLOW.md** - Architecture

## 🎓 Tips & Tricks

### Batch Processing Multiple Files
```bash
# Move PDFs to current directory, then:
python batch_process.py

# Results in output/*.json
```

### Customizing Field Patterns
```python
# Edit src/field_extractor.py
def extract_your_field(self):
    patterns = [
        r"Your Pattern: (.+)",
        r"Alternative: (.+)"
    ]
    return self._extract_with_patterns(patterns)

# Add to extract_all_fields():
self.fields["your_field"] = self.extract_your_field()
```

### Testing Extraction Patterns
1. Use `debug_pdf.py` to see raw text
2. Test regex at https://regex101.com
3. Add pattern to `field_extractor.py`
4. Test with `main.py -v`

### Performance Optimization
- Use lower DPI for draft extraction
- Cache results for repeated processing
- Process overnight for large batches
- Use SSD for faster image operations

## ✅ Quick Checks

```bash
# 1. Is Python working?
python --version                # Should show 3.8+

# 2. Are packages installed?
pip list | grep -E "PyPDF2|pdf2image|pytesseract"

# 3. Is Tesseract installed?
tesseract --version

# 4. Test basic extraction
python main.py -i "Charles Alleman docs.pdf" -o "test.json"

# 5. Test OCR
python main.py -i "Charles Alleman.pdf" -o "test_ocr.json" -v
```

## 🎯 Success Criteria

Your system is working correctly when:
- ✅ JSON files appear in `output/` folder
- ✅ Confidence scores are > 50% for normal PDFs
- ✅ Key fields (address, parcel) are extracted
- ✅ OCR activates for scanned PDFs (after Tesseract install)
- ✅ No Python errors during processing

## 🆘 Getting Help

1. Check console output for error messages
2. Use `--verbose` flag to see detailed info
3. Run `debug_pdf.py` to inspect extracted text
4. Review `OCR_SETUP.md` for Tesseract issues
5. Check `config.py` for configuration options

---

**Need more detail?** See [README.md](README.md) or [GETTING_STARTED.md](GETTING_STARTED.md)
