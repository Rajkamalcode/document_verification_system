document.addEventListener('DOMContentLoaded', function() {
    const processBtn = document.getElementById('processBtn');
    const loadSampleBtn = document.getElementById('loadSampleBtn');
    const documentPayload = document.getElementById('documentPayload');
    const resultsContainer = document.getElementById('resultsContainer');
    const previewContainer = document.getElementById('previewContainer');
    const metadataPanel = document.getElementById('metadataPanel');
    const metadataContent = document.getElementById('metadataContent');
    const ocrTextPanel = document.getElementById('ocrTextPanel');
    const doctrTextBtn = document.getElementById('doctrTextBtn');
    const pytesseractTextBtn = document.getElementById('pytesseractTextBtn');
    const doctrTextContent = document.getElementById('doctrTextContent');
    const pytesseractTextContent = document.getElementById('pytesseractTextContent');
    
    // Helper function to extract filename from path
    function getFilenameFromPath(path) {
        // Handle both Windows and Unix paths
        return path.split(/[\/\\]/).pop();
    }
    
    // Sample payload for demonstration
    const samplePayload = [
        {
            "type": "MODT",
            "location": "modt_example.pdf",
            "fields": {
                "name": "John Doe",
                "application_number": "APP123456",
                "date": "15/06/2023",
                "property_details": "Flat No. 101, Building A, Green Valley, Mumbai"
            }
        },
        {
            "type": "REPAYMENT_KIT",
            "location": "repayment_kit.pdf",
            "fields": {
                "loan_amount": "5,00,000",
                "interest_rate": "8.5%",
                "tenure": "60",
                "emi_amount": "10,250"
            }
        },
        {
            "type": "KYC",
            "location": "kyc_document.pdf",
            "fields": {
                "name": "Jane Smith",
                "address": "123 Main St, Bangalore, Karnataka",
                "id_number": "ABCDE1234F",
                "date_of_birth": "10/05/1985"
            }
        },
        {
            "type": "SANCTION_LETTER",
            "location": "sanction_letter.pdf",
            "fields": {
                "loan_amount": "7,50,000",
                "applicant_name": "Robert Johnson",
                "sanction_date": "20/07/2023",
                "terms": "Tenure: 10 years, Interest: 9.5% p.a."
            }
        }
    ];
    
    // Load sample data
    loadSampleBtn.addEventListener('click', function() {
        documentPayload.value = JSON.stringify(samplePayload, null, 2);
    });
    
    // Process documents
    processBtn.addEventListener('click', function() {
        let payload;
        try {
            payload = JSON.parse(documentPayload.value);
            if (!Array.isArray(payload)) {
                throw new Error('Payload must be an array');
            }
        } catch (e) {
            alert('Invalid JSON payload: ' + e.message);
            return;
        }
        
        // Show loading state
        resultsContainer.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"></div><p class="mt-2">Processing documents...</p></div>';
        
        // Send request to API
        fetch('/api/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            displayResults(data);
        })
        .catch(error => {
            resultsContainer.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
        });
    });
    
    // Toggle between DocTR and Pytesseract text
    doctrTextBtn.addEventListener('click', function() {
        doctrTextContent.style.display = 'block';
        pytesseractTextContent.style.display = 'none';
        doctrTextBtn.classList.add('active');
        pytesseractTextBtn.classList.remove('active');
    });
    
    pytesseractTextBtn.addEventListener('click', function() {
        doctrTextContent.style.display = 'none';
        pytesseractTextContent.style.display = 'block';
        doctrTextBtn.classList.remove('active');
        pytesseractTextBtn.classList.add('active');
    });
    
    // Display processing results
    function displayResults(results) {
        if (!results || results.length === 0) {
            resultsContainer.innerHTML = '<div class="alert alert-info">No results returned</div>';
            return;
        }
        
        let html = '';
        
        results.forEach((result, index) => {
            if (result.error) {
                html += `<div class="alert alert-danger">${result.error}</div>`;
                return;
            }
            
            const docName = getFilenameFromPath(result.document_path);
            
            html += `
            <div class="card document-card mb-3" data-document="${encodeURIComponent(docName)}" data-index="${index}">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h5>${result.document_type}</h5>
                    <span class="badge bg-info">${result.ocr_engine.toUpperCase()}</span>
                </div>
                <div class="card-body">
                    <div class="document-info mb-3">
                        <div class="row">
                            <div class="col-md-6">
                                <p><strong>Document:</strong> ${docName}</p>
                            </div>
                            <div class="col-md-6 text-md-end">
                                <p><strong>Processing Time:</strong> ${result.processing_time.toFixed(2)} seconds</p>
                            </div>
                        </div>
                    </div>
                    
                    <h6 class="mt-3">Field Comparison:</h6>
                    <div class="table-responsive">
                        <table class="table table-bordered table-hover comparison-table">
                            <thead class="table-light">
                                <tr>
                                    <th>Field</th>
                                    <th>Expected</th>
                                    <th>Extracted</th>
                                    <th>Match</th>
                                </tr>
                            </thead>
                            <tbody>`;
            
            // Calculate overall match percentage
            let matchCount = 0;
            let totalFields = Object.keys(result.comparison).length;
            
            for (const [fieldName, comparison] of Object.entries(result.comparison)) {
                const matchClass = comparison.match ? 'table-success' : 'table-danger';
                const iconClass = comparison.match ? 'success' : 'failure';
                const iconType = comparison.match ? 'check-circle' : 'times-circle';
                const similarityPercent = (comparison.similarity * 100).toFixed(1);
                
                if (comparison.match) {
                    matchCount++;
                }
                
                html += `
                <tr class="${matchClass}">
                    <td><strong>${fieldName}</strong></td>
                    <td>${comparison.expected || 'N/A'}</td>
                    <td>${comparison.extracted || 'Not found'}</td>
                    <td>
                        <div class="d-flex align-items-center">
                            <i class="fas fa-${iconType} match-icon ${iconClass} me-2"></i>
                            <div class="progress flex-grow-1" style="height: 8px;">
                                <div class="progress-bar" role="progressbar" 
                                    style="width: ${similarityPercent}%; background-color: ${getColorForSimilarity(comparison.similarity)};" 
                                    aria-valuenow="${similarityPercent}" aria-valuemin="0" aria-valuemax="100">
                                </div>
                            </div>
                            <span class="ms-2 badge ${comparison.match ? 'bg-success' : 'bg-danger'}">${similarityPercent}%</span>
                        </div>
                    </td>
                </tr>`;
            }
            
            const overallMatchPercent = totalFields > 0 ? (matchCount / totalFields * 100).toFixed(1) : 0;
            
            html += `
                            </tbody>
                        </table>
                    </div>
                    
                    <div class="mt-3 d-flex justify-content-between align-items-center">
                        <div>
                            <strong>Overall Match:</strong> ${matchCount}/${totalFields} fields
                        </div>
                        <div class="progress" style="width: 60%;">
                            <div class="progress-bar" role="progressbar" style="width: ${overallMatchPercent}%;" 
                                aria-valuenow="${overallMatchPercent}" aria-valuemin="0" aria-valuemax="100">
                                ${overallMatchPercent}%
                            </div>
                        </div>
                    </div>
                </div>
                <div class="card-footer">
                    <button class="btn btn-sm btn-primary preview-btn" data-document="${encodeURIComponent(docName)}">
                        <i class="fas fa-eye"></i> Preview
                    </button>
                    <button class="btn btn-sm btn-info text-btn" data-document="${encodeURIComponent(docName)}">
                        <i class="fas fa-file-alt"></i> View Text
                    </button>
                </div>
            </div>`;
        });
        
        resultsContainer.innerHTML = html;
        
        // Add event listeners to preview buttons
        document.querySelectorAll('.preview-btn').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.stopPropagation();
                const docName = decodeURIComponent(this.getAttribute('data-document'));
                previewDocument(docName);
                
                // Update active document card
                document.querySelectorAll('.document-card').forEach(card => {
                    card.classList.remove('active');
                });
                this.closest('.document-card').classList.add('active');
            });
        });
        
        // Add event listeners to text view buttons
        document.querySelectorAll('.text-btn').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.stopPropagation();
                const docName = decodeURIComponent(this.getAttribute('data-document'));
                fetchExtractedText(docName);
                
                // Update active document card
                document.querySelectorAll('.document-card').forEach(card => {
                    card.classList.remove('active');
                });
                this.closest('.document-card').classList.add('active');
            });
        });
        
        // Add event listeners to document cards
        document.querySelectorAll('.document-card').forEach(card => {
            card.addEventListener('click', function() {
                const docName = decodeURIComponent(this.getAttribute('data-document'));
                previewDocument(docName);
                
                // Update active document card
                document.querySelectorAll('.document-card').forEach(c => {
                    c.classList.remove('active');
                });
                this.classList.add('active');
            });
        });
    }
    
    // Fetch extracted text for a document
    function fetchExtractedText(filename) {
        // Show loading state
        doctrTextContent.innerHTML = '<div class="text-center"><div class="spinner-border spinner-border-sm" role="status"></div><p class="mt-2">Loading text...</p></div>';
        pytesseractTextContent.innerHTML = '<div class="text-center"><div class="spinner-border spinner-border-sm" role="status"></div><p class="mt-2">Loading text...</p></div>';
        
        // Show OCR text panel
        ocrTextPanel.style.display = 'block';
        
        // Fetch extracted text
        fetch(`/api/extracted-text/${encodeURIComponent(filename)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Update DocTR text
                if (data.doctr) {
                    doctrTextContent.innerHTML = `<pre class="extracted-text">${data.doctr}</pre>`;
                } else {
                    doctrTextContent.innerHTML = '<p class="text-muted">No DocTR text available</p>';
                }
                
                // Update Pytesseract text
                if (data.pytesseract) {
                    pytesseractTextContent.innerHTML = `<pre class="extracted-text">${data.pytesseract}</pre>`;
                } else {
                    pytesseractTextContent.innerHTML = '<p class="text-muted">No Pytesseract text available</p>';
                }
                
                // Show DocTR text by default
                doctrTextBtn.click();
            })
            .catch(error => {
                doctrTextContent.innerHTML = `<div class="alert alert-danger">Error loading text: ${error.message}</div>`;
                pytesseractTextContent.innerHTML = `<div class="alert alert-danger">Error loading text: ${error.message}</div>`;
            });
    }
    
    // Preview document
    function previewDocument(filename) {
        // Show loading state
        previewContainer.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"></div><p class="mt-2">Loading preview...</p></div>';
        
        // Show metadata panel
        metadataPanel.style.display = 'block';
        metadataContent.innerHTML = '<div class="text-center"><div class="spinner-border spinner-border-sm" role="status"></div><p class="mt-2">Loading metadata...</p></div>';
        
        // Fetch metadata
        fetch(`/api/preview/${encodeURIComponent(filename)}`)
            .then(response => response.json())
            .then(data => {
                displayMetadata(data.metadata);
            })
            .catch(error => {
                metadataContent.innerHTML = `<div class="alert alert-danger">Error loading metadata: ${error.message}</div>`;
            });
        
        // For PDF files, use PDF.js to render
        if (filename.toLowerCase().endsWith('.pdf')) {
            const pdfUrl = `/documents/${encodeURIComponent(filename)}`;
            
            // Create canvas for PDF rendering
            previewContainer.innerHTML = `
                <div class="pdf-preview-container">
                    <canvas id="pdfCanvas" class="pdf-preview"></canvas>
                    <div class="mt-2 d-flex justify-content-between">
                        <button id="prevPage" class="btn btn-sm btn-secondary" disabled>
                            <i class="fas fa-chevron-left"></i> Previous
                        </button>
                        <span id="pageInfo">Page 1</span>
                        <button id="nextPage" class="btn btn-sm btn-secondary">
                            <i class="fas fa-chevron-right"></i> Next
                        </button>
                    </div>
                </div>
            `;
            
            // Load and render PDF
            let pdfDoc = null;
            let pageNum = 1;
            let pageRendering = false;
            let pageNumPending = null;
            const canvas = document.getElementById('pdfCanvas');
            const ctx = canvas.getContext('2d');
            
            function renderPage(num) {
                pageRendering = true;
                
                // Update page info
                document.getElementById('pageInfo').textContent = `Page ${num}`;
                
                // Get page
                pdfDoc.getPage(num).then(function(page) {
                    // Adjust canvas size to page
                    const viewport = page.getViewport({ scale: 1.5 });
                    canvas.height = viewport.height;
                    canvas.width = viewport.width;
                    
                    // Render PDF page
                    const renderContext = {
                        canvasContext: ctx,
                        viewport: viewport
                    };
                    
                    const renderTask = page.render(renderContext);
                    
                    // Wait for rendering to finish
                    renderTask.promise.then(function() {
                        pageRendering = false;
                        if (pageNumPending !== null) {
                            // New page rendering is pending
                            renderPage(pageNumPending);
                            pageNumPending = null;
                        }
                    });
                });
                
                // Update button states
                document.getElementById('prevPage').disabled = num <= 1;
                document.getElementById('nextPage').disabled = num >= pdfDoc.numPages;
            }
            
            function queueRenderPage(num) {
                if (pageRendering) {
                    pageNumPending = num;
                } else {
                    renderPage(num);
                }
            }
            
            // Previous page
            document.getElementById('prevPage').addEventListener('click', function() {
                if (pageNum <= 1) return;
                pageNum--;
                queueRenderPage(pageNum);
            });
            
            // Next page
            document.getElementById('nextPage').addEventListener('click', function() {
                if (pageNum >= pdfDoc.numPages) return;
                pageNum++;
                queueRenderPage(pageNum);
            });
            
            // Load PDF
            pdfjsLib.getDocument(pdfUrl).promise.then(function(pdfDoc_) {
                pdfDoc = pdfDoc_;
                document.getElementById('pageInfo').textContent = `Page ${pageNum} of ${pdfDoc.numPages}`;
                renderPage(pageNum);
            }).catch(function(error) {
                previewContainer.innerHTML = `<div class="alert alert-danger">Error loading PDF: ${error.message}</div>`;
            });
        } else if (/\.(jpe?g|png|gif|bmp)$/i.test(filename)) {
            // For images, display directly
            previewContainer.innerHTML = `<img src="/documents/${encodeURIComponent(filename)}" class="img-fluid" alt="Document Preview">`;
        } else {
            // For other file types
            previewContainer.innerHTML = `
                <div class="text-center">
                    <i class="fas fa-file fa-4x text-muted mb-3"></i>
                    <p>Preview not available for this file type</p>
                    <a href="/documents/${encodeURIComponent(filename)}" class="btn btn-primary" target="_blank">
                        <i class="fas fa-download"></i> Download File
                    </a>
                </div>
            `;
        }
    }
    
    // Display metadata
    function displayMetadata(metadata) {
        if (!metadata) {
            metadataContent.innerHTML = '<div class="alert alert-warning">No metadata available</div>';
            return;
        }
        
        let html = '<div class="metadata-list">';
        
        for (const [key, value] of Object.entries(metadata)) {
            if (value) {
                html += `
                <div class="metadata-item">
                    <div class="metadata-label">${formatMetadataKey(key)}</div>
                    <div class="metadata-value">${value}</div>
                </div>`;
            }
        }
        
        html += '</div>';
        metadataContent.innerHTML = html;
    }
    
    // Format metadata key for display
    function formatMetadataKey(key) {
        return key
            .replace(/([A-Z])/g, ' $1') // Add space before capital letters
            .replace(/_/g, ' ') // Replace underscores with spaces
            .replace(/^./, str => str.toUpperCase()); // Capitalize first letter
    }
    
    // Get color based on similarity value
    function getColorForSimilarity(similarity) {
        // Red to green gradient based on similarity
        if (similarity < 0.5) {
            // Red to yellow gradient for 0-0.5
            const g = Math.floor(similarity * 2 * 255);
            return `rgb(255, ${g}, 0)`;
        } else {
            // Yellow to green gradient for 0.5-1
            const r = Math.floor((1 - (similarity - 0.5) * 2) * 255);
            return `rgb(${r}, 255, 0)`;
        }
    }
});
