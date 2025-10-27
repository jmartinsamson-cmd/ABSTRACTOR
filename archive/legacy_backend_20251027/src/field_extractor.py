"""
Field Extractor - Pattern matching and field identification
"""
import re
from typing import Dict, Any, Optional, List
from datetime import datetime


class FieldExtractor:
    """Extract structured fields from PDF text using pattern matching"""
    
    def __init__(self, text: str):
        self.text = text
        self.fields = {}
        
    def extract_all_fields(self) -> Dict[str, Any]:
        """Extract all recognized fields from the document"""
        self.fields = {
            "owner_name": self.extract_owner_name(),
            "property_address": self.extract_property_address(),
            "parcel_number": self.extract_parcel_number(),
            "legal_description": self.extract_legal_description(),
            "deed_info": self.extract_deed_info(),
            "tax_info": self.extract_tax_info(),
            "lot_info": self.extract_lot_info(),
            "subdivision": self.extract_subdivision(),
            "county": self.extract_county(),
            "state": self.extract_state(),
            "additional_fields": self.extract_additional_fields()
        }
        return self.fields
    
    def extract_owner_name(self) -> Optional[str]:
        """Extract owner/grantor/grantee name"""
        patterns = [
            r"(?:Owner|Grantee|Grantor)[\s:]+([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)",
            r"(?:Name|Owner Name)[\s:]+([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)",
            r"^([A-Z][a-z]+\s+[A-Z][a-z]+)$"  # Simple name pattern
        ]
        return self._extract_with_patterns(patterns)
    
    def extract_property_address(self) -> Optional[str]:
        """Extract property address"""
        patterns = [
            r"(?:Property Address|Address|Property Location)[\s:]+(.+?)(?:\n|$)",
            r"(?:Located at|Premises at)[\s:]+(.+?)(?:\n|$)",
            r"\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd)[,\s]+[A-Z][a-z]+[,\s]+[A-Z]{2}\s+\d{5}"
        ]
        return self._extract_with_patterns(patterns)
    
    def extract_parcel_number(self) -> Optional[str]:
        """Extract parcel/PIN/APN number"""
        patterns = [
            r"(?:Parcel|PIN|APN|Parcel Number|Parcel ID)[\s:#]+([A-Z0-9\-]+)",
            r"(?:Tax ID|Tax Parcel)[\s:#]+([A-Z0-9\-]+)",
            r"\b\d{2,3}-\d{2,3}-\d{2,4}-\d{2,4}\b"  # Common parcel format
        ]
        return self._extract_with_patterns(patterns)
    
    def extract_legal_description(self) -> Optional[str]:
        """Extract legal description of property"""
        patterns = [
            r"(?:Legal Description|Legal)[\s:]+(.+?)(?=\n\n|\n[A-Z][a-z]+:)",
            r"(?:Description|Described as follows)[\s:]+(.+?)(?=\n\n|\n[A-Z][a-z]+:)",
            r"Lot\s+\d+.*?Block\s+\d+.*?(?:Subdivision|Addition).*?(?=\n\n|\n[A-Z])"
        ]
        result = self._extract_with_patterns(patterns, multiline=True)
        if result:
            # Clean up the legal description
            result = re.sub(r'\s+', ' ', result).strip()
        return result
    
    def extract_deed_info(self) -> Dict[str, Optional[str]]:
        """Extract deed book, page, volume, etc."""
        deed_info = {
            "book": None,
            "page": None,
            "volume": None,
            "document_number": None,
            "recorded_date": None
        }
        
        # Book and Page
        book_match = re.search(r"(?:Book|Deed Book)[\s:#]+(\d+)", self.text, re.IGNORECASE)
        if book_match:
            deed_info["book"] = book_match.group(1)
        
        page_match = re.search(r"(?:Page|Pg)[\s:#]+(\d+)", self.text, re.IGNORECASE)
        if page_match:
            deed_info["page"] = page_match.group(1)
        
        # Volume
        volume_match = re.search(r"(?:Volume|Vol)[\s:#]+(\d+)", self.text, re.IGNORECASE)
        if volume_match:
            deed_info["volume"] = volume_match.group(1)
        
        # Document Number
        doc_match = re.search(r"(?:Document|Doc|Instrument)[\s#:]+(\d+)", self.text, re.IGNORECASE)
        if doc_match:
            deed_info["document_number"] = doc_match.group(1)
        
        # Recorded Date
        date_patterns = [
            r"(?:Recorded|Filed|Date Recorded)[\s:]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            r"(?:Recorded|Filed|Date Recorded)[\s:]+([A-Za-z]+\s+\d{1,2},\s+\d{4})"
        ]
        for pattern in date_patterns:
            date_match = re.search(pattern, self.text, re.IGNORECASE)
            if date_match:
                deed_info["recorded_date"] = date_match.group(1)
                break
        
        return deed_info
    
    def extract_tax_info(self) -> Dict[str, Optional[str]]:
        """Extract tax-related information"""
        tax_info = {
            "tax_year": None,
            "tax_amount": None,
            "assessed_value": None,
            "tax_id": None
        }
        
        # Tax year
        year_match = re.search(r"(?:Tax Year|Year)[\s:]+(\d{4})", self.text, re.IGNORECASE)
        if year_match:
            tax_info["tax_year"] = year_match.group(1)
        
        # Tax amount
        amount_patterns = [
            r"(?:Tax Amount|Taxes|Annual Tax)[\s:]+\$?([\d,]+\.?\d*)",
            r"(?:Total Tax|Tax Due)[\s:]+\$?([\d,]+\.?\d*)"
        ]
        for pattern in amount_patterns:
            amount_match = re.search(pattern, self.text, re.IGNORECASE)
            if amount_match:
                tax_info["tax_amount"] = amount_match.group(1)
                break
        
        # Assessed value
        value_match = re.search(r"(?:Assessed Value|Assessment)[\s:]+\$?([\d,]+\.?\d*)", self.text, re.IGNORECASE)
        if value_match:
            tax_info["assessed_value"] = value_match.group(1)
        
        return tax_info
    
    def extract_lot_info(self) -> Optional[str]:
        """Extract lot number"""
        patterns = [
            r"(?:Lot|Lot Number|Lot No)[\s.:#]+(\d+[A-Z]?)",
            r"\bLot\s+(\d+[A-Z]?)\b"
        ]
        return self._extract_with_patterns(patterns)
    
    def extract_subdivision(self) -> Optional[str]:
        """Extract subdivision name"""
        patterns = [
            r"(?:Subdivision|Addition|Plat)[\s:]+([A-Za-z0-9\s]+?)(?:\n|,|$)",
            r"([A-Za-z\s]+(?:Subdivision|Addition|Estates|Heights))"
        ]
        return self._extract_with_patterns(patterns)
    
    def extract_county(self) -> Optional[str]:
        """Extract county name"""
        patterns = [
            r"(?:County|County of)[\s:]+([A-Za-z\s]+?)(?:\n|,|$)",
            r"([A-Za-z]+)\s+County"
        ]
        return self._extract_with_patterns(patterns)
    
    def extract_state(self) -> Optional[str]:
        """Extract state"""
        patterns = [
            r"(?:State|State of)[\s:]+([A-Za-z\s]+?)(?:\n|$)",
            r"\b([A-Z]{2})\s+\d{5}\b",  # State code from ZIP
            r",\s+([A-Z]{2})(?:\s|$)"
        ]
        return self._extract_with_patterns(patterns)
    
    def extract_additional_fields(self) -> Dict[str, str]:
        """Extract any additional labeled fields not covered above"""
        additional = {}
        
        # Generic key-value pattern
        pattern = r"^([A-Z][A-Za-z\s]+?):\s*(.+?)$"
        matches = re.finditer(pattern, self.text, re.MULTILINE)
        
        for match in matches:
            key = match.group(1).strip()
            value = match.group(2).strip()
            
            # Skip if already extracted in other fields
            skip_keys = ["owner", "address", "parcel", "legal", "deed", "tax", 
                        "lot", "subdivision", "county", "state"]
            if not any(skip_word in key.lower() for skip_word in skip_keys):
                additional[key] = value
        
        return additional
    
    def _extract_with_patterns(self, patterns: List[str], multiline: bool = False) -> Optional[str]:
        """Helper method to try multiple regex patterns"""
        flags = re.IGNORECASE | re.MULTILINE if multiline else re.IGNORECASE | re.DOTALL
        
        for pattern in patterns:
            match = re.search(pattern, self.text, flags)
            if match:
                # Return the first capturing group or the whole match
                return match.group(1).strip() if match.groups() else match.group(0).strip()
        return None
    
    def get_confidence_score(self) -> float:
        """
        Calculate a confidence score based on how many fields were extracted
        Returns a value between 0 and 1
        """
        total_fields = 0
        filled_fields = 0
        
        for key, value in self.fields.items():
            if key == "additional_fields":
                continue
            
            total_fields += 1
            
            if isinstance(value, dict):
                # For nested dicts like deed_info
                sub_total = len(value)
                sub_filled = sum(1 for v in value.values() if v is not None)
                filled_fields += sub_filled / sub_total if sub_total > 0 else 0
            elif value is not None:
                filled_fields += 1
        
        return filled_fields / total_fields if total_fields > 0 else 0.0
