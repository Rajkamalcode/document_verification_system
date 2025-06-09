import re
import spacy
import re
from pathlib import Path
import os
import logging

logger = logging.getLogger(__name__)

# Define output directory for debug prompts
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'debug_prompts')

try:
    # Optional: For improved name/address/DOB parsing, you can integrate NLP libraries like spaCy
    nlp = spacy.load("en_core_web_sm")
    USE_NLP = True
except:
    USE_NLP = False


def ensure_dir(directory):
    """Ensure directory exists"""
    os.makedirs(directory, exist_ok=True)
def extract_fields(text):
    """Extract fields from KYC document, identifying Indian IDs by number patterns"""
    fields = {}

    # 1. Name extraction (fallback to NLP if no label found)
    name_patterns = [
        r"\b(?:Name|Customer Name|Applicant(?:'s)? Name)\s*[:\-]\s*([A-Za-z ]{2,})",
        r"\bFull Name\s*[:\-]\s*([A-Za-z ]{2,})"
    ]
    for pat in name_patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            fields['name'] = m.group(1).strip()
            break
    else:
        if USE_NLP:
            doc = nlp(text)
            # take first PERSON entity as name
            for ent in doc.ents:
                if ent.label_ == 'PERSON':
                    fields['name'] = ent.text
                    break

    # 2. Address extraction (label or NLP)
    address_patterns = [
        r"\b(?:Address|Residence|Residential Address)\s*[:\-]\s*(.+?)(?=\n\n|$)",
        r"\b(?:Permanent Address|Current Address|Communication Address)\s*[:\-]\s*(.+?)(?=\n\n|$)"
    ]
    for pat in address_patterns:
        m = re.search(pat, text, re.DOTALL | re.IGNORECASE)
        if m:
            fields['address'] = m.group(1).strip()
            break
    else:
        if USE_NLP:
            doc = nlp(text)
            addr_chunks = [ent.text for ent in doc.ents if ent.label_ == 'GPE']
            if addr_chunks:
                fields['address'] = ', '.join(addr_chunks[:2])

    # 3. DOB extraction (label or date parse)
    dob_patterns = [
        r"\b(?:DOB|Date of Birth|Birth Date)\s*[:\-]\s*(\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4})",
        r"\bBorn on\s*[:\-]\s*(\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4})"
    ]
    for pat in dob_patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            fields['date_of_birth'] = m.group(1).strip()
            break
    else:
        if USE_NLP:
            doc = nlp(text)
            for ent in doc.ents:
                if ent.label_ == 'DATE':
                    fields['date_of_birth'] = ent.text
                    break

    # 4. Gender extraction
    gen = re.search(r"\b(?:Gender|Sex)\s*[:\-]\s*(Male|Female|Other)\b", text, re.IGNORECASE)
    if gen:
        fields['gender'] = gen.group(1)

    # 5. Mobile extraction
    mob = re.search(r"\b(?:Mobile|Phone|Contact|Cell) No?\.?\s*[:\-]\s*(\+?[0-9][0-9\- ]{8,14}[0-9])", text, re.IGNORECASE)
    if mob:
        fields['mobile_number'] = mob.group(1)

    # 6. Email extraction
    email = re.search(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", text)
    if email:
        fields['email'] = email.group(1)

    # 7. ID extraction by pattern only
    id_patterns = {
        'PAN': r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
        'AADHAAR': r"\b\d{4}\s*\d{4}\s*\d{4}\b|\b\d{12}\b",
        'PASSPORT': r"\b[A-Z][0-9]{7}\b",
        'VOTER_ID': r"\b[A-Z]{3}[0-9]{7}\b",
        'DL': r"\b[A-Z]{2}[0-9]{2}[A-Za-z0-9]{11}\b"
    }
    for id_name, pat in id_patterns.items():
        m = re.search(pat, text)
        if m:
            fields.setdefault('id_numbers', []).append({
                'type': id_name,
                'number': m.group(0).strip()
            })
    # If multiple found, user can decide which is primary KYC ID
    print(fields)   
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
        
        # Create a filename for the document (for debugging)
        filename = "kyc document.pdf"
        
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
            # Remove "Not Found" values
            if value and value.lower() != "not found":
                cleaned_fields[clean_name] = value
        
        # Merge with regex extraction for better results
        regex_fields = extract_fields(text)
        
        # Combine the results, prioritizing LLM for most fields but keeping regex for critical fields
        final_fields = {**cleaned_fields, **regex_fields}
        
        return final_fields
    
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Error using LLM for field extraction: {str(e)}")
        # Fall back to regex extraction
        return extract_fields(text)


def create_single_doc_extraction_prompt(filename, doc_text_content, doc_plain_tables, required_fields):
    """Create a prompt for LLM to extract Indian ID card details from a document"""
    # List out the crucial Indian ID fields explicitly
    field_names = ", ".join(required_fields.keys())
    prompt = f"""
You are a specialized Data Extractor AI focusing on Indian identity documents (Aadhaar, PAN, Passport, Driving License, Voter ID).
Task: From the given content of '{filename}', extract the following fields EXACTLY as they appear:
- name
- date_of_birth
- gender
- address
- id_numbers: a JSON array where each element is an object with 'type' (one of PAN, AADHAAR, PASSPORT, DL, VOTER_ID) and 'number'

PRINCIPLES:
1. EXTRACT ONLY from the document context below.
2. IF a field is not present, return "Not Found" for that field.
3. For 'id_numbers', include all recognized ID numbers; if none, return an empty array.
4. refer this regex for finding the id numbers         
        'PAN': r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
        'AADHAAR': r"\b\d{4}\s*\d{4}\s*\d{4}\b|\b\d{12}\b",
        'PASSPORT': r"\b[A-Z][0-9]{7}\b",
        'VOTER_ID': r"\b[A-Z]{3}[0-9]{7}\b",
        'DL': r"\b[A-Z]{2}[0-9]{2}[A-Za-z0-9]{11}\b"
--- Document Content Start ({filename}) ---
{doc_text_content}
--- Document Content End ({filename}) ---

Fields to extract: {field_names}

Output: A single JSON object, no additional narrative. Format:
```json
{{
    "name": "LITERAL text or Not Found",
    "date_of_birth": "LITERAL text or Not Found",
    "gender": "LITERAL text or Not Found",
    "address": "LITERAL text or Not Found",
    "id_numbers": "LITERAL text or Not Found"
}}
```"""
    # Save prompt for debugging
    ensure_dir(OUTPUT_DIR)
    safe_stem = "".join(c if c.isalnum() or c in ('_', '-') else '_' for c in Path(filename).stem)
    debug_prompt_path = Path(OUTPUT_DIR) / f"id_card_extraction_prompt_{safe_stem}.txt"
    try:
        with open(debug_prompt_path, "w", encoding="utf-8") as f:
            f.write(prompt)
    except Exception as e:
        logger.warning(f"Could not save prompt: {e}")

    return prompt
