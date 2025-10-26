# PDF Form Abstractor

An automated PDF parsing and form-filling application to extract key information from property/abstract reports and populate standardized forms.

## ✅ Current Status: Phase 1 Complete!

The extraction pipeline is **working and tested** on your sample PDFs. The system successfully extracts property information and exports it to structured JSON files.

## 🚀 Quick Start

```bash
# Process a single PDF
python main.py --input "Charles Alleman docs.pdf" --output "output/result.json"

# Process all sample PDFs
python batch_process.py

# Debug extraction issues
python debug_pdf.py "Charles Alleman.pdf"
```

## 🔧 OCR Setup (for Scanned PDFs)

If you have scanned PDFs, install Tesseract OCR:

**Quick Install (Windows - Run as Administrator):**
```powershell
.\install_tesseract.ps1
```

**Or see [OCR_SETUP.md](OCR_SETUP.md) for detailed instructions.**

Once installed, OCR will automatically activate when low-quality text is detected!

## 📊 Test Results

✅ **Charles Alleman docs.pdf**: 54% confidence
- Extracted: Address, Parcel Number, Lot, State, Deed Info

⚠️ **Charles Alleman.pdf**: 0% confidence (scanned/garbled - needs OCR)

## 🎯 What Works Now

- ✅ PDF text extraction (PyPDF2)
- ✅ OCR support for scanned PDFs (with Tesseract)
- ✅ Automatic fallback to OCR when text quality is low
- ✅ Pattern-based field extraction (owner, address, parcel, deed info, etc.)
- ✅ JSON export with confidence scoring
- ✅ Batch processing
- ✅ Debug utilities

## 📁 Project Structure

```
ABSTRACTOR/
├── main.py                 # Single PDF processor
├── batch_process.py        # Batch processor
├── debug_pdf.py           # Debug utility
├── inspect_form.py        # Form field analyzer
├── src/
│   ├── parser.py          # PDF text extraction
│   ├── field_extractor.py # Field extraction logic
│   └── form_filler.py     # Form filling (next phase)
├── output/                # Extracted JSON files
├── config.py              # Configuration
└── requirements.txt       # Python dependencies
```

## 📖 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 3 steps
- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Installation guide
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Detailed overview
- **[WORKFLOW.md](WORKFLOW.md)** - Architecture and workflow

## 🔄 Next Steps

1. **Improve extraction patterns** for your specific documents
2. **Add OCR support** for scanned PDFs (Charles Alleman.pdf)
3. **Map fields to STEP2.pdf** coordinates
4. **Implement form filling** with text overlay

## 💡 Usage Examples

```bash
# Extract with verbose output
python main.py -i "input.pdf" -o "output/result.json" -v

# Process batch
python batch_process.py

# Debug text extraction
python debug_pdf.py "input.pdf"

# Analyze form fields
python inspect_form.py "STEP2.pdf"
```

## 🎓 Key Features

- **Flexible Pattern Matching**: Easily customizable regex patterns
- **Confidence Scoring**: Know how reliable each extraction is
- **Batch Processing**: Handle multiple files at once
- **Debug Tools**: Inspect raw text and troubleshoot issues
- **JSON Export**: Structured data ready for form filling

## 🛠️ Development Status

### Phase 1: Extraction ✅ COMPLETE
- [x] Project scaffolding
- [x] PDF text extraction
- [x] Field pattern matching
- [x] JSON export
- [x] Batch processing
- [x] Debug utilities

### Phase 2: Enhancement 🔄 IN PROGRESS
- [ ] OCR for scanned PDFs
- [ ] Improved extraction patterns
- [ ] Data validation

### Phase 3: Form Filling 📋 PLANNED
- [ ] Map fields to STEP2.pdf coordinates
- [ ] Text overlay implementation
- [ ] Batch form filling
