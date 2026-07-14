from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Document(models.Model):
    DOC_TYPES = [
        ('INVOICE', 'Invoice'),
        ('PO', 'Purchase Order'),
        ('QUOTATION', 'Quotation'),
        ('RFQ', 'RFQ'),
        ('DELIVERY_CHALLAN', 'Delivery Challan'),
        ('GRN', 'Goods Receipt Note'),
        ('CONTRACT', 'Contract'),
        ('UNKNOWN', 'Unknown')
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending Extraction'),
        ('REVIEW_REQUIRED', 'Review Required'),
        ('VALIDATED', 'Validated'),
        ('PROCESSED', 'Processed into ERP'),
        ('REJECTED', 'Rejected')
    ]

    uploader = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    file = models.FileField(upload_to='uploads/%Y/%m/%d/')
    original_filename = models.CharField(max_length=255)
    
    document_type = models.CharField(max_length=50, choices=DOC_TYPES, default='UNKNOWN')
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='PENDING')
    
    # Store the exact JSON returned by the AI
    extracted_data = models.JSONField(null=True, blank=True)
    
    # Validation error logs for the frontend to display
    validation_errors = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'documents_document'
