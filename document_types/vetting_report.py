import re

def extract_fields(text):
    """Extract fields from Vetting Report document"""
    fields = {}
    
    # Extract document status with improved regex
    status_patterns = [
        r'(?:Document\s+Status|Status\s+of\s+Document|Status)\s*:?\s*(.+?)(?:\n|\Z)',
        r'(?:Status\s+of\s+Verification|Verification\s+Status)\s*:?\s*(.+?)(?:\n|\Z)',
        r'(?:The\s+document\s+is)\s*(.+?)(?:\n|\Z)'
    ]
    
    for pattern in status_patterns:
        status_match = re.search(pattern, text, re.IGNORECASE)
        if status_match:
            fields['document_status'] = status_match.group(1).strip()
            break
    
    # Extract verification details with improved regex
    verification_patterns = [
        r'(?:Verification\s+Details|Details\s+of\s+Verification)\s*:?\s*(.+?)(?:\n\n|\Z)',
        r'(?:Verification\s+Process|Process\s+of\s+Verification)\s*:?\s*(.+?)(?:\n\n|\Z)',
        r'(?:The\s+following\s+aspects\s+have\s+been\s+verified)\s*:?\s*(.+?)(?:\n\n|\Z)'
    ]
    
    for pattern in verification_patterns:
        verification_match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if verification_match:
            fields['verification_details'] = verification_match.group(1).strip()
            break
    
    # Extract comments with improved regex
    comments_patterns = [
        r'(?:Comments|Remarks|Observations|Notes)\s*:?\s*(.+?)(?:\n\n|\Z)',
        r'(?:Additional\s+Comments|Further\s+Remarks)\s*:?\s*(.+?)(?:\n\n|\Z)',
        r'(?:The\s+following\s+(?:issues|observations)\s+were\s+noted)\s*:?\s*(.+?)(?:\n\n|\Z)'
    ]
    
    for pattern in comments_patterns:
        comments_match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if comments_match:
            fields['comments'] = comments_match.group(1).strip()
            break
    
    # Extract verified by with improved regex
    verified_patterns = [
        r'(?:Verified\s+By|Vetted\s+By|Verification\s+Officer)\s*:?\s*([A-Za-z\s\.]+)',
        r'(?:Name\s+of\s+(?:the\s+)?Verifier|Verifier(?:\'s)?\s+Name)\s*:?\s*([A-Za-z\s\.]+)',
        r'(?:Signature\s+of)\s*:?\s*([A-Za-z\s\.]+)'
    ]
    
    for pattern in verified_patterns:
        verified_match = re.search(pattern, text, re.IGNORECASE)
        if verified_match:
            fields['verified_by'] = verified_match.group(1).strip()
            break
    
    # Extract verification date (additional field)
    verification_date_patterns = [
        r'(?:Verification\s+Date|Date\s+of\s+Verification)\s*:?\s*(\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4})',
        r'(?:Verified\s+on|Vetted\s+on)\s*:?\s*(\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4})',
        r'(?:Date)\s*:?\s*(\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4})'
    ]
    
    for pattern in verification_date_patterns:
        verification_date_match = re.search(pattern, text, re.IGNORECASE)
        if verification_date_match:
            fields['verification_date'] = verification_date_match.group(1).strip()
            break
    
    # Extract document type (additional field)
    document_type_patterns = [
        r'(?:Document\s+Type|Type\s+of\s+Document)\s*:?\s*([A-Za-z\s]+)',
        r'(?:Nature\s+of\s+Document|Document\s+Category)\s*:?\s*([A-Za-z\s]+)'
    ]
    
    for pattern in document_type_patterns:
        document_type_match = re.search(pattern, text, re.IGNORECASE)
        if document_type_match:
            fields['document_type'] = document_type_match.group(1).strip()
            break
    
    return fields