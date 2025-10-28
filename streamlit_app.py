import streamlit as st
from pathlib import Path
import sys
import tempfile
import json
from datetime import datetime
import io
import PyPDF2

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.cover_page_generator import BradleyAbstractCoverPage
from src.parser import PDFParser
from src.field_extractor import FieldExtractor
from src.pdf_assembler import PDFAssembler

st.set_page_config(page_title="Abstractor - Property Abstract Generator", layout="wide", page_icon="🏛️")

# Initialize session state
if 'extracted_data' not in st.session_state:
    st.session_state.extracted_data = {}
if 'pdf_processed' not in st.session_state:
    st.session_state.pdf_processed = False
if 'uploaded_pdfs' not in st.session_state:
    st.session_state.uploaded_pdfs = []

st.title("🏛️ Bradley Abstract - Property Abstract Generator")
st.markdown("**Upload client PDFs → Auto-extract data → Edit inline → Generate complete abstract**")

# Sidebar
with st.sidebar:
    st.markdown("### 📤 Upload Client Documents")
    uploaded_files = st.file_uploader(
        "Choose PDF(s) for this client",
        type=['pdf'],
        help="Upload all property documents for this client (e.g., deed + title search)",
        accept_multiple_files=True
    )
    
    st.markdown("---")
    
    # OCR is always enabled for best text extraction
    use_ocr = True
    st.info("📄 **Smart Text Extraction:** Uses pdfplumber + OCR fallback for best results")
    
    if uploaded_files and len(uploaded_files) > 0:
        extract_button = st.button("🔍 Extract Data from PDFs", type="primary", use_container_width=True, key="extract_btn")
        
        if extract_button:
            with st.spinner("Extracting data from all PDFs..."):
                try:
                    # Save uploaded files
                    st.session_state.uploaded_pdfs = []
                    all_text = ""
                    
                    for uploaded_file in uploaded_files:
                        # Save temporarily
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                            file_bytes = uploaded_file.read()
                            tmp_file.write(file_bytes)
                            tmp_path = tmp_file.name
                        
                        # Store file info
                        st.session_state.uploaded_pdfs.append({
                            'name': uploaded_file.name,
                            'bytes': file_bytes,
                            'temp_path': tmp_path
                        })
                        
                        # Parse PDF
                        parser = PDFParser(tmp_path, use_ocr=use_ocr)
                        text = parser.extract_text()
                        all_text += f"\n\n=== {uploaded_file.name} ===\n{text}"
                    
                    # Extract fields from combined text
                    extractor = FieldExtractor(all_text)
                    fields = extractor.extract_all_fields()
                    
                    # Store in session state
                    st.session_state.extracted_data = {
                        'client_name': fields.get('client_name', ''),
                        'file_number': fields.get('file_number', ''),
                        'property_description': fields.get('property_description', ''),
                        'period_of_search': fields.get('period_of_search', ''),
                        'present_owners': fields.get('present_owners', ''),
                        'names_searched': 'All names searched 20 years for Federal judgments & liens',
                        'conveyance_documents': fields.get('conveyance_documents', ''),
                        'encumbrances': fields.get('encumbrances', ''),
                        'assessment_number': fields.get('assessment_number', '0610429400'),
                        'tax_status': 'Taxes Paid Annually'
                    }
                    st.session_state.pdf_processed = True
                    
                    # Automatically generate the PDF after extraction
                    st.success("✅ Data extracted successfully! Generating PDF...")
                    
                    # Generate cover page
                    generator = BradleyAbstractCoverPage()
                    
                    # Create temp file for cover page
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_cover:
                        tmp_cover_path = tmp_cover.name
                    
                    success = generator.fill_cover_page(st.session_state.extracted_data, tmp_cover_path)
                    
                    if success:
                        # Read cover page bytes
                        with open(tmp_cover_path, 'rb') as f:
                            cover_page_bytes = f.read()
                        
                        # Assemble complete PDF: cover page + all source documents
                        assembler = PDFAssembler()
                        
                        # Get source document paths/bytes
                        source_docs = [pdf_info['bytes'] for pdf_info in st.session_state.uploaded_pdfs]
                        
                        # Assemble: cover page as "billing" (page 1), no bradley form (already in cover), all source docs
                        complete_pdf_bytes = assembler.assemble_abstract(
                            billing_pdf_bytes=cover_page_bytes,
                            bradley_form_bytes=None,  # Cover page already contains the form
                            scanned_documents=source_docs,
                            output_path=None
                        )
                        
                        # Save to output folder
                        client_name = st.session_state.extracted_data.get('client_name', 'client')
                        file_number = st.session_state.extracted_data.get('file_number', 'unknown')
                        output_path = Path("output") / f"complete_abstract_{file_number.replace('/', '_')}.pdf"
                        output_path.parent.mkdir(exist_ok=True)
                        
                        with open(output_path, 'wb') as f:
                            f.write(complete_pdf_bytes)
                        
                        # Store the PDF for download
                        st.session_state.generated_pdf = complete_pdf_bytes
                        st.session_state.output_path = str(output_path)
                        
                        # Show page count
                        pdf_reader = PyPDF2.PdfReader(io.BytesIO(complete_pdf_bytes))
                        st.session_state.page_count = len(pdf_reader.pages)
                        
                        st.success(f"✅ Complete property abstract generated! ({st.session_state.page_count} pages)")
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error extracting data: {str(e)}")
                    st.exception(e)
    
    st.markdown("---")
    st.markdown("### 💡 How it works")
    st.markdown("""
    1. Upload client property PDF(s)
    2. Click **Extract Data from PDFs**
    3. PDF automatically generated!
    4. Download or edit if needed
    """)

# Main content area
if st.session_state.pdf_processed:
    # Show generated PDF download
    if 'generated_pdf' in st.session_state:
        st.success("🎉 Your Property Abstract is Ready!")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.download_button(
                label="📥 Download Complete Property Abstract PDF",
                data=st.session_state.generated_pdf,
                file_name=f"bradley_abstract_{st.session_state.extracted_data.get('file_number', 'document').replace('/', '_')}.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )
        with col2:
            st.info(f"📄 **{st.session_state.page_count}** pages total")
        
        st.info(f"💾 Saved to: `{st.session_state.output_path}`")
        
        st.markdown("---")
    
    # Expandable section for editing and regenerating
    with st.expander("✏️ Edit Extracted Data & Regenerate", expanded=False):
        st.info("Need to make changes? Edit the fields below and click 'Regenerate PDF'")
        
        # Create editable form
        with st.form("edit_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                client_name = st.text_input(
                    "Client Name (FOR:) *", 
                    value=st.session_state.extracted_data.get('client_name', ''),
                    placeholder="Enter or verify client name"
                )
                file_number = st.text_input(
                    "File Number *", 
                    value=st.session_state.extracted_data.get('file_number', ''),
                    placeholder="e.g., 2024-001"
                )
                property_description = st.text_area(
                    "Property Description *",
                    value=st.session_state.extracted_data.get('property_description', ''),
                    placeholder="Enter complete property description",
                    height=120
                )
            
            with col2:
                period_of_search = st.text_input(
                    "Period of Search *",
                    value=st.session_state.extracted_data.get('period_of_search', ''),
                    placeholder="e.g., 20 years, 1/1/2004 - present"
                )
                present_owners = st.text_input(
                    "Present Owner(s) *",
                    value=st.session_state.extracted_data.get('present_owners', ''),
                    placeholder="Enter current property owner(s)"
                )
                
                names_searched = st.text_area(
                    "Names Searched",
                    value=st.session_state.extracted_data.get('names_searched', 'All names searched 20 years for Federal judgments & liens'),
                    height=80
                )
            
            st.markdown("---")
            st.markdown("#### 📑 Additional Information")
            
            col3, col4 = st.columns(2)
            
            with col3:
                conveyance_docs = st.text_area(
                    "Conveyance Documents",
                    value=st.session_state.extracted_data.get('conveyance_documents', ''),
                    placeholder="List relevant conveyance documents",
                    height=100
                )
            
            with col4:
                encumbrances = st.text_area(
                    "Encumbrances",
                    value=st.session_state.extracted_data.get('encumbrances', ''),
                    placeholder="List any encumbrances",
                    height=100
                )
            
            st.markdown("#### 💰 Tax Information")
            col5, col6 = st.columns(2)
            with col5:
                assessment_number = st.text_input(
                    "Assessment Number", 
                    value=st.session_state.extracted_data.get('assessment_number', '0610429400')
                )
            with col6:
                tax_status = st.text_input(
                    "Tax Payment Status", 
                    value=st.session_state.extracted_data.get('tax_status', 'Taxes Paid Annually')
                )
            
            st.markdown("---")
            
            # Submit button
            col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 2])
            with col_btn2:
                submit = st.form_submit_button("🔄 Regenerate PDF with Edits", type="primary", use_container_width=True)
        
        if submit:
            if not client_name or not file_number or not property_description:
                st.error("⚠️ Please fill in all required fields (*)")
            else:
                with st.spinner("Generating cover page..."):
                    try:
                        # Create data dictionary
                        data = {
                            'client_name': client_name,
                            'file_number': file_number,
                            'property_description': property_description,
                            'period_of_search': period_of_search,
                            'present_owners': present_owners,
                            'names_searched': names_searched,
                            'conveyance_documents': conveyance_docs,
                            'encumbrances': encumbrances,
                            'assessment_number': assessment_number,
                            'tax_status': tax_status
                        }
                        
                        # Generate cover page
                        generator = BradleyAbstractCoverPage()
                        cover_page_buffer = io.BytesIO()
                        
                        # Create temp file for cover page
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_cover:
                            tmp_cover_path = tmp_cover.name
                        
                        success = generator.fill_cover_page(data, tmp_cover_path)
                        
                        if not success:
                            st.error("❌ Failed to generate cover page.")
                        else:
                            # Read cover page bytes
                            with open(tmp_cover_path, 'rb') as f:
                                cover_page_bytes = f.read()
                            
                            # Assemble complete PDF: cover page + all source documents
                            assembler = PDFAssembler()
                            
                            # Get source document paths/bytes
                            source_docs = [pdf_info['bytes'] for pdf_info in st.session_state.uploaded_pdfs]
                            
                            # Assemble: cover page as "billing" (page 1), no bradley form (already in cover), all source docs
                            complete_pdf_bytes = assembler.assemble_abstract(
                                billing_pdf_bytes=cover_page_bytes,
                                bradley_form_bytes=None,  # Cover page already contains the form
                                scanned_documents=source_docs,
                                output_path=None
                            )
                            
                            # Save to output folder
                            output_path = Path("output") / f"complete_abstract_{file_number.replace('/', '_')}.pdf"
                            output_path.parent.mkdir(exist_ok=True)
                            
                            with open(output_path, 'wb') as f:
                                f.write(complete_pdf_bytes)
                            
                            st.success(f"✅ Complete property abstract generated successfully!")
                            
                            # Provide download button
                            st.download_button(
                                label="📥 Download Complete Property Abstract PDF",
                                data=complete_pdf_bytes,
                                file_name=f"bradley_abstract_{file_number.replace('/', '_')}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                            
                            st.info(f"📁 Saved to: `{output_path}`")
                            
                            # Show page count
                            pdf_reader = PyPDF2.PdfReader(io.BytesIO(complete_pdf_bytes))
                            st.info(f"📄 Total pages: {len(pdf_reader.pages)} (1 cover page + {len(pdf_reader.pages)-1} document pages)")
                            
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        st.exception(e)

else:
    # Welcome screen when no PDFs uploaded
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        ### 🚀 Get Started
        
        **Step 1:** Upload client property document PDF(s) using the sidebar
        
        **Step 2:** Click "Extract Data from PDFs" to automatically extract information
        
        **Step 3:** Review and edit the extracted fields
        
        **Step 4:** Generate your complete property abstract
        
        ---
        
        #### ✨ Features
        - 🤖 **Smart extraction** - Automatically pulls data from multiple PDFs
        - ✏️ **Inline editing** - Fix any mistakes or add missing information
        - 📄 **Complete assembly** - Cover page + all source documents in one PDF
        - 🔍 **OCR support** - Works with scanned documents too
        
        ---
        
        *Upload document(s) to begin →*
        """)
    
    # Show example data option
    st.markdown("---")
    if st.button("� Or start with manual entry (no upload)"):
        st.session_state.extracted_data = {
            'client_name': '',
            'file_number': '',
            'property_description': '',
            'period_of_search': '',
            'present_owners': '',
            'names_searched': 'All names searched 20 years for Federal judgments & liens',
            'conveyance_documents': '',
            'encumbrances': '',
            'assessment_number': '0610429400',
            'tax_status': 'Taxes Paid Annually'
        }
        st.session_state.pdf_processed = True
        st.rerun()
