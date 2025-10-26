# PDF Form Abstractor - Configuration

# OCR Settings
OCR_ENABLED = True  # Use OCR for scanned/low-quality PDFs
OCR_DPI = 300  # Higher DPI = better quality but slower (200-400 recommended)
OCR_LANGUAGE = 'eng'  # Tesseract language (eng, fra, spa, etc.)
TESSERACT_PATH = None  # Set if Tesseract not in PATH (e.g., r'C:\Program Files\Tesseract-OCR\tesseract.exe')

# Text quality thresholds for OCR detection
MIN_TEXT_LENGTH = 50  # Minimum characters to consider text valid
MIN_ALPHANUMERIC_RATIO = 0.6  # Minimum ratio of alphanumeric chars
MIN_WORD_DENSITY = 50  # Minimum chars per word

# Field patterns can be customized here
# Add or modify patterns based on your specific PDF formats

FIELD_PATTERNS = {
    "owner_name": [
        r"(?:Owner|Grantee|Grantor)[\s:]+([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)",
        r"(?:Name|Owner Name)[\s:]+([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)",
    ],
    "property_address": [
        r"(?:Property Address|Address|Property Location)[\s:]+(.+?)(?:\n|$)",
        r"(?:Located at|Premises at)[\s:]+(.+?)(?:\n|$)",
    ],
    # Add more custom patterns as needed
}

# Form field mapping for STEP2.pdf (static form - uses coordinates)
# Coordinates are (x, y, page) where y=0 is bottom of page
# Standard letter size: 612 x 792 points
FORM_FIELD_COORDINATES = {
    # Page 1 - Example coordinates (adjust based on actual form)
    "owner_name": {"x": 100, "y": 700, "page": 0, "font_size": 10},
    "property_address": {"x": 100, "y": 680, "page": 0, "font_size": 10},
    "parcel_number": {"x": 100, "y": 660, "page": 0, "font_size": 10},
    "legal_description": {"x": 100, "y": 640, "page": 0, "font_size": 9, "max_width": 400},
    "county": {"x": 100, "y": 620, "page": 0, "font_size": 10},
    "state": {"x": 200, "y": 620, "page": 0, "font_size": 10},
    
    # Deed information
    "deed_book": {"x": 100, "y": 600, "page": 0, "font_size": 10},
    "deed_page": {"x": 150, "y": 600, "page": 0, "font_size": 10},
    "deed_document_number": {"x": 200, "y": 600, "page": 0, "font_size": 10},
    "deed_recorded_date": {"x": 300, "y": 600, "page": 0, "font_size": 10},
    
    # Tax information
    "tax_year": {"x": 100, "y": 580, "page": 0, "font_size": 10},
    "tax_amount": {"x": 150, "y": 580, "page": 0, "font_size": 10},
    "assessed_value": {"x": 250, "y": 580, "page": 0, "font_size": 10},
    
    # Lot information
    "lot_number": {"x": 100, "y": 560, "page": 0, "font_size": 10},
    "subdivision": {"x": 200, "y": 560, "page": 0, "font_size": 10},
}

# Field mapping - maps extracted field names to coordinate keys
FORM_FIELD_MAPPING = {
    "owner_name": "owner_name",
    "property_address": "property_address",
    "parcel_number": "parcel_number",
    "legal_description": "legal_description",
    "county": "county",
    "state": "state",
    "lot_info": "lot_number",
    "subdivision": "subdivision",
}

# Nested field mapping for deed_info
DEED_INFO_MAPPING = {
    "book": "deed_book",
    "page": "deed_page",
    "document_number": "deed_document_number",
    "recorded_date": "deed_recorded_date",
}

# Nested field mapping for tax_info
TAX_INFO_MAPPING = {
    "year": "tax_year",
    "amount": "tax_amount",
    "assessed_value": "assessed_value",
}

# Output settings
OUTPUT_JSON_INDENT = 2
OUTPUT_ENCODING = "utf-8"
