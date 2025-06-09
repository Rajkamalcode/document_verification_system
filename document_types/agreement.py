import re

def extract_fields(text):
    """Extract fields from Agreement document"""
    fields = {}
    
    # Extract parties with improved regex
    parties_patterns = [
        r'(?:BETWEEN|PARTIES|This\s+Agreement\s+is\s+made\s+between)\s*:?\s*(.+?)(?:\n\n|AND|\Z)',
        r'(?:This\s+Agreement\s+is\s+made\s+(?:and\s+)?entered\s+into\s+by\s+and\s+between)\s*:?\s*(.+?)(?:\n\n|AND|\Z)',
        r'(?:THIS\s+AGREEMENT\s+made\s+(?:on|at).*?between)\s*:?\s*(.+?)(?:\n\n|AND|\Z)'
    ]
    
    for pattern in parties_patterns:
        parties_match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if parties_match:
            fields['parties'] = parties_match.group(1).strip()
            break
    
    # Extract agreement date with improved regex
    date_patterns = [
        r'(?:dated|agreement\s+date|date\s+of\s+agreement)\s*:?\s*(\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4})',
        r'(?:This\s+Agreement\s+is\s+made\s+(?:on|at)\s+(?:this)?)\s*(?:the\s+)?(\d{1,2}(?:st|nd|rd|th)?\s+(?:day\s+of\s+)?[A-Za-z]+,?\s+\d{4})',
        r'(?:dated|executed\s+on)\s+(?:this\s+)?(\d{1,2}(?:st|nd|rd|th)?\s+(?:day\s+of\s+)?[A-Za-z]+,?\s+\d{4})'
    ]
    
    for pattern in date_patterns:
        date_match = re.search(pattern, text, re.IGNORECASE)
        if date_match:
            fields['agreement_date'] = date_match.group(1).strip()
            break
    
    # Extract terms with improved regex
    terms_patterns = [
        r'(?:TERMS\s+(?:AND\s+)?CONDITIONS|CONDITIONS\s+(?:AND\s+)?TERMS)\s*:?\s*(.+?)(?:\n\n|\Z)',
        r'(?:NOW\s+THEREFORE\s+THE\s+PARTIES\s+AGREE\s+AS\s+FOLLOWS)\s*:?\s*(.+?)(?:\n\n|\Z)',
        r'(?:The\s+parties\s+hereby\s+agree\s+to\s+the\s+following\s+terms)\s*:?\s*(.+?)(?:\n\n|\Z)'
    ]
    
    for pattern in terms_patterns:
        terms_match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if terms_match:
            fields['terms'] = terms_match.group(1).strip()
            break
    
    # Extract signatures with improved regex
    signatures_patterns = [
        r'(?:SIGNED|SIGNATURE|IN\s+WITNESS\s+WHEREOF)\s*:?\s*(.+?)(?:\n\n|\Z)',
        r'(?:The\s+parties\s+have\s+executed\s+this\s+Agreement\s+as\s+of\s+the\s+date\s+first\s+above\s+written)\s*:?\s*(.+?)(?:\n\n|\Z)',
        r'(?:SIGNED\s+AND\s+DELIVERED\s+by\s+the\s+within\s+named)\s*:?\s*(.+?)(?:\n\n|\Z)'
    ]
    
    for pattern in signatures_patterns:
        signatures_match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if signatures_match:
            fields['signatures'] = signatures_match.group(1).strip()
            break
    
    # Extract agreement type (additional field)
    type_patterns = [
        r'(?:Agreement\s+Type|Type\s+of\s+Agreement)\s*:\s*([A-Za-z\s]+)',
        r'(?:THIS\s+)([A-Za-z\s]+\s+AGREEMENT)',
        r'(?:AGREEMENT\s+FOR\s+)([A-Za-z\s]+)'
    ]
    
    for pattern in type_patterns:
        type_match = re.search(pattern, text, re.IGNORECASE)
        if type_match:
            fields['agreement_type'] = type_match.group(1).strip()
            break
    
    # Extract governing law (additional field)
    law_patterns = [
        r'(?:Governing\s+Law|Applicable\s+Law)\s*:\s*(.+?)(?:\n|\Z)',
        r'(?:This\s+Agreement\s+shall\s+be\s+governed\s+by\s+the\s+laws\s+of)\s*(.+?)(?:\n|\Z)',
        r'(?:The\s+laws\s+of)\s*(.+?)\s*(?:shall\s+govern\s+this\s+Agreement)'
    ]
    
    for pattern in law_patterns:
        law_match = re.search(pattern, text, re.IGNORECASE)
        if law_match:
            fields['governing_law'] = law_match.group(1).strip()
            break
    
    return fields