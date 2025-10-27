import streamlit as st
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from cover_page_generator import BradleyAbstractCoverPage

st.set_page_config(page_title="Abstractor - Bradley Abstract Cover Page", layout="wide")

st.title("🏛️ Bradley Abstract - Cover Page Generator")
st.markdown("Generate professional cover pages for property abstracts")

# Sidebar for navigation
with st.sidebar:
    st.image("https://via.placeholder.com/150x100/1e3a8a/ffffff?text=Bradley+Abstract", use_container_width=True)
    st.markdown("---")
    st.subheader("Navigation")
    page = st.radio("Select Function:", ["Generate Cover Page", "About"], index=0)

if page == "Generate Cover Page":
    st.subheader("📋 Fill Out Cover Page Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        client_name = st.text_input("Client Name (FOR:)", placeholder="Enter client name")
        file_number = st.text_input("File Number", placeholder="e.g., 2024-001")
        property_description = st.text_area(
            "Property Description",
            placeholder="Enter complete property description",
            height=100
        )
    
    with col2:
        period_of_search = st.text_input(
            "Period of Search",
            placeholder="e.g., 20 years, 1/1/2004 - present"
        )
        present_owners = st.text_input(
            "Present Owner(s)",
            placeholder="Enter current property owner(s)"
        )
        
        # Optional fields
        st.markdown("**Optional Fields:**")
        names_searched = st.text_area(
            "Names Searched (optional)",
            value="All names searched 20 years for Federal judgments & liens",
            height=60
        )
    
    st.markdown("---")
    
    col3, col4 = st.columns(2)
    
    with col3:
        conveyance_docs = st.text_area(
            "Conveyance Documents (optional)",
            placeholder="List relevant conveyance documents",
            height=80
        )
    
    with col4:
        encumbrances = st.text_area(
            "Encumbrances (optional)",
            placeholder="List any encumbrances",
            height=80
        )
    
    # Tax information
    st.markdown("**Tax Information:**")
    col5, col6 = st.columns(2)
    with col5:
        assessment_number = st.text_input("Assessment Number", value="0610429400")
    with col6:
        tax_status = st.text_input("Tax Payment Status", value="Taxes Paid Annually")
    
    st.markdown("---")
    
    # Generate button
    if st.button("🎯 Generate Cover Page PDF", type="primary", use_container_width=True):
        if not client_name or not file_number or not property_description:
            st.error("⚠️ Please fill in required fields: Client Name, File Number, and Property Description")
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
                        
                        # Display PDF preview
                        with st.expander("📄 Preview Generated PDF", expanded=True):
                            st.info("PDF generated at: " + str(output_path))
                    else:
                        st.error("❌ Failed to generate cover page. Please check the logs.")
                        
                except Exception as e:
                    st.error(f"❌ Error generating cover page: {str(e)}")
                    st.exception(e)

elif page == "About":
    st.subheader("📖 About This Application")
    
    with st.expander("What changed?", expanded=True):
        st.write("""
        **Version 2.0 - Cover Page Generator**
        
        This application generates professional Bradley Abstract LLC cover pages for property abstracts.
        
        **Features:**
        - ✅ Automated cover page generation
        - ✅ Fillable PDF form fields
        - ✅ Professional formatting matching Bradley Abstract branding
        - ✅ Download generated PDFs
        
        **Archived Modules:**
        Core processing/extraction/pipeline code was archived to `archive/legacy_backend_20251027/`.
        Selectively restored modules for cover page generation.
        """)
    
    st.subheader("🔧 Technical Details")
    st.info("""
    **Template:** `templates/bradley_abstract_cover.pdf`
    
    **Required Fields:**
    - Client Name (FOR)
    - File Number
    - Property Description
    - Period of Search
    - Present Owner(s)
    
    **Output:** `output/cover_page_[file_number].pdf`
    """)
    
    st.subheader("💡 Usage Tips")
    st.markdown("""
    1. Fill in all required fields (marked with *)
    2. Optional fields will be included if provided
    3. Click "Generate Cover Page PDF" to create the document
    4. Download the generated PDF using the download button
    5. Use this as the first page for your property abstract documents
    """)
