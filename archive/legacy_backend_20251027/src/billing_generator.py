"""
Billing Page Generator for Property Abstracts
Generates the first page of the final PDF with billing information
"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from datetime import datetime
from pathlib import Path
import io


class BillingPageGenerator:
    """Generates a billing page PDF for property abstracts"""
    
    def __init__(self):
        self.page_width, self.page_height = letter
        
    def generate(self, client_info=None, output_path=None):
        """
        Generate a billing page PDF
        
        Args:
            client_info (dict): Client and billing information
                - client_name: str
                - property_address: str
                - abstract_date: str (optional, defaults to today)
                - fee_amount: str (optional)
                - notes: str (optional)
            output_path (str): Path to save PDF, or None to return bytes
            
        Returns:
            bytes if output_path is None, else None (saves to file)
        """
        if client_info is None:
            client_info = {}
        
        # Create PDF buffer or file
        if output_path:
            c = canvas.Canvas(str(output_path), pagesize=letter)
        else:
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=letter)
        
        # Company header
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(self.page_width / 2, self.page_height - 1*inch, 
                           "Bradley Property Abstracts")
        
        c.setFont("Helvetica", 10)
        c.drawCentredString(self.page_width / 2, self.page_height - 1.3*inch,
                           "Professional Title Research Services")
        
        # Draw line separator
        c.line(1*inch, self.page_height - 1.5*inch, 
               self.page_width - 1*inch, self.page_height - 1.5*inch)
        
        # Invoice details
        y_position = self.page_height - 2*inch
        
        c.setFont("Helvetica-Bold", 14)
        c.drawString(1*inch, y_position, "BILLING STATEMENT")
        y_position -= 0.5*inch
        
        # Date
        abstract_date = client_info.get('abstract_date', 
                                       datetime.now().strftime("%B %d, %Y"))
        c.setFont("Helvetica", 11)
        c.drawString(1*inch, y_position, f"Date: {abstract_date}")
        y_position -= 0.3*inch
        
        # Client information
        c.setFont("Helvetica-Bold", 11)
        c.drawString(1*inch, y_position, "Client Information:")
        y_position -= 0.25*inch
        
        c.setFont("Helvetica", 11)
        client_name = client_info.get('client_name', 'N/A')
        c.drawString(1.3*inch, y_position, f"Name: {client_name}")
        y_position -= 0.25*inch
        
        property_address = client_info.get('property_address', 'N/A')
        c.drawString(1.3*inch, y_position, f"Property: {property_address}")
        y_position -= 0.5*inch
        
        # Services section
        c.setFont("Helvetica-Bold", 11)
        c.drawString(1*inch, y_position, "Services Provided:")
        y_position -= 0.25*inch
        
        c.setFont("Helvetica", 11)
        c.drawString(1.3*inch, y_position, "• Property Abstract Research")
        y_position -= 0.2*inch
        c.drawString(1.3*inch, y_position, "• Title Document Compilation")
        y_position -= 0.2*inch
        c.drawString(1.3*inch, y_position, "• Legal Description Verification")
        y_position -= 0.5*inch
        
        # Fee information
        c.setFont("Helvetica-Bold", 11)
        c.drawString(1*inch, y_position, "Fee:")
        fee_amount = client_info.get('fee_amount', 'Contact for pricing')
        c.drawString(2*inch, y_position, f"{fee_amount}")
        y_position -= 0.5*inch
        
        # Notes section
        notes = client_info.get('notes', '')
        if notes:
            c.setFont("Helvetica-Bold", 11)
            c.drawString(1*inch, y_position, "Notes:")
            y_position -= 0.25*inch
            
            c.setFont("Helvetica", 10)
            # Wrap notes text
            max_width = self.page_width - 2.5*inch
            lines = self._wrap_text(notes, c, max_width)
            for line in lines:
                c.drawString(1.3*inch, y_position, line)
                y_position -= 0.2*inch
        
        # Footer
        footer_y = 1*inch
        c.setFont("Helvetica-Oblique", 9)
        c.drawCentredString(self.page_width / 2, footer_y,
                           "Thank you for your business!")
        
        # Finalize
        c.showPage()
        c.save()
        
        if output_path:
            return None
        else:
            buffer.seek(0)
            return buffer.read()
    
    def _wrap_text(self, text, canvas_obj, max_width):
        """Wrap text to fit within max_width"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            test_line = ' '.join(current_line)
            if canvas_obj.stringWidth(test_line, "Helvetica", 10) > max_width:
                if len(current_line) > 1:
                    current_line.pop()
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(test_line)
                    current_line = []
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
