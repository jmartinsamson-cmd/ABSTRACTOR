# ABSTRACTOR

Automated PDF parsing and assembly with a Streamlit UI. Upload client PDFs, auto-extract fields, review/edit, and generate a complete Bradley Abstract with a filled cover page plus merged documents.

## Quick start

### 1) Python env and packages

Use the provided script:

```bash
bash setup_and_run.sh
```

This creates/activates a virtualenv (prefers `.venv`) and installs dependencies from `requirements.txt`.

System OCR deps (for scanned PDFs) are listed in `packages.txt` and should be installed already in this devcontainer:

- tesseract-ocr, tesseract-ocr-eng
- poppler-utils

If running elsewhere, install them via your OS package manager.

### 2) Run Streamlit

- VS Code: Command Palette → "Run Task" → "Run Streamlit app"
- Or manually:

```bash
./.venv/bin/python -m streamlit run streamlit_app.py --server.headless true --server.port 8501
```

Then open the URL shown in the terminal (typically <http://localhost:8501>).

### 3) Use the app

- Upload one or more PDF files in the sidebar.
- Click "Extract Data from PDFs" to parse and prefill fields.
- Edit fields as needed.
- Click "Generate Cover Page" to create the cover and assemble the final abstract PDF.
- Download from the button that appears, or find output files in `output/`.

## Internals

- `src/parser.py`: PDF text extraction (PyPDF2). Falls back to OCR (pytesseract + pdf2image) when text quality is low.
- `src/field_extractor.py`: Regex-based field extraction.
- `src/cover_page_generator.py`: Generates the Bradley Abstract cover using PyMuPDF (fitz) and ReportLab.
  - Adapter `BradleyAbstractCoverPage.generate_cover_page(data, output_path)` is used by the UI.
- `src/pdf_assembler.py`: Merges cover + (optional) form + original docs into a single PDF via PyPDF2.
- Template file: `templates/bradley_abstract_cover.pdf`.

## Git MCP server (optional)

A local MCP server exposing Git tools is included for MCP-capable clients.


- Location: `tools/git-mcp-server/`
- Start via VS Code task: "Start Git MCP server" (or "Start Git MCP server (dev)")
- Exposed tools: `git_status`, `git_log`, `git_diff`, `git_commit`, `git_push`

## Troubleshooting

- OCR doesn’t work: ensure `tesseract-ocr` and `poppler-utils` are installed on the system.
- Import errors for PyMuPDF/ReportLab: re-run `bash setup_and_run.sh`.
- Template missing: confirm `templates/bradley_abstract_cover.pdf` exists.
- Streamlit CORS/XSRF warning: informational by default; app still runs. If you need cross-origin embedding, disable `server.enableXsrfProtection` in Streamlit config (not recommended unless you know the implications).

## License

This repository’s code is provided as-is by the owner. See repository settings for license details.
