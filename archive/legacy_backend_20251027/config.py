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
        r"(?:Owner|Grantee|Grantor|Name|Owner Name|Primary Ownership|Percent of Ownership|Ownership Began|Ownership Ended)[\s:]*([A-Z][a-zA-Z\s\-']{2,})",
        r"(?:Owner:|Name:)[\s]*([A-Z][a-zA-Z\s\-']{2,})",
        r"^([A-Z][a-zA-Z\s\-']{2,})$",  # single-line name
        r"([A-Z][a-zA-Z\s\-']{2,})",  # fallback: any capitalized word sequence
    ],
    "property_address": [
        r"(?:Property Address|Address|Property Location|Site Address)[\s:]+(.+?)(?:\n|$)",
        r"(?:Located at|Premises at|Situs:)[\s:]+(.+?)(?:\n|$)",
        r"(\d{1,5}\s+[A-Z][a-zA-Z\s]+)",  # fallback: number + street name
    ],
    "parcel_number": [
        r"(?:Parcel Number|Parcel No\.?|APN)[\s:]+([\w\-]+)",
        r"([A-Z0-9]{5,})",  # fallback: any long alphanumeric sequence
    ],
    "legal_description": [
        r"(?:Legal Description|Description|LOTS|Block|Plat|Section|Township|Range|Tract)[\s:]+(.+?)(?:\n|$)",
        r"LOTS[\s:]*([A-Za-z0-9\-\s\(\)]+)",
    ],
    "COB": [
        r"COB[\s:]*([0-9]+); Page: ([0-9]+); Filed: ([0-9/]+) ([0-9:AMP]+)\s*\[([a-zA-Z0-9: ]+)\]",
    ],
    "MOB": [
        r"MOB[\s:]*([0-9]+); Page: ([0-9]+); Filed: ([0-9/]+) ([0-9:AMP]+)\s*\[([a-zA-Z0-9: ]+)\]",
    ],
    "millage_rate": [
        r"Millage Rate[\s:]*([0-9.]+)",
    ],
    "homestead_pct": [
        r"Homestead Pct[\s:]*([0-9.]+)",
    ],
    "homestead_code": [
        r"Homestead Code[\s:]*([A-Z])",
    ],
    "homestead_credit": [
        r"Homestead Credit[\s:]*([0-9.,]+)\s*Status: *\((AC|IN)\) ([A-Za-z]+)",
    ],
    "note": [
        r"Note[\s:]*([A-Za-z0-9.,;:'\"\s\-]+)",
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
    # Owner(s)
    "owner_name": {"x": 120, "y": 715, "page": 0, "font_size": 11},
    # Property address
    "property_address": {"x": 120, "y": 695, "page": 0, "font_size": 11},
    # Parcel number
    "parcel_number": {"x": 120, "y": 675, "page": 0, "font_size": 11},
    # Legal description
    "legal_description": {"x": 120, "y": 655, "page": 0, "font_size": 10, "max_width": 420},
    # Deed info
    "deed_book": {"x": 120, "y": 635, "page": 0, "font_size": 11},
    "deed_page": {"x": 170, "y": 635, "page": 0, "font_size": 11},
    "deed_recorded_date": {"x": 220, "y": 635, "page": 0, "font_size": 11},
    "deed_type": {"x": 320, "y": 635, "page": 0, "font_size": 11},
    "deed_parties": {"x": 120, "y": 615, "page": 0, "font_size": 11, "max_width": 420},
    # Tax info
    "tax_year": {"x": 120, "y": 595, "page": 0, "font_size": 11},
    "assessed_value": {"x": 170, "y": 595, "page": 0, "font_size": 11},
    "tax_amount": {"x": 270, "y": 595, "page": 0, "font_size": 11},
    "homestead": {"x": 370, "y": 595, "page": 0, "font_size": 11},
    "millage": {"x": 470, "y": 595, "page": 0, "font_size": 11},
    # Subdivision/block/lot
    "subdivision": {"x": 120, "y": 575, "page": 0, "font_size": 11},
    "block": {"x": 220, "y": 575, "page": 0, "font_size": 11},
    "lot_number": {"x": 320, "y": 575, "page": 0, "font_size": 11},
    # Supporting images (positions for each type)
    "signature_img": {"x": 120, "y": 500, "page": 0, "width": 120, "height": 40, "source_index": 0},
    "plat_img": {"x": 260, "y": 500, "page": 0, "width": 180, "height": 120, "source_index": 1},
    "stamp_img": {"x": 460, "y": 500, "page": 0, "width": 80, "height": 40, "source_index": 2},
    "seal_img": {"x": 560, "y": 500, "page": 0, "width": 80, "height": 40, "source_index": 3},
    "attached_page_img": {"x": 120, "y": 400, "page": 1, "width": 400, "height": 600, "source_index": 4},
}

# Field mapping - maps extracted field names to coordinate keys
FORM_FIELD_MAPPING = {
    # Owner(s)
    "owner_name": "owner_name",
    # Property address
    "property_address": "property_address",
    # Parcel number
    "parcel_number": "parcel_number",
    # Legal description
    "legal_description": "legal_description",
    # Deed info
    "deed_book": "deed_book",
    "deed_page": "deed_page",
    "deed_recorded_date": "deed_recorded_date",
    "deed_type": "deed_type",
    "deed_parties": "deed_parties",
    # Tax info
    "tax_year": "tax_year",
    "assessed_value": "assessed_value",
    "tax_amount": "tax_amount",
    "homestead": "homestead",
    "millage": "millage",
    # Subdivision/block/lot
    "subdivision": "subdivision",
    "block": "block",
    "lot_info": "lot_number",
    # Images
    "signature_img": "signature_img",
    "plat_img": "plat_img",
    "stamp_img": "stamp_img",
    "seal_img": "seal_img",
    "attached_page_img": "attached_page_img",
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
    # Signatures
    "signature_img": {
        "page": 0,
        "x": 120,
        "y": 500,
        "width": 120,
        "height": 40,
        "source_index": 0,
    },
    # Plats
    "plat_img": {
        "page": 0,
        "x": 260,
        "y": 500,
        "width": 180,
        "height": 120,
        "source_index": 1,
    },
    # Stamps
    "stamp_img": {
        "page": 0,
        "x": 460,
        "y": 500,
        "width": 80,
        "height": 40,
        "source_index": 2,
    },
    # Seals
    "seal_img": {
        "page": 0,
        "x": 560,
        "y": 500,
        "width": 80,
        "height": 40,
        "source_index": 3,
    },
    # Attached legal pages
    "attached_page_img": {
        "page": 1,
        "x": 120,
        "y": 400,
        "width": 400,
        "height": 600,
        "source_index": 4,
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
