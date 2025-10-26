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

# Custom CSS - Girly Theme
st.markdown("""
<style>
    /* Main app background - target all containers */
    .main {
        background: linear-gradient(135deg, #c9b3e6 0%, #b39ddb 50%, #9575cd 100%) !important;
    }
    
    /* Remove white background from all containers */
    .main .block-container {
        background: transparent !important;
        padding-top: 2rem;
    }
    
    /* Target the main content area */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #c9b3e6 0%, #b39ddb 50%, #9575cd 100%) !important;
    }
    
    /* Ensure all content blocks are transparent */
    .element-container {
        background: transparent !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #d4b3ff 0%, #e6d9ff 100%);
    }
    
    /* Title styling */
    .main-title {
        text-align: center;
        background: linear-gradient(135deg, #ff69b4, #ff1493, #db7093);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3.5em;
        font-weight: bold;
        margin-bottom: 0.3em;
        text-shadow: 2px 2px 4px rgba(255, 182, 193, 0.3);
        font-family: 'Arial Rounded MT Bold', sans-serif;
    }
    
    .subtitle {
        text-align: center;
        color: #d946a6;
        font-size: 1.3em;
        margin-bottom: 2em;
        font-style: italic;
        font-weight: 500;
    }
    
    /* Success boxes */
    .success-box {
        padding: 1.2em;
        background: linear-gradient(135deg, #ffd4f0 0%, #ffe8f5 100%);
        border: 2px solid #ffb3d9;
        border-radius: 15px;
        color: #c71585;
        box-shadow: 0 4px 6px rgba(255, 105, 180, 0.2);
    }
    
    /* Error boxes */
    .error-box {
        padding: 1.2em;
        background: linear-gradient(135deg, #ffe0e6 0%, #fff0f3 100%);
        border: 2px solid #ffb3c1;
        border-radius: 15px;
        color: #c91563;
        box-shadow: 0 4px 6px rgba(255, 105, 135, 0.2);
    }
    
    /* Info boxes */
    .info-box {
        padding: 1.2em;
        background: linear-gradient(135deg, #e8d4ff 0%, #f5e8ff 100%);
        border: 2px solid #d4b3ff;
        border-radius: 15px;
        color: #8b5bb5;
        box-shadow: 0 4px 6px rgba(186, 135, 255, 0.2);
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #ff69b4, #ff1493);
        color: white;
        border-radius: 25px;
        border: none;
        padding: 0.75em 2em;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(255, 105, 180, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #ff1493, #ff69b4);
        box-shadow: 0 6px 8px rgba(255, 105, 180, 0.4);
        transform: translateY(-2px);
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #ff1493;
        font-weight: bold;
    }
    
    /* Expander headers */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #ffe8f5 0%, #fff0f8 100%);
        border-radius: 10px;
        color: #d946a6;
        font-weight: bold;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background: linear-gradient(135deg, #fff5f9 0%, #fffafc 100%);
        border: 2px dashed #ffb3d9;
        border-radius: 15px;
        padding: 1em;
    }
    
    /* Download buttons */
    .stDownloadButton>button {
        background: linear-gradient(135deg, #da70d6, #ba55d3);
        color: white;
        border-radius: 20px;
        font-weight: bold;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(135deg, #ffe8f5 0%, #fff0f8 100%);
        border-radius: 10px 10px 0 0;
        color: #d946a6;
        font-weight: bold;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #ff69b4, #ff1493);
        color: white;
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
    
    # Header
    st.markdown('<h1 class="main-title">✨� ABSTRACTOR 💖✨</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">🌸 Magical PDF Form Processing - Extract, OCR, Fill 🌸</p>', unsafe_allow_html=True)
    
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
    st.sidebar.markdown("### � Statistics")
    st.sidebar.metric("Files Processed", len(st.session_state.processed_files))
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📁✨ Upload Source PDFs")
        st.header("📁 Upload Source PDFs")
        
        # File uploader
        uploaded_files = st.file_uploader(
            "Drop PDF files here or click to browse",
            type=['pdf'],
            accept_multiple_files=True,
            help="Upload one or more PDF files to extract data from"
        )
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} file(s) selected")
            
            # Show file list
            with st.expander("📋 Selected Files"):
                for i, file in enumerate(uploaded_files, 1):
                    file_size = len(file.getvalue()) / 1024 / 1024  # MB
                    st.write(f"{i}. **{file.name}** ({file_size:.2f} MB)")
    
    with col2:
        st.header("💝 Quick Info")
        st.markdown("""
        **How to use:**
        1. 📤 Upload source PDF(s)
        2. ⚙️ Configure options (sidebar)
        3. ✨ Click "Process PDFs"
        4. 💖 Download results
        
        **Features:**
        - 💕 Text extraction
        - 🌸 OCR for scanned docs
        - 🎀 Pattern matching
        - ✨ Auto form filling
        - 🦋 Batch processing
        """)
    
    # Process button
    st.markdown("---")
    
    if uploaded_files:
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        
        with col_btn2:
            process_button = st.button(
                "✨� Process PDFs 💖✨",
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
                    
                    # Show extracted fields
                    if result['extracted_data']:
                        st.subheader("Extracted Fields:")
                        st.json(result['extracted_data'])
                    else:
                        st.warning("No fields extracted - check patterns in config.py")
                    
                    # Show extracted images
                    if result.get('images') and len(result['images']) > 0:
                        st.subheader("🖼️ Extracted Images:")
                        
                        # Display images in columns
                        img_cols = st.columns(min(len(result['images']), 3))
                        for idx, img_data in enumerate(result['images']):
                            col_idx = idx % 3
                            with img_cols[col_idx]:
                                try:
                                    # Display image from bytes
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
