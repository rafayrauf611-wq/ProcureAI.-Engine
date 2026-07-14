from django.test import TestCase
from documents.models import Document
from documents.validators import ValidationEngine
from suppliers.models import Supplier

class ValidationEngineTests(TestCase):
    def setUp(self):
        self.document = Document.objects.create(
            original_filename="invoice_123.pdf",
            document_type="INVOICE"
        )
        Supplier.objects.create(name="TechCorp", email="billing@techcorp.com")

    def test_math_validation_success(self):
        valid_data = {
            "supplier": {"value": "TechCorp", "confidence": 99},
            "subtotal": {"value": 100.00, "confidence": 95},
            "tax": {"value": 10.00, "confidence": 95},
            "shipping": {"value": 5.00, "confidence": 95},
            "discount": {"value": 0.00, "confidence": 90},
            "grand_total": {"value": 115.00, "confidence": 98}
        }
        
        validator = ValidationEngine(self.document, valid_data)
        is_valid = validator.validate()
        
        self.assertTrue(is_valid)
        self.assertEqual(self.document.status, 'VALIDATED')

    def test_math_validation_failure(self):
        invalid_data = {
            "supplier": {"value": "TechCorp", "confidence": 99},
            "subtotal": {"value": 100.00, "confidence": 95},
            "tax": {"value": 10.00, "confidence": 95},
            "shipping": {"value": 0.00, "confidence": 95},
            "discount": {"value": 0.00, "confidence": 90},
            "grand_total": {"value": 999.00, "confidence": 98} # Deliberate mismatch
        }
        
        validator = ValidationEngine(self.document, invalid_data)
        is_valid = validator.validate()
        
        self.assertFalse(is_valid)
        self.assertEqual(self.document.status, 'REVIEW_REQUIRED')
        self.assertTrue(any("Math mismatch" in err['error'] for err in self.document.validation_errors))
