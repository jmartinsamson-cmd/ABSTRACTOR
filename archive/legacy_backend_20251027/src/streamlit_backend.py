"""
New Backend Integration for Streamlit App
This module provides the new process_pdf_new function that implements the reworked workflow
while keeping the UI exactly the same.
"""

from src.abstract_workflow import AbstractWorkflow


def process_documents_new(uploaded_files, use_ocr=True, client_info=None):
    """
    New backend logic for processing documents
    Replaces the old process_pdf function with the new workflow:
    1. Generate billing page
    2. Extract data from scanned documents  
    3. Fill Bradley Abstract form
    4. Assemble: billing + form + scanned docs
    
    Args:
        uploaded_files: List of Streamlit uploaded files
        use_ocr: Whether to use OCR
        client_info: Optional dictionary with client/billing information
        
    Returns:
        dict: Processing results compatible with existing UI
    """
    workflow = AbstractWorkflow()
    
    # Process using new workflow
    result = workflow.process_documents(
        uploaded_files=uploaded_files,
        client_info=client_info,
        use_ocr=use_ocr
    )
    
    # Transform result to match existing UI expectations
    ui_result = {
        'status': result['status'],
        'message': result['message'],
        'extracted_data': result['extracted_data'],
        'final_pdf_bytes': result['final_pdf_bytes'],
        'billing_pdf_bytes': result['billing_pdf_bytes'],
        'filled_form_bytes': result['filled_form_bytes'],
        'scanned_docs': result['scanned_docs'],
        'num_files': len(uploaded_files),
        'num_fields': len(result['extracted_data']),
        'images_extracted': len(result['extracted_data'].get('images', []))
    }
    
    return ui_result


def regenerate_with_edits(scanned_docs, client_info, extracted_data):
    """
    Regenerate PDF after user edits
    
    Args:
        scanned_docs: List of scanned document bytes
        client_info: Updated client information from user edits
        extracted_data: Original extracted data
        
    Returns:
        dict: Updated PDFs
    """
    workflow = AbstractWorkflow()
    
    result = workflow.update_client_info_and_regenerate(
        scanned_docs=scanned_docs,
        client_info=client_info,
        extracted_data=extracted_data
    )
    
    return result
