import os
import random
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

def generate_modt_sample():
    """Generate a sample MODT document"""
    filename = "documents/modt_example.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=1,  # Center
        spaceAfter=20
    )
    
    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading2'],
        fontSize=12,
        spaceAfter=10
    )
    
    normal_style = styles['Normal']
    
    # Content elements
    elements = []
    
    # Title
    # Title
    elements.append(Paragraph("MEMORANDUM OF DEPOSIT OF TITLE DEEDS", title_style))
    
    # Date
    elements.append(Paragraph("Date: 15/06/2023", normal_style))
    elements.append(Spacer(1, 12))
    
    # Borrower details
    elements.append(Paragraph("BORROWER DETAILS", heading_style))
    elements.append(Paragraph("Name: Rajkamal", normal_style))
    elements.append(Paragraph("Application No: APP123456", normal_style))
    elements.append(Paragraph("Address: 123 Main Street, Mumbai, Maharashtra", normal_style))
    elements.append(Spacer(1, 12))
    
    # Loan details
    elements.append(Paragraph("LOAN DETAILS", heading_style))
    elements.append(Paragraph("Loan Amount: Rs. 50,00,000", normal_style))
    elements.append(Paragraph("Interest Rate: 8.5% per annum", normal_style))
    elements.append(Paragraph("Tenure: 240 months", normal_style))
    elements.append(Spacer(1, 12))
    
    # Property details
    elements.append(Paragraph("PROPERTY DETAILS", heading_style))
    elements.append(Paragraph("Property Address: Flat No. 101, Building A, Green Valley, Mumbai", normal_style))
    elements.append(Paragraph("Property Type: Residential Apartment", normal_style))
    elements.append(Paragraph("Area: 1200 sq. ft.", normal_style))
    elements.append(Spacer(1, 20))
    
    # Agreement text
    agreement_text = """
    THIS MEMORANDUM OF DEPOSIT OF TITLE DEEDS is made on the date mentioned above between the Borrower and the Lender.
    
    WHEREAS the Borrower has requested the Lender to grant a loan facility and the Lender has agreed to grant such facility on the terms and conditions contained in the Loan Agreement.
    
    NOW THIS DEED WITNESSETH that in consideration of the Lender granting the loan facility to the Borrower, the Borrower hereby deposits with the Lender the title deeds relating to the Property as security for the due repayment of the loan amount together with interest, costs, charges and expenses.
    """
    elements.append(Paragraph(agreement_text, normal_style))
    elements.append(Spacer(1, 20))
    
    # Signatures
    elements.append(Paragraph("SIGNED AND DELIVERED", heading_style))
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("_________________________", normal_style))
    elements.append(Paragraph("Signature of Borrower", normal_style))
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("_________________________", normal_style))
    elements.append(Paragraph("Signature of Lender", normal_style))
    
    # Build the document
    doc.build(elements)
    print(f"Generated {filename}")

def generate_repayment_kit():
    """Generate a sample Repayment Kit document"""
    filename = "documents/repayment_kit.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=1,  # Center
        spaceAfter=20
    )
    
    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading2'],
        fontSize=12,
        spaceAfter=10
    )
    
    normal_style = styles['Normal']
    
    # Content elements
    elements = []
    
    # Title
    elements.append(Paragraph("LOAN REPAYMENT KIT", title_style))
    elements.append(Spacer(1, 12))
    
    # Customer details
    elements.append(Paragraph("CUSTOMER DETAILS", heading_style))
    elements.append(Paragraph("Name: Rajkamal", normal_style))
    elements.append(Paragraph("Loan Account Number: LOAN123456", normal_style))
    elements.append(Paragraph("Address: 123 Main Street, Mumbai, Maharashtra", normal_style))
    elements.append(Spacer(1, 12))
    
    # Loan details
    elements.append(Paragraph("LOAN DETAILS", heading_style))
    elements.append(Paragraph("Loan Amount: Rs. 5,00,000", normal_style))
    elements.append(Paragraph("Interest Rate: 8.5%", normal_style))
    elements.append(Paragraph("Tenure: 60 months", normal_style))
    elements.append(Paragraph("EMI Amount: Rs. 10,250", normal_style))
    elements.append(Paragraph("EMI Due Date: 5th of every month", normal_style))
    elements.append(Spacer(1, 12))
    
    # Repayment methods
    elements.append(Paragraph("REPAYMENT METHODS", heading_style))
    
    # Create a table for repayment methods
    data = [
        ["Method", "Details"],
        ["ECS/NACH", "Automatic deduction from your bank account"],
        ["Online Banking", "Pay through your bank's net banking facility"],
        ["Mobile App", "Pay through our mobile application"],
        ["Cheque", "Submit post-dated cheques to our branch"]
    ]
    
    table = Table(data, colWidths=[100, 350])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 20))
    
    # Important notes
    elements.append(Paragraph("IMPORTANT NOTES", heading_style))
    notes = """
    1. Please ensure sufficient balance in your account on the EMI due date.
    2. Late payment will attract penal interest at 2% per month on the overdue amount.
    3. Prepayment charges: 2% of the principal amount prepaid.
    4. For any queries, please contact our customer care at 1800-123-4567.
    """
    elements.append(Paragraph(notes, normal_style))
    
    # Build the document
    doc.build(elements)
    print(f"Generated {filename}")

def generate_kyc_document():
    """Generate a sample KYC document"""
    filename = "documents/kyc_document.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=1,  # Center
        spaceAfter=20
    )
    
    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading2'],
        fontSize=12,
        spaceAfter=10
    )
    
    normal_style = styles['Normal']
    
    # Content elements
    elements = []
    
    # Title
    elements.append(Paragraph("KNOW YOUR CUSTOMER (KYC) FORM", title_style))
    elements.append(Spacer(1, 12))
    
    # Personal details
    elements.append(Paragraph("PERSONAL DETAILS", heading_style))
    elements.append(Paragraph("Name: Jane Smith", normal_style))
    elements.append(Paragraph("Date of Birth: 10/05/1985", normal_style))
    elements.append(Paragraph("Gender: Female", normal_style))
    elements.append(Paragraph("Nationality: Indian", normal_style))
    elements.append(Spacer(1, 12))
    
    # Contact details
    elements.append(Paragraph("CONTACT DETAILS", heading_style))
    elements.append(Paragraph("Address: 123 Main St, Bangalore, Karnataka", normal_style))
    elements.append(Paragraph("Mobile: +91 9876543210", normal_style))
    elements.append(Paragraph("Email: jane.smith@example.com", normal_style))
    elements.append(Spacer(1, 12))
    
    # ID details
    elements.append(Paragraph("IDENTIFICATION DETAILS", heading_style))
    elements.append(Paragraph("PAN: ABCDE1234F", normal_style))
    elements.append(Paragraph("Aadhaar: 1234 5678 9012", normal_style))
    elements.append(Paragraph("Passport Number: Z1234567", normal_style))
    elements.append(Spacer(1, 12))
    
    # Bank details
    elements.append(Paragraph("BANK ACCOUNT DETAILS", heading_style))
    elements.append(Paragraph("Bank Name: State Bank of India", normal_style))
    elements.append(Paragraph("Account Number: 12345678901", normal_style))
    elements.append(Paragraph("IFSC Code: SBIN0001234", normal_style))
    elements.append(Paragraph("Account Type: Savings", normal_style))
    elements.append(Spacer(1, 20))
    
    # Declaration
    elements.append(Paragraph("DECLARATION", heading_style))
    declaration = """
    I hereby declare that the information provided above is true and correct to the best of my knowledge.
    I understand that any false statement may result in rejection of my application or termination of services.
    """
    elements.append(Paragraph(declaration, normal_style))
    elements.append(Spacer(1, 20))
    
    # Signature
    elements.append(Paragraph("Date: 15/06/2023", normal_style))
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("_________________________", normal_style))
    elements.append(Paragraph("Signature of Applicant", normal_style))
    
    # Build the document
    doc.build(elements)
    print(f"Generated {filename}")

def generate_sanction_letter():
    """Generate a sample Sanction Letter"""
    filename = "documents/sanction_letter.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=1,  # Center
        spaceAfter=20
    )
    
    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading2'],
        fontSize=12,
        spaceAfter=10
    )
    
    normal_style = styles['Normal']
    
    # Content elements
    elements = []
    
    # Title
    elements.append(Paragraph("LOAN SANCTION LETTER", title_style))
    elements.append(Spacer(1, 12))
    
    # Reference and date
    elements.append(Paragraph("Ref: SAN/2023/07/123", normal_style))
    elements.append(Paragraph("Date: 20/07/2023", normal_style))
    elements.append(Spacer(1, 12))
    
    # Addressee
    elements.append(Paragraph("To,", normal_style))
    elements.append(Paragraph("Mr. Robert Johnson", normal_style))
    elements.append(Paragraph("456 Park Avenue", normal_style))
    elements.append(Paragraph("Delhi, 110001", normal_style))
    elements.append(Spacer(1, 20))
    
    # Subject
    elements.append(Paragraph("Subject: Sanction of Home Loan", normal_style))
    elements.append(Spacer(1, 12))
    
    # Salutation
    elements.append(Paragraph("Dear Mr. Johnson,", normal_style))
    elements.append(Spacer(1, 12))
    
    # Body
    body_text = """
    We are pleased to inform you that your application for a Home Loan has been approved. The details of the sanctioned loan are as follows:
    """
    elements.append(Paragraph(body_text, normal_style))
    elements.append(Spacer(1, 12))
    
    # Loan details
    elements.append(Paragraph("LOAN DETAILS", heading_style))
    elements.append(Paragraph("Loan Amount: Rs. 7,50,000", normal_style))
    elements.append(Paragraph("Interest Rate: 9.5% per annum (floating)", normal_style))
    elements.append(Paragraph("Tenure: 10 years (120 months)", normal_style))
    elements.append(Paragraph("EMI Amount: Rs. 9,800 (approximate)", normal_style))
    elements.append(Paragraph("Processing Fee: Rs. 15,000 + GST", normal_style))
    elements.append(Spacer(1, 12))
    
    # Terms and conditions
    elements.append(Paragraph("TERMS AND CONDITIONS", heading_style))
    terms = """
    1. The loan is subject to execution of loan agreement and other security documents.
    2. The property should be clear of all encumbrances and charges.
    3. The loan disbursement will be made directly to the seller/builder.
    4. The borrower must obtain adequate insurance coverage for the property.
    5. The bank reserves the right to recall the loan in case of any default in repayment.
    """
    elements.append(Paragraph(terms, normal_style))
    elements.append(Spacer(1, 20))
    
    # Closing
    closing_text = """
    This sanction letter is valid for a period of 60 days from the date of issue. Please visit our nearest branch along with the original property documents to complete the loan formalities.
    
    We look forward to a long and mutually beneficial relationship.
    """
    elements.append(Paragraph(closing_text, normal_style))
    elements.append(Spacer(1, 20))
    
    # Signature
    elements.append(Paragraph("Yours sincerely,", normal_style))
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("_________________________", normal_style))
    elements.append(Paragraph("Loan Officer", normal_style))
    elements.append(Paragraph("ABC Bank Ltd.", normal_style))
    
    # Build the document
    doc.build(elements)
    print(f"Generated {filename}")

def main():
    # Create documents directory if it doesn't exist
    os.makedirs("documents", exist_ok=True)
    
    # Generate sample documents
    generate_modt_sample()
    generate_repayment_kit()
    generate_kyc_document()
    generate_sanction_letter()
    
    print("Sample documents generated successfully!")

if __name__ == "__main__":
    main()
