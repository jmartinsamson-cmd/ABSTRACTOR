"""
ABSTRACTOR - Web Application
Streamlit-based web interface for PDF form processing
Access from any browser - no installation required!
"""

import streamlit as st
import json
from pathlib import Path
import tempfile
import sys
import os

# Add current directory to path for module imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import core modules
from src.parser import PDFParser
from src.field_extractor import FieldExtractor
from src.form_filler import FormFiller

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
    try:
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Save uploaded file
            input_file = temp_path / uploaded_file.name
            with open(input_file, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            
            # Step 1: Extract text
            st.info(f"📖 Extracting text from {uploaded_file.name}...")
            parser = PDFParser(str(input_file))
            
            # Try standard extraction first
            text = parser.extract_text()
            
            # Use OCR if enabled and text is minimal
            if use_ocr and len(text.strip()) < 100:
                st.info("🔍 Low text detected - using OCR...")
                # OCR is built into PDFParser
                parser_with_ocr = PDFParser(str(input_file), use_ocr=True)
                text = parser_with_ocr.extract_text()
            
            # Step 2: Extract fields
            st.info("🔎 Extracting fields...")
            extractor = FieldExtractor(text)
            extracted_data = extractor.extract_all_fields()
            
            # Store results
            result = {
                'filename': uploaded_file.name,
                'extracted_data': extracted_data,
                'text_length': len(text),
                'fields_found': len(extracted_data)
            }
            
            # Step 3: Extract images from PDF
            images = []
            if use_ocr:  # Extract images if processing enabled
                st.info("🖼️ Extracting images...")
                try:
                    images = parser.get_largest_images(min_width=150, min_height=150, max_count=5)
                    result['images_extracted'] = len(images)
                    result['images'] = images  # Store image data for display
                except Exception as img_error:
                    st.warning(f"Could not extract images: {str(img_error)}")
                    result['images_extracted'] = 0
                    result['images'] = []
            
            # Step 4: Fill form if template provided
            filled_pdf_bytes = None
            if template_path:
                # Check if template exists
                template_file = Path(template_path)
                if not template_file.exists():
                    # Try relative to script directory
                    script_dir = Path(__file__).parent
                    template_file = script_dir / template_path
                
                if template_file.exists():
                    st.info("✍️ Filling form template with text and images...")
                    
                    try:
                        # Create output file in temp directory
                        output_file = temp_path / f"{Path(uploaded_file.name).stem}_filled.pdf"
                        
                        filler = FormFiller(str(template_file))
                        filler.fill_form(
                            extracted_data, 
                            str(output_file),
                            verbose=False,
                            images=images if images else None
                        )
                        
                        # Read filled PDF into bytes
                        with open(output_file, 'rb') as f:
                            filled_pdf_bytes = f.read()
                        
                        result['filled_form'] = True
                        st.success(f"✅ Form filled successfully!")
                    except Exception as fill_error:
                        st.error(f"❌ Error filling form: {str(fill_error)}")
                        result['filled_form'] = False
                else:
                    st.warning(f"⚠️ Template not found: {template_path}")
                    st.info(f"📁 Looked in: {template_file.absolute()}")
                    st.error("❌ **ACTION NEEDED:** Add your STEP2.pdf template to the templates/ folder")
                    result['filled_form'] = False
            else:
                result['filled_form'] = False
            
            return result, filled_pdf_bytes
            
    except Exception as e:
        st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
        return None, None

def main():
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
    
    # Template path
    template_path = st.sidebar.text_input(
        "📋 Form Template Path",
        value="templates/STEP2.pdf",
        help="Path to the PDF form template (Legacy STEP2)"
    )
    
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
                
                # Update progress
                progress_bar.progress((i + 1) / (total_files + 1))
            
            # Step 2: Create single filled PDF from combined data
            if enable_filling and template_path and all_extracted_data:
                status_text.markdown(f"**Creating final STEP2 form with combined data...**")
                
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
                            
                            output_file = temp_path / "STEP2_filled.pdf"
                            
                            filler = FormFiller(str(template_file))
                            filler.fill_form(
                                all_extracted_data,
                                str(output_file),
                                verbose=False,
                                images=all_images if all_images else None
                            )
                            
                            # Read filled PDF
                            with open(output_file, 'rb') as f:
                                filled_pdf_bytes = f.read()
                            
                            # Store single filled form
                            st.session_state.filled_forms["STEP2_filled.pdf"] = filled_pdf_bytes
                            st.success("✅ Single STEP2 form created successfully!")
                        else:
                            st.error(f"❌ Template not found: {template_path}")
                
                except Exception as fill_error:
                    st.error(f"❌ Error creating filled form: {str(fill_error)}")
            
            progress_bar.progress(1.0)
            status_text.empty()
            progress_bar.empty()
            
            # Show completion message
            st.markdown('<div class="success-box"><h3>✅ Processing Complete!</h3></div>', unsafe_allow_html=True)
    
    # Results section
    if st.session_state.extraction_results:
        st.markdown("---")
        st.header("📊 Results")

        # Tabs for different views
        tab1, tab2, tab3 = st.tabs(["📋 Extracted Data", "📥 Downloads", "📈 Summary"])

        with tab1:
            # Show extracted data for each file
            for filename, result in st.session_state.extraction_results.items():
                with st.expander(f"📄 {filename}", expanded=True):
                    col_a, col_b, col_c = st.columns([1, 1, 1])
                    with col_a:
                        st.metric("Text Length", f"{result['text_length']:,} chars")
                    with col_b:
                        st.metric("Fields Found", result['fields_found'])
                    with col_c:
                        st.metric("Images Extracted", result.get('images_extracted', 0))

                    # Editable form overlay for extracted fields
                    st.subheader("Edit Extracted Fields:")
                    with st.form(f"edit_form_{filename}"):
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
                        # Refill PDF using FormFiller
                        import tempfile
                        from src.form_filler import FormFiller
                        template_path = st.sidebar.text_input(
                            "📋 Form Template Path",
                            value="templates/STEP2.pdf",
                            help="Path to the PDF form template (Legacy STEP2)"
                        )
                        with tempfile.TemporaryDirectory() as temp_dir:
                            output_file = Path(temp_dir) / f"{Path(filename).stem}_edited_filled.pdf"
                            filler = FormFiller(template_path)
                            images = result.get('images', None)
                            try:
                                filler.fill_form(edited_fields, str(output_file), verbose=False, images=images)
                                with open(output_file, 'rb') as f:
                                    edited_pdf_bytes = f.read()
                                st.session_state.filled_forms[f"{Path(filename).stem}_edited_filled.pdf"] = edited_pdf_bytes
                                st.success("PDF updated and refilled with your edits!")
                            except Exception as e:
                                st.error(f"Error updating PDF: {str(e)}")

                    # Inline PDF viewer for filled PDF (if available)
                    st.subheader("Review Filled PDF:")
                    pdf_key = f"{Path(filename).stem}_edited_filled.pdf"
                    pdf_bytes = st.session_state.filled_forms.get(pdf_key)
                    if pdf_bytes:
                        # Embed PDF in HTML using base64
                        import base64
                        b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
                        pdf_display = f'<iframe src="data:application/pdf;base64,{b64_pdf}" width="700" height="900" type="application/pdf"></iframe>'
                        st.components.v1.html(pdf_display, height=900)
                        # Save to output folder
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
