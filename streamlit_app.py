"""
ABSTRACTOR - Web Application
Streamlit-based web interface for PDF form processing
Access from any browser - no installation required!
"""

import streamlit as st
import json
from pathlib import Path
import tempfile

# Import core modules
from src.pdf_parser import PDFParser
from src.field_extractor import FieldExtractor
from src.form_filler import FormFiller
from src.ocr_handler import OCRHandler

# Page configuration
st.set_page_config(
    page_title="Abstractor - PDF Form Processor",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-title {
        text-align: center;
        color: #1f77b4;
        font-size: 3em;
        font-weight: bold;
        margin-bottom: 0.5em;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2em;
        margin-bottom: 2em;
    }
    .success-box {
        padding: 1em;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        color: #155724;
    }
    .error-box {
        padding: 1em;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        color: #721c24;
    }
    .info-box {
        padding: 1em;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        color: #0c5460;
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
                ocr_handler = OCRHandler(str(input_file))
                text = ocr_handler.extract_text_with_ocr()
            
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
            
            # Step 3: Fill form if template provided
            filled_pdf_bytes = None
            if template_path and Path(template_path).exists():
                st.info("✍️ Filling form template...")
                
                # Create output file in temp directory
                output_file = temp_path / f"{Path(uploaded_file.name).stem}_filled.pdf"
                
                filler = FormFiller(template_path)
                filler.fill_form(extracted_data, str(output_file))
                
                # Read filled PDF into bytes
                with open(output_file, 'rb') as f:
                    filled_pdf_bytes = f.read()
                
                result['filled_form'] = True
            else:
                result['filled_form'] = False
            
            return result, filled_pdf_bytes
            
    except Exception as e:
        st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
        return None, None

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-title">📄 ABSTRACTOR</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Automated PDF Form Processing - Extract, OCR, Fill</p>', unsafe_allow_html=True)
    
    # Sidebar configuration
    st.sidebar.header("⚙️ Configuration")
    
    # OCR option
    use_ocr = st.sidebar.checkbox(
        "Enable OCR",
        value=True,
        help="Use Optical Character Recognition for scanned/handwritten PDFs"
    )
    
    # Form filling option
    enable_filling = st.sidebar.checkbox(
        "Fill Forms Automatically",
        value=True,
        help="Automatically fill form template with extracted data"
    )
    
    # Template path
    template_path = st.sidebar.text_input(
        "Form Template Path",
        value="templates/STEP2.pdf",
        help="Path to the PDF form template"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Statistics")
    st.sidebar.metric("Files Processed", len(st.session_state.processed_files))
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
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
        st.header("🎯 Quick Info")
        st.markdown("""
        **How to use:**
        1. Upload source PDF(s)
        2. Configure options (sidebar)
        3. Click "Process PDFs"
        4. Download results
        
        **Features:**
        - ✅ Text extraction
        - ✅ OCR for scanned docs
        - ✅ Pattern matching
        - ✅ Auto form filling
        - ✅ Batch processing
        """)
    
    # Process button
    st.markdown("---")
    
    if uploaded_files:
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        
        with col_btn2:
            process_button = st.button(
                "🚀 Process PDFs",
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
            
            # Process each file
            total_files = len(uploaded_files)
            
            for i, uploaded_file in enumerate(uploaded_files):
                status_text.markdown(f"**Processing {i+1}/{total_files}: {uploaded_file.name}**")
                
                # Determine template path for filling
                template = template_path if enable_filling else None
                
                # Process the PDF
                result, filled_pdf = process_pdf(uploaded_file, use_ocr, template)
                
                if result:
                    # Store results
                    st.session_state.extraction_results[uploaded_file.name] = result
                    if filled_pdf:
                        st.session_state.filled_forms[uploaded_file.name] = filled_pdf
                    
                    # Update processed files list
                    if uploaded_file.name not in st.session_state.processed_files:
                        st.session_state.processed_files.append(uploaded_file.name)
                
                # Update progress
                progress_bar.progress((i + 1) / total_files)
            
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
                    col_a, col_b = st.columns([1, 1])
                    
                    with col_a:
                        st.metric("Text Length", f"{result['text_length']:,} chars")
                    with col_b:
                        st.metric("Fields Found", result['fields_found'])
                    
                    # Show extracted fields
                    if result['extracted_data']:
                        st.subheader("Extracted Fields:")
                        st.json(result['extracted_data'])
                    else:
                        st.warning("No fields extracted - check patterns in config.py")
        
        with tab2:
            st.subheader("📥 Download Results")
            
            # Download extracted data as JSON
            for filename, result in st.session_state.extraction_results.items():
                col_download1, col_download2 = st.columns([2, 1])
                
                with col_download1:
                    st.write(f"**{filename}**")
                
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
            
            # Download filled forms
            if st.session_state.filled_forms:
                st.markdown("---")
                st.subheader("📝 Filled Forms")
                
                for filename, pdf_bytes in st.session_state.filled_forms.items():
                    col_form1, col_form2 = st.columns([2, 1])
                    
                    with col_form1:
                        st.write(f"**{Path(filename).stem}_filled.pdf**")
                    
                    with col_form2:
                        st.download_button(
                            label="📥 Download PDF",
                            data=pdf_bytes,
                            file_name=f"{Path(filename).stem}_filled.pdf",
                            mime="application/pdf",
                            key=f"pdf_{filename}"
                        )
        
        with tab3:
            st.subheader("📈 Processing Summary")
            
            # Overall statistics
            total_processed = len(st.session_state.extraction_results)
            total_fields = sum(r['fields_found'] for r in st.session_state.extraction_results.values())
            total_filled = len(st.session_state.filled_forms)
            
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            
            with col_stat1:
                st.metric("PDFs Processed", total_processed)
            with col_stat2:
                st.metric("Total Fields Extracted", total_fields)
            with col_stat3:
                st.metric("Forms Filled", total_filled)
            
            # Per-file breakdown
            st.markdown("### File Details")
            for filename, result in st.session_state.extraction_results.items():
                cols = st.columns([3, 1, 1, 1])
                cols[0].write(filename)
                cols[1].write(f"{result['text_length']:,} chars")
                cols[2].write(f"{result['fields_found']} fields")
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
