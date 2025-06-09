import re

def extract_fields(text):
    """Extract fields from Annexure document"""
    fields = {}
    
    # Extract reference number with improved regex
    ref_patterns = [
        r'(?:Reference|Ref\.?|Annexure)\s*(?:Number|No\.?)?\s*:?\s*([A-Z0-9-/]+)',
        r'(?:Annexure\s*(?:Number|No\.?)?)\s*:?\s*([A-Z0-9-/]+)',
        r'(?:Document\s+Reference|Reference\s+ID)\s*:?\s*([A-Z0-9-/]+)'
    ]
    
    for pattern in ref_patterns:
        ref_match = re.search(pattern, text, re.IGNORECASE)
        if ref_match:
            fields['reference_number'] = ref_match.group(1).strip()
            break
    
    # Extract related document with improved regex
    related_patterns = [
        r'(?:Related\s+to|In\s+reference\s+to|With\s+reference\s+to)\s*:?\s*(.+?)(?:\n|\Z)',
        r'(?:Related\s+Document|Parent\s+Document|Main\s+Document)\s*:?\s*(.+?)(?:\n|\Z)',
        r'(?:This\s+annexure\s+is\s+related\s+to)\s*:?\s*(.+?)(?:\n|\Z)'
    ]
    
    for pattern in related_patterns:
        related_match = re.search(pattern, text, re.IGNORECASE)
        if related_match:
            fields['related_document'] = related_match.group(1).strip()
            break
    
    # Extract details with improved regex
    details_patterns = [
        r'(?:Details|Content|Information|Description)\s*:?\s*(.+?)(?:\n\n|\Z)',
        r'(?:Annexure\s+Details|Content\s+of\s+Annexure)\s*:?\s*(.+?)(?:\n\n|\Z)',
        r'(?:The\s+following\s+(?:details|information)\s+is\s+provided)\s*:?\s*(.+?)(?:\n\n|\Z)'
    ]
    
    for pattern in details_patterns:
        details_match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if details_match:
            fields['details'] = details_match.group(1).strip()
            break
    
    # Extract attachments with improved regex
    attachments_patterns = [
        r'(?:Attachments|Enclosed|Attached|Enclosures)\s*:?\s*(.+?)(?:\n\n|\Z)',
        r'(?:List\s+of\s+Attachments|Attached\s+Documents)\s*:?\s*(.+?)(?:\n\n|\Z)',
        r'(?:The\s+following\s+documents\s+are\s+attached)\s*:?\s*(.+?)(?:\n\n|\Z)'
    ]
    
    for pattern in attachments_patterns:
        attachments_match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if attachments_match:
            fields['attachments'] = attachments_match.group(1).strip()
            break
    
    # Extract date (additional field)
    date_patterns = [
        r'(?:Date|Dated)\s*:?\s*(\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4})',
        r'(?:Annexure\s+Date|Date\s+of\s+Annexure)\s*:?\s*(\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4})',
        r'(?:Dated\s+this)\s*(?:the\s+)?(\d{1,2}(?:st|nd|rd|th)?\s+(?:day\s+of\s+)?[A-Za-z]+,?\s+\d{4})'
    ]
    
    for pattern in date_patterns:
        date_match = re.search(pattern, text, re.IGNORECASE)
        if date_match:
            fields['date'] = date_match.group(1).strip()
            break
    
    # Extract prepared by (additional field)
    prepared_patterns = [
        r'(?:Prepared\s+By|Created\s+By|Author)\s*:?\s*([A-Za-z\s\.]+)',
        r'(?:Name\s+of\s+(?:the\s+)?Preparer|Preparer(?:\'s)?\s+Name)\s*:?\s*([A-Za-z\s\.]+)',
        r'(?:Signature\s+of)\s*:?\s*([A-Za-z\s\.]+)'
    ]
    
    for pattern in prepared_patterns:
        prepared_match = re.search(pattern, text, re.IGNORECASE)
        if prepared_match:
            fields['prepared_by'] = prepared_match.group(1).strip()
            break
    
    return fields
