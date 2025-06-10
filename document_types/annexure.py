import re
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

# Define output directory for debug prompts
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'debug_prompts')

def ensure_dir(directory):
    """Ensure directory exists"""
    os.makedirs(directory, exist_ok=True)

def extract_fields_regex(text):
    """Extract fields from Annexure document using regex patterns"""
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
        r'(?:Related\s+Document|Parent\s+Document|Main\s+Document)\s*:?\s*(.+?)(?:\n|\Z)'
    ]
    
    for pattern in related_patterns:
        related_match = re.search(pattern, text, re.IGNORECASE)
        if related_match:
            fields['related_document'] = related_match.group(1).strip()
            break
    
    # Extract details with improved regex
    details_patterns = [
        r'(?:Details|Description|Content)\s*:?\s*(.+?)(?:\n\n|\n[A-Z\s]+:|\Z)',
        r'(?:Annexure\s+Details|Document\s+Details)\s*:?\s*(.+?)(?:\n\n|\n[A-Z\s]+:|\Z)'
    ]
    
    for pattern in details_patterns:
        details_match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if details_match:
            fields['details'] = details_match.group(1).strip()
            break
    
    # Extract attachments with improved regex
    attachments_patterns = [
        r'(?:Attachments|Enclosures|Enclosed)\s*:?\s*(.+?)(?:\n\n|\n[A-Z\s]+:|\Z)',
        r'(?:List\s+of\s+Attachments|Attached\s+Documents)\s*:?\s*(.+?)(?:\n\n|\n[A-Z\s]+:|\Z)'
    ]
    
    for pattern in attachments_patterns:
        attachments_match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if attachments_match:
            fields['attachments'] = attachments_match.group(1).strip()
            break
    
    # Extract date with improved regex
    date_patterns = [
        r'(?:Date|Dated)\s*:?\s*(\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4})',
        r'(?:Date\s+of\s+(?:Annexure|Document|Preparation))\s*:?\s*(\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4})'
    ]
    
    for pattern in date_patterns:
        date_match = re.search(pattern, text, re.IGNORECASE)
        if date_match:
            fields['date'] = date_match.group(1).strip()
            break
    
    # Extract prepared by with improved regex
    prepared_patterns = [
        r'(?:Prepared\s+by|Author|Created\s+by)\s*:?\s*([A-Za-z\s\.]+)',
        r'(?:Signature|Signed\s+by)\s*:?\s*([A-Za-z\s\.]+)'
    ]
    
    for pattern in prepared_patterns:
        prepared_match = re.search(pattern, text, re.IGNORECASE)
        if prepared_match:
            fields['prepared_by'] = prepared_match.group(1).strip()
            break
    
    return fields

def extract_fields_llm(text, required_fields):
    """Extract fields from Annexure document using LLM"""
    try:
        from utils import ollama
        import logging
        logger = logging.getLogger(__name__)
        
        # Create a filename for the document (for debugging)
        filename = "annexure_document.pdf"
        
        # Extract tables (if any)
        doc_plain_tables = []  # We don't have tables in this example
        
        # Create the prompt for LLM
        prompt = create_single_doc_extraction_prompt(filename, text, doc_plain_tables, required_fields)
        
        # Call the LLM
        logger.info("Calling Ollama API for Annexure field extraction")
        response = ollama.call_ollama_api(
            prompt=prompt,
            ollama_url=None,  # Use default URL
            model_name="gemma3:12b-it-qat",  # Or whatever model you're using
            step_name="Extract Annexure fields"
        )
        logger.info(f"LLM response: {response}")
        
        # Check if response is None (API call failed)
        if response is None:
            logger.warning("Ollama API call returned None. Falling back to regex extraction.")
            return {}
        
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
            
            # Remove "Not Found" values
            if value and isinstance(value, str) and value.lower() != "not found":
                cleaned_fields[clean_name] = value
            elif not isinstance(value, str):  # Handle non-string values like arrays
                cleaned_fields[clean_name] = value
        
        logger.info(f"LLM extracted fields: {cleaned_fields}")
        return cleaned_fields
    
    except Exception as e:
        logger.error(f"Error using LLM for field extraction: {str(e)}")
        return {}

def extract_fields(text, expected_fields=None):
    """Main extraction function that combines regex and LLM approaches"""
    logger.info("Extracting fields from Annexure document")
    
    # First, extract fields using regex
    regex_fields = extract_fields_regex(text)
    logger.info(f"Regex extracted fields: {regex_fields}")
    
    # Then try to extract using LLM if expected fields are provided
    llm_fields = {}
    try:
        if expected_fields:
            llm_fields = extract_fields_llm(text, expected_fields)
            logger.info(f"LLM extracted fields: {llm_fields}")
    except Exception as e:
        logger.error(f"Error in LLM extraction: {str(e)}")
    
    # Combine results, prioritizing LLM for non-empty values
    final_fields = regex_fields.copy()
    for field, value in llm_fields.items():
        if value:  # Only update if LLM found a value
            final_fields[field] = value
    
    logger.info(f"Final extracted fields: {final_fields}")
    return final_fields

def create_single_doc_extraction_prompt(filename, doc_text_content, doc_plain_tables, required_fields):
    """Create a prompt for LLM to extract fields from a document"""
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
- Reference Number: Look for "Reference:", "Ref:", "Annexure Number:" patterns
- Related Document: Look for "Related to:", "In reference to:", "Parent Document:" patterns
- Details: Extract from "Details:", "Description:", "Content:" sections
- Attachments: Look for "Attachments:", "Enclosures:", "List of Attachments:" patterns
- Date: Look for "Date:", "Dated:", "Date of Annexure:" patterns
- Prepared By: Look for "Prepared by:", "Author:", "Created by:", "Signature:" patterns

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
