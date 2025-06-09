import re
import os
import sys
import json
import time
from pathlib import Path

# Import functions from document_processor.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import document_processor

def extract_fields(text):
    """Extract fields from Sanction Letter document"""
    fields = {}
    
    # Extract loan amount with improved regex
    loan_patterns = [
        r'(?:Loan\s+Amount|Sanctioned\s+Amount|Amount\s+Sanctioned)\s*:\s*(?:Rs\.?|₹)?\s*([0-9,.]+)',
        r'(?:We\s+are\s+pleased\s+to\s+sanction\s+a\s+loan\s+of)\s*(?:Rs\.?|₹)?\s*([0-9,.]+)',
        r'(?:Total\s+Loan\s+Amount|Facility\s+Amount)\s*:\s*(?:Rs\.?|₹)?\s*([0-9,.]+)'
    ]
    
    for pattern in loan_patterns:
        loan_match = re.search(pattern, text, re.IGNORECASE)
        if loan_match:
            fields['loan_amount'] = loan_match.group(1).strip()
            break
    
    # Extract applicant name with improved regex
    name_patterns = [
        r'(?:Applicant|Borrower|Customer|Client)(?:\'s)?\s*(?:Name)?\s*:\s*([A-Za-z\s\.]+)',
        r'(?:Name\s+of\s+(?:the\s+)?Applicant|Borrower(?:\'s)?\s+Name)\s*:\s*([A-Za-z\s\.]+)',
        r'(?:Dear\s+(?:Mr\.|Mrs\.|Ms\.|Dr\.)?)\s*([A-Za-z\s\.]+)'
    ]
    
    for pattern in name_patterns:
        name_match = re.search(pattern, text, re.IGNORECASE)
        if name_match:
            fields['applicant_name'] = name_match.group(1).strip()
            break
    
    # Extract sanction date with improved regex
    date_patterns = [
        r'(?:Sanction\s+Date|Date\s+of\s+Sanction)\s*:\s*(\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4})',
        r'(?:Letter\s+Date|Date\s+of\s+Letter|Date)\s*:\s*(\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4})',
        r'(?:Dated|Issued\s+on)\s*:\s*(\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4})'
    ]
    
    for pattern in date_patterns:
        date_match = re.search(pattern, text, re.IGNORECASE)
        if date_match:
            fields['sanction_date'] = date_match.group(1).strip()
            break
    
    # Extract terms with improved regex
    terms_patterns = [
        r'(?:Terms\s+(?:and\s+)?Conditions|Conditions\s+(?:and\s+)?Terms)\s*:?\s*(.+?)(?:\n\n|\Z)',
        r'(?:The\s+loan\s+is\s+sanctioned\s+on\s+the\s+following\s+terms\s+and\s+conditions)\s*:?\s*(.+?)(?:\n\n|\Z)',
        r'(?:TERMS\s+OF\s+SANCTION|SANCTION\s+TERMS)\s*:?\s*(.+?)(?:\n\n|\Z)'
    ]
    
    for pattern in terms_patterns:
        terms_match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if terms_match:
            fields['terms'] = terms_match.group(1).strip()
            break
    
    # Extract interest rate (additional field)
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
    
    # Extract tenure (additional field)
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
    
    # Extract loan purpose (additional field)
    purpose_patterns = [
        r'(?:Loan\s+Purpose|Purpose\s+of\s+Loan)\s*:\s*(.+?)(?:\n|\Z)',
        r'(?:Purpose|End\s+Use)\s*:\s*(.+?)(?:\n|\Z)',
        r'(?:The\s+loan\s+is\s+being\s+sanctioned\s+for\s+the\s+purpose\s+of)\s*(.+?)(?:\n|\Z)'
    ]
    
    for pattern in purpose_patterns:
        purpose_match = re.search(pattern, text, re.IGNORECASE)
        if purpose_match:
            fields['loan_purpose'] = purpose_match.group(1).strip()
            break
    
    return fields

def extract_fields_with_llm(text, required_fields):
    """Extract fields using LLM if available, otherwise fall back to regex"""
    # This is a placeholder for LLM-based extraction
    # In a real implementation, you would call an LLM API here
    print("LLM-based extraction not implemented, falling back to regex")
    return extract_fields(text)

def compare_with_expected(extracted_fields, expected_fields):
    """Compare extracted fields with expected fields"""
    # Use document_processor's compare_fields function if available
    try:
        return document_processor.compare_fields(expected_fields, extracted_fields)
    except Exception as e:
        print(f"Error using document_processor.compare_fields: {e}")
        
        # Fallback to simple comparison
        results = {}
        
        for field_name, expected_value in expected_fields.items():
            if field_name in extracted_fields:
                extracted_value = extracted_fields[field_name]
                
                # Simple text similarity (word overlap)
                expected_words = set(str(expected_value).lower().split())
                extracted_words = set(str(extracted_value).lower().split())
                
                if expected_words and extracted_words:
                    common_words = expected_words.intersection(extracted_words)
                    all_words = expected_words.union(extracted_words)
                    similarity = len(common_words) / len(all_words)
                else:
                    similarity = 0
                
                match = similarity >= 0.5  # Threshold for match
                
                results[field_name] = {
                    "expected": expected_value,
                    "extracted": extracted_value,
                    "similarity": similarity,
                    "match": match
                }
            else:
                results[field_name] = {
                    "expected": expected_value,
                    "extracted": None,
                    "similarity": 0,
                    "match": False
                }
        
        return results

def save_results(results, output_path):
    """Save results to a JSON file"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {output_path}")

def main():
    """Main function for standalone execution"""
    # Define variables instead of using command-line arguments
    pdf_path = "D:/table ocr/doc/document_verification_system/document_types/sanction_letter.py"  # Path to the PDF file
    ocr_engine = "doctr"  # OCR engine to use (options: 'doctr' or 'pytesseract')
    expected_fields = {  # Expected fields for comparison (None if not used)
        "loan_amount": "500000",
        "applicant_name": "John Doe",
        "sanction_date": "01/01/2023",
        "interest_rate": "8.5%"
    }
    output_path = "sanction_letter_results.json"  # Path to save results
    save_text = True  # Whether to save extracted text to file
    
    # Check if file exists
    if not os.path.exists(pdf_path):
        print(f"Error: File not found: {pdf_path}")
        return 1
    
    # Extract text using selected OCR engine
    try:
        if ocr_engine == 'doctr':
            extracted_text, processing_time = document_processor.extract_text_doctr(pdf_path)
        else:
            extracted_text, processing_time = document_processor.extract_text_pytesseract(pdf_path)
        
        print(f"Text extraction completed in {processing_time:.2f} seconds")
    except Exception as e:
        print(f"Error using document_processor functions: {e}")
        print("Falling back to local OCR functions...")
        
        # Fallback to local OCR functions
        if ocr_engine == 'doctr':
            extracted_text = extract_text_with_doctr(pdf_path)
        else:
            extracted_text = extract_text_with_pytesseract(pdf_path)
    
    if not extracted_text:
        print("Error: Text extraction failed")
        return 1
    
    # Save extracted text if requested
    if save_text:
        text_output = f"{os.path.splitext(pdf_path)[0]}_{ocr_engine}_text.txt"
        with open(text_output, 'w', encoding='utf-8') as f:
            f.write(extracted_text)
        print(f"Extracted text saved to {text_output}")
    
    # Extract fields
    print("Extracting fields from text...")
    extracted_fields = extract_fields(extracted_text)
    
    # Print extracted fields
    print("\nExtracted Fields:")
    for field, value in extracted_fields.items():
        print(f"  {field}: {value}")
    
    # Compare with expected fields if provided
    if expected_fields:
        try:
            print("\nComparing with expected fields...")
            comparison = compare_with_expected(extracted_fields, expected_fields)
            
            # Print comparison results
            print("\nComparison Results:")
            match_count = 0
            for field, result in comparison.items():
                match_status = "✓" if result["match"] else "✗"
                similarity = f"{result['similarity'] * 100:.1f}%"
                print(f"  {field}: {match_status} ({similarity})")
                if result["match"]:
                    match_count += 1
            
            print(f"\nOverall: {match_count}/{len(comparison)} fields matched")
            
            # Save results
            results = {
                "pdf_path": pdf_path,
                "ocr_engine": ocr_engine,
                "extracted_fields": extracted_fields,
                "comparison": comparison,
                "match_count": match_count,
                "total_fields": len(comparison)
            }
            save_results(results, output_path)
            
        except Exception as e:
            print(f"Error comparing with expected fields: {str(e)}")
    else:
        # Save just the extracted fields
        results = {
            "pdf_path": pdf_path,
            "ocr_engine": ocr_engine,
            "extracted_fields": extracted_fields
        }
        save_results(results, output_path)
    
    return 0

# These functions are only used as fallbacks if document_processor functions fail
def extract_text_with_doctr(pdf_path):
    """Extract text from PDF using DocTR"""
    try:
        # Import DocTR only when needed
        import os
        os.environ['USE_TF'] = '0'  # Force DocTR to use PyTorch
        from doctr.io import DocumentFile
        from doctr.models import ocr_predictor
        import time
        
        print(f"Extracting text from {pdf_path} using DocTR...")
        start_time = time.time()
        
        # Initialize DocTR model
        model = ocr_predictor(pretrained=True)
        
        # Load PDF
        doc = DocumentFile.from_pdf(pdf_path)
        
        # Analyze
        result = model(doc)
        
        # Extract text
        doctr_text = ""
        for page in result.pages:
            for block in page.blocks:
                for line in block.lines:
                    for word in line.words:
                        doctr_text += word.value + " "
                    doctr_text += "\n"
                doctr_text += "\n"
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"DocTR extraction completed in {processing_time:.2f} seconds")
        return doctr_text
    except Exception as e:
        print(f"Error in DocTR OCR: {str(e)}")
        return None

def extract_text_with_pytesseract(pdf_path):
    """Extract text from PDF using Pytesseract"""
    try:
        import pytesseract
        import pdf2image
        import time
        
        print(f"Extracting text from {pdf_path} using Pytesseract...")
        start_time = time.time()
        
        # Convert PDF to images
        pages = pdf2image.convert_from_path(pdf_path)
        
        pytesseract_text = ""
        
        for i, page in enumerate(pages):
            print(f"Processing page {i+1}/{len(pages)}...")
            # Extract text from each page
            page_text = pytesseract.image_to_string(page, config='--psm 6')
            pytesseract_text += f"--- Page {i+1} ---\n"
            pytesseract_text += page_text + "\n\n"
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"Pytesseract extraction completed in {processing_time:.2f} seconds")
        return pytesseract_text
    except Exception as e:
        print(f"Error in Pytesseract OCR: {str(e)}")
        return None

def find_pdf_files():
    """Find PDF files in the documents folder"""
    # Try to find the documents folder
    possible_paths = [
        "documents",
        "../documents",
        "../../documents",
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "documents")
    ]
    
    pdf_files = []
    
    for path in possible_paths:
        if os.path.exists(path) and os.path.isdir(path):
            print(f"Searching for PDFs in {path}")
            for file in os.listdir(path):
                if file.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(path, file))
    
    return pdf_files

if __name__ == "__main__":
    # Try to find a valid PDF file
    pdf_files = find_pdf_files()
    
    if not pdf_files:
        print("No PDF files found in the documents folder.")
        print("Please specify a valid PDF file path in the main() function.")
        sys.exit(1)
    
    # Use the first PDF file found
    pdf_path = pdf_files[0]
    print(f"Using PDF file: {pdf_path}")
    
    # Set default values for testing
    ocr_engine = "doctr"
    expected_fields = {
        "loan_amount": "500000",
        "applicant_name": "John Doe",
        "sanction_date": "01/01/2023",
        "interest_rate": "8.5%"
    }
    
    # Update the pdf_path in the main function
    # This is a bit hacky, but it works for testing
    main.__defaults__ = (pdf_path, ocr_engine, expected_fields, "sanction_letter_results.json", True)
    
    # Run the main function
    try:
        exit_code = main()
        print(f"Script completed with exit code: {exit_code}")
    except Exception as e:
        print(f"Error running main function: {e}")
        import traceback
        traceback.print_exc()
