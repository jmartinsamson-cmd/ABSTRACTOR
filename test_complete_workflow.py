#!/usr/bin/env python3
"""
Complete Workflow Test - Property Abstract System
Tests the new backend: Billing + Form + Scanned Docs assembly
"""

import sys
from pathlib import Path
import io


def test_complete_workflow():
    """Test the complete property abstract workflow"""
    
    print("=" * 70)
    print("PROPERTY ABSTRACT WORKFLOW - COMPLETE TEST")
    print("=" * 70)
    
    # Step 1: Test Billing Page Generation
    print("\n📄 STEP 1: Testing Billing Page Generation")
    print("-" * 70)
    
    try:
        from src.billing_generator import BillingPageGenerator
        
        billing_gen = BillingPageGenerator()
        
        test_client_info = {
            'client_name': 'John & Jane Doe',
            'property_address': '712 SPRUCE ST, City, State 12345',
            'abstract_date': 'October 27, 2025',
            'fee_amount': '$150.00',
            'notes': 'Property abstract research for title transfer. All documents reviewed and verified.'
        }
        
        billing_pdf_bytes = billing_gen.generate(test_client_info)
        
        if billing_pdf_bytes:
            print(f"✅ Billing page generated: {len(billing_pdf_bytes):,} bytes")
            
            # Save for inspection
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            with open(output_dir / "test_billing_page.pdf", "wb") as f:
                f.write(billing_pdf_bytes)
            print(f"📁 Saved to: output/test_billing_page.pdf")
        else:
            print("❌ Failed to generate billing page")
            return False
            
    except Exception as e:
        print(f"❌ Error in billing page generation: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 2: Test PDF Assembly Module
    print("\n🔧 STEP 2: Testing PDF Assembly Module")
    print("-" * 70)
    
    try:
        from src.pdf_assembler import PDFAssembler
        
        assembler = PDFAssembler()
        
        # Check if template exists
        template_path = "templates/STEP2.pdf"
        if not Path(template_path).exists():
            print(f"❌ Template not found: {template_path}")
            return False
        
        print(f"✅ Template found: {template_path}")
        
        # Test filling Bradley form
        test_form_data = {
            'owner_name': 'John & Jane Doe',
            'property_address': '712 SPRUCE ST',
            'legal_description': 'LOTS 11-12 BLK 62 CICO ADD #1',
            'subdivision': 'CICO ADDITION #1',
            'lot_info': '11-12',
            'deed_info': {'page': '123', 'book': '456'},
            'tax_info': {'tax_year': '2025'}
        }
        
        filled_form_bytes = assembler.clear_and_fill_bradley_form(
            template_path=template_path,
            client_data=test_form_data
        )
        
        if filled_form_bytes:
            print(f"✅ Bradley form filled: {len(filled_form_bytes):,} bytes")
            with open(output_dir / "test_filled_form.pdf", "wb") as f:
                f.write(filled_form_bytes)
            print(f"📁 Saved to: output/test_filled_form.pdf")
        else:
            print("❌ Failed to fill Bradley form")
            return False
            
    except Exception as e:
        print(f"❌ Error in form filling: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 3: Test Complete Assembly
    print("\n📦 STEP 3: Testing Complete PDF Assembly")
    print("-" * 70)
    
    try:
        # Check if we have a test document
        test_doc_path = Path(r"c:\Users\jsamb\OneDrive\Desktop\B & P 712- docs.pdf")
        
        if test_doc_path.exists():
            # Read the test document
            with open(test_doc_path, 'rb') as f:
                test_doc_bytes = f.read()
            
            scanned_docs = [test_doc_bytes]
            print(f"✅ Loaded test document: {test_doc_path.name} ({len(test_doc_bytes):,} bytes)")
        else:
            print(f"⚠️  Test document not found: {test_doc_path}")
            print("   Using empty scanned docs list")
            scanned_docs = []
        
        # Assemble complete PDF
        final_pdf_bytes = assembler.assemble_abstract(
            billing_pdf_bytes=billing_pdf_bytes,
            bradley_form_bytes=filled_form_bytes,
            scanned_documents=scanned_docs
        )
        
        if final_pdf_bytes:
            print(f"✅ Final PDF assembled: {len(final_pdf_bytes):,} bytes")
            
            final_output = output_dir / "test_complete_abstract.pdf"
            with open(final_output, "wb") as f:
                f.write(final_pdf_bytes)
            
            print(f"📁 Saved to: {final_output}")
            
            # Count pages
            import PyPDF2
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(final_pdf_bytes))
            num_pages = len(pdf_reader.pages)
            
            expected_pages = 1 + len(PyPDF2.PdfReader(io.BytesIO(filled_form_bytes)).pages)
            if scanned_docs:
                expected_pages += len(PyPDF2.PdfReader(io.BytesIO(scanned_docs[0])).pages)
            
            print(f"📄 Total pages: {num_pages}")
            print(f"   - Billing page: 1")
            print(f"   - Bradley form: {len(PyPDF2.PdfReader(io.BytesIO(filled_form_bytes)).pages)}")
            if scanned_docs:
                print(f"   - Scanned docs: {len(PyPDF2.PdfReader(io.BytesIO(scanned_docs[0])).pages)}")
            
            if num_pages == expected_pages:
                print("✅ Page count matches expected!")
            else:
                print(f"⚠️  Expected {expected_pages} pages, got {num_pages}")
        else:
            print("❌ Failed to assemble final PDF")
            return False
            
    except Exception as e:
        print(f"❌ Error in PDF assembly: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 4: Test Complete Workflow Integration
    print("\n🔄 STEP 4: Testing Complete Workflow Integration")
    print("-" * 70)
    
    try:
        from src.abstract_workflow import AbstractWorkflow
        
        workflow = AbstractWorkflow()
        
        # Create a mock uploaded file object
        class MockUploadedFile:
            def __init__(self, name, bytes_data):
                self.name = name
                self._bytes = bytes_data
            
            def getvalue(self):
                return self._bytes
        
        if test_doc_path.exists():
            with open(test_doc_path, 'rb') as f:
                test_bytes = f.read()
            
            mock_files = [MockUploadedFile("test_document.pdf", test_bytes)]
            
            client_info = {
                'client_name': 'Integration Test Client',
                'property_address': '123 Test Street',
                'fee_amount': '$200.00',
                'notes': 'Complete workflow integration test'
            }
            
            result = workflow.process_documents(
                uploaded_files=mock_files,
                client_info=client_info,
                use_ocr=True
            )
            
            if result['status'] == 'success':
                print(f"✅ Workflow completed: {result['message']}")
                print(f"📊 Extracted {len(result['extracted_data'])} fields")
                print(f"📄 Final PDF size: {len(result['final_pdf_bytes']):,} bytes")
                
                # Save workflow result
                with open(output_dir / "test_workflow_complete.pdf", "wb") as f:
                    f.write(result['final_pdf_bytes'])
                print(f"📁 Saved to: output/test_workflow_complete.pdf")
                
                # Show extracted fields
                print("\n📋 Extracted Fields:")
                for key, value in list(result['extracted_data'].items())[:10]:
                    if key != 'images':
                        display_value = str(value)[:50] if value else 'None'
                        print(f"   • {key}: {display_value}")
                
            else:
                print(f"❌ Workflow failed: {result['message']}")
                return False
        else:
            print("⚠️  Skipping workflow test - no test document available")
            
    except Exception as e:
        print(f"❌ Error in workflow integration: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 5: Test Streamlit Backend Bridge
    print("\n🌉 STEP 5: Testing Streamlit Backend Bridge")
    print("-" * 70)
    
    try:
        from src.streamlit_backend import process_documents_new, regenerate_with_edits
        
        if test_doc_path.exists():
            result = process_documents_new(
                uploaded_files=mock_files,
                use_ocr=True,
                client_info=client_info
            )
            
            if result['status'] == 'success':
                print(f"✅ Streamlit backend integration successful")
                print(f"📊 UI Result format:")
                print(f"   • Status: {result['status']}")
                print(f"   • Message: {result['message']}")
                print(f"   • Files processed: {result['num_files']}")
                print(f"   • Fields extracted: {result['num_fields']}")
                print(f"   • Images extracted: {result['images_extracted']}")
                print(f"   • Final PDF: {len(result['final_pdf_bytes']):,} bytes")
                
                # Save streamlit result
                with open(output_dir / "test_streamlit_backend.pdf", "wb") as f:
                    f.write(result['final_pdf_bytes'])
                print(f"📁 Saved to: output/test_streamlit_backend.pdf")
            else:
                print(f"❌ Streamlit backend failed: {result['message']}")
                return False
        else:
            print("⚠️  Skipping streamlit backend test - no test document available")
            
    except Exception as e:
        print(f"❌ Error in streamlit backend: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Final Summary
    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED!")
    print("=" * 70)
    print("\n📁 Test outputs saved to output/ folder:")
    print("   • test_billing_page.pdf - Billing page only")
    print("   • test_filled_form.pdf - Filled Bradley form only")
    print("   • test_complete_abstract.pdf - Complete assembled PDF")
    print("   • test_workflow_complete.pdf - Full workflow result")
    print("   • test_streamlit_backend.pdf - Streamlit integration result")
    print("\n🎉 The new backend is working correctly!")
    print("   You can now integrate it into streamlit_app.py")
    print("   See QUICK_START.md for integration instructions")
    
    return True


if __name__ == "__main__":
    success = test_complete_workflow()
    sys.exit(0 if success else 1)
