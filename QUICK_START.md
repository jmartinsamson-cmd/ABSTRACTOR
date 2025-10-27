# Quick Start - Integrating the New Backend

## 1. Install Dependencies

```bash
pip install reportlab
```

## 2. Minimal Changes to streamlit_app.py

You only need to change **two small sections** in your existing `streamlit_app.py`:

### A. Add Import at the Top

Add this line with your other imports (around line 10):

```python
from src.streamlit_backend import process_documents_new, regenerate_with_edits
```

### B. Replace Process Button Logic

Find this section (around line 629):

```python
if process_button:
    # OLD CODE BELOW - REPLACE ALL OF THIS
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Clear previous results
    st.session_state.extraction_results = {}
    st.session_state.filled_forms = {}
    
    # ... rest of old code ...
```

**Replace with this:**

```python
if process_button:
    progress_bar = st.progress(0)
    status_text = st.empty()
    status_text.markdown("**Processing documents with new workflow...**")
    
    # Call new backend
    result = process_documents_new(
        uploaded_files=uploaded_files,
        use_ocr=use_ocr,
        client_info=None  # Set to None for now, or collect from UI
    )
    
    progress_bar.progress(1.0)
    
    if result['status'] == 'success':
        # Store results in session state
        st.session_state.final_pdf_bytes = result['final_pdf_bytes']
        st.session_state.filled_forms = {"Property_Abstract.pdf": result['final_pdf_bytes']}
        st.session_state.extraction_results = {
            f"Combined_{result['num_files']}_files": {
                'extracted_data': result['extracted_data'],
                'images_extracted': result['images_extracted'],
                'fields_found': result['num_fields']
            }
        }
        
        st.success(f"✅ {result['message']}")
        st.write(f"📊 Summary: Processed {result['num_files']} file(s), "
                f"extracted {result['num_fields']} fields, "
                f"collected {result['images_extracted']} images")
        
        # Debug view
        with st.expander("🔍 View Extracted Data"):
            st.json(result['extracted_data'])
    else:
        st.error(f"❌ {result['message']}")
    
    status_text.empty()
    progress_bar.empty()
```

## 3. Test It

```bash
streamlit run streamlit_app.py
```

Upload PDFs and click "Process PDFs" - you should now get:
1. ✅ Billing page (first)
2. ✅ Filled Bradley Abstract form
3. ✅ All scanned documents appended

## That's It!

The UI stays exactly the same. Only the backend processing changes.

## Optional: Add Billing Info Input

If you want to collect billing information through the UI, add this **before** the file uploader section:

```python
# Add after the sidebar configuration, before "Upload Source PDFs"
st.markdown("---")
st.markdown('<h2 class="section-header">💳 Billing Information</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    client_name_input = st.text_input("Client Name", key="billing_client_name")
    fee_amount_input = st.text_input("Fee Amount", value="$150.00", key="billing_fee")
with col2:
    abstract_date_input = st.date_input("Abstract Date", key="billing_date")
    billing_notes = st.text_area("Notes", height=100, key="billing_notes")

# Create client_info dict
client_info = {
    'client_name': client_name_input if client_name_input else None,
    'fee_amount': fee_amount_input if fee_amount_input else "$150.00",
    'abstract_date': abstract_date_input.strftime("%B %d, %Y") if abstract_date_input else None,
    'notes': billing_notes if billing_notes else ''
}
```

Then pass `client_info` to the process function:

```python
result = process_documents_new(
    uploaded_files=uploaded_files,
    use_ocr=use_ocr,
    client_info=client_info  # ← Pass it here instead of None
)
```

## Troubleshooting

**PDF not generating?**
- Check that `templates/STEP2.pdf` exists
- Make sure reportlab is installed: `pip list | grep reportlab`
- Check the Streamlit console for errors

**Want to customize billing page?**
- Edit `src/billing_generator.py`
- Modify the `generate()` method
- Change header, fonts, layout as needed

**Need help?**
- See `WORKFLOW_GUIDE.md` for technical details
- See `IMPLEMENTATION_SUMMARY.md` for overview
- Check existing code in new modules for examples
