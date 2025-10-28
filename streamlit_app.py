import streamlit as st
from pathlib import Path
import sys
import tempfile
import io
import PyPDF2

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from cover_page_generator import BradleyAbstractCoverPage
from parser import PDFParser
# from field_extractor import FieldExtractor  # legacy regex extractor (unused)
from pdf_assembler import PDFAssembler
from schema_loader import load_schema
from preview import render_cover_preview_png

st.set_page_config(page_title="Abstractor - Property Abstract Generator", layout="wide", page_icon="🏛️")

# Inject Canva-inspired theme CSS
def _inject_theme_css():
    css_path = Path(__file__).parent / "assets" / "canva_theme.css"
    if css_path.exists():
        try:
            css = css_path.read_text()
            st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
        except Exception:
            # Non-fatal if theme can't be injected
            pass

_inject_theme_css()

# Initialize session state
if 'extracted_data' not in st.session_state:
    st.session_state.extracted_data = {}
if 'pdf_processed' not in st.session_state:
    st.session_state.pdf_processed = False
if 'uploaded_pdfs' not in st.session_state:
    st.session_state.uploaded_pdfs = []

# Hero header (styled)
st.markdown(
        """
        <div class="canva-header">
            <h1 class="site-title">Bradley Abstract — Property Abstract Generator</h1>
            <p class="subtitle">Upload → Auto-extract → Review → Generate your complete abstract</p>
        </div>
        """,
        unsafe_allow_html=True,
)

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
    
    use_ocr = st.checkbox("Enable OCR (for scanned PDFs)", value=False)
    if use_ocr:
        # Show environment readiness for OCR
        try:
            from word_index import ocr_environment_status
            env = ocr_environment_status()
            if not (env.get('tesseract_bin') and env.get('poppler_pdfinfo')):
                missing = []
                if not env.get('tesseract_bin'):
                    missing.append('tesseract')
                if not env.get('poppler_pdfinfo'):
                    missing.append('poppler (pdfinfo)')
                st.warning(f"OCR requested but missing: {', '.join(missing)}. We'll fall back to the PDF text layer if available.")
                with st.expander("How to enable OCR on Linux (optional)"):
                    st.markdown("Install system dependencies:")
                    st.code("sudo apt-get update\nsudo apt-get install -y tesseract-ocr poppler-utils", language="bash")
                    st.markdown("Then reinstall Python deps if needed:")
                    st.code("pip3 install pdf2image pytesseract", language="bash")
        except Exception:
            st.warning("OCR requested; unable to verify OCR environment. If OCR fails, we'll fall back to text layer.")
    
    if uploaded_files and len(uploaded_files) > 0:
        if st.button("🔍 Extract Data from PDFs", type="primary", use_container_width=True):
            with st.spinner("Extracting data from all PDFs..."):
                try:
                    # Save uploaded files
                    st.session_state.uploaded_pdfs = []
                    all_text = ""
                    tmp_paths = []
                    
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
                        tmp_paths.append(tmp_path)
                        
                        # Parse PDF
                        parser = PDFParser(tmp_path, use_ocr=use_ocr)
                        text = parser.extract_text()
                        all_text += f"\n\n=== {uploaded_file.name} ===\n{text}"
                    # Schema-based extraction (zone + regex) with confidences
                    from schema_loader import load_schema
                    from word_index import collect_words_from_sources
                    from extract import extract_fields_from_schema

                    schema = load_schema('bradley_cover_v1.yml')
                    words = collect_words_from_sources(tmp_paths, prefer_ocr=use_ocr)
                    fv_map = extract_fields_from_schema(words, all_text, schema)
                    
                    # Store in session state
                    def _v(m, k):
                        fv = m.get(k)
                        return fv.value if fv else ''
                    st.session_state.extracted_data = {
                        'client_name': _v(fv_map, 'for_field'),
                        'file_number': _v(fv_map, 'file_number'),
                        'property_description': _v(fv_map, 'property_description'),
                        'period_of_search': _v(fv_map, 'period_of_search'),
                        'present_owners': _v(fv_map, 'present_owners'),
                        'names_searched': 'All names searched 20 years for Federal judgments & liens',
                        'conveyance_documents': '',
                        'encumbrances': '',
                        'assessment_number': '0610429400',
                        'tax_status': 'Taxes Paid Annually'
                    }
                    st.session_state.field_confidences = {k: v.confidence for k, v in fv_map.items()}
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
    st.info("Live preview updates as you type. Red fields must be corrected before rendering.")

    # Inputs (no form to enable live updates)
    col1, col2 = st.columns(2)
    with col1:
        client_name = st.text_input(
            "Client Name (FOR:) *",
            value=st.session_state.extracted_data.get('client_name', ''),
            placeholder="Enter or verify client name",
            key="client_name_input",
        )
        file_number = st.text_input(
            "File Number *",
            value=st.session_state.extracted_data.get('file_number', ''),
            placeholder="e.g., 2024-001",
            key="file_number_input",
        )
        property_description = st.text_area(
            "Property Description *",
            value=st.session_state.extracted_data.get('property_description', ''),
            placeholder="Enter complete property description",
            height=120,
            key="property_description_input",
        )
    with col2:
        period_of_search = st.text_input(
            "Period of Search *",
            value=st.session_state.extracted_data.get('period_of_search', ''),
            placeholder="e.g., 20 years, 1/1/2004 - present",
            key="period_of_search_input",
        )
        present_owners = st.text_input(
            "Present Owner(s) *",
            value=st.session_state.extracted_data.get('present_owners', ''),
            placeholder="Enter current property owner(s)",
            key="present_owners_input",
        )
        names_searched = st.text_area(
            "Names Searched",
            value=st.session_state.extracted_data.get('names_searched', 'All names searched 20 years for Federal judgments & liens'),
            height=80,
            key="names_searched_input",
        )

    st.markdown("---")
    st.markdown("#### 📑 Additional Information")
    col3, col4 = st.columns(2)
    with col3:
        conveyance_docs = st.text_area(
            "Conveyance Documents",
            value=st.session_state.extracted_data.get('conveyance_documents', ''),
            placeholder="List relevant conveyance documents",
            height=100,
            key="conveyance_docs_input",
        )
    with col4:
        encumbrances = st.text_area(
            "Encumbrances",
            value=st.session_state.extracted_data.get('encumbrances', ''),
            placeholder="List any encumbrances",
            height=100,
            key="encumbrances_input",
        )

    st.markdown("#### 💰 Tax Information")
    col5, col6 = st.columns(2)
    with col5:
        assessment_number = st.text_input(
            "Assessment Number",
            value=st.session_state.extracted_data.get('assessment_number', '0610429400'),
            key="assessment_number_input",
        )
    with col6:
        tax_status = st.text_input(
            "Tax Payment Status",
            value=st.session_state.extracted_data.get('tax_status', 'Taxes Paid Annually'),
            key="tax_status_input",
        )

    # Build data mapping for schema fields
    cover_data = {
        'for_field': client_name,
        'file_number': file_number,
        'property_description': property_description,
        'period_of_search': period_of_search,
        'present_owners': present_owners,
        'names_searched': names_searched,
        'conveyance_documents': conveyance_docs,
        'encumbrances': encumbrances,
    }

    # Live preview with flags
    st.markdown("---")
    st.markdown("### 👀 Preview (what will be printed)")
    template_path = str(Path(__file__).parent / 'templates' / 'bradley_abstract_cover.pdf')
    try:
        schema = load_schema('bradley_cover_v1.yml')
        confidences = st.session_state.get('field_confidences', {})
        png_bytes, statuses, transform = render_cover_preview_png(template_path, schema, cover_data, confidences=confidences)
        st.image(png_bytes, caption=f"Alignment: {transform.get('status', 'n/a')}", use_column_width=True)
        # Legend and statuses
        cols = st.columns([1, 2])
        with cols[0]:
            st.markdown(
                """
                <div>
                  <span class="legend-chip">🟢 confidence ≥ 0.85</span>
                </div>
                <div style="margin-top: 0.35rem;">
                  <span class="legend-chip">🟡 0.60 – 0.85</span>
                </div>
                <div style="margin-top: 0.35rem;">
                  <span class="legend-chip">🔴 &lt; 0.60</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with cols[1]:
            bad = []
            for k, s in statuses.items():
                color = '🟢' if s['color']=='green' else ('🟡' if s['color']=='yellow' else '🔴')
                errs = (", ".join(s['errors'])) if s['errors'] else ""
                st.write(f"{color} {k.replace('_',' ').title()} — {s['confidence']:.2f} {errs}")
                if s['color'] == 'red':
                    bad.append(k)
    except Exception as e:
        st.warning(f"Preview unavailable: {e}")
        bad = []

    st.markdown("---")
    # Render button is disabled if any red fields
    disabled = len(bad) > 0
    if disabled:
        st.error("Fix red fields before rendering.")
    if st.button("🎯 Generate Cover Page", type="primary", use_container_width=True, disabled=disabled):
        with st.spinner("Generating cover page..."):
            try:
                # Legacy-compatible mapping for generator
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

                generator = BradleyAbstractCoverPage()
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_cover:
                    tmp_cover_path = tmp_cover.name
                success = generator.generate_cover_page(data, tmp_cover_path)
                if not success:
                    st.error("❌ Failed to generate cover page.")
                else:
                    with open(tmp_cover_path, 'rb') as f:
                        cover_page_bytes = f.read()
                    assembler = PDFAssembler()
                    source_docs = [pdf_info['bytes'] for pdf_info in st.session_state.uploaded_pdfs]
                    complete_pdf_bytes = assembler.assemble_abstract(
                        billing_pdf_bytes=cover_page_bytes,
                        bradley_form_bytes=None,
                        scanned_documents=source_docs,
                        output_path=None
                    )
                    safe_fn = (file_number or "").replace('/', '_')
                    output_path = Path("output") / f"complete_abstract_{safe_fn}.pdf"
                    output_path.parent.mkdir(exist_ok=True)
                    with open(output_path, 'wb') as f:
                        f.write(complete_pdf_bytes)
                    st.success("✅ Complete property abstract generated successfully!")
                    st.download_button(
                        label="📥 Download Complete Property Abstract PDF",
                        data=complete_pdf_bytes,
                        file_name=f"bradley_abstract_{safe_fn}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    st.info(f"📁 Saved to: `{output_path}`")
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
    if st.button("📝 Or start with manual entry (no upload)"):
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
