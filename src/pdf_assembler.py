"""
PDF Assembly Module
Combines billing page + cleared/filled Bradley Abstract form + scanned documents
"""

import PyPDF2
from pathlib import Path
import io
from typing import List, Union, Optional, Any


class PDFAssembler:
    """Assembles multiple PDFs into a single document"""
    
    def __init__(self):
        self.merger = None
    
    def assemble_abstract(
        self,
        billing_pdf_bytes: bytes,
        bradley_form_bytes: Optional[bytes],
        scanned_documents: List[Any],
        output_path: Optional[str] = None
    ) -> bytes:
        """
        Assemble complete property abstract PDF
        
        Args:
            billing_pdf_bytes: Billing page PDF as bytes
            bradley_form_bytes: Filled Bradley Abstract form as bytes
            scanned_documents: List of scanned PDFs (bytes or file paths)
            output_path: Optional path to save assembled PDF
            
        Returns:
            bytes: Assembled PDF as bytes
        """
        merger = PyPDF2.PdfMerger()
        
        try:
            # 1. Add billing page (first page)
            if billing_pdf_bytes:
                merger.append(io.BytesIO(billing_pdf_bytes))
            
            # 2. Add cleared and filled Bradley Abstract form
            if bradley_form_bytes:
                merger.append(io.BytesIO(bradley_form_bytes))
            
            # 3. Append all scanned legal documents
            for doc in scanned_documents:
                if isinstance(doc, bytes):
                    merger.append(io.BytesIO(doc))
                elif isinstance(doc, str) and Path(doc).exists():
                    merger.append(str(doc))
                else:
                    # Assume it's a file-like object
                    merger.append(doc)
            
            # Write to output
            output_buffer = io.BytesIO()
            merger.write(output_buffer)
            output_buffer.seek(0)
            result_bytes = output_buffer.read()
            
            # Save to file if path provided
            if output_path:
                with open(output_path, 'wb') as f:
                    f.write(result_bytes)
            
            merger.close()
            return result_bytes
            
        except Exception as e:
            if merger:
                merger.close()
            raise Exception(f"Error assembling PDF: {str(e)}")
    
    def clear_and_fill_bradley_form(
        self,
        template_path: str,
        client_data: dict,
        output_path: Optional[str] = None
    ) -> bytes:
        """
        Clear existing form data and fill with new client information
        
        Args:
            template_path: Path to Bradley Abstract form template
            client_data: Dictionary with client information to fill
            output_path: Optional path to save filled form
            
        Returns:
            bytes: Filled form as bytes
        """
        # Import the existing FormFiller
        from src.form_filler import FormFiller  # type: ignore
        
        # Create temporary output
        if output_path is None:
            import tempfile
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            output_path = temp_file.name
            temp_file.close()
            cleanup_temp = True
        else:
            cleanup_temp = False
        
        try:
            # Fill the form with client data
            filler = FormFiller(template_path)
            filler.fill_form(
                client_data,
                output_path,
                verbose=False,
                images=client_data.get('images', [])
            )
            
            # Read the result
            with open(output_path, 'rb') as f:
                result_bytes = f.read()
            
            # Cleanup temp file if needed
            if cleanup_temp:
                import os
                os.unlink(output_path)
            
            return result_bytes
            
        except Exception as e:
            if cleanup_temp:
                import os
                try:
                    os.unlink(output_path)
                except Exception:
                    pass
            raise Exception(f"Error filling Bradley form: {str(e)}")
    
    def extract_text_from_pdfs(self, pdf_files: List[Union[bytes, str]]) -> dict:
        """
        Extract text from multiple PDFs for data extraction
        
        Args:
            pdf_files: List of PDF files (bytes or paths)
            
        Returns:
            dict: Extracted text from each PDF
        """
        extracted_data = {}
        
        for i, pdf_file in enumerate(pdf_files):
            try:
                if isinstance(pdf_file, bytes):
                    pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file))
                else:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                
                extracted_data[f"document_{i+1}"] = {
                    'text': text,
                    'page_count': len(pdf_reader.pages)
                }
            except Exception as e:
                extracted_data[f"document_{i+1}"] = {
                    'text': '',
                    'page_count': 0,
                    'error': str(e)
                }
        
        return extracted_data
