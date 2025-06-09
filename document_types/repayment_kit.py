import re

def extract_fields(text):
    """Extract fields from Repayment Kit document"""
    fields = {}
    
    # Extract loan amount with improved regex
    loan_patterns = [
        r'(?:Loan\s+Amount|Principal|Sanctioned\s+Amount)\s*:\s*(?:Rs\.?|₹)?\s*([0-9,.]+)',
        r'(?:Amount\s+of\s+Loan|Loan\s+Facility)\s*:\s*(?:Rs\.?|₹)?\s*([0-9,.]+)',
        r'(?:Total\s+Loan\s+Amount)\s*:\s*(?:Rs\.?|₹)?\s*([0-9,.]+)'
    ]
    
    for pattern in loan_patterns:
        loan_match = re.search(pattern, text, re.IGNORECASE)
        if loan_match:
            fields['loan_amount'] = loan_match.group(1).strip()
            break
    
    # Extract interest rate with improved regex
    interest_patterns = [
        r'(?:Interest\s+Rate|ROI|Rate\s+of\s+Interest)\s*:\s*([0-9.]+)%',
        r'(?:Interest\s+@|Interest\s+at\s+the\s+rate\s+of)\s*([0-9.]+)%',
        r'(?:Interest\s+charged\s+at)\s*([0-9.]+)%'
    ]
    
    for pattern in interest_patterns:
        interest_match = re.search(pattern, text, re.IGNORECASE)
        if interest_match:
            fields['interest_rate'] = interest_match.group(1).strip() + "%"
            break
    
    # Extract tenure with improved regex
    tenure_patterns = [
        r'(?:Tenure|Term|Period|Duration)\s*:\s*(\d+)\s*(?:months|years)',
        r'(?:Loan\s+(?:Tenure|Term|Period|Duration))\s*:\s*(\d+)\s*(?:months|years)',
        r'(?:for\s+a\s+period\s+of)\s*(\d+)\s*(?:months|years)'
    ]
    
    for pattern in tenure_patterns:
        tenure_match = re.search(pattern, text, re.IGNORECASE)
        if tenure_match:
            fields['tenure'] = tenure_match.group(1).strip()
            break
    
    # Extract EMI amount with improved regex
    emi_patterns = [
        r'(?:EMI|Monthly\s+(?:Payment|Installment)|Equated\s+Monthly\s+Installment)\s*:\s*(?:Rs\.?|₹)?\s*([0-9,.]+)',
        r'(?:EMI\s+Amount|Monthly\s+Repayment)\s*:\s*(?:Rs\.?|₹)?\s*([0-9,.]+)',
        r'(?:Your\s+EMI\s+is)\s*(?:Rs\.?|₹)?\s*([0-9,.]+)'
    ]
    
    for pattern in emi_patterns:
        emi_match = re.search(pattern, text, re.IGNORECASE)
        if emi_match:
            fields['emi_amount'] = emi_match.group(1).strip()
            break
    
    # Extract customer name (additional field)
    name_patterns = [
        r'(?:Customer\s+Name|Name\s+of\s+(?:the\s+)?Customer|Borrower(?:\'s)?\s+Name)\s*:\s*([A-Za-z\s\.]+)',
        r'(?:Name|Borrower)\s*:\s*([A-Za-z\s\.]+)'
    ]
    
    for pattern in name_patterns:
        name_match = re.search(pattern, text, re.IGNORECASE)
        if name_match:
            fields['customer_name'] = name_match.group(1).strip()
            break
    
    # Extract loan account number (additional field)
    account_patterns = [
        r'(?:Loan\s+Account\s+(?:Number|No)|Account\s+(?:Number|No))\s*:\s*([A-Za-z0-9-]+)',
        r'(?:Loan\s+(?:Number|No|ID))\s*:\s*([A-Za-z0-9-]+)'
    ]
    
    for pattern in account_patterns:
        account_match = re.search(pattern, text, re.IGNORECASE)
        if account_match:
            fields['loan_account_number'] = account_match.group(1).strip()
            break
    
    # Extract first EMI date (additional field)
    first_emi_patterns = [
        r'(?:First\s+EMI\s+Date|Date\s+of\s+First\s+EMI)\s*:\s*(\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4})',
        r'(?:First\s+Installment\s+Date)\s*:\s*(\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4})'
    ]
    
    for pattern in first_emi_patterns:
        first_emi_match = re.search(pattern, text, re.IGNORECASE)
        if first_emi_match:
            fields['first_emi_date'] = first_emi_match.group(1).strip()
            break
    
    # Extract last EMI date (additional field)
    last_emi_patterns = [
        r'(?:Last\s+EMI\s+Date|Date\s+of\s+Last\s+EMI)\s*:\s*(\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4})',
        r'(?:Last\s+Installment\s+Date)\s*:\s*(\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4})'
    ]
    
    for pattern in last_emi_patterns:
        last_emi_match = re.search(pattern, text, re.IGNORECASE)
        if last_emi_match:
            fields['last_emi_date'] = last_emi_match.group(1).strip()
            break
    
    return fields
