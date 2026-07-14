from django.test import TestCase
from django.contrib.auth import get_user_model
from documents.models import Document
from procurement.models import PurchaseOrder, Demand
from procurement.workflow import AutomationWorkflow

User = get_user_model()

class WorkflowAutomationTests(TestCase):
    def setUp(self):
        User.objects.create_superuser('admin', 'admin@erp.com', 'password')
        
        self.valid_ai_data = {
            "supplier": {"value": "Global Supplies"},
            "supplier_email": {"value": "sales@global.com"},
            "SKU": {"value": "SKU-999"},
            "quantity": {"value": 50},
            "grand_total": {"value": 5000.00}
        }
        
        self.document = Document.objects.create(
            original_filename="quote_001.pdf",
            document_type="QUOTATION",
            status="VALIDATED",
            extracted_data=self.valid_ai_data
        )

    def test_supplier_source_workflow(self):
        AutomationWorkflow.execute_post_validation(self.document)
        
        # Verify document status updated
        self.document.refresh_from_db()
        self.assertEqual(self.document.status, 'PROCESSED')
        
        # Verify ERP records were created
        self.assertTrue(Demand.objects.exists())
        
        po = PurchaseOrder.objects.first()
        self.assertIsNotNone(po)
        self.assertEqual(po.total_amount, 5000.00)
        self.assertEqual(po.supplier.name, "Global Supplies")
