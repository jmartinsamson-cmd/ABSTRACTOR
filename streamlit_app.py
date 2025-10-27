import streamlit as st
import json
from pathlib import Path
import tempfile
import sys
import os
from src.parser import PDFParser
from src.field_extractor import FieldExtractor
from src.form_filler import FormFiller
import streamlit.components.v1 as components
# Add current directory to path for module imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)


"""
ABSTRACTOR - Web Application
Streamlit-based web interface for PDF form processing
Access from any browser - no installation required!
"""
sys.path.insert(0, current_dir)
# Page configuration
st.set_page_config(
    page_title="Abstractor - PDF Form Processor ✨",
    page_icon="�",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Polished Girly Theme
st.markdown("""
<style>
    /* Main app background */
    .main {
        background: linear-gradient(135deg, #d4c5e8 0%, #c5b3db 50%, #b39dce 100%) !important;
    }
    
    .main .block-container {
        background: transparent !important;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #d4c5e8 0%, #c5b3db 50%, #b39dce 100%) !important;
    }
    
    .element-container {
        background: transparent !important;
    }
    
    /* Sidebar - professional with shadow */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #e6d9ff 0%, #f0e8ff 100%);
        box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
        padding-top: 1rem;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
        font-size: 1rem;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
        color: #7b5fa8;
    }
    
    /* Header - horizontal layout */
    .main-header {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
        margin-bottom: 0.5rem;
        padding: 1rem 0;
        border-bottom: 2px solid rgba(255, 105, 180, 0.3);
    }
    
    .main-title {
        background: linear-gradient(135deg, #ff69b4, #ff1493);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.5em;
        font-weight: bold;
        margin: 0;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    
    .subtitle {
        text-align: center;
        color: #c946a6;
        font-size: 1em;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2d2d2d;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Upload box - centered and refined */
    [data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.95);
        border: 2px dashed #c99cde;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        max-width: 700px;
        margin: 0 auto;
    }
    
    [data-testid="stFileUploader"] label {
        font-size: 0.95rem;
        color: #555;
    }
    
    /* Info cards */
    .info-card {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
        padding: 1.25rem;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
        margin-bottom: 1rem;
    }
    
    .info-card h3 {
        font-size: 1.1rem;
        font-weight: 600;
        color: #7b5fa8;
        margin-bottom: 0.75rem;
    }
    
    .info-card ul {
        margin: 0;
        padding-left: 1.2rem;
        font-size: 0.9rem;
        line-height: 1.8;
        color: #444;
    }
    
    .info-card li {
        margin-bottom: 0.4rem;
    }
    
    /* Success/Error boxes */
    .success-box {
        padding: 1rem;
        background: rgba(220, 255, 220, 0.9);
        border-left: 4px solid #4caf50;
        border-radius: 8px;
        color: #2e7d32;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    }
    
    .error-box {
        padding: 1rem;
        background: rgba(255, 220, 220, 0.9);
        border-left: 4px solid #f44336;
        border-radius: 8px;
        color: #c62828;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #da70d6, #ba55d3);
        color: white;
        border-radius: 20px;
        border: none;
        padding: 0.6rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        box-shadow: 0 3px 6px rgba(186, 85, 211, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #ba55d3, #9370db);
        box-shadow: 0 4px 8px rgba(186, 85, 211, 0.4);
        transform: translateY(-1px);
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #9370db;
        font-weight: 700;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.85rem;
        color: #666;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.85);
        border-radius: 8px;
        color: #7b5fa8;
        font-weight: 600;
        font-size: 0.95rem;
    }
    
    /* Download buttons */
    .stDownloadButton>button {
        background: linear-gradient(135deg, #9370db, #7b68ee);
        color: white;
        border-radius: 16px;
        font-weight: 600;
        font-size: 0.9rem;
        padding: 0.5rem 1.5rem;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        border-bottom: 2px solid rgba(147, 112, 219, 0.2);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.7);
        border-radius: 8px 8px 0 0;
        color: #7b5fa8;
        font-weight: 600;
        padding: 0.6rem 1.2rem;
        font-size: 0.95rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #da70d6, #ba55d3);
        color: white;
    }
    
    /* Responsive design */
    @media (max-width: 1024px) {
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        
        .main-title {
            font-size: 2rem;
        }
        
        .section-header {
            font-size: 1.3rem;
        }
    }
    
    @media (max-width: 768px) {
        .main-title {
            font-size: 1.8rem;
        }
        
        [data-testid="stFileUploader"] {
            max-width: 100%;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'processed_files' not in st.session_state:
    st.session_state.processed_files = []
if 'extraction_results' not in st.session_state:
    st.session_state.extraction_results = {}
if 'filled_forms' not in st.session_state:
    st.session_state.filled_forms = {}

def process_pdf(uploaded_file, use_ocr=True, template_path=None):
    """Process a single PDF file"""
    REQUIRED_FIELDS = [
        "owner_name", "property_address", "parcel_number", "legal_description"
        # Add more required fields as needed
    ]
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Save uploaded file
            input_file = temp_path / uploaded_file.name
            with open(input_file, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            
            # Step 1: Extract text
            st.info(f"📖 Extracting text from {uploaded_file.name}...")
            parser = PDFParser(str(input_file))
            text = parser.extract_text()
            
            if use_ocr and len(text.strip()) < 100:
                st.info("🔍 Low text detected - using OCR...")
                parser_with_ocr = PDFParser(str(input_file), use_ocr=True)
                text = parser_with_ocr.extract_text()
            
            # Step 2: Extract fields
            st.info("🔎 Extracting fields...")
            extractor = FieldExtractor(text)
            extracted_data = extractor.extract_all_fields()
            
            # Required field check
            missing_fields = [f for f in REQUIRED_FIELDS if f not in extracted_data or not extracted_data[f]]
            if missing_fields:
                st.warning(f"Missing required fields: {', '.join(missing_fields)}. Please review and edit before export.")
                result = {
                    'filename': uploaded_file.name,
                    'extracted_data': extracted_data,
                    'text_length': len(text),
                    'fields_found': len(extracted_data),
                    'missing_fields': missing_fields
                }
                return result, None
            
            # Store results
            result = {
                'filename': uploaded_file.name,
                'extracted_data': extracted_data,
                'text_length': len(text),
                'fields_found': len(extracted_data)
            }
            
            # Step 3: Extract images from PDF
            images = []
            if use_ocr:
                st.info("🖼️ Extracting images...")
                try:
                    images = parser.get_largest_images(min_width=150, min_height=150, max_count=5)
                    result['images_extracted'] = len(images)
                    result['images'] = images
                except Exception as img_error:
                    st.warning(f"Image extraction failed: {str(img_error)}. Export will proceed without images.")
                    result['images_extracted'] = 0
                    result['images'] = []
            
            # Step 4: Fill form if template provided
            filled_pdf_bytes = None
            if template_path:
                template_file = Path(template_path)
                if not template_file.exists():
                    script_dir = Path(__file__).parent
                    template_file = script_dir / template_path
                
                if not template_file.exists():
                    st.error(f"❌ Template not found: {template_path}")
                    st.info(f"📁 Looked in: {template_file.absolute()}")
                    st.error("❌ ACTION NEEDED: Add your STEP2.pdf template to the templates/ folder and retry export.")
                    result['filled_form'] = False
                    return result, None
                
                st.info("✍️ Filling form template with text and images...")
                try:
                    output_file = temp_path / f"{Path(uploaded_file.name).stem}_filled.pdf"
                    filler = FormFiller(str(template_file))
                    filler.fill_form(
                        extracted_data,
                        str(output_file),
                        verbose=False,
                        images=images
                    )
                    with open(output_file, 'rb') as f:
                        filled_pdf_bytes = f.read()
                    result['filled_form'] = True
                    st.success("✅ Form filled successfully!")
                except Exception as fill_error:
                    st.error(f"❌ Error filling form: {str(fill_error)}")
                    result['filled_form'] = False
                    return result, None
            else:
                result['filled_form'] = False
            
            return result, filled_pdf_bytes
            
    except Exception as e:
        st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
        st.info("You may retry the operation or check your input files and configuration.")
        return None, None

def main():
    # Final PDF generation section
    if st.session_state.extraction_results:
        st.markdown("---")
        st.header("📝 Finalize and Download Completed PDF")
        st.info("After reviewing and editing, generate a single, finalized PDF with all merged data and images, ready for downstream submission.")
        # Aggregate all edited data and images
        all_edited_data = {}
        all_images = []
        for filename, result in st.session_state.extraction_results.items():
            # Use latest edits if available
            pdf_key = f"{Path(filename).stem}_edited_filled.pdf"
            if pdf_key in st.session_state.filled_forms:
                # Optionally parse edited fields from filled PDF (if tracked)
                # For now, use original extracted data
                all_edited_data.update(result['extracted_data'])
            else:
                all_edited_data.update(result['extracted_data'])
            if result.get('images'):
                all_images.extend(result['images'])

        # Button to generate final PDF
        if st.button("Generate Final PDF", key="generate_final_pdf_btn"):
            from src.form_filler import FormFiller
            template_path = "templates/STEP2.pdf"
            st.write("### Debug: Merged Data for Final PDF")
            st.json(all_edited_data)
            st.write("### Debug: Merged Images for Final PDF")
            st.write(all_images)
            with tempfile.TemporaryDirectory() as temp_dir:
                output_file = Path(temp_dir) / "STEP2_final.pdf"
                filler = FormFiller(template_path)
                try:
                    filler.fill_form(
                        all_edited_data,
                        str(output_file),
                        verbose=True,
                        images=all_images
                    )
                    with open(output_file, "rb") as f:
                        final_pdf_bytes = f.read()
                    # Save to output folder
                    output_dir = Path("output")
                    output_dir.mkdir(exist_ok=True)
                    output_path = output_dir / "STEP2_final.pdf"
                    with open(output_path, "wb") as f:
                        f.write(final_pdf_bytes)
                    st.session_state.final_pdf_bytes = final_pdf_bytes
                    st.session_state.final_pdf_path = str(output_path)
                    st.success(f"Finalized PDF saved to: {output_path}")
                except Exception as e:
                    import traceback
                    st.error(f"Error generating final PDF: {str(e)}")
                    st.text(traceback.format_exc())

        # Always show download button and preview if PDF exists in session state
        if hasattr(st.session_state, "final_pdf_bytes") and st.session_state.final_pdf_bytes:
            st.download_button(
                label="⬇️ Download Final PDF",
                data=st.session_state.final_pdf_bytes,
                file_name="STEP2_final.pdf",
                mime="application/pdf",
                key="download_final_pdf_btn"
            )
            import base64
            b64_pdf = base64.b64encode(st.session_state.final_pdf_bytes).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{b64_pdf}" width="900" height="900" type="application/pdf"></iframe>'
            components.html(pdf_display, height=900)

            st.markdown("---")
            st.subheader("⬆️ Upload Edited PDF to Save")
            uploaded_edited_pdf = st.file_uploader("Re-upload your edited PDF here to save changes to the output folder.", type=["pdf"], key="edited_pdf_upload")
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            # List all edited PDFs in output folder
            edited_pdfs = [f for f in os.listdir(output_dir) if f.lower().endswith('.pdf') and f.startswith('edited_')]
            most_recent_pdf = None
            if edited_pdfs:
                # Sort by modified time, newest first
                edited_pdfs.sort(key=lambda f: os.path.getmtime(output_dir / f), reverse=True)
                most_recent_pdf = edited_pdfs[0]

            # Handle upload/save with feedback and filename validation
            if uploaded_edited_pdf:
                save_path = output_dir / f"edited_{uploaded_edited_pdf.name}"
                if save_path.exists():
                    st.error(f"A file named {save_path.name} already exists.")
                    overwrite = st.checkbox(f"Overwrite {save_path.name}?", key="overwrite_checkbox")
                    if overwrite:
                        with open(save_path, "wb") as f:
                            f.write(uploaded_edited_pdf.getbuffer())
                        st.success(f"Edited PDF overwritten: {save_path}")
                        most_recent_pdf = save_path.name
                    else:
                        new_name = st.text_input("Rename your file:", value=f"edited_{uploaded_edited_pdf.name}", key="rename_input")
                        if st.button("Save as new file", key="save_new_file_btn"):
                            new_path = output_dir / new_name
                            with open(new_path, "wb") as f:
                                f.write(uploaded_edited_pdf.getbuffer())
                            st.success(f"Edited PDF saved as: {new_path}")
                            most_recent_pdf = new_path.name
                else:
                    with open(save_path, "wb") as f:
                        f.write(uploaded_edited_pdf.getbuffer())
                    st.success(f"Edited PDF saved to: {save_path}")
                    most_recent_pdf = save_path.name

            st.markdown("---")
            st.subheader("📄 Edited PDFs in Output Folder")
            if edited_pdfs:
                for fname in edited_pdfs:
                    col1, col2 = st.columns([3,1])
                    with col1:
                        st.write(fname)
                        st.caption(f"Last modified: {os.path.getmtime(output_dir / fname):.0f}")
                    with col2:
                        with open(output_dir / fname, "rb") as f:
                            pdf_bytes = f.read()
                        st.download_button("⬇️ Download", data=pdf_bytes, file_name=fname, mime="application/pdf", key=f"download_{fname}")
                        if st.button("👁️ View Inline", key=f"view_{fname}"):
                            st.session_state["view_pdf_inline"] = fname

                # Auto-display most recent PDF inline
                if most_recent_pdf:
                    st.markdown("---")
                    st.subheader(f"👁️ Most Recent Edited PDF: {most_recent_pdf}")
                    with open(output_dir / most_recent_pdf, "rb") as f:
                        b64_uploaded = base64.b64encode(f.read()).decode('utf-8')
                        pdf_display = f'<iframe src="data:application/pdf;base64,{b64_uploaded}" width="900" height="900" type="application/pdf"></iframe>'
                        components.html(pdf_display, height=900)
            else:
                st.info("No edited PDFs found in output folder.")

            st.markdown("---")
            st.subheader("⬆️ Upload Edited PDF to Save")
            uploaded_edited_pdf = st.file_uploader("Re-upload your edited PDF here to save changes to the output folder.", type=["pdf"], key="edited_pdf_upload")
            if uploaded_edited_pdf:
                output_dir = Path("output")
                output_dir.mkdir(exist_ok=True)
                output_path = output_dir / f"edited_{uploaded_edited_pdf.name}"
                with open(output_path, "wb") as f:
                    f.write(uploaded_edited_pdf.getbuffer())
                st.success(f"Edited PDF saved to: {output_path}")
                # Optionally display the uploaded PDF inline
                b64_uploaded = base64.b64encode(uploaded_edited_pdf.getbuffer()).decode('utf-8')
                pdf_display = f'<iframe src="data:application/pdf;base64,{b64_uploaded}" width="900" height="900" type="application/pdf"></iframe>'
                components.html(pdf_display, height=900)
    """Main Streamlit application"""
    
    # Header - horizontal layout with divider
    st.markdown('''
    <div class="main-header">
        <h1 class="main-title">✨ ABSTRACTOR 💖</h1>
    </div>
    <p class="subtitle">Magical PDF Form Processing - Extract, OCR, Fill</p>
    ''', unsafe_allow_html=True)
    
    # Sidebar configuration
    st.sidebar.header("💫 Configuration")
    
    # OCR option
    use_ocr = st.sidebar.checkbox(
        "✨ Enable OCR Magic",
        value=True,
        help="Use Optical Character Recognition for scanned/handwritten PDFs"
    )
    
    # Form filling option
    enable_filling = st.sidebar.checkbox(
        "💝 Fill Forms Automatically",
        value=True,
        help="Automatically fill form template with extracted data"
    )
    
    # Use fixed template path in code
    template_path = "templates/STEP2.pdf"
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Statistics")
    st.sidebar.metric("Files Processed", len(st.session_state.processed_files))
    
    # Main content area - upload section with centered layout
    st.markdown('<h2 class="section-header">📁 Upload Source PDFs</h2>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666; margin-bottom: 1.5rem;">Upload one or more PDFs to extract information and fill your form</p>', unsafe_allow_html=True)
    
    # File uploader - centered
    uploaded_files = st.file_uploader(
        "Drop PDF files here or click to browse",
        type=['pdf'],
        accept_multiple_files=True,
        help="Upload one or more PDF files to extract data from",
        label_visibility="collapsed"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} file(s) selected")
        
        # Show file list
        with st.expander("📋 Selected Files"):
            for i, file in enumerate(uploaded_files, 1):
                file_size = len(file.getvalue()) / 1024 / 1024  # MB
                st.write(f"{i}. **{file.name}** ({file_size:.2f} MB)")
    
    # Quick Info panel - positioned below upload
    st.markdown('''
    <div class="info-card" style="margin-top: 2rem; max-width: 700px; margin-left: auto; margin-right: auto;">
        <h3 style="margin-top: 0; color: #7b68a6; font-size: 1.1rem;">� Quick Info</h3>
        <ul style="margin: 0.5rem 0; padding-left: 1.5rem; font-size: 0.85rem; line-height: 1.6;">
            <li>Upload multiple source PDFs to combine into one output</li>
            <li>Enable OCR for scanned documents in the sidebar</li>
            <li>Images are automatically extracted and can be inserted</li>
            <li>All data is combined into a single filled PDF</li>
        </ul>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="margin-top: 2rem; max-width: 700px; margin-left: auto; margin-right: auto;">
        <p style="font-size: 0.85rem; color: #7b68a6; font-weight: 600; margin-bottom: 0.5rem;">How to use:</p>
        <ol style="margin: 0.5rem 0; padding-left: 1.5rem; font-size: 0.85rem; line-height: 1.6; color: #666;">
            <li>Upload source PDF(s) above</li>
            <li>Configure options in the sidebar</li>
            <li>Click "Process PDFs" to extract and fill</li>
            <li>Download your filled form and data</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    # Process button - centered
    st.markdown('<div style="margin: 2rem 0 1rem 0;"><hr style="border: none; border-top: 1px solid rgba(0,0,0,0.1);"></div>', unsafe_allow_html=True)
    
    if uploaded_files:
        # Center the process button
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        
        with col_btn2:
            process_button = st.button(
                "✨ Process PDFs 💖",
                type="primary",
                use_container_width=True
            )
        
        if process_button:
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Clear previous results
            st.session_state.extraction_results = {}
            st.session_state.filled_forms = {}
            
            # Collect all extracted data and images from all PDFs
            all_extracted_data = {}
            all_images = []
            total_files = len(uploaded_files)
            
            # Step 1: Extract data from all source PDFs
            for i, uploaded_file in enumerate(uploaded_files):
                status_text.markdown(f"**Extracting from {i+1}/{total_files}: {uploaded_file.name}**")
                
                # Process the PDF (without filling)
                result, _ = process_pdf(uploaded_file, use_ocr, template_path=None)
                
                if result:
                    # Store extraction results
                    st.session_state.extraction_results[uploaded_file.name] = result
                    
                    # Merge extracted data
                    all_extracted_data.update(result['extracted_data'])
                    
                    # Collect images from this PDF
                    if result.get('images'):
                        all_images.extend(result['images'])
                    
                    # Update processed files list
                    if uploaded_file.name not in st.session_state.processed_files:
                        st.session_state.processed_files.append(uploaded_file.name)
                    
                    st.success(f"✅ Extracted {result['fields_found']} fields and {result.get('images_extracted', 0)} images from {uploaded_file.name}")
                else:
                    st.error(f"❌ Failed to process {uploaded_file.name}")
                
                # Update progress
                progress_bar.progress((i + 1) / (total_files + 1))
            
            # Step 2: Create single filled PDF from combined data
            if enable_filling and template_path and all_extracted_data:
                status_text.markdown("**Creating final STEP2 form with combined data...**")
                
                try:
                    with tempfile.TemporaryDirectory() as temp_dir:
                        temp_path = Path(temp_dir)
                        
                        # Check template exists
                        template_file = Path(template_path)
                        if not template_file.exists():
                            script_dir = Path(__file__).parent
                            template_file = script_dir / template_path
                        
                        if template_file.exists():
                            st.info("✍️ Filling STEP2 template with combined data...")
                            st.write(f"📊 Debug: Merged {len(all_extracted_data)} fields from {total_files} file(s)")
                            st.write(f"🖼️ Debug: {len(all_images)} images collected")
                            
                            output_file = temp_path / "STEP2_filled.pdf"
                            
                            filler = FormFiller(str(template_file))
                            filler.fill_form(
                                all_extracted_data,
                                str(output_file),
                                verbose=False,
                                images=all_images
                            )
                            
                            # Read filled PDF
                            with open(output_file, 'rb') as f:
                                filled_pdf_bytes = f.read()
                            
                            # Store single filled form
                            st.session_state.filled_forms["STEP2_filled.pdf"] = filled_pdf_bytes
                            st.success(f"✅ Single STEP2 form created successfully! ({len(filled_pdf_bytes)} bytes)")
                        else:
                            st.error(f"❌ Template not found: {template_path}")
                            st.error(f"📁 Searched in: {template_file.absolute()}")
                            st.error("❌ ACTION NEEDED: Add STEP2.pdf to templates/ folder")
                
                except Exception as fill_error:
                    import traceback
                    st.error(f"❌ Error creating filled form: {str(fill_error)}")
                    st.code(traceback.format_exc())
            elif enable_filling and not all_extracted_data:
                st.warning("⚠️ No data was extracted from the uploaded files. PDF form was not filled.")
            elif not enable_filling:
                st.info("ℹ️ Form filling is disabled. Enable 'Fill Forms Automatically' in sidebar to generate PDF.")
            
            progress_bar.progress(1.0)
            status_text.empty()
            progress_bar.empty()
            
            # Show completion message with summary
            st.markdown('<div class="success-box"><h3>✅ Processing Complete!</h3></div>', unsafe_allow_html=True)
            st.write(f"📊 **Summary:** Processed {total_files} file(s), extracted {len(all_extracted_data)} fields, collected {len(all_images)} images")
            
            # Debug: Show what was extracted
            with st.expander("🔍 View Extracted Data (Debug)"):
                st.json(all_extracted_data)
                st.write(f"Total fields: {len(all_extracted_data)}")
    
    # Results section
    if st.session_state.extraction_results:
        st.markdown("---")
        st.header("📊 Results")

        # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Extracted Data", "📥 Downloads", "📈 Summary", "🖊️ PDF.js Editor"])
    with tab4:
        st.subheader("🖊️ In-Browser PDF Editing (PDF.js)")
        st.info("Edit, annotate, and highlight your PDF directly in the browser. Changes are not saved to backend automatically.")
        # Embed PDF.js viewer/editor
        # Use the first filled PDF for demo (can be extended for selection)
        import base64
        pdf_bytes = None
        if st.session_state.filled_forms:
            # Use the first PDF in filled_forms
            pdf_bytes = list(st.session_state.filled_forms.values())[0]
        if pdf_bytes:
            b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
            # PDF.js viewer HTML (hosted version or local)
            pdfjs_url = "https://mozilla.github.io/pdf.js/web/viewer.html"
            # Pass PDF as base64 data URI
            pdfjs_iframe = f'''<iframe src="{pdfjs_url}?file=data:application/pdf;base64,{b64_pdf}" width="900" height="900" allowfullscreen></iframe>'''
            components.html(pdfjs_iframe, height=900)
        else:
            st.warning("No filled PDF available for editing.")

        with tab1:
            # User selects which file to view/edit
            file_options = list(st.session_state.extraction_results.keys())
            selected_file = st.selectbox("Select a file to view/edit:", file_options, index=len(file_options)-1 if file_options else 0)
            if selected_file:
                result = st.session_state.extraction_results[selected_file]
                with st.expander(f"📄 {selected_file}", expanded=True):
                    col_a, col_b, col_c = st.columns([1, 1, 1])
                    with col_a:
                        st.metric("Text Length", f"{result['text_length']:,} chars")
                    with col_b:
                        st.metric("Fields Found", result['fields_found'])
                    with col_c:
                        st.metric("Images Extracted", result.get('images_extracted', 0))

                    # Editable form overlay for extracted fields
                    st.subheader("Edit Extracted Fields:")
                    with st.form(f"edit_form_{selected_file}"):
                        edited_fields = {}
                        for key, value in result['extracted_data'].items():
                            if isinstance(value, dict):
                                st.markdown(f"**{key}:**")
                                edited_fields[key] = {}
                                for subkey, subval in value.items():
                                    edited_fields[key][subkey] = st.text_input(f"{key} - {subkey}", value=subval if subval is not None else "")
                            else:
                                edited_fields[key] = st.text_input(key, value=value if value is not None else "")
                        submit_edits = st.form_submit_button("Apply Edits & Refill PDF")

                    # If edits submitted, refill PDF and update preview
                    if submit_edits:
                        st.info("Refilling PDF with updated fields...")
                        from src.form_filler import FormFiller
                        template_path = "templates/STEP2.pdf"
                        with tempfile.TemporaryDirectory() as temp_dir:
                            output_file = Path(temp_dir) / f"{Path(selected_file).stem}_edited_filled.pdf"
                            filler = FormFiller(template_path)
                            images = result.get('images', None)
                            try:
                                filler.fill_form(edited_fields, str(output_file), verbose=False, images=images)
                                with open(output_file, 'rb') as f:
                                    edited_pdf_bytes = f.read()
                                st.session_state.filled_forms[f"{Path(selected_file).stem}_edited_filled.pdf"] = edited_pdf_bytes
                                st.success("PDF updated and refilled with your edits!")
                            except Exception as e:
                                st.error(f"Error updating PDF: {str(e)}")

                    # Inline PDF viewer for filled PDF (if available)
                    st.subheader("Review Filled PDF:")
                    pdf_key = f"{Path(selected_file).stem}_edited_filled.pdf"
                    pdf_bytes = st.session_state.filled_forms.get(pdf_key)
                    if pdf_bytes:
                        import base64
                        b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
                        pdf_display = f'<iframe src="data:application/pdf;base64,{b64_pdf}" width="700" height="900" type="application/pdf"></iframe>'
                        components.html(pdf_display, height=900)
                        output_dir = Path("output")
                        output_dir.mkdir(exist_ok=True)
                        output_path = output_dir / pdf_key
                        with open(output_path, "wb") as f:
                            f.write(pdf_bytes)
                        st.success(f"Updated PDF saved to: {output_path}")
                    else:
                        st.info("No edited PDF available yet. Make edits and refill to preview.")

                    # Show extracted images
                    if result.get('images') and len(result['images']) > 0:
                        st.subheader("🖼️ Extracted Images:")
                        img_cols = st.columns(min(len(result['images']), 3))
                        for idx, img_data in enumerate(result['images']):
                            col_idx = idx % 3
                            with img_cols[col_idx]:
                                try:
                                    from PIL import Image
                                    import io
                                    image = Image.open(io.BytesIO(img_data['data']))
                                    st.image(image, 
                                            caption=f"Image {idx+1}: {img_data['width']}x{img_data['height']}px",
                                            use_container_width=True)
                                except Exception as e:
                                    st.error(f"Could not display image {idx+1}: {str(e)}")
        
        with tab2:
            st.subheader("📥 Download Results")
            
            # Download filled form (single PDF)
            if st.session_state.filled_forms:
                st.markdown("### 📝 Filled STEP2 Form")
                st.info("✨ This single PDF contains combined data from all uploaded source files")
                
                for filename, pdf_bytes in st.session_state.filled_forms.items():
                    col_form1, col_form2 = st.columns([3, 1])
                    
                    with col_form1:
                        st.write(f"**{filename}**")
                        st.caption(f"Created from {len(st.session_state.extraction_results)} source file(s)")
                    
                    with col_form2:
                        st.download_button(
                            label="� Download PDF",
                            data=pdf_bytes,
                            file_name=filename,
                            mime="application/pdf",
                            key=f"pdf_{filename}"
                        )
            else:
                st.info("No filled forms available. Enable 'Fill Forms Automatically' and process PDFs.")
            
            # Optional: Download extracted data as JSON
            if st.session_state.extraction_results:
                st.markdown("---")
                st.markdown("### � Source Data (Optional)")
                
                for filename, result in st.session_state.extraction_results.items():
                    col_download1, col_download2 = st.columns([3, 1])
                    
                    with col_download1:
                        st.write(f"**{filename}** - Extracted fields")
                    
                    with col_download2:
                        # Download JSON
                        json_data = json.dumps(result['extracted_data'], indent=2)
                        st.download_button(
                            label="📄 JSON",
                            data=json_data,
                            file_name=f"{Path(filename).stem}_data.json",
                            mime="application/json",
                            key=f"json_{filename}"
                        )
        
        with tab3:
            st.subheader("📈 Processing Summary")
            
            # Overall statistics
            total_processed = len(st.session_state.extraction_results)
            total_fields = sum(r['fields_found'] for r in st.session_state.extraction_results.values())
            total_filled = len(st.session_state.filled_forms)
            total_images = sum(r.get('images_extracted', 0) for r in st.session_state.extraction_results.values())
            
            col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
            
            with col_stat1:
                st.metric("PDFs Processed", total_processed)
            with col_stat2:
                st.metric("Total Fields Extracted", total_fields)
            with col_stat3:
                st.metric("Images Extracted", total_images)
            with col_stat4:
                st.metric("Forms Filled", total_filled)
            
            # Show all extracted images that went into the final form
            if total_images > 0:
                st.markdown("---")
                st.markdown("### 🖼️ All Images Used in Final Form")
                
                all_imgs = []
                for filename, result in st.session_state.extraction_results.items():
                    if result.get('images'):
                        for img in result['images']:
                            all_imgs.append({
                                'source': filename,
                                'data': img
                            })
                
                if all_imgs:
                    img_cols = st.columns(min(len(all_imgs), 4))
                    for idx, img_info in enumerate(all_imgs):
                        col_idx = idx % 4
                        with img_cols[col_idx]:
                            try:
                                from PIL import Image
                                import io
                                
                                image = Image.open(io.BytesIO(img_info['data']['data']))
                                st.image(image, 
                                        caption=f"From: {Path(img_info['source']).stem}",
                                        use_container_width=True)
                                st.caption(f"{img_info['data']['width']}x{img_info['data']['height']}px")
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
            
            # Per-file breakdown
            st.markdown("---")
            st.markdown("### 📋 File Details")
            for filename, result in st.session_state.extraction_results.items():
                cols = st.columns([3, 1, 1, 1, 1])
                cols[0].write(filename)
                cols[1].write(f"{result['text_length']:,} chars")
                cols[2].write(f"{result['fields_found']} fields")
                cols[3].write(f"{result.get('images_extracted', 0)} images")
                cols[3].write("✅ Filled" if result.get('filled_form') else "—")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2em;'>
        <p><strong>ABSTRACTOR</strong> - Automated PDF Form Processing</p>
        <p>Built with Python • Streamlit • PyPDF2 • Tesseract OCR</p>
        <p>© 2025 - Access from anywhere, no installation required</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
