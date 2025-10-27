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
        r"(?:Owner|Grantee|Grantor|Name|Owner Name)[\s:]+([A-Z][a-zA-Z\s\-']{2,})",
        r"(?:Owner:|Name:)[\s]*([A-Z][a-zA-Z\s\-']{2,})",
    ],
    "property_address": [
        r"(?:Property Address|Address|Property Location|Site Address)[\s:]+(.+?)(?:\n|$)",
        r"(?:Located at|Premises at|Situs:)[\s:]+(.+?)(?:\n|$)",
    ],
    "parcel_number": [
        r"(?:Parcel Number|Parcel No\.?|APN)[\s:]+([\w\-]+)",
    ],
    "legal_description": [
        r"(?:Legal Description|Description)[\s:]+(.+?)(?:\n|$)",
    ],
    "county": [
        r"County[\s:]+([A-Za-z\s]+)",
    ],
    "state": [
        r"State[\s:]+([A-Za-z]{2,})",
    ],
    "deed_book": [
        r"Deed Book[\s:]+([\w\-]+)",
    ],
    "deed_page": [
        r"Deed Page[\s:]+([\w\-]+)",
    ],
    "deed_document_number": [
        r"Document Number[\s:]+([\w\-]+)",
    ],
    "deed_recorded_date": [
        r"Recorded Date[\s:]+([\d\-/]+)",
    ],
    "tax_year": [
        r"Tax Year[\s:]+([\d]{4})",
    ],
    "tax_amount": [
        r"Tax Amount[\s:]+([\d,.]+)",
    ],
    "assessed_value": [
        r"Assessed Value[\s:]+([\d,.]+)",
    ],
    "lot_number": [
        r"Lot Number[\s:]+([\w\-]+)",
    ],
    "subdivision": [
        r"Subdivision[\s:]+([A-Za-z0-9\s\-]+)",
    ],
}

# Form field mapping for STEP2.pdf (static form - uses coordinates)
# Coordinates are (x, y, page) where y=0 is bottom of page
# Standard letter size: 612 x 792 points
FORM_FIELD_COORDINATES = {
    # Calibrated coordinates for STEP2.pdf based on ExamplePDFout
    "owner_name": {"x": 120, "y": 715, "page": 0, "font_size": 11},
    "property_address": {"x": 120, "y": 695, "page": 0, "font_size": 11},
    "parcel_number": {"x": 120, "y": 675, "page": 0, "font_size": 11},
    "legal_description": {"x": 120, "y": 655, "page": 0, "font_size": 10, "max_width": 420},
    "county": {"x": 120, "y": 635, "page": 0, "font_size": 11},
    "state": {"x": 220, "y": 635, "page": 0, "font_size": 11},
    # Deed information
    "deed_book": {"x": 120, "y": 615, "page": 0, "font_size": 11},
    "deed_page": {"x": 170, "y": 615, "page": 0, "font_size": 11},
    "deed_document_number": {"x": 220, "y": 615, "page": 0, "font_size": 11},
    "deed_recorded_date": {"x": 320, "y": 615, "page": 0, "font_size": 11},
    # Tax information
    "tax_year": {"x": 120, "y": 595, "page": 0, "font_size": 11},
    "tax_amount": {"x": 170, "y": 595, "page": 0, "font_size": 11},
    "assessed_value": {"x": 270, "y": 595, "page": 0, "font_size": 11},
    # Lot information
    "lot_number": {"x": 120, "y": 575, "page": 0, "font_size": 11},
    "subdivision": {"x": 220, "y": 575, "page": 0, "font_size": 11},
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
    # Add any new fields here as needed
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
    "tax_year": "tax_year",
    "amount": "tax_amount",
    "assessed_value": "assessed_value",
}

# Image positions for STEP2.pdf template
# Define where extracted images should be placed on the form
IMAGE_POSITIONS = {
    # Calibrated image positions for STEP2.pdf based on ExamplePDFout
    "photo_main": {
        "page": 0,
        "x": 420,
        "y": 120,
        "width": 140,
        "height": 190,
        "source_index": 0,
    },
    "id_document": {
        "page": 0,
        "x": 420,
        "y": 330,
        "width": 140,
        "height": 90,
        "source_index": 1,
    },
    "signature": {
        "page": 1,
        "x": 120,
        "y": 670,
        "width": 190,
        "height": 45,
        "source_index": 2,
    },
    # Add more image positions as needed
}

# Output settings
OUTPUT_JSON_INDENT = 2
OUTPUT_ENCODING = "utf-8"
