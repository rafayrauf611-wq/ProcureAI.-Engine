from decimal import Decimal
from django.db.models import Q
from suppliers.models import Supplier
from procurement.models import PurchaseOrder, Quotation
from finance.models import Invoice

class ValidationEngine:
    
    def __init__(self, document, extracted_data: dict):
        self.document = document
        self.data = extracted_data
        self.errors = []
        self.requires_review = False

    def validate(self) -> bool:
        """
        Runs the full suite of validations.
        Returns True if valid, False if review or rejection is required.
        """
        self._check_confidence_scores()
        self._validate_supplier()
        self._validate_math_totals()
        
        if self.document.document_type == 'INVOICE':
            self._validate_invoice_duplicates()
            self._validate_po_presence()

        if self.errors or self.requires_review:
            self.document.status = 'REVIEW_REQUIRED'
            self.document.validation_errors = self.errors
        else:
            self.document.status = 'VALIDATED'
            
        self.document.save()
        return not self.requires_review

    def _check_confidence_scores(self):
        """Flags document if any extracted field has < 85% confidence."""
        for field, details in self.data.items():
            if isinstance(details, dict) and 'confidence' in details:
                if details['confidence'] < 85:
                    self.requires_review = True
                    self.errors.append({
                        "field": field,
                        "error": f"Low confidence ({details['confidence']}%): {details.get('reason', 'N/A')}"
                    })

    def _validate_supplier(self):
        supplier_data = self.data.get('supplier', {})
        supplier_name = supplier_data.get('value')
        
        if not supplier_name:
            self.errors.append({"field": "supplier", "error": "Missing supplier name."})
            self.requires_review = True
            return

        # Check for duplicates or missing records in the database
        supplier_exists = Supplier.objects.filter(name__iexact=supplier_name).exists()
        if not supplier_exists:
            self.errors.append({"field": "supplier", "error": f"Supplier '{supplier_name}' not found in system."})
            self.requires_review = True

    def _validate_math_totals(self):
        """Validates that subtotal + tax + shipping - discount == grand_total."""
        try:
            subtotal = Decimal(str(self.data.get('subtotal', {}).get('value', 0)))
            tax = Decimal(str(self.data.get('tax', {}).get('value', 0)))
            shipping = Decimal(str(self.data.get('shipping', {}).get('value', 0)))
            discount = Decimal(str(self.data.get('discount', {}).get('value', 0)))
            grand_total = Decimal(str(self.data.get('grand_total', {}).get('value', 0)))

            calculated_total = (subtotal + tax + shipping) - discount
            
            if calculated_total != grand_total:
                self.errors.append({
                    "field": "totals", 
                    "error": f"Math mismatch: Calculated {calculated_total} != Stated {grand_total}"
                })
                self.requires_review = True
                
        except (ValueError, TypeError, Decimal.InvalidOperation):
            self.errors.append({"field": "totals", "error": "Invalid numerical values for totals calculation."})
            self.requires_review = True

    def _validate_invoice_duplicates(self):
        inv_number = self.data.get('invoice_number', {}).get('value')
        supplier_name = self.data.get('supplier', {}).get('value')
        
        if inv_number and Invoice.objects.filter(
            purchase_order__supplier__name__iexact=supplier_name, 
            id=inv_number # Assuming invoice_number maps to an external ID or we add an 'invoice_number' field to Invoice
        ).exists():
            self.errors.append({"field": "invoice_number", "error": f"Duplicate invoice detected: {inv_number}"})
            self.requires_review = True

    def _validate_po_presence(self):
        po_number = self.data.get('PO_number', {}).get('value')
        if not po_number:
            self.errors.append({"field": "PO_number", "error": "Missing Purchase Order reference on Invoice."})
            self.requires_review = True
        elif not PurchaseOrder.objects.filter(id=po_number).exists():
            self.errors.append({"field": "PO_number", "error": f"Referenced PO #{po_number} does not exist in the system."})
            self.requires_review = True
