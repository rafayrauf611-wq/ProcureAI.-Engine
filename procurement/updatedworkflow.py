from django.db import transaction
from django.contrib.auth import get_user_model
from inventory.models import Item
from suppliers.models import Supplier
from procurement.models import StoreRequisition, Demand, Quotation, PurchaseOrder, GoodsReceiptNote
from finance.models import Invoice
from procurement.approvals import ApprovalService
from documents.models import Document
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class AutomationWorkflow:
    
    @staticmethod
    @transaction.atomic
    def execute_post_validation(document: Document):
        """
        Routes the validated document to the correct ERP generation workflow.
        """
        if document.status != 'VALIDATED':
            raise ValueError(f"Document {document.id} is not in VALIDATED status.")

        doc_type = document.document_type
        data = document.extracted_data

        if doc_type == 'INVOICE':
            AutomationWorkflow._process_invoice(data)
        elif doc_type == 'PO' or doc_type == 'QUOTATION':
            AutomationWorkflow._process_supplier_source(data)
        elif doc_type == 'GRN':
            AutomationWorkflow._process_receipt(data)
            
        document.status = 'PROCESSED'
        document.save(update_fields=['status'])
        logger.info(f"Successfully processed Document {document.id} into ERP.")

    @staticmethod
    def _process_supplier_source(data: dict):
        """
        End-to-end automation: Item -> Req -> Demand -> Quote -> PO.
        """
        admin_user = User.objects.filter(is_superuser=True).first()
        
        # 1. Resolve or Create Supplier & Item
        supplier_name = data.get("supplier", {}).get("value", "Unknown Supplier")
        supplier_email = data.get("supplier_email", {}).get("value", "ai@unknown.com")
        supplier, _ = Supplier.objects.get_or_create(name=supplier_name, defaults={'email': supplier_email})
        
        sku = data.get("SKU", {}).get("value", "SKU-AI-GEN")
        item, _ = Item.objects.get_or_create(sku=sku, defaults={'name': 'AI Extracted Item'})

        # 2. Build Requisition & Demand
        qty = int(data.get("quantity", {}).get("value", 1))
        req = StoreRequisition.objects.create(requested_by=admin_user, item=item, quantity=qty, status='DEMAND_ADDED')
        demand = Demand.objects.create(requisition=req, status='CST_READY')

        # 3. Create Quotation & PO
        total = float(data.get("grand_total", {}).get("value", 0.0))
        unit_price = total / qty if qty > 0 else 0
        
        quote = Quotation.objects.create(
            demand=demand, supplier=supplier, unit_price=unit_price, delivery_days=7, is_chosen=True
        )
        
        po = PurchaseOrder.objects.create(
            demand=demand, supplier=supplier, total_amount=total, status='PENDING_BUDGET'
        )

        # 4. Trigger Dynamic Rule Engine for Approval
        ApprovalService.route_for_approval(po)

    @staticmethod
    def _process_receipt(data: dict):
        """Automates GRN generation from an extracted Delivery Challan/GRN."""
        po_number = data.get("PO_number", {}).get("value")
        qty = int(data.get("quantity", {}).get("value", 0))
        
        try:
            po = PurchaseOrder.objects.get(id=po_number)
            GoodsReceiptNote.objects.create(
                purchase_order=po,
                received_quantity=qty,
                qad_status='PENDING'
            )
        except PurchaseOrder.DoesNotExist:
            logger.error(f"Cannot generate GRN: PO #{po_number} does not exist.")

    @staticmethod
    def _process_invoice(data: dict):
        """Automates Vendor Invoice generation for the Three-Way Match."""
        po_number = data.get("PO_number", {}).get("value")
        grand_total = float(data.get("grand_total", {}).get("value", 0.0))
        
        try:
            po = PurchaseOrder.objects.get(id=po_number)
            grn = GoodsReceiptNote.objects.filter(purchase_order=po).last()
            
            if grn:
                Invoice.objects.create(
                    purchase_order=po,
                    grn=grn,
                    billed_amount=grand_total,
                    is_paid=False
                )
        except PurchaseOrder.DoesNotExist:
            logger.error(f"Cannot generate Invoice: PO #{po_number} does not exist.")
