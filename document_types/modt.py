import re
from pathlib import Path
import os
import logging

logger = logging.getLogger(__name__)

# Define output directory for debug prompts
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'debug_prompts')

def ensure_dir(directory):
    """Ensure directory exists"""
    os.makedirs(directory, exist_ok=True)

def extract_fields(text):
    """Extract fields from MODT (Memorandum of Deposit of Title Deeds) document"""
    fields = {}
    
    # Extract name with improved regex
    # Look for patterns like "Name: John Doe", "Borrower: John Doe", "Borrower's Name: John Doe"
    name_patterns = [
        r'(?:Name|Borrower(?:\'s)?(?:\s+Name)?)\s*:\s*([A-Za-z\s\.]+)',
        r'(?:Name|Borrower)(?:\s+of)?\s+(?:the)?\s+(?:Applicant|Customer|Borrower)\s*:\s*([A-Za-z\s\.]+)'
    ]
    
    for pattern in name_patterns:
        name_match = re.search(pattern, text, re.IGNORECASE)
        if name_match:
            fields['name'] = name_match.group(1).strip()
            break
    
    # Extract application number with improved regex
    # Look for patterns like "Application No: ABC12345", "App #: ABC12345", "Application Number: ABC12345"
    app_patterns = [
        r'(?:Application\s+(?:No|Number)|App\s+#)\s*:\s*([A-Za-z0-9-]+)',
        r'(?:Application|Loan)\s+(?:ID|Reference)\s*(?:Number|No)?\s*:\s*([A-Za-z0-9-]+)'
    ]
    
    for pattern in app_patterns:
        app_match = re.search(pattern, text, re.IGNORECASE)
        if app_match:
            fields['application_number'] = app_match.group(1).strip()
            break
    
    # Extract date with improved regex
    # Look for patterns like "Date: DD/MM/YYYY", "Dated: DD-MM-YYYY", "Date of Agreement: DD/MM/YYYY"
    date_patterns = [
        r'(?:Date|Dated)\s*:\s*(\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4})',
        r'(?:Date\s+of\s+(?:Agreement|Execution|MODT))\s*:\s*(\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4})',
        r'(?:This\s+(?:agreement|document)\s+is\s+dated)\s+(?:the\s+)?(\d{1,2}(?:st|nd|rd|th)?\s+(?:day\s+of\s+)?[A-Za-z]+,?\s+\d{4})'
    ]
    
    for pattern in date_patterns:
        date_match = re.search(pattern, text, re.IGNORECASE)
        if date_match:
            fields['date'] = date_match.group(1).strip()
            break
    
    # Extract property details with improved regex
    # First try to extract the entire PROPERTY DETAILS section
    property_section_patterns = [
        r'PROPERTY\s+DETAILS\s*(?:\n|:)(.*?)(?:\n\n|\n[A-Z\s]+:|$)',
        r'(?:SCHEDULE\s+OF\s+PROPERTY|PROPERTY\s+SCHEDULE)\s*(?:\n|:)(.*?)(?:\n\n|\n[A-Z\s]+:|$)'
    ]
    
    for pattern in property_section_patterns:
        property_section_match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if property_section_match:
            # Extract the entire property details section
            property_section = property_section_match.group(1).strip()
            fields['property_details'] = property_section
            break
    
    # If we couldn't extract the entire section, try to extract just the property address
    if 'property_details' not in fields:
        property_address_patterns = [
            r'(?:Property\s+Address|Address\s+of\s+(?:the\s+)?Property)\s*:\s*(.+?)(?:\n|$)',
            r'(?:Property|Asset)\s+(?:Details|Description)\s*:\s*(.+?)(?:\n|$)',
            r'(?:Property|Asset)\s+(?:located\s+at|situated\s+at)\s*:\s*(.+?)(?:\n|$)'
        ]
        
        for pattern in property_address_patterns:
            property_address_match = re.search(pattern, text, re.IGNORECASE)
            if property_address_match:
                fields['property_details'] = property_address_match.group(1).strip()
                break
    
    # Extract loan amount (additional field that might be present)
    loan_patterns = [
        r'(?:Loan\s+Amount|Facility\s+Amount)\s*:\s*(?:Rs\.?|₹)?\s*([0-9,.]+)',
        r'(?:Amount\s+of\s+Loan|Loan\s+Facility)\s*:\s*(?:Rs\.?|₹)?\s*([0-9,.]+)'
    ]
    
    for pattern in loan_patterns:
        loan_match = re.search(pattern, text, re.IGNORECASE)
        if loan_match:
            fields['loan_amount'] = loan_match.group(1).strip()
            break
    
    return fields

def extract_fields_with_llm(text, required_fields):
    """Extract fields from MODT document using LLM
    
    Args:
        text: Extracted text from document
        required_fields: Dictionary of fields to extract (from API payload)
    """
    try:
        from utils import ollama
        import logging
        logger = logging.getLogger(__name__)
        
        # Check if 'value' is in required_fields and map it to 'loan_amount'
        if 'value' in required_fields:
            required_fields['loan_amount'] = required_fields.pop('value')
        
        # Create a filename for the document (for debugging)
        filename = "modt_document.pdf"
        
        # Extract tables (if any)
        doc_plain_tables = []  # We don't have tables in this example
        
        # Create the prompt for LLM
        prompt = create_single_doc_extraction_prompt(filename, text, doc_plain_tables, required_fields)
        
        # Call the LLM
        logger.info("Calling Ollama API for MODT field extraction")
        response = ollama.call_ollama_api(
            prompt=prompt,
            ollama_url=None,  # Use default URL
            model_name="gemma3:12b-it-qat",  # Or whatever model you're using
            step_name="Extract MODT fields"
        )
        print("THE LLM", response)
        # Check if response is None (API call failed)
        if response is None:
            logger.warning("Ollama API call returned None. Falling back to regex extraction.")
            return extract_fields(text)
        
        # Parse the JSON response
        import json
        import re
        
        # Try to extract JSON from the response
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # If no JSON code block, try to find JSON object directly
            json_match = re.search(r'({.*})', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = response
        
        try:
            extracted_fields = json.loads(json_str)
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON from LLM response. Trying field-by-field extraction.")
            # If JSON parsing fails, try to extract field by field
            extracted_fields = {}
            for field_name in required_fields.keys():
                field_pattern = rf'{field_name}["\']?\s*:\s*["\']?(.*?)["\']?(?:,|\n|}})'
                field_match = re.search(field_pattern, response, re.IGNORECASE | re.DOTALL)
                if field_match:
                    extracted_fields[field_name] = field_match.group(1).strip().strip('"\'')
        
        # Clean up the extracted fields
        cleaned_fields = {}
        for field_name, value in extracted_fields.items():
            # Convert field name to lowercase and remove spaces
            clean_name = field_name.lower().replace(' ', '_')
            
            # Handle the "value" field specifically - map it to "loan_amount"
            if clean_name == "value":
                clean_name = "loan_amount"
                
            # Remove "Not Found" values
            if value and isinstance(value, str) and value.lower() != "not found":
                cleaned_fields[clean_name] = value
            elif not isinstance(value, str):  # Handle non-string values like arrays
                cleaned_fields[clean_name] = value
        
        logger.info(f"LLM extracted fields: {cleaned_fields}")
        return cleaned_fields
    
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Error using LLM for field extraction: {str(e)}")
        # Fall back to regex extraction
        return extract_fields(text)

def create_single_doc_extraction_prompt(filename, doc_text_content, doc_plain_tables, required_fields):
    """Create a prompt for LLM to extract fields from a document
    
    Args:
        filename: Name of the document
        doc_text_content: Extracted text from document
        doc_plain_tables: List of tables extracted from document
        required_fields: Dictionary of fields to extract
    """
    # Get the field names as a comma-separated list
    field_names = ", ".join(required_fields.keys())
    
    prompt = f"""You are a Data Extractor AI. Task: Extract info from '{filename}' provided below.
PRINCIPLES for '{filename}':
1. EXTRACT AS-IS.
2. SOURCE FROM THIS DOCUMENT ONLY.
Document Content for '{filename}':
--- Start Content: {filename} ---
## Text Content (English):
{doc_text_content}
## Extracted Tables (Plain Text):
"""
    if doc_plain_tables:
        for table_str_with_header in doc_plain_tables: 
            prompt += f"```text\n{table_str_with_header}\n```\n\n"
    else: 
        prompt += "[No relevant tables provided]\n"
    
    prompt += f"--- End Content: {filename} ---\n\n"
    prompt += f"""Instructions for Extraction from '{filename}' (above ONLY):
For EACH field, find info WITHIN '{filename}' and extract LITERALLY. If not found, use "Not Found".
Fields to extract: {field_names}

Output: Single JSON object.
```json
{{
"""
    
    # Add expected fields to the prompt
    for field_name, expected_value in required_fields.items():
        prompt += f'    "{field_name}": "LITERAL text from \'{filename}\' OR Not Found",\n'
    
    # Remove the last comma and close the JSON
    prompt = prompt.rstrip(',\n') + "\n}\n```\n"
    
    # Add detailed extraction logic
    prompt += f"""Detailed Extraction Logic for '{filename}':
- Name: Look for "Name:", "Borrower:", "Borrower's Name:" patterns
- Application Number: Look for "Application No:", "App #:", "Application Number:" patterns
- Date: Look for "Date:", "Dated:", "Date of Agreement:" patterns
- Property Details: Extract from "PROPERTY DETAILS" section, including address, type, and area
- Loan Amount: Look for "Loan Amount:", "Facility Amount:" patterns

Output MUST be a single, well-formed JSON object for '{filename}'.
"""
    
    # Save the prompt for debugging
    ensure_dir(OUTPUT_DIR)
    safe_stem = "".join(c if c.isalnum() or c in ('_', '-') else '_' for c in Path(filename).stem)
    debug_prompt_path = Path(OUTPUT_DIR) / f"single_doc_extraction_prompt_{safe_stem}.txt"
    try:
        with open(debug_prompt_path, "w", encoding="utf-8") as f: 
            f.write(prompt)
    except Exception as e: 
        print(f"Warning: Could not save single doc extraction prompt for {filename}: {e}")
    
    return prompt
