"""
Property Abstract Workflow
Orchestrates the complete workflow for generating property abstracts
"""

from pathlib import Path
from typing import List, Dict, Optional
import io
from src.billing_generator import BillingPageGenerator
from src.pdf_assembler import PDFAssembler
from src.parser import PDFParser
from src.field_extractor import FieldExtractor


class AbstractWorkflow:
    """
    Manages the complete workflow for property abstract generation:
    1. Generate billing page
    2. Extract data from scanned documents
    3. Clear and fill Bradley Abstract form
    4. Assemble all PDFs (billing + form + scanned docs)
    5. Provide preview for editing
    """
    
    def __init__(self, bradley_template_path: str = "templates/STEP2.pdf"):
        self.bradley_template = bradley_template_path
        self.billing_generator = BillingPageGenerator()
        self.pdf_assembler = PDFAssembler()
        
    def process_documents(
        self,
        uploaded_files: List,
        client_info: Optional[Dict] = None,
        use_ocr: bool = True
    ) -> Dict:
        """
        Process uploaded documents and create property abstract
        
        Args:
            uploaded_files: List of uploaded PDF files (Streamlit file objects)
            client_info: Dictionary with client and billing information
            use_ocr: Whether to use OCR for text extraction
            
        Returns:
            dict with results:
                - billing_pdf_bytes: Billing page PDF
                - filled_form_bytes: Filled Bradley Abstract form
                - scanned_docs: List of scanned document bytes
                - final_pdf_bytes: Complete assembled PDF
                - extracted_data: Extracted data from documents
                - status: Success/error status
                - message: Status message
        """
        result = {
            'billing_pdf_bytes': None,
            'filled_form_bytes': None,
            'scanned_docs': [],
            'final_pdf_bytes': None,
            'extracted_data': {},
            'status': 'processing',
            'message': ''
        }
        
        try:
            # Step 1: Extract data from all uploaded documents
            all_extracted_data = {}
            all_images = []
            scanned_docs_bytes = []
            
            for uploaded_file in uploaded_files:
                # Save uploaded file bytes
                file_bytes = uploaded_file.getvalue()
                scanned_docs_bytes.append(file_bytes)
                
                # Extract text and data - PDFParser needs a file path
                import tempfile
                import os
                
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                    temp_file.write(file_bytes)
                    temp_path = temp_file.name
                
                try:
                    # Use existing parser with file path
                    parser = PDFParser(temp_path, use_ocr=use_ocr)
                    text = parser.extract_text()
                    
                    # Extract fields
                    extractor = FieldExtractor(text)
                    extracted_fields = extractor.extract_all_fields()
                    all_extracted_data.update(extracted_fields)
                    
                    # Extract images
                    try:
                        images = parser.get_largest_images(
                            min_width=150,
                            min_height=150,
                            max_count=5
                        )
                        all_images.extend(images)
                    except Exception:
                        # Image extraction is optional
                        pass
                finally:
                    # Clean up temp file
                    try:
                        os.unlink(temp_path)
                    except Exception:
                        pass
            
            result['scanned_docs'] = scanned_docs_bytes
            result['extracted_data'] = all_extracted_data
            
            # Step 2: Merge client_info with extracted data (client_info takes precedence)
            if client_info is None:
                client_info = {}
            
            # Combine: extracted data provides defaults, client_info overrides
            combined_data = {**all_extracted_data, **client_info}
            combined_data['images'] = all_images
            
            # Step 3: Generate billing page
            billing_info = {
                'client_name': combined_data.get('owner_name', 
                                                combined_data.get('client_name', 'N/A')),
                'property_address': combined_data.get('property_address', 'N/A'),
                'abstract_date': client_info.get('abstract_date', None),
                'fee_amount': client_info.get('fee_amount', 'Contact for pricing'),
                'notes': client_info.get('notes', '')
            }
            
            billing_pdf_bytes = self.billing_generator.generate(billing_info)
            result['billing_pdf_bytes'] = billing_pdf_bytes
            
            # Step 4: Clear and fill Bradley Abstract form
            filled_form_bytes = self.pdf_assembler.clear_and_fill_bradley_form(
                template_path=self.bradley_template,
                client_data=combined_data
            )
            result['filled_form_bytes'] = filled_form_bytes
            
            # Step 5: Assemble complete PDF
            final_pdf_bytes = self.pdf_assembler.assemble_abstract(
                billing_pdf_bytes=billing_pdf_bytes,
                bradley_form_bytes=filled_form_bytes,
                scanned_documents=scanned_docs_bytes
            )
            result['final_pdf_bytes'] = final_pdf_bytes
            
            result['status'] = 'success'
            result['message'] = f'Successfully processed {len(uploaded_files)} document(s)'
            
        except Exception as e:
            result['status'] = 'error'
            result['message'] = f'Error processing documents: {str(e)}'
        
        return result
    
    def update_client_info_and_regenerate(
        self,
        scanned_docs: List[bytes],
        client_info: Dict,
        extracted_data: Dict
    ) -> Dict:
        """
        Regenerate PDF with updated client information
        
        Args:
            scanned_docs: List of scanned document bytes
            client_info: Updated client information
            extracted_data: Previously extracted data
            
        Returns:
            dict with updated PDFs
        """
        result = {
            'billing_pdf_bytes': None,
            'filled_form_bytes': None,
            'final_pdf_bytes': None,
            'status': 'processing',
            'message': ''
        }
        
        try:
            # Merge client_info with extracted data
            combined_data = {**extracted_data, **client_info}
            
            # Generate billing page
            billing_info = {
                'client_name': combined_data.get('owner_name',
                                                combined_data.get('client_name', 'N/A')),
                'property_address': combined_data.get('property_address', 'N/A'),
                'abstract_date': client_info.get('abstract_date', None),
                'fee_amount': client_info.get('fee_amount', 'Contact for pricing'),
                'notes': client_info.get('notes', '')
            }
            
            billing_pdf_bytes = self.billing_generator.generate(billing_info)
            result['billing_pdf_bytes'] = billing_pdf_bytes
            
            # Fill Bradley Abstract form
            filled_form_bytes = self.pdf_assembler.clear_and_fill_bradley_form(
                template_path=self.bradley_template,
                client_data=combined_data
            )
            result['filled_form_bytes'] = filled_form_bytes
            
            # Assemble complete PDF
            final_pdf_bytes = self.pdf_assembler.assemble_abstract(
                billing_pdf_bytes=billing_pdf_bytes,
                bradley_form_bytes=filled_form_bytes,
                scanned_documents=scanned_docs
            )
            result['final_pdf_bytes'] = final_pdf_bytes
            
            result['status'] = 'success'
            result['message'] = 'PDF regenerated with updated information'
            
        except Exception as e:
            result['status'] = 'error'
            result['message'] = f'Error regenerating PDF: {str(e)}'
        
        return result
