import streamlit as st
from pathlib import Path
import sys
import tempfile
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from cover_page_generator import BradleyAbstractCoverPage
from parser import PDFParser
from field_extractor import FieldExtractor

st.set_page_config(page_title="Abstractor - Smart Cover Page", layout="wide", page_icon="🏛️")

# Initialize session state
if 'extracted_data' not in st.session_state:
    st.session_state.extracted_data = {}
if 'pdf_processed' not in st.session_state:
    st.session_state.pdf_processed = False

st.title("🏛️ Bradley Abstract - Smart Cover Page Generator")
st.markdown("**Upload a PDF → Auto-extract data → Edit inline → Generate cover page**")

# Sidebar
with st.sidebar:
    st.markdown("### 📤 Upload Document")
    uploaded_file = st.file_uploader(
        "Choose PDF to extract data from",
        type=['pdf'],
        help="Upload a property document to automatically extract information"
    )
    
    st.markdown("---")
    
    use_ocr = st.checkbox("Enable OCR (for scanned PDFs)", value=False)
    
    if uploaded_file:
        if st.button("🔍 Extract Data from PDF", type="primary", use_container_width=True):
            with st.spinner("Extracting data from PDF..."):
                try:
                    # Save uploaded file temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                        tmp_file.write(uploaded_file.read())
                        tmp_path = tmp_file.name
                    
                    # Parse PDF
                    parser = PDFParser(tmp_path, use_ocr=use_ocr)
                    text = parser.extract_text()
                    
                    # Extract fields
                    extractor = FieldExtractor(text)
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
                    st.success("✅ Data extracted successfully! Review and edit below.")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error extracting data: {str(e)}")
                    st.exception(e)
    
    st.markdown("---")
    st.markdown("### 💡 How it works")
    st.markdown("""
    1. Upload a property PDF
    2. Click Extract Data
    3. Review & edit fields
    4. Generate cover page
    """)

# Main content area
if st.session_state.pdf_processed or st.session_state.extracted_data:
    st.subheader("✏️ Review and Edit Extracted Information")
    st.info("� All fields are editable. Update any information as needed before generating the cover page.")
    
    # Create editable form
    with st.form("cover_page_form"):
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
            submit = st.form_submit_button("🎯 Generate Cover Page", type="primary", use_container_width=True)
        
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
                        output_path = Path("output") / f"cover_page_{file_number.replace('/', '_')}.pdf"
                        output_path.parent.mkdir(exist_ok=True)
                        
                        success = generator.generate_cover_page(data, str(output_path))
                        
                        if success:
                            st.success(f"✅ Cover page generated successfully!")
                            
                            # Provide download button
                            with open(output_path, "rb") as pdf_file:
                                st.download_button(
                                    label="📥 Download Cover Page PDF",
                                    data=pdf_file,
                                    file_name=f"bradley_abstract_cover_{file_number.replace('/', '_')}.pdf",
                                    mime="application/pdf",
                                    use_container_width=True
                                )
                            
                            st.info(f"📁 Saved to: `{output_path}`")
                        else:
                            st.error("❌ Failed to generate cover page.")
                            
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        st.exception(e)

else:
    # Welcome screen when no PDF is uploaded
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        ### 🚀 Get Started
        
        **Step 1:** Upload a property document PDF using the sidebar
        
        **Step 2:** Click "Extract Data from PDF" to automatically extract information
        
        **Step 3:** Review and edit the extracted fields
        
        **Step 4:** Generate your professional cover page
        
        ---
        
        #### ✨ Features
        - 🤖 **Smart extraction** - Automatically pulls data from your PDFs
        - ✏️ **Inline editing** - Fix any mistakes or add missing information
        - 📄 **Professional output** - Generate Bradley Abstract branded cover pages
        - 🔍 **OCR support** - Works with scanned documents too
        
        ---
        
        *Upload a document to begin →*
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
