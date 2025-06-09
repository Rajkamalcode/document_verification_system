import re

def extract_fields(text):
    """Extract fields from Legal Report document"""
    fields = {}
    
    # Extract property details with improved regex
    property_patterns = [
        r'(?:Property\s+Details|Subject\s+Property|Property\s+Description)\s*:?\s*(.+?)(?:\n\n|\Z)',
        r'(?:Details\s+of\s+(?:the\s+)?Property|Property\s+under\s+Reference)\s*:?\s*(.+?)(?:\n\n|\Z)',
        r'(?:SCHEDULE\s+OF\s+PROPERTY|PROPERTY\s+SCHEDULE)\s*:?\s*(.+?)(?:\n\n|\Z)'
    ]
    
    for pattern in property_patterns:
        property_match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if property_match:
            fields['property_details'] = property_match.group(1).strip()
            break
    
    # Extract legal opinion with improved regex
    opinion_patterns = [
        r'(?:Legal\s+Opinion|Opinion|Conclusion)\s*:?\s*(.+?)(?:\n\n|\Z)',
        r'(?:Opinion\s+of\s+(?:the\s+)?Advocate|Lawyer(?:\'s)?\s+Opinion)\s*:?\s*(.+?)(?:\n\n|\Z)',
        r'(?:Based\s+on\s+(?:the\s+)?(?:above|foregoing)(?:\s+facts)?(?:\s+and\s+circumstances)?[,.]?\s+(?:I|we)\s+are\s+of\s+the\s+opinion\s+that)\s*(.+?)(?:\n\n|\Z)'
    ]
    
    for pattern in opinion_patterns:
        opinion_match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if opinion_match:
            fields['legal_opinion'] = opinion_match.group(1).strip()
            break
    
    # Extract encumbrances with improved regex
    encumbrance_patterns = [
        r'(?:Encumbrances|Charges|Liens|Mortgages)\s*:?\s*(.+?)(?:\n\n|\Z)',
        r'(?:Details\s+of\s+Encumbrances|Encumbrance\s+Details)\s*:?\s*(.+?)(?:\n\n|\Z)',
        r'(?:The\s+property\s+is\s+(?:free\s+from|subject\s+to)\s+encumbrances\s+(?:as\s+follows)?)\s*:?\s*(.+?)(?:\n\n|\Z)'
    ]
    
    for pattern in encumbrance_patterns:
        encumbrance_match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if encumbrance_match:
            fields['encumbrances'] = encumbrance_match.group(1).strip()
            break
    
    # Extract recommendations with improved regex
    recommendations_patterns = [
        r'(?:Recommendations|Suggestions|Advice)\s*:?\s*(.+?)(?:\n\n|\Z)',
        r'(?:We|I)\s+(?:recommend|suggest|advise)\s*:?\s*(.+?)(?:\n\n|\Z)',
        r'(?:Recommended\s+Course\s+of\s+Action)\s*:?\s*(.+?)(?:\n\n|\Z)'
    ]
    
    for pattern in recommendations_patterns:
        recommendations_match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if recommendations_match:
            fields['recommendations'] = recommendations_match.group(1).strip()
            break
    
    # Extract title verification (additional field)
    title_patterns = [
        r'(?:Title\s+Verification|Verification\s+of\s+Title)\s*:?\s*(.+?)(?:\n\n|\Z)',
        r'(?:Title\s+of\s+the\s+Property|Property\s+Title)\s*:?\s*(.+?)(?:\n\n|\Z)',
        r'(?:Title\s+Investigation|Investigation\s+of\s+Title)\s*:?\s*(.+?)(?:\n\n|\Z)'
    ]
    
    for pattern in title_patterns:
        title_match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if title_match:
            fields['title_verification'] = title_match.group(1).strip()
            break
    
    # Extract document verification (additional field)
    document_patterns = [
        r'(?:Document\s+Verification|Verification\s+of\s+Documents)\s*:?\s*(.+?)(?:\n\n|\Z)',
        r'(?:Documents\s+Verified|List\s+of\s+Documents\s+Verified)\s*:?\s*(.+?)(?:\n\n|\Z)',
        r'(?:The\s+following\s+documents\s+have\s+been\s+verified)\s*:?\s*(.+?)(?:\n\n|\Z)'
    ]
    
    for pattern in document_patterns:
        document_match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if document_match:
            fields['document_verification'] = document_match.group(1).strip()
            break
    
    return fields