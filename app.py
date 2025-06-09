from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import json
import logging
import traceback
import document_processor
import config
from werkzeug.utils import secure_filename  # Add this import

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/process', methods=['POST'])
def process_documents():
    try:
        payload = request.json
        if not payload:
            logger.warning("API request received with no payload")
            return jsonify({"error": "No payload provided"}), 400
        
        logger.info(f"Processing {len(payload)} documents")
        results = []
        
        for doc_info in payload:
            doc_type = doc_info.get('type')
            doc_location = doc_info.get('location')
            expected_fields = doc_info.get('fields', {})
            extraction_method = doc_info.get('extraction_method', config.DEFAULT_EXTRACTION_METHOD)
            
            if not doc_type or not doc_location:
                logger.warning(f"Missing document type or location: {doc_info}")
                results.append({
                    "error": "Missing document type or location",
                    "document": doc_info
                })
                continue
            
            # Extract just the filename if a full path is provided
            doc_filename = os.path.basename(doc_location)
            # Construct full path to document
            doc_path = os.path.join(config.DOCUMENTS_FOLDER, doc_filename)
            logger.info(f"Processing document: {doc_path} of type {doc_type} with method {extraction_method}")
            
            # Override extraction method if specified in the request
            if extraction_method and doc_type in config.DOCUMENT_TYPES:
                config.DOCUMENT_TYPES[doc_type]['extraction_method'] = extraction_method
            
            # Process document with expected fields
            processing_result = document_processor.process_document(doc_path, doc_type, expected_fields)
            
            # Check for processing errors
            if "error" in processing_result:
                logger.error(f"Error processing document: {processing_result['error']}")
                results.append({
                    "document_type": doc_type,
                    "document_path": doc_filename,  # Return just the filename
                    "error": processing_result['error']
                })
                continue
            
            # Compare expected fields with extracted fields
            comparison_result = document_processor.compare_fields(expected_fields, processing_result['extracted_fields'])
            
            # Log field extraction results
            match_count = sum(1 for field in comparison_result.values() if field.get('match', False))
            total_fields = len(comparison_result)
            logger.info(f"Field extraction results: {match_count}/{total_fields} fields matched")
            
            results.append({
                "document_type": doc_type,
                "document_path": doc_filename,  # Return just the filename
                "expected_fields": expected_fields,
                "extracted_fields": processing_result['extracted_fields'],
                "comparison": comparison_result,
                "metadata": processing_result['metadata'],
                "ocr_engine": processing_result.get('ocr_engine'),
                "extraction_method": processing_result.get('extraction_method', extraction_method),
                "processing_time": processing_result.get('processing_time')
            })
        
        logger.info(f"Successfully processed {len(results)} documents")
        return jsonify(results)
    
    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"Error in process_documents: {str(e)}\n{error_details}")
        return jsonify({"error": str(e), "details": error_details}), 500

@app.route('/api/document-types')
def get_document_types():
    try:
        logger.info("Retrieving document types")
        return jsonify(config.DOCUMENT_TYPES)
    except Exception as e:
        logger.error(f"Error retrieving document types: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/documents/<path:filename>')
def serve_document(filename):
    try:
        logger.info(f"Serving document: {filename}")
        return send_from_directory(config.DOCUMENTS_FOLDER, filename)
    except Exception as e:
        logger.error(f"Error serving document {filename}: {str(e)}")
        return jsonify({"error": f"Error serving document: {str(e)}"}), 500

@app.route('/api/preview/<path:filename>')
def preview_document(filename):
    try:
        # Extract just the filename if a full path is provided
        filename = os.path.basename(filename)
        file_path = os.path.join(config.DOCUMENTS_FOLDER, filename)
        logger.info(f"Previewing document: {file_path}")
        
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}")
            return jsonify({"error": "File not found"}), 404
        
        metadata = document_processor.extract_metadata(file_path)
        return jsonify({"metadata": metadata})
    except Exception as e:
        logger.error(f"Error previewing document {filename}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/extracted-text/<path:filename>')
def get_extracted_text(filename):
    """Get the extracted text for a document"""
    try:
        # Extract just the filename if a full path is provided
        filename = os.path.basename(filename)
        logger.info(f"Retrieving extracted text for: {filename}")
        base_name = os.path.splitext(filename)[0]
        
        # Check for both OCR engine outputs
        doctr_file = os.path.join(document_processor.EXTRACTED_TEXT_DIR, f"{base_name}_doctr.txt")
        pytesseract_file = os.path.join(document_processor.EXTRACTED_TEXT_DIR, f"{base_name}_pytesseract.txt")
        
        result = {}
        
        if os.path.exists(doctr_file):
            logger.info(f"Found DocTR text file: {doctr_file}")
            with open(doctr_file, 'r', encoding='utf-8') as f:
                result['doctr'] = f.read()
        
        if os.path.exists(pytesseract_file):
            logger.info(f"Found Pytesseract text file: {pytesseract_file}")
            with open(pytesseract_file, 'r', encoding='utf-8') as f:
                result['pytesseract'] = f.read()
        
        if not result:
            logger.warning(f"No extracted text found for: {filename}")
            return jsonify({"error": "No extracted text found for this document"}), 404
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error retrieving extracted text for {filename}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/extract-now/<path:filename>/<string:doc_type>')
def extract_now(filename, doc_type):
    """Extract text and fields from a document on demand"""
    try:
        # Extract just the filename if a full path is provided
        filename = os.path.basename(filename)
        logger.info(f"On-demand extraction for {filename} as {doc_type}")
        file_path = os.path.join(config.DOCUMENTS_FOLDER, filename)
        
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}")
            return jsonify({"error": "File not found"}), 404
        
        if doc_type not in config.DOCUMENT_TYPES:
            logger.warning(f"Invalid document type: {doc_type}")
            return jsonify({"error": "Invalid document type"}), 400
        
        # Get expected fields from query parameters if available
        expected_fields = {}
        for key, value in request.args.items():
            if key.startswith('field_'):
                field_name = key[6:]  # Remove 'field_' prefix
                expected_fields[field_name] = value
        
        # Process document with expected fields
        processing_result = document_processor.process_document(file_path, doc_type, expected_fields)
        
        return jsonify({
            "document_type": doc_type,
            "document_path": filename,  # Return just the filename
            "extracted_fields": processing_result['extracted_fields'],
            "metadata": processing_result['metadata'],
            "ocr_engine": processing_result.get('ocr_engine'),
            "processing_time": processing_result.get('processing_time')
        })
    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"Error in extract_now: {str(e)}\n{error_details}")
        return jsonify({"error": str(e), "details": error_details}), 500

@app.route('/api/document-modules')
def get_document_modules():
    """Get a list of available document type modules"""
    try:
        logger.info("Retrieving available document modules")
        document_types_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'document_types')
        modules = []
        
        for file in os.listdir(document_types_dir):
            if file.endswith('.py') and file != '__init__.py':
                module_name = os.path.splitext(file)[0].upper()
                modules.append(module_name)
        
        return jsonify({"available_modules": modules})
    except Exception as e:
        logger.error(f"Error retrieving document modules: {str(e)}")
        return jsonify({"error": str(e)}), 500
@app.route('/test-document', methods=['GET'])
def test_document_page():
    """Render the test document page"""
    return render_template('test_document.html')

@app.route('/api/test-document', methods=['POST'])
def test_document():
    """Process a single document upload with specified fields"""
    try:
        # Check if file was uploaded
        if 'document' not in request.files:
            return jsonify({"error": "No document uploaded"}), 400
        
        file = request.files['document']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Get document type and extraction method
        doc_type = request.form.get('document_type')
        extraction_method = request.form.get('extraction_method', config.DEFAULT_EXTRACTION_METHOD).lower()
        
        if not doc_type:
            return jsonify({"error": "Document type is required"}), 400
        
        logger.info(f"Processing document with type {doc_type} and extraction method {extraction_method}")
        
        # Get expected fields from form
        expected_fields = {}
        for key, value in request.form.items():
            if key.startswith('field_') and value:
                field_name = key[6:]  # Remove 'field_' prefix
                expected_fields[field_name] = value
        
        # Save the uploaded file to a temporary location
        temp_dir = os.path.join(config.DOCUMENTS_FOLDER, 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Create a safe filename
        filename = secure_filename(file.filename)
        file_path = os.path.join(temp_dir, filename)
        file.save(file_path)
        
        # Create a temporary config for this document processing
        if doc_type in config.DOCUMENT_TYPES:
            # Make a deep copy of the config to avoid modifying the global config
            import copy
            temp_config = copy.deepcopy(config.DOCUMENT_TYPES[doc_type])
            temp_config['extraction_method'] = extraction_method
            
            # Temporarily override the config
            original_config = config.DOCUMENT_TYPES[doc_type]
            config.DOCUMENT_TYPES[doc_type] = temp_config
            
            logger.info(f"Temporarily overriding extraction method for {doc_type} to {extraction_method}")
            
            try:
                # Process the document with the temporary config
                processing_result = document_processor.process_document(file_path, doc_type, expected_fields)
            finally:
                # Restore the original config
                config.DOCUMENT_TYPES[doc_type] = original_config
        else:
            # Process the document with default settings
            processing_result = document_processor.process_document(file_path, doc_type, expected_fields)
        
        # Compare expected fields with extracted fields if provided
        comparison_result = {}
        if expected_fields:
            comparison_result = document_processor.compare_fields(expected_fields, processing_result['extracted_fields'])
        
        # Return the results
        return jsonify({
            "document_type": doc_type,
            "document_path": filename,
            "expected_fields": expected_fields,
            "extracted_fields": processing_result['extracted_fields'],
            "comparison": comparison_result,
            "metadata": processing_result['metadata'],
            "ocr_engine": processing_result.get('ocr_engine'),
            "extraction_method": extraction_method,
            "processing_time": processing_result.get('processing_time')
        })
    
    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"Error in test_document: {str(e)}\n{error_details}")
        return jsonify({"error": str(e), "details": error_details}), 500

if __name__ == '__main__':
    # Ensure documents folder exists
    os.makedirs(config.DOCUMENTS_FOLDER, exist_ok=True)
    
    # Ensure extracted text folder exists
    os.makedirs(document_processor.EXTRACTED_TEXT_DIR, exist_ok=True)
    
    logger.info(f"Starting application on port {config.PORT}")
    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)
