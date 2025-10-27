# Property Abstract Workflow - Implementation Guide

## Overview
This document explains the reworked backend logic for the Property Abstract application. The Streamlit UI remains unchanged, but the backend has been completely rewritten to implement the new workflow.

## New Workflow

### 1. **Billing Page Generation**
- **Module**: `src/billing_generator.py`
- **Purpose**: Creates a professional billing page as the first page of the final PDF
- **Features**:
  - Company header (Bradley Property Abstracts)
  - Client information
  - Property address
  - Services provided
  - Fee information
  - Custom notes
  - Professional formatting

### 2. **Data Extraction from Scanned Documents**
- **Modules**: Existing `src/parser.py` and `src/field_extractor.py`
- **Purpose**: Extract text and structured data from uploaded legal documents
- **Features**:
  - OCR support for scanned documents
  - Field extraction (owner, address, legal description, etc.)
  - Image extraction for supporting documents

### 3. **Bradley Abstract Form Filling**
- **Module**: `src/pdf_assembler.py` (clear_and_fill_bradley_form method)
- **Purpose**: Clear old data and fill the Bradley Abstract form with new client information
- **Features**:
  - Uses existing FormFiller with client data
  - Clears previous entries
  - Maps extracted fields to form positions
  - Inserts images where configured

### 4. **PDF Assembly**
- **Module**: `src/pdf_assembler.py`
- **Purpose**: Combine all components into a single PDF
- **Assembly Order**:
  1. Billing page (first)
  2. Filled Bradley Abstract form
  3. All scanned legal documents (appended)

### 5. **Live Preview & Editing**
- **Implementation**: Streamlit UI (existing components)
- **Features**:
  - Preview assembled PDF inline
  - Edit client information
  - Regenerate PDF with updates
  - Download final version

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit UI (Unchanged)                  │
│  - File upload                                               │
│  - Configuration options                                     │
│  - Process button                                            │
│  - Preview and edit sections                                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              New Backend (src/streamlit_backend.py)          │
│  - process_documents_new()                                   │
│  - regenerate_with_edits()                                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│          Workflow Orchestrator (src/abstract_workflow.py)    │
│  - Coordinates all steps                                     │
│  - Manages data flow between modules                         │
└─────┬───────────┬───────────┬──────────────┬────────────────┘
      │           │           │              │
      ▼           ▼           ▼              ▼
┌──────────┐ ┌─────────┐ ┌─────────┐ ┌──────────────┐
│ Billing  │ │ Parser  │ │  Form   │ │   PDF        │
│Generator │ │Extractor│ │ Filler  │ │  Assembler   │
└──────────┘ └─────────┘ └─────────┘ └──────────────┘
```

## Key Modules

### src/billing_generator.py
```python
class BillingPageGenerator:
    - generate(client_info, output_path) -> bytes
```
Generates a professional billing page with company branding and client information.

### src/pdf_assembler.py
```python
class PDFAssembler:
    - assemble_abstract(billing, form, scanned_docs) -> bytes
    - clear_and_fill_bradley_form(template, client_data) -> bytes
    - extract_text_from_pdfs(pdf_files) -> dict
```
Handles all PDF manipulation: clearing, filling, and assembling.

### src/abstract_workflow.py
```python
class AbstractWorkflow:
    - process_documents(uploaded_files, client_info, use_ocr) -> dict
    - update_client_info_and_regenerate(scanned_docs, client_info, extracted_data) -> dict
```
Orchestrates the complete workflow from upload to final PDF.

### src/streamlit_backend.py
```python
- process_documents_new(uploaded_files, use_ocr, client_info) -> dict
- regenerate_with_edits(scanned_docs, client_info, extracted_data) -> dict
```
Bridge between Streamlit UI and the new workflow modules.

## Integration with Streamlit App

The existing Streamlit app (`streamlit_app.py`) needs minimal changes:

1. **Import new backend**:
```python
from src.streamlit_backend import process_documents_new, regenerate_with_edits
```

2. **Replace process button logic**:
```python
if process_button:
    result = process_documents_new(
        uploaded_files=uploaded_files,
        use_ocr=use_ocr,
        client_info=None  # or collect from UI
    )
    
    if result['status'] == 'success':
        st.session_state.final_pdf_bytes = result['final_pdf_bytes']
        st.session_state.billing_pdf_bytes = result['billing_pdf_bytes']
        st.session_state.filled_form_bytes = result['filled_form_bytes']
        st.session_state.scanned_docs = result['scanned_docs']
        st.session_state.extracted_data = result['extracted_data']
```

3. **Update edit/regenerate logic**:
```python
if submit_edits:
    result = regenerate_with_edits(
        scanned_docs=st.session_state.scanned_docs,
        client_info=edited_client_info,
        extracted_data=st.session_state.extracted_data
    )
    
    if result['status'] == 'success':
        st.session_state.final_pdf_bytes = result['final_pdf_bytes']
```

## Benefits of New Architecture

1. **Clear Separation of Concerns**:
   - Billing generation isolated
   - Form filling isolated
   - PDF assembly isolated
   - Workflow orchestration separate from UI

2. **Maintainability**:
   - Each module has a single responsibility
   - Easy to test individual components
   - Easy to modify one part without affecting others

3. **Flexibility**:
   - Easy to add new features (e.g., different billing templates)
   - Easy to change assembly order
   - Easy to add new document types

4. **Reusability**:
   - Modules can be used independently
   - Workflow can be reused in CLI or other interfaces
   - Backend logic separated from Streamlit

## Testing

Run the test script to verify the workflow:
```bash
python test_pdf_gen.py
```

This will test the complete flow with sample documents.

## Next Steps

1. Install new dependency: `pip install reportlab`
2. Update streamlit_app.py to use new backend
3. Test with your wife's actual documents
4. Fine-tune billing page layout if needed
5. Adjust form field mappings in config.py as needed

## Notes

- The UI (buttons, layout, styling) remains exactly as before
- All existing configuration options (OCR, etc.) are preserved
- The Bradley Abstract form template path is configurable
- Client information can be collected from UI or extracted from documents
