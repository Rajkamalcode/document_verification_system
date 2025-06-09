import os

# Application settings
DEBUG = True
HOST = '0.0.0.0'
PORT = 5432

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCUMENTS_FOLDER = os.path.join(BASE_DIR, 'documents')

# Tesseract path
TESSERACT_CMD = r'C:\Users\intern-rajkamal\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

# Extraction method settings
DEFAULT_EXTRACTION_METHOD = "both"  # Options: "regex", "llm", "both"
LLM_MODEL = "gemma3:12b-it-qat"  # Default LLM model to use

# Similarity threshold for field comparison
SIMILARITY_THRESHOLD = 0.7

# Document types configuration
DOCUMENT_TYPES = {
    "MODT": {
        "description": "Memorandum of Deposit of Title Deeds",
        "ocr_engine": "doctr",
        "extraction_method": "llm",  # Use both regex and LLM
        "fields": ["name", "application_number", "date", "property_details", "loan_amount"],
        "exact_match_fields": ["application_number", "date"]  # Fields that require exact matching
    },
    "REPAYMENT_KIT": {
        "description": "Loan Repayment Kit",
        "ocr_engine": "doctr",
        "extraction_method": "regex",
        "fields": ["loan_amount", "interest_rate", "tenure", "emi_amount", "customer_name", "loan_account_number"],
        "exact_match_fields": ["loan_account_number", "emi_amount"]
    },
    "AGREEMENT": {
        "description": "Legal Agreement",
        "ocr_engine": "doctr",
        "extraction_method": "regex",
        "fields": ["parties", "agreement_date", "terms", "signatures", "agreement_type", "governing_law"],
        "exact_match_fields": ["agreement_date", "agreement_type"]
    },
    "KYC": {
        "description": "Know Your Customer Document",
        "ocr_engine": "doctr",
        "extraction_method": "regex",
        "fields": ["name", "address", "id_number", "date_of_birth", "gender", "mobile_number", "email"],
        "exact_match_fields": ["id_number", "mobile_number", "email"]
    },
    "SANCTION_LETTER": {
        "description": "Loan Sanction Letter",
        "ocr_engine": "doctr",
        "extraction_method": "regex",
        "fields": ["loan_amount", "applicant_name", "sanction_date", "terms", "interest_rate", "tenure", "loan_purpose"],
        "exact_match_fields": ["sanction_date", "loan_amount"]
    },
    "LEGAL_REPORT": {
        "description": "Legal Report on Property",
        "ocr_engine": "doctr",
        "extraction_method": "regex",
        "fields": ["property_details", "legal_opinion", "encumbrances", "recommendations", "title_verification", "document_verification"],
        "exact_match_fields": []
    },
    "VETTING_REPORT": {
        "description": "Document Vetting Report",
        "ocr_engine": "doctr",
        "extraction_method": "regex",
        "fields": ["document_status", "verification_details", "comments", "verified_by", "verification_date", "document_type"],
        "exact_match_fields": ["verification_date", "document_type"]
    },
    "ANNEXURE": {
        "description": "Annexure to Main Document",
        "ocr_engine": "doctr",
        "extraction_method": "regex",
        "fields": ["reference_number", "related_document", "details", "attachments", "date", "prepared_by"],
        "exact_match_fields": ["reference_number", "date"]
    }
}
