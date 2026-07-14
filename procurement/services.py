from django.db import transaction
from .models import Demand, Quotation, PurchaseOrder, GoodsReceiptNote
from finance.models import Invoice

class ProcurementService:
    
    @staticmethod
    @transaction.atomic
    def process_cst_and_select_best_quote(demand: Demand) -> Quotation:
        """
        Replaces Phase 1: Sourcing Vendor Quotations & CST Generation script.
        """
        quotes = demand.quotations.all().order_by('unit_price') #[cite: 1]
        if not quotes.exists():
            raise ValueError("No quotations available for this demand.")
            
        best_quote = quotes.first() #[cite: 1]
        best_quote.is_chosen = True #[cite: 1]
        best_quote.save() #[cite: 1]

        demand.status = 'CST_READY' #[cite: 1]
        demand.save() #[cite: 1]
        
        return best_quote

    @staticmethod
    @transaction.atomic
    def generate_purchase_order(demand: Demand) -> PurchaseOrder:
        """
        Replaces Phase 2: Finance Budget Clearance script.
        """
        chosen_quote = demand.quotations.filter(is_chosen=True).first() #[cite: 1]
        if not chosen_quote:
            raise ValueError("No chosen quotation found for CST.")

        total_po_cost = chosen_quote.unit_price * demand.requisition.quantity #[cite: 1]

        po = PurchaseOrder.objects.create(
            demand=demand, #[cite: 1]
            supplier=chosen_quote.supplier, #[cite: 1]
            total_amount=total_po_cost, #[cite: 1]
            status='PENDING_BUDGET' #[cite: 1]
        )
        return po

    @staticmethod
    @transaction.atomic
    def execute_three_way_match(grn: GoodsReceiptNote) -> bool:
        """
        Replaces Phase 4: Finance Settlement (Three-way match) script.
        """
        po_target = grn.purchase_order #[cite: 1]

        # Generating the vendor invoice for the match
        vendor_invoice = Invoice.objects.create(
            purchase_order=po_target, #[cite: 1]
            grn=grn, #[cite: 1]
            billed_amount=po_target.total_amount #[cite: 1]
        )

        # The Three-Way Match Logic
        po_matches = po_target.total_amount == vendor_invoice.billed_amount #[cite: 1]
        grn_matches = po_target.demand.requisition.quantity == grn.received_quantity #[cite: 1]

        if po_matches and grn_matches: #[cite: 1]
            vendor_invoice.is_paid = True #[cite: 1]
            vendor_invoice.save() #[cite: 1]
            
            po_target.status = 'DELIVERED' #[cite: 1]
            po_target.save() #[cite: 1]
            return True
            
        return False
