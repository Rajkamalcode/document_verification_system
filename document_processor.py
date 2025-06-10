import os
os.environ['USE_TF'] = '0'  # Force DocTR to use PyTorch

import re
import time
import pytesseract
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
import pdf2image
from PIL import Image
import pdfplumber
import torch
import config
import importlib
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure pytesseract path
pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_CMD

# Initialize sentence transformer model for semantic matching
import os
from sentence_transformers import SentenceTransformer, util
import torch

# Set environment variables to prevent downloads
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'

# Initialize sentence transformer model for semantic matching with local_files_only
try:
    model_path = r'C:\Users\intern-rajkamal\.cache\torch\hub\sentence-transformers\all-MiniLM-L6-v2'
    model = SentenceTransformer(model_path, local_files_only=True)
    logger.info(f"Successfully loaded model from {model_path}")
    
    # Test the model to make sure it works
    test_embedding = model.encode("This is a test sentence")
    logger.info(f"Model test successful. Embedding shape: {test_embedding.shape}")
except Exception as e:
    logger.error(f"Error loading model: {e}")
    # Fallback to a simple model or disable semantic matching
    model = None

# Initialize DocTR model
doctr_model = ocr_predictor(pretrained=True)

# Create directory for extracted text files
EXTRACTED_TEXT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'extracted_texts')
os.makedirs(EXTRACTED_TEXT_DIR, exist_ok=True)

def extract_text_doctr(pdf_path):
    """Extract text using DocTR"""
    start_time = time.time()
    
    try:
        # Load PDF
        doc = DocumentFile.from_pdf(pdf_path)
        
        # Analyze
        result = doctr_model(doc)
        
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
        
        # Save extracted text to file
        save_extracted_text(pdf_path, doctr_text, "doctr")
        
        return doctr_text, processing_time
    except Exception as e:
        logger.error(f"Error in DocTR OCR: {str(e)}")
        return f"Error extracting text: {str(e)}", 0

def extract_text_pytesseract(pdf_path):
    """Extract text using Pytesseract"""
    start_time = time.time()
    
    try:
        # Convert PDF to images
        pages = pdf2image.convert_from_path(pdf_path)
        
        pytesseract_text = ""
        
        for i, page in enumerate(pages):
            # Extract text from each page
            page_text = pytesseract.image_to_string(page, config='--psm 6')
            pytesseract_text += f"--- Page {i+1} ---\n"
            pytesseract_text += page_text + "\n\n"
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Save extracted text to file
        save_extracted_text(pdf_path, pytesseract_text, "pytesseract")
        
        return pytesseract_text, processing_time
    except Exception as e:
        logger.error(f"Error in Pytesseract OCR: {str(e)}")
        return f"Error extracting text: {str(e)}", 0

def save_extracted_text(pdf_path, text, ocr_engine):
    """Save extracted text to a file"""
    try:
        filename = os.path.basename(pdf_path)
        base_name = os.path.splitext(filename)[0]
        
        # Check if this is a temporary file
        if 'temp' in pdf_path:
            output_file = os.path.join(EXTRACTED_TEXT_DIR, f"temp_{base_name}_{ocr_engine}.txt")
        else:
            output_file = os.path.join(EXTRACTED_TEXT_DIR, f"{base_name}_{ocr_engine}.txt")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)
        
        logger.info(f"Saved extracted text to {output_file}")
    except Exception as e:
        logger.error(f"Error saving extracted text: {str(e)}")

def extract_metadata(pdf_path):
    """Extract metadata from PDF"""
    metadata = {
        "filename": os.path.basename(pdf_path),
        "filesize": f"{os.path.getsize(pdf_path) / 1024:.2f} KB",
        "pages": 0
    }
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            metadata["pages"] = len(pdf.pages)
            if pdf.metadata:
                for key, value in pdf.metadata.items():
                    if value and isinstance(value, str):
                        metadata[key] = value
    except Exception as e:
        logger.error(f"Error extracting metadata: {str(e)}")
    
    return metadata

def process_document(document_path, document_type, expected_fields=None):
    """Process document based on its type and extract relevant fields"""
    if not os.path.exists(document_path):
        return {"error": f"Document not found at {document_path}"}
    
    doc_type_config = config.DOCUMENT_TYPES.get(document_type)
    if not doc_type_config:
        return {"error": f"Unknown document type: {document_type}"}
    
    try:
        # Extract text using the appropriate OCR engine
        if doc_type_config['ocr_engine'] == 'doctr':
            text, processing_time = extract_text_doctr(document_path)
        else:
            text, processing_time = extract_text_pytesseract(document_path)
        
        # Extract metadata
        metadata = extract_metadata(document_path)
        
        # Import the appropriate document type module
        try:
            # Convert document type to lowercase for module name
            module_name = f"document_types.{document_type.lower()}"
            doc_module = importlib.import_module(module_name)
            
            # Extract fields using the module's extract_fields function
            # Pass expected_fields to the extract_fields function
            extracted_fields = doc_module.extract_fields(text, expected_fields)
            logger.info(f"Successfully extracted fields using {module_name} module")
            
            return {
                "document_path": document_path,
                "document_type": document_type,
                "ocr_engine": doc_type_config['ocr_engine'],
                "processing_time": processing_time,
                "metadata": metadata,
                "extracted_text": text,
                "extracted_fields": extracted_fields
            }
            
        except (ImportError, AttributeError) as e:
            logger.error(f"Error importing document type module: {str(e)}")
            return {
                "document_path": document_path,
                "document_type": document_type,
                "error": f"Error importing document type module: {str(e)}",
                "ocr_engine": doc_type_config.get('ocr_engine', 'unknown'),
                "processing_time": processing_time,
                "metadata": metadata,
                "extracted_text": text,
                "extracted_fields": {}
            }
            
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        return {
            "document_path": document_path,
            "document_type": document_type,
            "error": f"Error processing document: {str(e)}",
            "ocr_engine": doc_type_config.get('ocr_engine', 'unknown'),
            "processing_time": 0,
            "metadata": extract_metadata(document_path),
            "extracted_text": "",
            "extracted_fields": {}
        }

def normalize_field_name(field_name):
    """Normalize field name for comparison (lowercase, remove spaces, underscores)"""
    if not field_name:
        return ""
    return field_name.lower().replace(" ", "_").replace("-", "_")

def compare_fields(expected_fields, extracted_fields):
    """Compare expected fields with extracted fields using semantic similarity or exact matching"""
    results = {}
    
    # Normalize field names in extracted fields for easier matching
    normalized_extracted = {}
    for key, value in extracted_fields.items():
        normalized_key = normalize_field_name(key)
        normalized_extracted[normalized_key] = value
    
    for field_name, expected_value in expected_fields.items():
        normalized_field = normalize_field_name(field_name)
        
        # Try to find the field in extracted fields (with normalization)
        extracted_value = None
        matched_key = None
        
        # First try exact match with normalized name
        if normalized_field in normalized_extracted:
            extracted_value = normalized_extracted[normalized_field]
            matched_key = normalized_field
        else:
            # Try to find a partial match
            for ext_key, ext_value in normalized_extracted.items():
                if normalized_field in ext_key or ext_key in normalized_field:
                    extracted_value = ext_value
                    matched_key = ext_key
                    break
        
        if extracted_value:
            # Determine if this field needs exact matching
            # Check if the field is in the exact_match_fields list for this document type
            doc_type = None
            for dt, doc_config in config.DOCUMENT_TYPES.items():
                if field_name in doc_config.get('fields', []):
                    doc_type = dt
                    break
            
            use_exact_match = False
            if doc_type and field_name in config.DOCUMENT_TYPES[doc_type].get('exact_match_fields', []):
                use_exact_match = True
            
            if use_exact_match:
                # Use exact string matching
                match = str(expected_value).lower() == str(extracted_value).lower()
                similarity = 1.0 if match else 0.0
            else:
                # Use semantic similarity if model is available
                if model is not None:
                    try:
                        # Encode texts for semantic comparison
                        expected_embedding = model.encode(str(expected_value), convert_to_tensor=True)
                        extracted_embedding = model.encode(str(extracted_value), convert_to_tensor=True)
                        
                        # Compute similarity
                        similarity = util.pytorch_cos_sim(expected_embedding, extracted_embedding).item()
                    except Exception as e:
                        logger.error(f"Error computing semantic similarity: {str(e)}")
                        # Fallback to simple text comparison
                        similarity = simple_text_similarity(expected_value, extracted_value)
                else:
                    # Use simple text comparison
                    similarity = simple_text_similarity(expected_value, extracted_value)
            
            results[field_name] = {
                "expected": expected_value,
                "extracted": extracted_value,
                "similarity": similarity,
                "match": similarity >= config.SIMILARITY_THRESHOLD if not use_exact_match else (similarity == 1.0),
                "match_method": "exact" if use_exact_match else "semantic",
                "matched_field": matched_key  # Store the actual field name that was matched
            }
        else:
            results[field_name] = {
                "expected": expected_value,
                "extracted": None,
                "similarity": 0,
                "match": False,
                "match_method": "none",
                "matched_field": None
            }
    
    return results

def simple_text_similarity(text1, text2):
    """Calculate simple word overlap similarity between two texts"""
    # Convert both to strings and lowercase for comparison
    text1 = str(text1).lower()
    text2 = str(text2).lower()
    
    # Calculate simple similarity (word overlap)
    words1 = set(text1.split())
    words2 = set(text2.split())
    
    if words1 and words2:
        common_words = words1.intersection(words2)
        all_words = words1.union(words2)
        return len(common_words) / len(all_words)
    else:
        return 0
